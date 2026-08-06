# -*- coding: utf-8 -*-
"""
공동주택 공시가격 — V-World 공동주택가격속성조회 API

이 데이터가 중요한 이유는 감정평가 산식에 직접 들어가서가 아니다.
아파트의 법정 주방식은 거래사례비교법(감칙 제16조)이고 공시가격은 그 식에 없다.
실제 감정평가서 3건 어디에도 공시가격으로 아파트값을 구한 곳이 없었다.

쓰는 이유는 셋이다.

1) 거래가 0건인 단지의 유일한 세대별 실측 앵커.
   공시가격은 모든 세대에 개별로 매겨져 있고 층·향·위치가 이미 반영돼 있다.
   즉 단지 내 세대 간 공시가격 비율을 그대로 쓰면, 인근 단지에서 베껴온
   추정 격차율을 실측으로 대체할 수 있다. 분양전환 단지처럼 자체 거래가
   없는 물건에서 호별요인(실무기준 [610-3.1.3]②)을 잡는 가장 확실한 근거다.

2) 시산가액 합리성 검토(감칙 제12조②)의 참고자료.
   공시가격 대비 현실화율이 인근 단지와 크게 어긋나면 추정이 틀렸다는 신호다.

3) 5년 임대 분양전환가 산식의 건설원가 교차검증.

주의: data.go.kr 15124003은 랜딩 페이지일 뿐이고 실제 서비스 주체는 V-World다.
      V-World는 서비스별 개별 활용신청이 없다 — 키 하나로 전 서비스를 쓴다.
      발급: https://www.vworld.kr → 오픈API → 인증키 발급 (무료)
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

ENDPOINT = "https://api.vworld.kr/ned/data/getApartHousingPriceAttr"


@dataclass
class UnitPrice:
    """세대(호) 단위 공시가격."""

    pnu: str
    complex_name: str      # aphusNm
    dong: str              # dongNm
    ho: str                # hoNm
    area: float            # prvuseAr — 전용면적
    price: int             # pblntfPc — 공시가격(원)
    year: str              # stdrYear
    floor: int | None = None   # floorNm — API가 층을 직접 준다
    kind: str = ""             # aphusSeCodeNm (아파트/연립/다세대)
    addr: str = ""             # ldCodeNm
    updated: str = ""          # lastUpdtDt

    @property
    def unit_price(self) -> float:
        """전용 ㎡당 공시가격."""
        return self.price / self.area if self.area else 0.0


class HousingPriceClient:
    def __init__(self, key: str | None = None):
        self.key = key or os.getenv("VWORLD_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.key)

    def fetch(self, pnu: str, *, year: str | None = None, dong: str | None = None,
              ho: str | None = None, max_rows: int = 1000) -> list[UnitPrice]:
        """
        PNU(필지 고유번호 19자리)로 해당 단지의 세대별 공시가격을 가져온다.
        PNU는 법정동코드(10) + 산여부(1) + 본번(4) + 부번(4).
        카카오 지오코딩의 b_code(10자리)에 산여부·본번·부번을 붙여 만든다.
        """
        if not self.is_configured:
            return []
        out: list[UnitPrice] = []
        page = 1
        while True:
            params = {"key": self.key, "pnu": pnu, "format": "json",
                     "numOfRows": min(max_rows, 1000), "pageNo": page}
            if year:
                params["stdrYear"] = year
            if dong:
                params["dongNm"] = dong
            if ho:
                params["hoNm"] = ho
            r = requests.get(ENDPOINT, params=params, timeout=25)
            if r.status_code != 200:
                break
            try:
                body = r.json()
            except ValueError:
                break
            fields = (body.get("apartHousingPrices") or {}).get("field") or []
            if isinstance(fields, dict):
                fields = [fields]
            if not fields:
                break
            for f in fields:
                try:
                    fl = f.get("floorNm")
                    out.append(UnitPrice(
                        pnu=f.get("pnu", ""), complex_name=f.get("aphusNm", ""),
                        dong=f.get("dongNm", ""), ho=f.get("hoNm", ""),
                        area=float(f.get("prvuseAr") or 0),
                        price=int(float(f.get("pblntfPc") or 0)),
                        year=str(f.get("stdrYear") or ""),
                        floor=int(fl) if str(fl).strip().lstrip("-").isdigit() else None,
                        kind=f.get("aphusSeCodeNm", ""), addr=f.get("ldCodeNm", ""),
                        updated=f.get("lastUpdtDt", ""),
                    ))
                except (TypeError, ValueError):
                    continue
            if len(fields) < min(max_rows, 1000):
                break
            page += 1
        return out

    def floor_ratio_table(self, units: list[UnitPrice]) -> dict:
        """
        세대별 공시가격에서 층별효용비율을 실측한다.

        API가 floorNm으로 층을 직접 주므로 그것을 쓰고, 없을 때만 호명에서
        추출한다. 동일 전용면적끼리만 비교해야 층 효과가 분리된다.
        """
        import collections
        import statistics

        by_area: dict[float, list[tuple[int, float]]] = collections.defaultdict(list)
        for u in units:
            fl = u.floor if u.floor and u.floor > 0 else _floor_from_ho(u.ho)
            if fl and u.area and u.unit_price:
                by_area[round(u.area, 2)].append((fl, u.unit_price))

        result = {}
        for area, items in by_area.items():
            if len(items) < 4:
                continue
            med = statistics.median(v for _, v in items)
            if not med:
                continue
            maxfl = max(f for f, _ in items)
            bands: dict[int, list[float]] = collections.defaultdict(list)
            for fl, v in items:
                rel = fl / maxfl
                b = 0 if rel < 0.18 else (1 if rel < 0.35 else (2 if rel < 0.62 else 3))
                bands[b].append(v / med)
            result[area] = {
                "n": len(items), "max_floor": maxfl,
                "ratios": [round(statistics.median(bands[b]), 3) if bands.get(b) else None
                          for b in range(4)],
                "source": "공동주택 공시가격 세대별 실측 (V-World)",
            }
        return result


def _floor_from_ho(ho: str) -> int | None:
    """
    호명에서 층을 추출. '1204'->12, '304'->3.
    'B101'·'지하101' 같은 지하 호수는 층별효용 비교 대상이 아니므로 제외한다.
    """
    raw = str(ho).strip()
    if not raw:
        return None
    if raw[0].upper() == "B" or raw.startswith("지하"):
        return None
    s = "".join(ch for ch in raw if ch.isdigit())
    if len(s) < 3:
        return None
    try:
        fl = int(s[:-2])
    except ValueError:
        return None
    return fl or None


def make_pnu(b_code: str, bun: str, ji: str = "0", mountain: bool = False) -> str:
    """카카오 b_code(10자리) + 본번/부번 -> PNU 19자리."""
    return f"{b_code}{'2' if mountain else '1'}{str(bun).zfill(4)}{str(ji).zfill(4)}"
