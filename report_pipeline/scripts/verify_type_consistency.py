"""유형-보고서 정합성 검수 (2026-08-07 신설) — 검수시스템 3단계 중 마지막.

1) project_classifier로 공고문 원문에서 사업유형 판별
2) 보고서 콘텐츠(content.js)의 논리가 그 유형과 모순되는지 룰 기반 검사
   유형 오판/혼용 = 입찰 탈락급 치명 오류이므로 빌드 전 반드시 실행.

사용: python3 scripts/verify_type_consistency.py <원문텍스트.txt> <slug>
종료코드 0=통과, 1=경고 있음(사람 확인 필요), 2=치명(빌드 중단 권고)
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "apartment_notice_analyzer"))
from modules.project_classifier import classify  # noqa: E402


def load_content_text(slug: str) -> str:
    """content.js 전체를 문자열 하나로 덤프 (node로 평가)."""
    out = subprocess.run(
        ["node", "-e",
         f"const c=require('./content/{slug}/content.js');console.log(JSON.stringify(c))"],
        capture_output=True, text=True, cwd=os.path.join(REPO, "report_pipeline"))
    if out.returncode != 0:
        raise SystemExit(f"content.js 로드 실패: {out.stderr[:300]}")
    return out.stdout


# (유형, 보고서에 있으면 문제인 패턴, 심각도, 설명)
RULES = [
    ("private_rental", r"분양가상한제", "fatal",
     "임대 물건 보고서에 분양가상한제 논리 — 매매형 잣대 오적용(파라곤3차 실패 패턴)"),
    ("private_rental", r"HUG\s*분양보증|분양보증서", "fatal",
     "임대 물건에 분양보증 논리 — 임대보증금 보증(민특법 49조)과 별개 제도"),
    ("public_rental", r"장기일반민간임대|공공지원민간임대", "warn",
     "공공임대 보고서에 민간임대 유형 언급 — 분양전환권 법적 성격(법정 vs 계약) 혼동 위험"),
    ("public_sale", r"분양보증서?\s*\(?\s*HUG|HUG\s*(등\)?)?\s*.{0,10}분양보증", "warn",
     "공공분양(특히 민간참여형)은 HUG 분양보증 체계 밖일 수 있음 — 'HUG 보증서 확인' 프레임이면 '대체 보전구조 질문' 프레임으로 교체할 것"),
    ("housing_association", r"청약\s*(1순위|가점)|입주자모집공고", "warn",
     "주택조합 보고서에 청약 프레임 — 조합 가입은 청약이 아님"),
    ("private_sale", r"우선분양전환", "warn",
     "매매형 보고서에 분양전환 논리 — 임대 물건과 혼동 여부 확인"),
    ("non_housing", r"주택법|청약가점|하자담보책임", "fatal",
     "비주택(생숙·오피스텔) 보고서에 주택법 프레임 — 근거법이 다름(건축물분양법)"),
]


def main(notice_txt: str, slug: str) -> int:
    with open(notice_txt, encoding="utf-8") as f:
        r = classify(f.read())
    verdict = r["verdict"]
    print(f"[유형판별] {verdict} ({r['verdict_name']}) confidence={r['confidence']}")
    for w in r["warnings"]:
        print(f"  ! {w}")

    if r["confidence"] == "low":
        print("[치명] 유형 미확정 — 사용자 확인 전 빌드 금지")
        return 2

    content = load_content_text(slug)
    base_type = verdict.replace("혼합/경합: ", "").split(" + ")[0]
    issues = []
    for typ, pat, sev, msg in RULES:
        if typ != base_type:
            continue
        m = re.search(pat, content)
        if m:
            issues.append((sev, msg, m.group(0)))

    if not issues:
        print(f"[통과] 유형-보고서 정합성 문제 없음 (유형={base_type}, 룰 {sum(1 for t,_,_,_ in RULES if t==base_type)}건 검사)")
        return 0
    worst = 0
    for sev, msg, hit in issues:
        print(f"[{'치명' if sev=='fatal' else '경고'}] {msg}  (검출: '{hit}')")
        worst = max(worst, 2 if sev == "fatal" else 1)
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
