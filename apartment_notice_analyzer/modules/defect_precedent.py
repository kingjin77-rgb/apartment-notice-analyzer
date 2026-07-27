"""
defect_precedent.py
아파트 모집공고문 분석 — 4순위 모듈: 하자 판정기준 대조

배경:
  하자심사·분쟁조정위원회(adc.go.kr)는 공개 API를 제공하지 않는다.
  대신 국토교통부 고시 「공동주택 하자의 조사, 보수비용 산정 및 하자판정기준」이
  하자 유형별 판정기준을 명문화하고 있으므로, 이를 로컬 DB로 구축한다.

용도(2단계 독소조항 판별의 핵심):
  공고문에 흔히 등장하는 면책성 문구
    "○○는 하자가 아니며 보수 대상이 아님"
    "시공 특성상 발생하는 자연스러운 현상임"
  이 실제 하자판정기준상 '하자'에 해당하는지를 대조한다.
  → 해당하면 '독소조항(면책 남용)'으로 분류하고 법무법인 검토의견을 붙인다.

DB 확장:
  판정사례는 adc.go.kr > 하자판정사례 에서 수기 수집해
  data/defect_precedents.json 에 누적한다. (스키마 아래 참조)
"""

from __future__ import annotations

import os
import re
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("DEFECT_DB_PATH", "data/defect_precedents.json"))


# ─────────────────────────────────────────────────────────────
# 판정기준 시드 DB
#   근거: 국토교통부 고시 「공동주택 하자의 조사, 보수비용 산정 및
#         하자판정기준」(행정규칙일련번호 2100000282400) 제7조·제15조
#         / 공동주택관리법 시행령 [별표4] 시설공사별 담보책임기간
#
#   2026-07-27 법제처 Open API(law.go.kr, OC=test)로 현행 조문 직접 대조 완료:
#     - CRACK-01 균열폭 0.3mm: 고시 제7조·제89조 원문과 일치 (시행 2026-07-08)
#     - COND-01 결로 3년, LEAK-01 누수 5년, FIN-01 마감재 2년:
#       시행령 별표4(제36조제1항제2호, 개정 2021.1.5, 시행 2026-07-01)의
#       단열공사=3년군, 방수공사=5년군, 마감공사=2년군과 일치
#   NOISE-01 층간소음 58/50dB은 이 고시가 아니라 「주택건설기준 등에 관한
#   규정」 제14조의2(바닥충격음 차단성능기준)가 출처 — 별도 확인 필요.
#   liability_years=5는 바닥구조가 별표4상 철근콘크리트공사군(5년)에
#   속한다는 유추이며, 층간소음 전용 항목이 별표에 명시되어 있지는 않다.
# ─────────────────────────────────────────────────────────────

