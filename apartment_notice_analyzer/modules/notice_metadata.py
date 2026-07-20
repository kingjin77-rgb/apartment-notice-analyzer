"""공고문 텍스트에서 주소 등 메타데이터를 자동 추출 — 주변환경/학군조사에 주소 수동입력 없이 바로 사용."""
import re


def extract_project_address(notice_text: str) -> str | None:
    """'공급위치 : 경기도 의왕시 삼동 192-244번지 일원' 같은 줄에서 주소 추출."""
    match = re.search(r"공급위치\s*[:：]\s*(.+)", notice_text)
    if match:
        addr = match.group(1).strip()
        addr = re.sub(r"\s*일원\s*$", "", addr)
        return addr
    return None


def extract_sample_house_address(notice_text: str) -> str | None:
    """견본주택 주소 — 공급위치보다 정확한 지번인 경우가 많아 지도 API 좌표변환에 더 안정적."""
    match = re.search(r"견본주택\s*주소\s*[:：]?\s*(.+)", notice_text)
    if match:
        return match.group(1).strip()
    match = re.search(r"견본주택\s*[:：]\s*(경기도|서울|인천|부산|대구|광주|대전|울산|세종)[^\n]+", notice_text)
    if match:
        return match.group(0).split(":")[-1].strip()
    return None
