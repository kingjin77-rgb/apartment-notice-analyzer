"""
fire_safety_check.py
아파트 모집공고문 분석 — 확장 모듈: 공동주택 의무 소방시설 대조

근거 (2026-07-27 법제처 Open API(law.go.kr, OC=test)로 원문 대조 완료,
     소방시설 설치 및 관리에 관한 법률 시행령 MST=287375, 시행 2026-07-01,
     별표4 「특정소방대상물의 관계인이 설치·관리해야 하는 소방시설의 종류」):
  - "아파트등"의 정의: 주택으로 쓰는 층수가 5층 이상인 주택
  - 스프링클러설비: 층수 6층 이상인 특정소방대상물은 모든 층에 설치
    (기존 아파트등을 연면적·층고 변경 없이 리모델링하는 경우 등은 예외)
  - 주거용 주방자동소화장치: 아파트등 및 오피스텔의 모든 층(세대별) 설치 의무
  - 자동화재탐지설비(감지기): 공동주택 중 아파트등·기숙사·숙박시설은 모든 층 설치 의무

용도:
  공고문의 소방시설 사양표에 이 세 가지 의무 항목이 실제로 포함돼 있는지
  대조한다. 특히 세대별 필수 항목(주방자동소화장치·감지기)은 공용부 소방
  설비 목록에만 집중된 공고문에서 누락되기 쉽다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any

# (항목, 의무조건 설명, 공고문에서 찾을 키워드들)
MANDATORY_ITEMS: list[dict[str, Any]] = [
    {
        "code": "SPRINKLER-01",
        "name": "스프링클러설비(전층)",
        "condition": "6층 이상 아파트등은 모든 층에 스프링클러설비 설치 의무",
        "keywords": ["스프링클러"],
    },
    {
        "code": "KITCHEN-EXT-01",
        "name": "주거용 주방자동소화장치(세대별)",
        "condition": "아파트등은 모든 층(세대) 주방에 자동소화장치 설치 의무",
        "keywords": ["주방자동소화장치", "주방 자동소화장치", "자동소화장치", "자동식소화기"],
    },
    {
        "code": "DETECTOR-01",
        "name": "자동화재탐지설비(세대별 감지기)",
        "condition": "아파트등은 모든 층에 자동화재탐지설비 설치 의무",
        "keywords": ["자동화재탐지설비", "화재감지기", "감지기"],
    },
]


@dataclass
class FireSafetyFlag:
    code: str
    name: str
    condition: str
    found_in_notice: bool
    severity: str
    note: str


@dataclass
class FireSafetyReport:
    source: str = ""
    building_floors: int | None = None
    applicable: bool = True
    flags: list[FireSafetyFlag] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_max_floor(text: str) -> int | None:
    """공고문에서 '지상 O층' 형태의 최고층수를 찾는다."""
    candidates = [int(n) for n in re.findall(r"지상\s*(\d{1,3})\s*층", text)]
    return max(candidates) if candidates else None


def scan_fire_safety(text: str, source: str = "") -> FireSafetyReport:
    """
    >>> rep = scan_fire_safety(notice_text, source="OO아파트")
    >>> rep.applicable
    True
    """
    rep = FireSafetyReport(source=source)
    flat = re.sub(r"\s+", " ", text or "")

    floor = _extract_max_floor(flat)
    rep.building_floors = floor
    # "아파트등" 정의(5층 이상)에 해당 안 하면 이 대조 자체가 적용 대상 아님
    if floor is not None and floor < 5:
        rep.applicable = False
        rep.findings.append(f"층수 {floor}층 — 「소방시설법 시행령」상 '아파트등'(5층 이상) 기준 미해당, 본 대조 참고용")

    for item in MANDATORY_ITEMS:
        found = any(kw in flat for kw in item["keywords"])
        rep.flags.append(FireSafetyFlag(
            code=item["code"], name=item["name"], condition=item["condition"],
            found_in_notice=found,
            severity="하" if found else "중",
            note="공고문에 명시됨" if found else "공고문에서 확인 안 됨 — 세대별 의무설비 누락 여부 확인 필요",
        ))
        if not found:
            rep.findings.append(
                f"[중] {item['name']} 공고문 확인 안 됨 — {item['condition']}. "
                f"공용부 소방시설 목록에만 집중되어 세대 내 설비가 빠졌을 가능성."
            )
    return rep


def to_docx_rows(rep: FireSafetyReport) -> list[list[str]]:
    rows = [["항목", "법정 의무조건", "공고문 확인", "심각도"]]
    for f in rep.flags:
        rows.append([f.name, f.condition, "확인됨" if f.found_in_notice else "미확인", f.severity])
    return rows


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        raw = open(sys.argv[1], encoding="utf-8").read()
    else:
        raw = "본 아파트는 지상 15층 규모이며 스프링클러설비를 설치합니다."
    r = scan_fire_safety(raw, source="sample")
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
