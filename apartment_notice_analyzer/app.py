"""
아파트 모집공고문 분석 프로그램

Phase 1: 법령 조항 대조 (완료)
병렬 확장: 독소조항 / 동별·세대별 체크 / 주변환경 조사 / 학군조사

실행: streamlit run app.py
"""
import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from modules.ocr_parser import extract_text
from modules.section_splitter import split_sections
from modules.toxic_clause import analyze_toxic_clauses
from modules.unit_analysis import parse_supply_price_table, parse_supply_summary
from modules.surrounding_environment import KakaoLocalClient
from modules.school_district import build_school_district_report
from modules.hoa_disclosure_report import extract_disclosure_items, extract_disclosure_items_from_text, extract_loan_regulation_notice
from modules.notice_metadata import extract_project_address, extract_sample_house_address
from modules.report_generator import generate_report

load_dotenv()

st.set_page_config(page_title="모집공고문 분석", layout="wide")

_theme_css_path = os.path.join(os.path.dirname(__file__), "assets", "notion_theme.css")
with open(_theme_css_path, encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.title("아파트 모집공고문 분석 프로그램")

with st.sidebar:
    st.subheader("설정 상태")
    st.write("Claude API:", "✅" if os.getenv("ANTHROPIC_API_KEY") else "❌ (키워드 규칙 대체)")
    st.write("국가법령정보 API:", "✅" if os.getenv("LAW_GO_KR_OC") else "❌")
    st.write("Clova OCR:", "✅" if os.getenv("CLOVA_OCR_API_URL") else "❌ (스캔본 불가)")
    st.write("카카오 로컬 API:", "✅" if os.getenv("KAKAO_REST_API_KEY") else "❌ (주변환경 조사 불가)")
    st.write("NEIS API:", "✅" if os.getenv("NEIS_API_KEY") else "❌ (학군조사 불가)")

complex_name = st.text_input("단지명", value="○○아파트 (예시)")
address = st.text_input(
    "주소 (주변환경/학군 조사용 — 비워두면 공고문에서 자동 추출 시도)",
    placeholder="예: 경기도 화성시 동탄순환대로 127-5",
)

uploaded_file = st.file_uploader("모집공고문 PDF 업로드", type=["pdf"])
use_dummy = st.checkbox("PDF 없이 더미 샘플로 테스트", value=uploaded_file is None)

run_toxic = st.checkbox("독소조항 1차 스크리닝 실행", value=True)
run_unit = st.checkbox("동별/세대별 체크 실행", value=True)
run_env = st.checkbox("주변환경 조사 실행 (카카오 API 필요)", value=False)
run_school = st.checkbox("학군조사 실행 (카카오+NEIS API 필요)", value=False)
run_disclosure = st.checkbox("사전고지 유의사항 추출 (입예협 개선요구용)", value=True)

if st.button("분석 시작", type="primary"):
    if use_dummy or uploaded_file is None:
        dummy_path = os.path.join(os.path.dirname(__file__), "data", "sample_notice.txt")
        with open(dummy_path, encoding="utf-8") as f:
            dummy_text = f.read()
        notice_text = extract_text(pdf_bytes=None, dummy_text=dummy_text)
        st.info("더미 샘플 데이터로 분석합니다 (실제 공고문 아님).")
    else:
        notice_text = extract_text(pdf_bytes=uploaded_file.read())

    with st.expander("추출된 원문 텍스트"):
        st.text(notice_text)

    if not address:
        auto_addr = extract_sample_house_address(notice_text) or extract_project_address(notice_text)
        if auto_addr:
            address = auto_addr
            st.caption(f"📍 공고문에서 주소 자동 추출: {address}")

    with st.spinner("조항 분류 중..."):
        matched_sections = split_sections(notice_text)

    loan_notice = extract_loan_regulation_notice(notice_text)
    if loan_notice:
        st.warning(f"⚠ **대출규제 적용 기준일: {loan_notice['date']}**\n\n{loan_notice['text']}")

    st.subheader("1. 조항별 법령 대조 결과")
    for item in matched_sections:
        with st.container(border=True):
            st.write(item["text"])
            st.caption("관련 카테고리: " + (", ".join(item["categories"]) if item["categories"] else "없음"))

    toxic_results = None
    if run_toxic:
        with st.spinner("독소조항 스크리닝 중..."):
            toxic_results = analyze_toxic_clauses(matched_sections)
        st.subheader("2. 독소조항 1차 스크리닝")
        st.caption("⚠️ 최종 법률 판단 아님 — 변호사 검토 필요")
        flagged = [r for r in toxic_results if r["risk_level"] in ("검토 필요", "높음")]
        if not flagged:
            st.success("자동 기준으로 특이사항 없음")
        else:
            for r in flagged:
                st.warning(f"**{r['risk_level']}** — {r['text']}\n\n{r['reason']}")

    unit_rows = None
    supply_summary = None
    if run_unit:
        try:
            unit_rows = parse_supply_price_table(notice_text)
            supply_summary = parse_supply_summary(notice_text)
            st.subheader("3. 동별/세대별 체크 (타입별 공급금액)")
            if unit_rows:
                st.table(unit_rows)
            else:
                st.info("공급금액표 구조를 찾지 못했습니다. 이 문서는 다른 표 양식을 사용할 수 있습니다.")
        except Exception as e:
            st.subheader("3. 동별/세대별 체크 (타입별 공급금액)")
            st.error(f"이 기능 실행 중 오류 — 건너뜁니다: {e}")

    environment_survey = None
    if run_env:
        st.subheader("4. 주변환경 조사")
        try:
            client = KakaoLocalClient()
            if not client.is_configured:
                st.error("KAKAO_REST_API_KEY 미설정 — .env 확인")
            elif not address:
                st.error("주소를 입력해주세요.")
            else:
                with st.spinner("주변시설 검색 중..."):
                    environment_survey = client.full_survey(address)
                st.json(environment_survey)
        except Exception as e:
            st.error(f"주변환경 조사 실패(카카오 API 오류 등) — 건너뜁니다: {e}")

    school_report = None
    if run_school:
        st.subheader("5. 학군조사")
        try:
            client = KakaoLocalClient()
            if not client.is_configured or not address:
                st.error("카카오 API 키/주소 확인 필요")
            else:
                coords = client.geocode_address(address)
                if coords:
                    nearby_schools = client.search_category_nearby(*coords, "학교")
                    school_report = build_school_district_report(address, nearby_schools)
                    st.caption(school_report["disclaimer"])
                    st.table(nearby_schools)
        except Exception as e:
            st.error(f"학군조사 실패 — 건너뜁니다: {e}")

    disclosure_items = None
    if run_disclosure:
        st.subheader("6. 사전고지 유의사항 (입예협 개선요구용)")
        st.caption("공고문에 명시되어 있지만 놓치기 쉬운 환경권·생활불편 관련 조항 — 입주 전 입예협 차원 개선요구 검토용")
        try:
            if not use_dummy and uploaded_file is not None:
                uploaded_file.seek(0)
                disclosure_items = extract_disclosure_items(uploaded_file.read())
            else:
                disclosure_items = extract_disclosure_items_from_text(notice_text)
            from collections import defaultdict
            grouped = defaultdict(list)
            for it in disclosure_items:
                grouped[it["category"]].append(it)
            for cat, its in grouped.items():
                with st.expander(f"{cat} ({len(its)}건)"):
                    for it in its:
                        marker = " ⚠️이의제기불가 문구 포함" if it["has_waiver_phrase"] else ""
                        st.write(f"p.{it['page']} — {it['text']}{marker}")
        except Exception as e:
            st.error(f"사전고지 유의사항 추출 실패 — 건너뜁니다: {e}")
            disclosure_items = None

    try:
        tmp_path = os.path.join(tempfile.gettempdir(), f"{complex_name}_검수리포트.docx")
        generate_report(
            complex_name, matched_sections, tmp_path,
            toxic_results=toxic_results, unit_rows=unit_rows,
            environment_survey=environment_survey, school_report=school_report,
            disclosure_items=disclosure_items, loan_notice=loan_notice,
            price_rows=unit_rows, supply_summary=supply_summary,
        )
        with open(tmp_path, "rb") as f:
            st.download_button(
                "입주민 배포용 검수 리포트(docx) 다운로드",
                data=f.read(),
                file_name=f"{complex_name}_검수리포트.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    except Exception as e:
        st.error(f"리포트 생성 실패 — 위 결과는 화면에서 확인 가능: {e}")
