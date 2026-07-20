"""
FastAPI backend — 기존 modules/ 로직을 그대로 재사용해서 REST API로 노출.
Streamlit 앱(app.py)과 이 API는 같은 modules/를 공유한다 (로직 중복 없음).

실행: uvicorn api.main:app --reload --port 8000  (apartment_notice_analyzer/ 에서)
"""
import os
import sys
import tempfile
import uuid
from collections import defaultdict
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.ocr_parser import extract_text
from modules.section_splitter import split_sections
from modules.toxic_clause import analyze_toxic_clauses
from modules.unit_analysis import parse_supply_price_table, parse_supply_summary
from modules.surrounding_environment import KakaoLocalClient
from modules.school_district import build_school_district_report
from modules.hoa_disclosure_report import (
    extract_disclosure_items,
    extract_disclosure_items_from_text,
    extract_loan_regulation_notice,
)
from modules.notice_metadata import extract_project_address, extract_sample_house_address
from modules.report_generator import generate_report

load_dotenv()

app = FastAPI(title="아파트 모집공고문 분석 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("WEB_ORIGIN", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = os.path.join(tempfile.gettempdir(), "notice_analyzer_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


@app.get("/api/status")
def status():
    return {
        "claude_api": bool(os.getenv("ANTHROPIC_API_KEY")),
        "law_go_kr": bool(os.getenv("LAW_GO_KR_OC")),
        "clova_ocr": bool(os.getenv("CLOVA_OCR_API_URL")),
        "kakao_local": bool(os.getenv("KAKAO_REST_API_KEY")),
        "neis": bool(os.getenv("NEIS_API_KEY")),
    }


def _safe(fn, *args, **kwargs):
    """섹션 하나 실패해도 나머지는 계속 — 에러 메시지를 결과에 담아 반환."""
    try:
        return fn(*args, **kwargs), None
    except Exception as e:  # noqa: BLE001 — 사용자에게 원인 그대로 보여주기 위함
        return None, str(e)


@app.post("/api/analyze")
async def analyze(
    complex_name: str = Form("○○아파트 (예시)"),
    address: str = Form(""),
    use_dummy: bool = Form(False),
    run_toxic: bool = Form(True),
    run_unit: bool = Form(True),
    run_env: bool = Form(False),
    run_school: bool = Form(False),
    run_disclosure: bool = Form(True),
    file: Optional[UploadFile] = File(None),
):
    errors: dict[str, str] = {}
    file_bytes = await file.read() if file is not None else None

    if use_dummy or file_bytes is None:
        dummy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_notice.txt")
        with open(dummy_path, encoding="utf-8") as f:
            dummy_text = f.read()
        notice_text = extract_text(pdf_bytes=None, dummy_text=dummy_text)
        used_dummy = True
    else:
        notice_text = extract_text(pdf_bytes=file_bytes)
        used_dummy = False

    if not address:
        address = extract_sample_house_address(notice_text) or extract_project_address(notice_text) or ""

    matched_sections, err = _safe(split_sections, notice_text)
    matched_sections = matched_sections or []
    if err:
        errors["sections"] = err

    loan_notice = extract_loan_regulation_notice(notice_text)

    toxic_results = None
    if run_toxic:
        toxic_results, err = _safe(analyze_toxic_clauses, matched_sections)
        if err:
            errors["toxic"] = err

    unit_rows = supply_summary = None
    if run_unit:
        (unit_rows, err) = _safe(parse_supply_price_table, notice_text)
        if err:
            errors["unit"] = err
        supply_summary, _ = _safe(parse_supply_summary, notice_text)

    environment_survey = None
    if run_env:
        client = KakaoLocalClient()
        if not client.is_configured:
            errors["environment"] = "KAKAO_REST_API_KEY 미설정"
        elif not address:
            errors["environment"] = "주소 필요"
        else:
            environment_survey, err = _safe(client.full_survey, address)
            if err:
                errors["environment"] = err

    school_report = None
    if run_school:
        client = KakaoLocalClient()
        if not client.is_configured or not address:
            errors["school"] = "카카오 API 키/주소 확인 필요"
        else:
            coords, err = _safe(client.geocode_address, address)
            if err:
                errors["school"] = err
            elif coords:
                nearby_schools, err = _safe(client.search_category_nearby, *coords, "학교")
                if err:
                    errors["school"] = err
                else:
                    school_report, err = _safe(build_school_district_report, address, nearby_schools)
                    if err:
                        errors["school"] = err
                    elif school_report:
                        school_report["nearby_schools"] = nearby_schools

    disclosure_items = None
    if run_disclosure:
        if not used_dummy and file_bytes is not None:
            disclosure_items, err = _safe(extract_disclosure_items, file_bytes)
        else:
            disclosure_items, err = _safe(extract_disclosure_items_from_text, notice_text)
        if err:
            errors["disclosure"] = err

    disclosure_grouped = []
    if disclosure_items:
        grouped = defaultdict(list)
        for it in disclosure_items:
            grouped[it["category"]].append(it)
        disclosure_grouped = [{"category": cat, "items": its} for cat, its in grouped.items()]

    report_id = uuid.uuid4().hex
    report_path = os.path.join(REPORTS_DIR, f"{report_id}.docx")
    try:
        generate_report(
            complex_name, matched_sections, report_path,
            toxic_results=toxic_results, unit_rows=unit_rows,
            environment_survey=environment_survey, school_report=school_report,
            disclosure_items=disclosure_items, loan_notice=loan_notice,
            price_rows=unit_rows, supply_summary=supply_summary,
        )
        report_ready = True
    except Exception as e:  # noqa: BLE001
        errors["report"] = str(e)
        report_ready = False

    return {
        "used_dummy": used_dummy,
        "address": address,
        "notice_text": notice_text,
        "loan_notice": loan_notice,
        "matched_sections": matched_sections,
        "toxic_results": toxic_results,
        "unit_rows": unit_rows,
        "supply_summary": supply_summary,
        "environment_survey": environment_survey,
        "school_report": school_report,
        "disclosure_grouped": disclosure_grouped,
        "errors": errors,
        "report_id": report_id if report_ready else None,
        "complex_name": complex_name,
    }


@app.get("/api/report/{report_id}")
def download_report(report_id: str, complex_name: str = "검수리포트"):
    path = os.path.join(REPORTS_DIR, f"{report_id}.docx")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{complex_name}_검수리포트.docx",
    )
