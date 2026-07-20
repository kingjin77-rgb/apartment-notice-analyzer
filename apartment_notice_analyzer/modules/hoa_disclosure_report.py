"""
사전고지 유의사항 추출 (입예협 사전 개선요구용)

목적: 공고문에는 이미 기재돼 있지만, 분량이 많아(보통 60페이지 이상) 입주민이
개별적으로 정독하지 않으면 놓치기 쉬운 조항 — 특히 나중에 "이걸 왜 몰랐냐"며
개인이 이의를 제기해도 이미 공고문에 명시돼 법적으로 다투기 어려운 조항들을
미리 추려서, 입주 전 입예협 차원에서 시공사·시행사에 개선요구나 명확한 설명을
요청할 수 있게 하는 것.

이건 "독소조항"(불법/부당 특약, toxic_clause.py)과는 다른 개념입니다.
법적으로는 문제없는 정상적인 고지사항이지만, 실생활 불편·환경권 침해와
관련된 항목이라 사전 확인·협상 가치가 있는 조항을 찾는 것이 목적입니다.

한계: 키워드 기반이라 노이즈가 있습니다(관련 없는 문장이 섞일 수 있음).
카테고리별로 사람이 한 번 훑어보고 관련 없는 항목은 걸러내는 것을 전제로 합니다.
"""
import re
from collections import defaultdict

import fitz

CATEGORIES = {
    "인접시설·혐오시설": [
        "혐오", "장례식장", "소각", "폐기물", "발전기", "쓰레기", "변전", "정압기",
        "이동통신", "중계기", "전자파", "가스정압기", "한전", "축사", "근린생활시설",
    ],
    "소음·진동·냄새": ["소음", "진동", "매연", "냄새", "악취", "분진"],
    "조망·일조·사생활": ["조망", "일조", "사생활", "침해", "눈부심", "간섭", "노출"],
    "결로·누수·하자우려": ["결로", "곰팡이", "동파", "누수", "습기"],
    "동배치·구조적 제약": ["필로티", "최하층", "인접 세대", "인접세대", "인접동"],
}

# 청약자격/대출/세금 등 절차성 문구 — 카테고리 키워드와 우연히 겹쳐도 환경권 이슈가 아니므로 제외
EXCLUSION_KEYWORDS = [
    "대출", "청약통장", "가점", "예치금", "인지세", "부적격", "당첨자", "재당첨",
    "전매제한", "가입기간", "소득", "부동산가액", "청약자격", "세대주", "무주택",
]

# 이 문구가 붙어 있으면 "나중에 개인이 이의 제기해도 소용없는" 조항일 가능성이 높음 — 우선순위 표시용
WAIVER_HINTS = [
    "이의를 제기할 수 없", "이의를 제기할수 없", "책임지지 않", "책임지지 아니",
    "동의하는 것으로", "동의한 것으로", "무관합니다", "책임을 지지 않",
]

# 법무법인 검토의견 템플릿 (카테고리별 — 입예협이 시공사·시행사에 요청할 수 있는 확인/개선 사항 제안)
JL_OPINION_TEMPLATES = {
    "인접시설·혐오시설": "해당 시설과의 정확한 이격거리 및 저감대책(차폐, 방음벽 등) 시공사 서면 확인 요청 권장",
    "소음·진동·냄새": "실측 기준 예상 소음·진동 수준 및 저감조치 여부에 대한 사전 설명 요청 권장",
    "조망·일조·사생활": "동·호수별 실제 영향 범위를 견본주택/도면으로 사전 확인하고 계약 전 고지 요청 권장",
    "결로·누수·하자우려": "하자보수 범위에서 제외되는 부분(결로 등)에 대한 시공 개선 여부 확인 권장",
    "동배치·구조적 제약": "해당 동/세대 여부를 사전에 특정해 계약자에게 개별 고지하도록 요청 권장",
}

SEVERITY_HIGH_CATEGORIES = {"인접시설·혐오시설", "소음·진동·냄새"}
MIN_LEN = 15


def _has_exclusion(text: str) -> bool:
    return any(kw in text for kw in EXCLUSION_KEYWORDS)


def _categorize(text: str) -> str | None:
    for category, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            return category
    return None


def classify_severity(category: str, has_waiver_phrase: bool) -> str:
    """상/중/하 심각도 분류. 면책 문구(이의제기 불가 등) + 카테고리 조합으로 판단하는 휴리스틱이며,
    법적 심각도 판단이 아니라 '입예협이 먼저 챙겨봐야 할 우선순위' 기준입니다."""
    if has_waiver_phrase and category in SEVERITY_HIGH_CATEGORIES:
        return "상"
    if has_waiver_phrase or category in SEVERITY_HIGH_CATEGORIES:
        return "중"
    return "하"


SEVERITY_ORDER = {"상": 0, "중": 1, "하": 2}


def extract_loan_regulation_notice(full_text: str) -> dict | None:
    """
    대출규제(LTV/DSR 등) 적용 기준일 추출.
    공고문 안에 보통 "20XX.XX.XX. 발표된 [OO대책]에 따라 ... LTV/DSR ..." 형태로 명시되어 있음.
    """
    pattern = re.compile(
        r"(\d{4}\.\d{1,2}\.\d{1,2})\.?\s*발표된[^.]*?(LTV|DSR)[^.]*\."
    )
    match = pattern.search(full_text)
    if not match:
        return None
    return {"date": match.group(1), "text": match.group(0).strip()}


def extract_disclosure_items(pdf_bytes: bytes) -> list[dict]:
    """
    PDF 바이트에서 페이지별로 불릿(•) 단위 문장을 뽑아 카테고리별로 분류.
    반환: [{"page", "category", "text", "has_waiver_phrase", "severity", "jl_opinion"}, ...]
    심각도(상/중/하) 순으로 정렬되어 반환됩니다.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    results = []
    seen = set()

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()
        bullets = re.findall(r"•([^•]+)", page_text)
        for raw in bullets:
            text = re.sub(r"\s+", " ", raw).strip()
            if len(text) < MIN_LEN or text in seen or _has_exclusion(text):
                continue
            category = _categorize(text)
            if category is None:
                continue
            seen.add(text)
            has_waiver = any(w in text for w in WAIVER_HINTS)
            severity = classify_severity(category, has_waiver)
            results.append({
                "page": page_num,
                "category": category,
                "text": text,
                "has_waiver_phrase": has_waiver,
                "severity": severity,
                "jl_opinion": JL_OPINION_TEMPLATES.get(category, ""),
            })

    results.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 9))
    return results


def extract_disclosure_items_from_text(notice_text: str) -> list[dict]:
    """PDF 없이 순수 텍스트(더미 샘플 등)로 테스트할 때 쓰는 진입점. 페이지 번호는 항상 1."""
    bullets = re.findall(r"•([^•]+)", notice_text)
    results = []
    seen = set()
    for raw in bullets:
        text = re.sub(r"\s+", " ", raw).strip()
        if len(text) < MIN_LEN or text in seen or _has_exclusion(text):
            continue
        category = _categorize(text)
        if category is None:
            continue
        seen.add(text)
        has_waiver = any(w in text for w in WAIVER_HINTS)
        severity = classify_severity(category, has_waiver)
        results.append({
            "page": 1, "category": category, "text": text, "has_waiver_phrase": has_waiver,
            "severity": severity, "jl_opinion": JL_OPINION_TEMPLATES.get(category, ""),
        })
    results.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 9))
    return results


def group_by_category(items: list[dict]) -> dict:
    grouped = defaultdict(list)
    for item in items:
        grouped[item["category"]].append(item)
    return dict(grouped)
