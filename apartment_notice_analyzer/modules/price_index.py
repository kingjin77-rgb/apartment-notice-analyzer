# -*- coding: utf-8 -*-
"""
시점수정 — 한국부동산원 R-ONE 부동산통계 Open API

감칙 실무기준 [400-3.3.1.4]가 요구하는 시점수정을 실제 감정평가사와 동일한
근거로 수행한다. 실제 감정평가서(청암 CA2308-004)가 쓴 방식 그대로다.

    시점수정치 = 기준시점 지수 / 거래시점 지수

    예) 용인시 수지구 아파트, 거래 2023.04.02 → 기준 2023.08.29
        거래시점 적용지수(2023.03) 88.4 / 기준시점 적용지수(2023.07) 89.1
        시점수정치 = 89.1 / 88.4 ≒ 1.00792

주의(실무): 기준시점 당월 지수가 아직 발표되지 않은 경우가 많다. 감정평가서는
"기준시점 현재 가장 최근에 발표된 지수를 적용"한다고 명시하고 그 시점을 밝힌다.
이 모듈의 latest_available()이 그 처리를 담당한다.

인증키: https://www.reb.or.kr/r-one/portal/openapi/openApiActKeyPage.do (무료, 즉시발급)
개발가이드: https://www.reb.or.kr/r-one/portal/openapi/openApiDevPage.do
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

BASE = "https://www.reb.or.kr/r-one/openapi"

# 전국주택가격동향조사 통계표 ID (2026-08-06 실측 확인)
STATBL = {
    "아파트": "A_2024_00045",        # (월) 매매가격지수_아파트
    "주택종합": "A_2024_00016",       # (월) 매매가격지수_주택종합
    "연립다세대": "A_2024_00080",      # (월) 매매가격지수_연립/다세대
    "단독주택": "A_2024_00114",       # (월) 매매가격지수_단독주택
    "오피스텔": "A_2024_00615",       # (월) 오피스텔 매매가격지수
}


@dataclass
class TimeAdjustment:
    """시점수정 산출 결과 — 감정평가서에 그대로 옮길 수 있는 형태."""

    ratio: float                # 시점수정치
    deal_ym: str                # 거래시점 (YYYYMM)
    base_ym: str                # 기준시점 (YYYYMM)
    deal_index_ym: str          # 실제 적용한 거래시점 지수의 연월
    base_index_ym: str          # 실제 적용한 기준시점 지수의 연월
    deal_index: float
    base_index: float
    region: str
    statbl_nm: str = "(월) 매매가격지수_아파트"

    def describe(self) -> str:
        lag = ""
        if self.base_index_ym != self.base_ym[:6]:
            lag = (f"\n  ※ 기준시점({self.base_ym}) 지수가 미발표되어 "
                   f"발표된 가장 최근 지수({self.base_index_ym})를 적용함.")
        return (
            f"한국부동산원 전국주택가격동향조사 중 {self.region} 아파트 매매가격지수를 활용.\n"
            f"  거래시점 : {self.deal_ym} → {self.deal_index_ym} 지수 적용 : {self.deal_index}\n"
            f"  기준시점 : {self.base_ym} → {self.base_index_ym} 지수 적용 : {self.base_index}\n"
            f"  시점수정치 : {self.base_index} / {self.deal_index} ≒ {self.ratio:.5f}{lag}\n"
            f"  ※ 지수는 기준시점 재개편에 따라 소급 재산정되므로, 과거 감정평가서에\n"
            f"    기재된 지수값과 절대수치는 다를 수 있다(비율은 유효)."
        )


class PriceIndexClient:
    def __init__(self, key: str | None = None):
        self.key = key or os.getenv("REB_RONE_API_KEY")
        self._cache: dict[tuple[str, str], list[dict]] = {}

    @property
    def is_configured(self) -> bool:
        return bool(self.key)

    def _fetch_month(self, statbl_id: str, ym: str) -> list[dict]:
        """해당 연월의 전 지역 지수를 가져온다(약 230개 지역)."""
        ck = (statbl_id, ym)
        if ck in self._cache:
            return self._cache[ck]
        rows: list[dict] = []
        for page in range(1, 4):
            r = requests.get(f"{BASE}/SttsApiTblData.do", params={
                "KEY": self.key, "Type": "json", "pIndex": page, "pSize": 500,
                "STATBL_ID": statbl_id, "DTACYCLE_CD": "MM", "WRTTIME_IDTFR_ID": ym,
            }, timeout=30)
            if r.status_code != 200:
                break
            try:
                blocks = r.json().get("SttsApiTblData", [])
            except ValueError:
                break
            got = []
            for blk in blocks:
                if "row" in blk:
                    got += blk["row"]
            rows += got
            if len(got) < 500:
                break
        self._cache[ck] = rows
        return rows

    def index_of(self, region_keyword: str, ym: str, kind: str = "아파트") -> tuple[float, str] | None:
        """
        region_keyword 에 해당하는 지역의 지수를 찾는다.

        CLS_FULLNM 은 "경기>경부2권>용인시>수지구" 형태의 계층 경로다.
        단순 부분일치로 최심층을 고르면 "화성시" 검색이 그 하위인 "화성시>만세구"에
        걸려버린다. 그래서 경로의 '마지막 마디(CLS_NM)'가 정확히 일치하는 것을
        최우선으로 하고, 없을 때만 부분일치로 넘어간다.
        """
        rows = self._fetch_month(STATBL.get(kind, STATBL["아파트"]), ym)
        if not rows:
            return None

        def leaf(r) -> str:
            return (r.get("CLS_FULLNM") or "").split(">")[-1].strip()

        # 1순위: 말단 지역명 완전일치 (화성시 -> "...>화성시")
        exact = [r for r in rows if leaf(r) == region_keyword]
        if exact:
            # 같은 이름이 여러 시도에 있으면(예: 중구) 경로가 짧은 쪽을 택한다
            exact.sort(key=lambda r: (r.get("CLS_FULLNM") or "").count(">"))
            top = exact[0]
            return float(top["DTA_VAL"]), top["CLS_FULLNM"]

        # 2순위: 부분일치 중 경로가 가장 짧은 것 (상위 행정구역 우선)
        cands = [r for r in rows if region_keyword in (r.get("CLS_FULLNM") or "")]
        if not cands:
            return None
        cands.sort(key=lambda r: (r.get("CLS_FULLNM") or "").count(">"))
        top = cands[0]
        return float(top["DTA_VAL"]), top["CLS_FULLNM"]

    def latest_available(self, region_keyword: str, target_ym: str,
                        kind: str = "아파트", back_months: int = 6) -> tuple[float, str, str] | None:
        """
        target_ym 부터 과거로 훑어 가장 최근에 발표된 지수를 찾는다.
        감정평가 실무상 기준시점 당월 지수가 미발표인 경우가 흔하다.
        반환: (지수, 실제 적용 연월, 지역명)
        """
        y, m = int(target_ym[:4]), int(target_ym[4:6])
        for _ in range(back_months):
            hit = self.index_of(region_keyword, f"{y}{m:02d}", kind)
            if hit:
                return hit[0], f"{y}{m:02d}", hit[1]
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        return None

    def time_adjustment(self, *, region_keyword: str, deal_ym: str, base_ym: str,
                       kind: str = "아파트") -> TimeAdjustment | None:
        """거래시점 → 기준시점 시점수정치를 산출한다."""
        d = self.latest_available(region_keyword, deal_ym, kind)
        b = self.latest_available(region_keyword, base_ym, kind)
        if not d or not b:
            return None
        deal_idx, deal_at, region = d
        base_idx, base_at, _ = b
        if deal_idx == 0:
            return None
        return TimeAdjustment(
            ratio=base_idx / deal_idx, deal_ym=deal_ym, base_ym=base_ym,
            deal_index_ym=deal_at, base_index_ym=base_at,
            deal_index=round(deal_idx, 2), base_index=round(base_idx, 2),
            region=region,
        )
