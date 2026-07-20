"""
모집공고문 텍스트 -> 카테고리별 조항 분해

우선순위:
1. ANTHROPIC_API_KEY 설정 시 -> Claude API로 의미 기반 분류 (문장이 여러 카테고리에 걸쳐도 잘 잡음)
2. 미설정 시 -> data/law_mapping.json의 keywords로 단순 규칙 기반 분류 (데모/오프라인 모드)
"""
import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_law_mapping() -> dict:
    with open(os.path.join(DATA_DIR, "law_mapping.json"), encoding="utf-8") as f:
        return json.load(f)


def split_by_keywords(notice_text: str) -> list[dict]:
    """API 키 없을 때 쓰는 규칙 기반 분류 (문장 단위)."""
    mapping = _load_law_mapping()
    sentences = [s.strip() for s in re.split(r"(?<=[.\n])", notice_text) if s.strip()]

    results = []
    for sentence in sentences:
        matched_categories = []
        for cat in mapping["categories"]:
            if any(kw in sentence for kw in cat["keywords"]):
                matched_categories.append(cat["category"])
        if matched_categories:
            results.append({
                "text": sentence,
                "categories": matched_categories,
            })
    return results


def split_with_claude(notice_text: str, api_key: str | None = None) -> list[dict]:
    """Claude API로 의미 기반 조항 분류."""
    try:
        import anthropic
    except ImportError:
        return split_by_keywords(notice_text)

    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return split_by_keywords(notice_text)

    mapping = _load_law_mapping()
    category_names = [c["category"] for c in mapping["categories"]]

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = (
        "너는 아파트 모집공고문을 분석하는 법무 보조 도구다. "
        "입력된 공고문 텍스트를 조항 단위로 나누고, 각 조항이 다음 카테고리 중 "
        f"어디에 해당하는지 분류하라: {category_names}. "
        "해당사항 없으면 빈 리스트. 반드시 JSON 배열만 출력하라. "
        '형식: [{"text": "...", "categories": ["..."]}]'
    )
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": notice_text}],
        )
    except anthropic.APIError:
        # 크레딧 부족, 레이트리밋, 서버 오류 등 — 키워드 기반으로 대체
        return split_by_keywords(notice_text)
    raw = "".join(block.text for block in message.content if block.type == "text")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 모델이 JSON 형식을 안 지켰을 경우의 fallback
        return split_by_keywords(notice_text)


def split_sections(notice_text: str) -> list[dict]:
    """진입점: 환경에 따라 자동으로 최선의 방법 선택."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return split_with_claude(notice_text)
    return split_by_keywords(notice_text)
