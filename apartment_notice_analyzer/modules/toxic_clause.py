"""
독소조항/유의사항 판별

우선순위:
1. ANTHROPIC_API_KEY 있으면 -> Claude가 표준 조항(data/standard_contract_reference.json)과
   공고문 조항을 의미 비교해 위험도(risk_level) 판정
2. 없으면 -> red_flags 키워드 매칭만 (거친 필터, 오탐/누락 많음)

결과는 항상 "최종 법률 판단 아님, 변호사 검토 필요" 문구를 동반합니다.
"""
import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_reference() -> dict:
    with open(os.path.join(DATA_DIR, "standard_contract_reference.json"), encoding="utf-8") as f:
        return json.load(f)


def _keyword_risk_check(text: str, ref: dict) -> dict | None:
    for clause in ref["standard_clauses"]:
        for flag in clause["red_flags"]:
            if flag in text:
                return {
                    "risk_level": "확인 필요",
                    "matched_flag": flag,
                    "standard_reference": clause["standard_summary"],
                }
    return None


def analyze_with_claude(sections: list[dict], api_key: str | None = None) -> list[dict]:
    try:
        import anthropic
    except ImportError:
        return analyze_with_keywords(sections)

    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return analyze_with_keywords(sections)

    ref = _load_reference()
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "너는 아파트 공급계약 조항의 독소조항 여부를 1차 스크리닝하는 법무 보조 도구다. "
        "아래 표준 조항 요약을 기준선으로 삼아, 입력된 공고문 조항이 수분양자에게 "
        "비정상적으로 불리한지 판단하라. 반드시 JSON 배열만 출력. "
        '형식: [{"text": "...", "risk_level": "낮음|검토 필요|높음", "reason": "..."}] '
        "risk_level은 반드시 이 최종 판단이 아니라 1차 스크리닝임을 전제로 신중하게 판정하라. "
        f"표준 조항 기준선: {json.dumps(ref['standard_clauses'], ensure_ascii=False)}"
    )

    input_text = json.dumps([s["text"] for s in sections], ensure_ascii=False)
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": input_text}],
        )
    except anthropic.APIError:
        # 크레딧 부족, 레이트리밋, 서버 오류 등 — 키워드 기반으로 대체
        return analyze_with_keywords(sections)
    raw = "".join(block.text for block in message.content if block.type == "text")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return analyze_with_keywords(sections)


def analyze_with_keywords(sections: list[dict]) -> list[dict]:
    ref = _load_reference()
    results = []
    for item in sections:
        hit = _keyword_risk_check(item["text"], ref)
        if hit:
            results.append({
                "text": item["text"],
                "risk_level": hit["risk_level"],
                "reason": f"'{hit['matched_flag']}' 키워드 매칭 — {hit['standard_reference']}",
            })
        else:
            results.append({"text": item["text"], "risk_level": "낮음", "reason": ""})
    return results


def analyze_toxic_clauses(sections: list[dict]) -> list[dict]:
    """진입점. 결과는 참고용 1차 스크리닝이며 최종 법률 판단이 아님."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return analyze_with_claude(sections)
    return analyze_with_keywords(sections)
