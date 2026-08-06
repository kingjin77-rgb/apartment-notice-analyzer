"""
indoor_air_quality.py
아파트 모집공고문 분석 — 확장 모듈: 신축 공동주택 실내공기질

근거 (2026-07-27 법제처 Open API(law.go.kr, OC=test)로 원문 대조 완료,
     실내공기질 관리법 시행규칙 MST=287429, 시행 2026-07-22):
  - 제6조: 시공자는 측정 예정일 20일 전까지 측정계획을 입주예정자에게 알려야
    하며, 그 방법의 하나로 「주택공급에 관한 규칙」 제21조에 따른
    입주자모집공고에 포함시킬 수 있다.
  - 제7조제3항: 측정항목 8종 — 폼알데하이드/벤젠/톨루엔/에틸벤젠/자일렌/
    (구 항목 삭제)/스티렌/라돈
  - 제7조의2, 별표4의2(개정 2018.10.18): 신축 공동주택 실내공기질 권고기준

용도:
  분양공고문에 실내공기질 측정계획 고지가 빠져 있는지(제6조 절차 누락),
  공고문에 실측치가 기재된 경우 권고기준 초과 여부를 점검한다.
  입주 전 시점이라 실측치가 아직 없는 경우가 대부분이며, 이 경우
  "측정계획 고지 여부" 자체가 점검 대상이 된다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any

# 실내공기질 관리법 시행규칙 [별표 4의2] 신축 공동주택의 실내공기질 권고기준
RECOMMENDED_LIMITS: dict[str, dict[str, Any]] = {
    "폼알데하이드": {"limit": 210, "unit": "㎍/㎥"},
    "벤젠": {"limit": 30, "unit": "㎍/㎥"},
    "톨루엔": {"limit": 1000, "unit": "㎍/㎥"},
    "에틸벤젠": {"limit": 360, "unit": "㎍/㎥"},
    "자일렌": {"limit": 700, "unit": "㎍/㎥"},
    "스티렌": {"limit": 300, "unit": "㎍/㎥"},
    "라돈": {"limit": 148, "unit": "Bq/㎥"},
}

# 공고문에 측정계획 고지가 있는지 판별할 키워드 (제6조제1항)
MEASUREMENT_NOTICE_KEYWORDS = ["실내공기질 측정", "공기질 측정", "측정 계획", "측정계획"]


@dataclass
class AirQualityItem:
    substance: str
    measured: float | None
    unit: str
    limit: float
    exceeded: bool
    severity: str


@dataclass
class AirQualityReport:
    source: str = ""
    measurement_notice_found: bool = False
    items: list[AirQualityItem] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _find_measured_values(text: str) -> dict[str, float]:
    """공고문 본문에서 물질명 뒤에 붙은 수치(측정결과가 기재된 드문 경우)를 찾는다."""
    found: dict[str, float] = {}
    for name in RECOMMENDED_LIMITS:
        m = re.search(rf"{re.escape(name)}\D{{0,10}}?([\d,]+(?:\.\d+)?)\s*(?:㎍|ug|㎎|mg|Bq|ppm|CFU)", text)
        if m:
            try:
                found[name] = float(m.group(1).replace(",", ""))
            except ValueError:
                pass
    return found


def analyze_air_quality(text: str, source: str = "") -> AirQualityReport:
    """
    >>> rep = analyze_air_quality(notice_text, source="OO아파트")
    >>> rep.measurement_notice_found
    True
    """
    rep = AirQualityReport(source=source)
    flat = re.sub(r"\s+", " ", text or "")

    rep.measurement_notice_found = any(kw in flat for kw in MEASUREMENT_NOTICE_KEYWORDS)
    if not rep.measurement_notice_found:
        rep.findings.append(
            "[중] 실내공기질 측정계획 고지 확인 안 됨 — 「실내공기질 관리법 시행규칙」 "
            "제6조제1항에 따라 시공자는 측정 예정일 20일 전까지 입주예정자에게 측정계획을 "
            "알려야 하며 입주자모집공고에 포함시키는 방법도 인정된다. 공고문에 해당 내용이 "
            "없다면 별도 서면·홈페이지 고지 여부를 확인할 것."
        )

    measured = _find_measured_values(flat)
    for name, spec in RECOMMENDED_LIMITS.items():
        val = measured.get(name)
        if val is None:
            continue
        exceeded = val > spec["limit"]
        rep.items.append(AirQualityItem(
            substance=name, measured=val, unit=spec["unit"],
            limit=spec["limit"], exceeded=exceeded,
            severity="상" if exceeded else "하",
        ))
        if exceeded:
            rep.findings.append(
                f"[상] {name} {val}{spec['unit']} — 권고기준 {spec['limit']}{spec['unit']} 초과"
            )

    if not measured:
        rep.findings.append(
            "공고문에 실측치 기재 없음 — 입주 전 단계라 정상. 입주 직전 측정 결과 공개 여부를 "
            "입예협 차원에서 별도 확인할 것 (제7조 측정항목: 폼알데하이드·벤젠·톨루엔·"
            "에틸벤젠·자일렌·스티렌·라돈 7종)."
        )
    return rep


def to_docx_rows(rep: AirQualityReport) -> list[list[str]]:
    rows = [["오염물질", "측정치", "권고기준", "초과여부"]]
    for i in rep.items:
        rows.append([
            i.substance,
            f"{i.measured}{i.unit}",
            f"{i.limit}{i.unit} 이하",
            "초과" if i.exceeded else "기준이내",
        ])
    return rows


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        raw = open(sys.argv[1], encoding="utf-8").read()
    else:
        raw = "본 아파트는 입주 전 실내공기질 측정 계획을 수립하여 시행할 예정입니다."
    r = analyze_air_quality(raw, source="sample")
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