SEED_CRITERIA: list[dict[str, Any]] = [
    {
        "code": "CRACK-01",
        "category": "균열",
        "part": "콘크리트 벽체·슬래브",
        "criterion": "폭 0.3mm 이상 균열은 하자로 판정",
        "liability_years": 5,
        "keywords": ["균열", "크랙", "갈라짐", "실금"],
        "disclaimer_patterns": [
            r"(미세|경미|헤어)?\s*균열.{0,20}(하자.{0,5}아님|하자에\s*해당하지)",
            r"콘크리트\s*특성상.{0,30}균열",
            r"건조수축.{0,20}(자연스러운|불가피)",
        ],
    },
    {
        "code": "COND-01",
        "category": "결로",
        "part": "외벽·창호주변·발코니",
        "criterion": "설계기준 미달로 인한 결로는 하자. 단순 생활결로는 제외",
        "liability_years": 3,
        "keywords": ["결로", "곰팡이", "습기", "이슬"],
        "disclaimer_patterns": [
            r"결로.{0,40}(입주자|사용자).{0,20}(관리|책임)",
            r"결로.{0,30}하자.{0,5}(아님|제외)",
            r"환기\s*부족.{0,20}결로",
        ],
    },
    {
        "code": "LEAK-01",
        "category": "누수",
        "part": "지붕·외벽·창호·배관",
        "criterion": "누수는 원인 불문 하자. 담보책임기간 내 보수 의무",
        "liability_years": 5,
        "keywords": ["누수", "물샘", "침수", "빗물"],
        "disclaimer_patterns": [
            r"누수.{0,40}(면책|책임지지|보상하지)",
            r"집중호우.{0,30}(불가항력|면책)",
        ],
    },
    {
        "code": "NOISE-01",
        "category": "층간소음",
        "part": "바닥구조",
        "criterion": "경량 58dB·중량 50dB 초과 시 성능기준 미달",
        "liability_years": 5,
        "keywords": ["층간소음", "바닥충격음", "경량충격음", "중량충격음"],
        "disclaimer_patterns": [
            r"층간소음.{0,40}(입주자|사용자).{0,20}(책임|해결)",
            r"층간소음.{0,30}하자.{0,5}(아님|제외)",
        ],
    },
    {
        "code": "FIN-01",
        "category": "마감재",
        "part": "도배·바닥재·타일",
        "criterion": "들뜸·박리·오염·규격미달은 하자. 색상 미세차이는 제외",
        "liability_years": 2,
        "keywords": ["도배", "장판", "마루", "타일", "들뜸", "박리", "몰딩"],
        "disclaimer_patterns": [
            r"(마감재|자재).{0,40}(변경|대체).{0,20}(가능|있음).{0,30}(이의|민원).{0,10}(제기.{0,5})?(할\s*수\s*없|불가)",
            r"견본주택.{0,30}(실제|시공).{0,20}다를\s*수\s*있",
            r"색상.{0,20}차이.{0,30}하자.{0,5}아님",
        ],
    },
    {
        "code": "VIEW-01",
        "category": "조망·일조",
        "part": "세대 배치",
        "criterion": "일조권은 건축법상 이격 준수 시 하자 아님. 단 사전 고지의무 존재",
        "liability_years": 0,
        "keywords": ["조망", "일조", "채광", "일영", "가림"],
        "disclaimer_patterns": [
            r"조망.{0,40}(보장|책임).{0,20}(하지\s*않|없)",
            r"(향후|장래).{0,20}(건축물|신축).{0,40}(이의|민원).{0,10}(제기.{0,5})?(할\s*수\s*없|불가)",
        ],
    },
    {
        "code": "AREA-01",
        "category": "면적",
        "part": "전용·공용면적",
        "criterion": "실측면적이 계약면적 대비 오차 시 정산 의무 (주택공급규칙)",
        "liability_years": 0,
        "keywords": ["면적", "실측", "정산", "오차"],
        "disclaimer_patterns": [
            r"면적.{0,30}(오차|증감).{0,40}정산.{0,20}(하지\s*않|없|제외)",
            r"(1|일)\s*%.{0,20}이내.{0,30}정산.{0,10}(제외|없)",
        ],
    },
    {
        "code": "SCHED-01",
        "category": "입주지연",
        "part": "공급계약",
        "criterion": "지연 시 지체상금 지급 의무. 면책은 천재지변 등으로 한정",
        "liability_years": 0,
        "keywords": ["입주지연", "지체상금", "준공지연", "사용검사"],
        "disclaimer_patterns": [
            r"(입주|준공).{0,10}지연.{0,50}(배상|보상).{0,20}(하지\s*않|없|청구.{0,10}불가)",
            r"행정절차.{0,30}지연.{0,20}면책",
        ],
    },
]


# ─────────────────────────────────────────────────────────────
# 데이터 모델
# ─────────────────────────────────────────────────────────────

@dataclass
class DefectFlag:
    code: str
    category: str
    clause_text: str          # 공고문 원문 발췌
    criterion: str            # 대조한 판정기준
    liability_years: int
    severity: str             # 상 / 중 / 하
    verdict: str              # 판정 결과
    legal_opinion: str        # 법무법인 검토의견


@dataclass
class DefectReport:
    source: str = ""
    flags: list[DefectFlag] = field(default_factory=list)
    matched_keywords: dict[str, int] = field(default_factory=dict)
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────
# DB 로드
# ─────────────────────────────────────────────────────────────

def load_criteria() -> list[dict[str, Any]]:
    """시드 + 사용자 누적 판정사례 병합"""
    criteria = list(SEED_CRITERIA)
    if DB_PATH.exists():
        try:
            extra = json.loads(DB_PATH.read_text(encoding="utf-8"))
            if isinstance(extra, list):
                criteria.extend(extra)
                log.info("판정사례 %d건 추가 로드", len(extra))
        except Exception as e:  # noqa: BLE001
            log.warning("판정사례 DB 로드 실패: %s", e)
    return criteria


