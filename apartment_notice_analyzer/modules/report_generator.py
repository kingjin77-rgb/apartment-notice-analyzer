"""
분석 결과 -> 입주민 배포용 docx 리포트 생성

Phase 1: 법령 조항 대조
Phase 1.5 (병렬 확장): 독소조항, 동별/세대별 체크, 주변환경 조사, 학군조사
각 섹션은 데이터가 없으면 건너뛰고, 있으면만 추가되는 방식으로 설계.
"""
from datetime import date
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
import tempfile
import os


def _add_law_match_section(doc: Document, matched_sections: list[dict]) -> None:
    doc.add_heading("1. 조항별 법령 대조 결과", level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = "공고문 조항", "관련 카테고리", "비고"
    for item in matched_sections:
        row = table.add_row().cells
        row[0].text = item.get("text", "")
        row[1].text = ", ".join(item.get("categories", [])) or "-"
        row[2].text = "검토 필요" if item.get("categories") else ""


def _add_toxic_clause_section(doc: Document, toxic_results: list[dict]) -> None:
    doc.add_page_break()
    doc.add_heading("2. 독소조항 1차 스크리닝", level=1)
    p = doc.add_paragraph(
        "※ 아래 결과는 표준계약서 대비 자동 1차 스크리닝이며, 최종 법률 판단이 아닙니다. "
        "변호사 검토 후 확정됩니다."
    )
    p.runs[0].italic = True

    flagged = [r for r in toxic_results if r.get("risk_level") in ("검토 필요", "높음")]
    if not flagged:
        doc.add_paragraph("자동 스크리닝 기준으로 특이사항이 발견되지 않았습니다.")
        return

    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 2"
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = "조항", "위험도", "사유"
    for item in flagged:
        row = table.add_row().cells
        row[0].text = item.get("text", "")
        row[1].text = item.get("risk_level", "")
        row[2].text = item.get("reason", "")


def _add_unit_section(doc: Document, unit_rows: list[dict]) -> None:
    if not unit_rows:
        return
    doc.add_page_break()
    doc.add_heading("3. 동별/세대별 체크 (타입별 공급금액)", level=1)
    doc.add_paragraph(
        "※ 향(방위) 정보는 모집공고문 표에 없으며, 평면도 이미지 분석이 별도로 필요합니다."
    )
    table = doc.add_table(rows=1, cols=5)
    table.style = "Light Grid Accent 3"
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text, hdr[4].text = (
        "타입", "동/호", "층구분", "세대수", "공급금액(계)"
    )
    for row_data in unit_rows:
        row = table.add_row().cells
        row[0].text = row_data.get("타입", "-") or "-"
        row[1].text = "; ".join(row_data.get("동호그룹", [])) or "-"
        row[2].text = row_data.get("층구분", "-")
        row[3].text = row_data.get("세대수", "-")
        row[4].text = row_data.get("공급금액계", "-")


def _add_environment_section(doc: Document, environment_survey: dict) -> None:
    if not environment_survey:
        return
    doc.add_page_break()
    doc.add_heading("4. 주변환경 조사", level=1)

    if "error" in environment_survey:
        doc.add_paragraph(environment_survey["error"])
        return

    doc.add_heading("편의시설", level=2)
    for category, places in environment_survey.get("편의시설", {}).items():
        doc.add_paragraph(f"{category}: {len(places)}곳 (반경 내)", style="List Bullet")

    nuisance = environment_survey.get("유의시설", {})
    doc.add_heading("유의시설", level=2)
    if not nuisance:
        doc.add_paragraph("반경 내 검색된 유의시설 없음")
    else:
        for keyword, hits in nuisance.items():
            doc.add_paragraph(f"{keyword}: {len(hits)}곳 발견 — 거리 확인 필요", style="List Bullet")


def _add_school_section(doc: Document, school_report: dict) -> None:
    if not school_report:
        return
    doc.add_page_break()
    doc.add_heading("5. 학군조사", level=1)
    p = doc.add_paragraph(school_report.get("disclaimer", ""))
    if p.runs:
        p.runs[0].italic = True

    schools = school_report.get("objective_data", [])
    if not schools:
        doc.add_paragraph("반경 내 검색된 학교 정보 없음")
        return

    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid Accent 4"
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text = "학교명", "거리(참고)"
    for s in schools:
        row = table.add_row().cells
        row[0].text = s.get("place_name", "-")
        row[1].text = f"{s.get('distance', '-')}m" if s.get("distance") else "-"



def _add_loan_regulation_callout(doc: Document, loan_notice: dict) -> None:
    if not loan_notice:
        return
    box = doc.add_paragraph()
    run = box.add_run(f"⚠ 대출규제 적용 기준일: {loan_notice['date']}")
    run.bold = True
    run.font.size = Pt(12)
    detail = doc.add_paragraph(loan_notice.get("text", ""))
    if detail.runs:
        detail.runs[0].font.size = Pt(9)
    doc.add_paragraph()



def _add_charts_section(doc: Document, price_rows: list, summary: dict, disclosure_items: list) -> None:
    if not (price_rows or summary or disclosure_items):
        return
    from modules import chart_generator as cg

    doc.add_page_break()
    doc.add_heading("7. 종합 분석 그래프", level=1)
    doc.add_paragraph(
        "※ 아래 그래프는 공고문에 명시된 실제 수치만 사용했습니다(외부 시세 API 미사용, 100% 공고문 근거)."
    )

    tmp_dir = tempfile.mkdtemp(prefix="jl_charts_")

    if summary:
        p1 = os.path.join(tmp_dir, "special_breakdown.png")
        cg.chart_special_supply_breakdown(summary, p1)
        doc.add_picture(p1, width=Inches(5.5))

        p2 = os.path.join(tmp_dir, "special_vs_general.png")
        cg.chart_special_vs_general(summary, p2)
        doc.add_picture(p2, width=Inches(4.5))

    if price_rows:
        p3 = os.path.join(tmp_dir, "units_by_type.png")
        cg.chart_units_by_type(price_rows, p3)
        doc.add_picture(p3, width=Inches(5.5))

        p4 = os.path.join(tmp_dir, "avg_price.png")
        cg.chart_avg_price_by_type(price_rows, p4)
        doc.add_picture(p4, width=Inches(5.5))

        # 세대수가 가장 많은 타입 하나를 골라 층별 가격 추이 표시
        from collections import Counter
        type_counts = Counter(r["타입"] for r in price_rows)
        main_type = type_counts.most_common(1)[0][0] if type_counts else None
        if main_type:
            p5 = os.path.join(tmp_dir, "floor_price.png")
            result = cg.chart_price_by_floor(price_rows, main_type, p5)
            if result:
                doc.add_picture(p5, width=Inches(5.5))

    if disclosure_items:
        p6 = os.path.join(tmp_dir, "severity.png")
        cg.chart_disclosure_severity(disclosure_items, p6)
        doc.add_picture(p6, width=Inches(4.5))


def _add_hoa_disclosure_section(doc: Document, disclosure_items: list) -> None:
    if not disclosure_items:
        return
    doc.add_page_break()
    doc.add_heading("6. 사전고지 유의사항 (입예협 개선요구 검토용)", level=1)
    p = doc.add_paragraph(
        "※ 공고문에 명시되어 법적으로는 문제없으나, 분량이 많아 개별 입주민이 놓치기 쉬운 "
        "환경권·생활불편 관련 조항입니다. 상/중/하는 법적 심각도가 아니라 입예협이 먼저 "
        "챙겨볼 우선순위 기준이며, 법무법인 검토의견은 시공사·시행사에 요청할 수 있는 확인·개선사항 "
        "제안입니다. 키워드 기반 추출이므로 관련 없는 항목이 섞여 있을 수 있어 검토 후 선별이 필요합니다."
    )
    if p.runs:
        p.runs[0].italic = True

    from collections import defaultdict
    grouped = defaultdict(list)
    for item in disclosure_items:
        grouped[item["category"]].append(item)

    severity_order = {"상": 0, "중": 1, "하": 2}
    for category, items in grouped.items():
        items = sorted(items, key=lambda x: severity_order.get(x.get("severity", "하"), 9))
        doc.add_heading(category, level=2)
        table = doc.add_table(rows=1, cols=5)
        table.style = "Light Grid Accent 5"
        hdr = table.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text, hdr[4].text = (
            "심각도", "페이지", "내용", "비고", "법무법인 검토의견"
        )
        for it in items:
            row = table.add_row().cells
            row[0].text = it.get("severity", "-")
            row[1].text = str(it.get("page", "-"))
            row[2].text = it.get("text", "")
            row[3].text = "이의제기 불가 문구 포함" if it.get("has_waiver_phrase") else ""
            row[4].text = it.get("jl_opinion", "")


def generate_report(
    complex_name: str,
    matched_sections: list[dict],
    output_path: str,
    toxic_results=None,
    unit_rows=None,
    environment_survey=None,
    school_report=None,
    disclosure_items=None,
    loan_notice=None,
    price_rows=None,
    supply_summary=None,
) -> str:
    doc = Document()

    title = doc.add_heading(f"{complex_name} 모집공고문 검수 리포트", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"작성일: {date.today().isoformat()}   |   법무법인 제이엘 동탄분사무소").italic = True

    doc.add_paragraph()
    notice_p = doc.add_paragraph(
        "※ 본 리포트는 자동 분석 결과이며, 법률적 최종 판단은 담당 변호사 검토를 거쳐 확정됩니다."
    )
    notice_p.runs[0].font.size = Pt(9)

    if loan_notice:
        _add_loan_regulation_callout(doc, loan_notice)

    _add_law_match_section(doc, matched_sections)

    if toxic_results:
        _add_toxic_clause_section(doc, toxic_results)
    if unit_rows:
        _add_unit_section(doc, unit_rows)
    if environment_survey:
        _add_environment_section(doc, environment_survey)
    if school_report:
        _add_school_section(doc, school_report)
    if disclosure_items:
        _add_hoa_disclosure_section(doc, disclosure_items)

    _add_charts_section(doc, price_rows or [], supply_summary or {}, disclosure_items or [])

    doc.save(output_path)
    return output_path
