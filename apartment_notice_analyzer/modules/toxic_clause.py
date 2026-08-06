"""
독소조항/유의사항 판별

우선순위:
1. ANTHROPIC_API_KEY 있으면 -> Claude가 표준 조항(data/standard_contract_reference.json)과
   공고문 조항을 의미 비교해 위험도(risk_level) 판정
2. 없으면 -> 정규식 기반 red_flag 매칭 (어미 변형 대응) + defect_precedent 판정기준 병합

결과는 항상 "최종 법률 판단 아님, 변호사 검토 필요" 문구를 동반합니다.

[2026-08-06 수리 내역]
- risk_level "확인 필요" -> "검토 필요" 통일 (report_generator/app/ResultsView 필터와 불일치로
  키워드 모드 결과가 전량 소실되던 배선 버그 수정)
- red_flags 완전일치 -> 어미 불변부 정규식(RED_FLAG_PATTERNS)으로 교체
  ("~할 수 없다/없습니다/없으며/없음" 전부 매칭)
- defect_precedent.scan_clauses() 병합 (기존 미연결 사문 엔진 활성화)
"""
import os
import re
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# 어미·조사 변형에 강한 불변부 패턴. (표시명, 컴파일된 정규식, 카테고리)
RED_FLAG_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("이의제기 금지", re.compile(r"(이의|민원|소송|청구)\s*(를|을)?\s*(제기|요구)?\s*(할\s*수\s*없|불가|하지\s*못|못\s*하)"), "권리행사 제한"),
    ("일체 면책", re.compile(r"(사업주체|시행사|시공사|당사)[^.]{0,30}(책임(을|이)?\s*(지지|부담하지)\s*(않|아니)|면책)"), "사업자 면책"),
    ("책임 전가", re.compile(r"(불이익|손해|책임)[^.]{0,20}(계약자|수분양자|임차인|본인)[^.]{0,15}(있|귀속|부담)"), "사업자 면책"),
    ("환불 거부", re.compile(r"(환불|환급|반환|정산)[^.]{0,20}(요구할\s*수\s*없|하지\s*않|되지\s*않|불가)"), "대금 관련"),
    ("자동 해제/실권", re.compile(r"(최고|통지|유예)\s*(절차)?\s*없이[^.]{0,20}(해제|해지|취소|상실)"), "해제·해지"),
    ("도달 간주", re.compile(r"(발송|통지|송달)[^.]{0,25}(도달(한|된)\s*것으로|간주|본다|봅니다)"), "의사표시 의제"),
    ("변경 백지위임", re.compile(r"(변경|조정)\s*될\s*수\s*있(으며|음|습니다)[^.]{0,30}(이의|동의\s*없이|임의로)?"), "일방 변경권"),
    ("동등자재 변경", re.compile(r"동등\s*(이상|한)?[^.]{0,15}(자재|제품|사양)[^.]{0,20}(변경|대체)"), "마감재 변경"),
    ("위약금 이중청구", re.compile(r"위약금[^.]{0,40}(별도|외에|초과)[^.]{0,20}(손해|실비|배상|원상)"), "과도한 위약금"),
    ("보증 대상 제외", re.compile(r"(분양보증|보증)\s*(대상|범위)?[^.]{0,15}(해당(되지|하지)\s*않|제외)"), "보증 제외"),
    ("계약서 위임", re.compile(r"(자세한|구체적인|세부)[^.]{0,15}(사항|기준|내용)[^.]{0,20}(계약서|별도\s*약정)[^.]{0,15}(따르|정하|명시)"), "핵심조건 위임"),
    ("전속관할 합의", re.compile(r"(전속)?관할\s*(법원)?[^.]{0,20}(합의|소재지\s*법원|정한다)"), "분쟁해결 제한"),
]


def _load_reference() -> dict:
    with open(os.path.join(DATA_DIR, "standard_contract_reference.json"), encoding="utf-8") as f:
        return json.load(f)


def _keyword_risk_check(text: str, ref: dict) -> dict | None:
    """정규식 우선 매칭 + (하위호환) 문자열 red_flags. 복수 매칭 시 전부 수집."""
    flat = re.sub(r"\s+", " ", text or "")
    matched: list[dict] = []
    for label, pat, category in RED_FLAG_PATTERNS:
        if pat.search(flat):
            matched.append({"flag": label, "category": category})
    # 레거시 문자열 플래그 (정규식이 놓친 것 보강)
    for clause in ref.get("standard_clauses", []):
        for flag in clause.get("red_flags", []):
            if flag in flat and not any(m["flag"] == flag for m in matched):
                matched.append({"flag": flag, "category": clause.get("category", ""),
                                "standard_reference": clause.get("standard_summary", "")})
    if not matched:
        return None
    first = matched[0]
    return {
        "risk_level": "검토 필요",
        "matched_flag": first["flag"],
        "matched_all": matched,
        "standard_reference": first.get("standard_reference", first.get("category", "")),
    }


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
            flags = ", ".join(m["flag"] for m in hit.get("matched_all", [])[:4])
            results.append({
                "text": item["text"],
                "risk_level": hit["risk_level"],
                "reason": f"[{flags}] 패턴 매칭 — {hit['standard_reference']}",
            })
        else:
            results.append({"text": item["text"], "risk_level": "낮음", "reason": ""})
    return results


def _merge_defect_scan(sections: list[dict], results: list[dict]) -> list[dict]:
    """defect_precedent 판정기준을 병합 — 기존에 어디서도 호출되지 않던 엔진 활성화."""
    try:
        from . import defect_precedent
    except ImportError:
        try:
            import defect_precedent  # 스크립트 직접 실행 시
        except ImportError:
            return results
    full_text = "\n".join(s.get("text", "") for s in sections)
    try:
        rep = defect_precedent.scan_clauses(full_text)
    except Exception:
        return results
    for flag in getattr(rep, "flags", []):
        results.append({
            "text": getattr(flag, "matched_text", "") or getattr(flag, "criterion", ""),
            "risk_level": "높음" if getattr(flag, "severity", "중") == "상" else "검토 필요",
            "reason": f"[하자판례 기준 {getattr(flag, 'code', '')}] {getattr(flag, 'category', '')}",
            "engine": "defect_precedent",
        })
    return results


def analyze_toxic_clauses(sections: list[dict]) -> list[dict]:
    """진입점. 결과는 참고용 1차 스크리닝이며 최종 법률 판단이 아님."""
    if os.getenv("ANTHROPIC_API_KEY"):
        results = analyze_with_claude(sections)
    else:
        results = analyze_with_keywords(sections)
    return _merge_defect_scan(sections, results)