def save_precedent(record: dict[str, Any]) -> None:
    """adc.go.kr 에서 수집한 판정사례 1건 누적"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if DB_PATH.exists():
        try:
            data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            data = []
    data.append(record)
    DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# 대조 엔진
# ─────────────────────────────────────────────────────────────

LEGAL_OPINION_TEMPLATE = (
    "본 조항은 「공동주택관리법」상 하자담보책임({years}년)을 배제하거나 "
    "축소하는 취지로 해석될 여지가 있습니다. 「약관의 규제에 관한 법률」 제7조"
    "(사업자의 손해배상책임 배제·제한 조항의 무효)에 저촉될 수 있으므로, "
    "계약 체결 전 해당 문구의 삭제 또는 '관계 법령에 따른 하자담보책임은 "
    "그러하지 아니하다'는 단서 삽입을 요구할 것을 권고합니다."
)

VIEW_OPINION = (
    "조망·일조는 원칙적으로 하자담보책임 대상이 아니나, 사업주체는 「주택공급에 "
    "관한 규칙」상 중요사항 고지의무를 부담합니다. 인근 고밀 용도지역 및 개발계획 "
    "존재 여부를 공고문이 구체적으로 특정하지 않은 채 포괄적 면책만 규정한 경우, "
    "고지의무 위반을 주장할 실익이 있습니다. (landuse_analysis 결과와 교차 검토 권장)"
)


def _severity(code: str, years: int) -> str:
    if code.startswith(("LEAK", "SCHED", "AREA")):
        return "상"
    if years >= 5:
        return "상"
    if years >= 2:
        return "중"
    return "중"


def scan_clauses(text: str, source: str = "") -> DefectReport:
    """
    공고문 전문(또는 유의사항 섹션)을 넣으면 면책조항을 판정기준과 대조한다.

    >>> rep = scan_clauses(notice_text, source="의왕역SKVIEW")
    >>> rep.summary
    {'상': 3, '중': 6, '하': 0}
    """
    rep = DefectReport(source=source)
    criteria = load_criteria()
    flat = re.sub(r"\s+", " ", text or "")

    for c in criteria:
        # 키워드 출현 카운트
        hits = sum(len(re.findall(re.escape(k), flat)) for k in c.get("keywords", []))
        if hits:
            rep.matched_keywords[c["category"]] = hits

        for pat in c.get("disclaimer_patterns", []):
            for m in re.finditer(pat, flat):
                s = max(0, m.start() - 60)
                e = min(len(flat), m.end() + 60)
                excerpt = flat[s:e].strip()

                years = c.get("liability_years", 0)
                sev = _severity(c["code"], years)
                opinion = (
                    VIEW_OPINION if c["code"].startswith("VIEW")
                    else LEGAL_OPINION_TEMPLATE.format(years=years or 2)
                )

                rep.flags.append(DefectFlag(
                    code=c["code"],
                    category=c["category"],
                    clause_text=f"…{excerpt}…",
                    criterion=c["criterion"],
                    liability_years=years,
                    severity=sev,
                    verdict=(
                        f"공고문상 면책 문구가 하자판정기준({c['criterion']})과 "
                        f"충돌 소지 있음"
                    ),
                    legal_opinion=opinion,
                ))

    # 중복 제거 (동일 코드·동일 발췌)
    seen: set[tuple[str, str]] = set()
    uniq: list[DefectFlag] = []
    for f in rep.flags:
        key = (f.code, f.clause_text[:80])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(f)
    rep.flags = uniq

    rep.summary = {
        "상": sum(1 for f in rep.flags if f.severity == "상"),
        "중": sum(1 for f in rep.flags if f.severity == "중"),
        "하": sum(1 for f in rep.flags if f.severity == "하"),
    }
    return rep


def to_docx_rows(rep: DefectReport) -> list[list[str]]:
    rows = [["코드", "유형", "공고문 문구", "판정기준", "담보책임", "심각도"]]
    order = {"상": 0, "중": 1, "하": 2}
    for f in sorted(rep.flags, key=lambda x: order.get(x.severity, 3)):
        rows.append([
            f.code, f.category,
            f.clause_text[:120],
            f.criterion,
            f"{f.liability_years}년" if f.liability_years else "해당없음",
            f.severity,
        ])
    return rows


def to_opinion_blocks(rep: DefectReport) -> list[dict[str, str]]:
    """법무법인 검토의견 섹션용 (유형별 1개로 묶음)"""
    grouped: dict[str, DefectFlag] = {}
    for f in rep.flags:
        grouped.setdefault(f.category, f)
    return [
        {"heading": f"{k} 관련 조항", "severity": v.severity, "opinion": v.legal_opinion}
        for k, v in grouped.items()
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        raw = (
            "미세 균열은 콘크리트 특성상 발생하는 것으로 하자에 해당하지 않습니다. "
            "결로는 입주자의 환기 관리 책임입니다. "
            "견본주택과 실제 시공은 다를 수 있으며 이에 대해 이의를 제기할 수 없습니다."
        )
    r = scan_clauses(raw, source="sample")
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
