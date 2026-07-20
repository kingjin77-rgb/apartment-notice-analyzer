"""
동별/세대별 체크

1. 공고문 내 동/호수/타입/면적/향 표를 텍스트에서 파싱 (표 형태가 일정하지 않아 정규식은 최소한으로,
   기본은 줄 단위 파싱 + 사용자가 컬럼 매핑 확인하는 방식을 권장)
2. 평면도 이미지가 있으면 Claude Vision으로 향/구조/특이사항 분석
   (JL 올인원 도면분석기와 동일한 패턴 재사용)
"""
import os
import re
import base64


SUMMARY_ROW_LABELS = [
    "총공급세대수", "기관추천", "다자녀가구", "신혼부부", "노부모부양",
    "생애최초", "신생아", "특별공급계", "일반공급세대수", "최하층우선배정합계",
]


def parse_supply_summary(notice_text: str) -> dict | None:
    """
    '공급대상' 표 맨 아래 '계' 요약행 파싱.
    예: 계 820 82 82 123 24 57 82 450 370 64
    → 총공급세대수/기관추천~신생아 각 특별공급 유형/특별공급계/일반공급세대수/최하층우선배정합계
    """
    lines = [l.strip() for l in notice_text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        if line == "계" and i + len(SUMMARY_ROW_LABELS) < len(lines):
            candidate = lines[i + 1: i + 1 + len(SUMMARY_ROW_LABELS)]
            if all(re.match(r"^[\d,]+$", c) for c in candidate):
                return dict(zip(SUMMARY_ROW_LABELS, candidate))
    return None


def parse_unit_table(notice_text: str) -> list[dict]:
    """
    아주 단순한 라인 기반 파서.
    예: "101동 1503호 84A타입 남향 3면발코니" 같은 줄을 동/호수/타입/향으로 분해.
    실제 공고문은 표(HWP/PDF 표)로 오는 경우가 많아, 표 구조가 확인되면
    이 함수 대신 pandas로 표를 직접 읽는 방식으로 교체 권장.
    """
    pattern = re.compile(
        r"(?P<dong>\d{1,3}동)\s*(?P<ho>\d{3,4}호)?\s*(?P<type>\d{2,3}[A-Z]?\s*타입)?\s*(?P<direction>[동서남북]{1,2}향)?"
    )
    results = []
    for line in notice_text.splitlines():
        m = pattern.search(line)
        if m and m.group("dong"):
            results.append({
                "동": m.group("dong"),
                "호수": m.group("ho") or "-",
                "타입": m.group("type") or "-",
                "향": m.group("direction") or "-",
                "원문": line.strip(),
            })
    return results


FLOOR_PATTERN = re.compile(r"^\d{1,3}(-\d{1,3})?층(\s*이상)?$")
DONGHO_PATTERN = re.compile(r"동.*호")
# 세대수(1) + 공급금액(대지비/건축비/부가세/계=4) + 계약금(2) + 중도금(6) + 잔금(1) = 14
FIELDS_PER_FLOOR_ROW = 14
NUMERIC_TOKEN = re.compile(r"^[\d,]+$|^-$")


def parse_supply_price_table(notice_text: str) -> list[dict]:
    """
    '공급금액 및 납부일정' 표 파싱 (타입별 동/호 그룹 + 층별 금액 계층 구조).

    실제 이 표는 PyMuPDF로 추출하면 컬럼 구분 없이 한 줄씩 순서대로 쭉 나열되는데,
    구조가 '타입 코드' → '동/호 그룹 라인들' → ('층구분' + 14개 숫자필드) 반복 이므로
    상태기계(state machine)로 순서를 따라가며 파싱합니다.

    한계: 이 표가 정확히 이 순서/필드수로 나오는 문서에서만 동작 확인됨(SK 계열 템플릿 기준).
    다른 시공사 양식은 필드 순서가 다를 수 있어 재검증 필요.
    """
    lines = [l.strip() for l in notice_text.splitlines() if l.strip()]

    # "입주지정일" 헤더 라인 다음부터가 실제 데이터 시작
    start_idx = 0
    for i, line in enumerate(lines):
        if line == "입주지정일":
            start_idx = i + 1
            break

    results = []
    current_type = None
    current_donghos: list[str] = []
    i = start_idx
    n = len(lines)

    while i < n:
        line = lines[i]

        if FLOOR_PATTERN.match(line):
            floor = line
            i += 1
            fields = []
            while i < n and len(fields) < FIELDS_PER_FLOOR_ROW:
                if NUMERIC_TOKEN.match(lines[i]):
                    fields.append(lines[i])
                    i += 1
                else:
                    break
            if len(fields) == FIELDS_PER_FLOOR_ROW:
                results.append({
                    "타입": current_type,
                    "동호그룹": list(current_donghos),
                    "층구분": floor,
                    "세대수": fields[0],
                    "대지비": fields[1],
                    "건축비": fields[2],
                    "부가가치세": fields[3],
                    "공급금액계": fields[4],
                    "계약금_계약시": fields[5],
                    "계약금_계약후30일": fields[6],
                    "중도금_1회": fields[7],
                    "중도금_2회": fields[8],
                    "중도금_3회": fields[9],
                    "중도금_4회": fields[10],
                    "중도금_5회": fields[11],
                    "중도금_6회": fields[12],
                    "잔금": fields[13],
                })
            continue

        if DONGHO_PATTERN.search(line):
            current_donghos.append(line)
            i += 1
            continue

        # 그 외의 경우: 새로운 타입 코드로 간주 (예: "36", "45", "59A")
        current_type = line
        current_donghos = []
        i += 1

    return results


def analyze_floor_plan_image(image_bytes: bytes, media_type: str = "image/png", api_key: str | None = None) -> str:
    """평면도 이미지를 Claude Vision으로 분석 (향, 구조, 발코니 확장 가능 여부 등)."""
    try:
        import anthropic
    except ImportError:
        return "anthropic 패키지 미설치"

    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "ANTHROPIC_API_KEY 미설정"

    client = anthropic.Anthropic(api_key=api_key)
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64_image}},
                {"type": "text", "text": (
                    "이 아파트 평면도를 분석해줘. 향(방위), 구조(판상형/타워형), "
                    "발코니 확장 가능 범위, 방 개수/배치, 특이사항(맞통풍 여부, 벽식/기둥식 등)을 "
                    "입주민이 이해하기 쉽게 정리해줘."
                )},
            ],
        }],
    )
    return "".join(block.text for block in message.content if block.type == "text")
