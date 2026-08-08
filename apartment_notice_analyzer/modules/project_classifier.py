"""사업유형 자동 판별기 (2026-08-07 신설, 같은 날 적대적 검수 반영 v2)

분양공고문 텍스트를 받아 project_type_taxonomy.json 기준으로 사업유형을 판별한다.
유형 오판은 보고서 프레임 전체를 틀어뜨리는 치명 오류이므로:
  - 역할어(HUG·LH·GH 등)는 단독 매칭하지 않고 문맥으로만 점수화
  - 경합 시 혼합형으로 출력, 확신도 낮으면 "미확정" — 절대 단정하지 않음
  - 모든 판정에 원문 근거 발췌를 붙임 (보고서 표지에 명시할 것)

사용:
    from modules.project_classifier import classify
    result = classify(text)   # {'verdict', 'confidence', 'scores', 'evidence', 'flags', 'warnings'}
CLI:
    python3 -m modules.project_classifier <텍스트파일>
"""
import os
import re
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _load_taxonomy() -> dict:
    with open(os.path.join(DATA_DIR, "project_type_taxonomy.json"), encoding="utf-8") as f:
        return json.load(f)


def _find_with_context(text: str, phrase: str, ctx: int = 60):
    """문구 등장 위치들의 (횟수, 대표 문맥) 반환."""
    hits = [m.start() for m in re.finditer(re.escape(phrase), text)]
    if not hits:
        return 0, None
    i = hits[0]
    return len(hits), text[max(0, i - ctx): i + len(phrase) + ctx].strip()


# 역할어: 단독으로는 점수화하지 않고, 근접 문맥에 역할 확정어가 있어야 인정
ROLE_WORDS = {
    "HUG": ["분양보증", "임대보증금"],
    "주택도시보증공사": ["분양보증", "임대보증금"],
    "한국토지주택공사": ["사업주체", "시행자", "공공시행자", "택지를 공급"],
    "LH": ["사업주체", "시행자", "공공시행자", "택지를 공급"],
}


def classify(text: str) -> dict:
    tx = " ".join(text.split())
    tax = _load_taxonomy()
    scores, evidence, flags = {}, {}, {}

    for t in tax["types"]:
        tid = t["id"]
        s = 0
        ev = []
        for sig in t["positive_signals"]:
            n, ctx = _find_with_context(tx, sig)
            if not n:
                continue
            # 역할어 성분이 포함된 시그널은 taxonomy에서 이미 문맥형("HUG 분양보증")으로
            # 정의돼 있으므로 그대로 인정. 단독 역할어가 시그널로 남아있다면 문맥 검사.
            bare_role = sig in ROLE_WORDS
            if bare_role:
                ok = any(r in (ctx or "") for r in ROLE_WORDS[sig])
                if not ok:
                    continue
            s += min(n, 5)  # 한 시그널 최대 5점(반복 도배 방지)
            ev.append({"signal": sig, "count": n, "context": ctx})
        for sig in t["negative_signals"]:
            n, _ = _find_with_context(tx, sig)
            if n:
                s -= min(n, 5) * 2  # 부정 신호는 2배 감점
        scores[tid] = s
        evidence[tid] = ev
        # sub_flags 감지
        fl = {}
        for k, desc in t.get("sub_flags", {}).items():
            kw_map = {
                "price_cap": ["분양가상한제"],
                "mixed_use": ["오피스텔"],
                "private_participation": ["민간참여"],
                "land_lease": ["토지임대료", "건물만 분양"],
                "pre_subscription": ["사전청약"],
                "small_scale": ["소규모주택 정비", "가로주택"],
                "public_implementation": ["공공재개발", "공공재건축"],
                "trust_method": ["신탁"],
                "association_kind": ["리모델링", "수직증축"],
                "conversion_marketing": ["확정분양가", "분양전환"],
                "youth_housing": ["청년안심주택", "역세권 청년주택"],
                "conversion": ["분양전환"],
                "kind": ["생활숙박", "오피스텔"],
                "mixed_with_apartment": ["오피스텔"],
                "general_portion": ["일반분양"],
            }
            for kw in kw_map.get(k, []):
                n, ctx = _find_with_context(tx, kw)
                if n:
                    fl[k] = {"keyword": kw, "count": n, "context": ctx, "note": desc}
                    break
        if fl:
            flags[tid] = fl

    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top_id, top_s = ranked[0]
    second_id, second_s = ranked[1] if len(ranked) > 1 else (None, 0)

    warnings = []
    # 타이브레이커(실사례 규칙): 민간분양 vs 공공분양 경합인데 '민간참여 공공주택' 문구가
    # 있으면 공공분양(민간참여형)으로 확정 — 에버포레 A1BL 사례(공공사업 내 '민영주택' 표기).
    top_pair = {top_id, second_id}
    if top_pair == {"private_sale", "public_sale"} and "민간참여 공공주택" in tx:
        top_id, top_s = "public_sale", max(top_s, second_s)
        second_id, second_s = ("private_sale", min(scores["private_sale"], scores["public_sale"]))
        warnings.append("타이브레이커 적용: '민간참여 공공주택' 문구 확인 → 공공분양(민간참여형)으로 확정. "
                        "'민영주택' 표기는 사업 내 공급유형일 뿐 사업방식이 아님")

    # 혼합/미확정 판정
    if top_s <= 2:
        verdict, confidence = "미확정", "low"
        warnings.append("신호가 약함 — 사용자에게 유형 확인을 요청할 것 (추정 금지)")
    elif second_s > 0 and top_s - second_s <= 2 and not any("타이브레이커" in w for w in warnings):
        verdict = f"혼합/경합: {top_id} + {second_id}"
        confidence = "medium"
        warnings.append("복수 유형 신호 경합 — 혼합형으로 다루고 단정하지 말 것")
    else:
        verdict, confidence = top_id, ("high" if top_s - second_s >= 5 or any("타이브레이커" in w for w in warnings) else "medium")

    top = next(t for t in tax["types"] if t["id"] == (top_id if top_s > 2 else ranked[0][0]))
    return {
        "verdict": verdict,
        "verdict_name": top["name"] if top_s > 2 else "미확정",
        "confidence": confidence,
        "scores": dict(ranked),
        "evidence": {top_id: evidence.get(top_id, [])[:6]},
        "flags": flags.get(top_id, {}),
        "focus_priority": top.get("focus_priority", []) if top_s > 2 else [],
        "pitfalls": top.get("pitfalls", []) if top_s > 2 else [],
        "warnings": warnings,
    }


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], encoding="utf-8") as f:
        r = classify(f.read())
    print(json.dumps(r, ensure_ascii=False, indent=2))
