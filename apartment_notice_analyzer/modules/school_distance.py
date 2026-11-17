# -*- coding: utf-8 -*-
"""
학교 접근성 — 개별요인 [주택지대 별표2] "공공 및 편익시설과의 접근성" 세항목

나이스(NEIS) 학교기본정보는 주소만 주고 좌표를 안 준다. 카카오 지오코딩으로
좌표를 붙인 뒤 대상 좌표까지의 직선거리를 구한다. 배정학구 경계(학구도안내서비스)가
아니라 최근접 거리이므로 "배정 초등학교"가 아니라 "최근접 초등학교" 기준임을
분석 결과에 항상 명시해야 한다 — 배정 여부는 학구도안내서비스 데이터가 있어야 확정된다.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass

import requests

NEIS_BASE = "https://open.neis.go.kr/hub"
KAKAO_LOCAL = "https://dapi.kakao.com/v2/local"

SCHOOL_KIND = {"초등학교": "초등학교", "중학교": "중학교", "고등학교": "고등학교"}


@dataclass
class SchoolDistance:
    school_kind: str
    school_name: str
    dist_m: int
    note: str = "최근접 거리 기준 (배정학구 아님 — 학구도안내서비스 별도 확인 필요)"


class SchoolDistanceFinder:
    def __init__(self, neis_key: str | None = None, kakao_key: str | None = None):
        self.neis_key = neis_key or os.getenv("NEIS_API_KEY")
        self.kakao_key = kakao_key or os.getenv("KAKAO_REST_API_KEY")
        self._geo_cache: dict[str, tuple[float, float] | None] = {}

    @property
    def is_configured(self) -> bool:
        return bool(self.neis_key and self.kakao_key)

    def _kakao_headers(self) -> dict:
        return {"Authorization": f"KakaoAK {self.kakao_key}"}

    def _geocode(self, addr: str) -> tuple[float, float] | None:
        if addr in self._geo_cache:
            return self._geo_cache[addr]
        result = None
        for endpoint, key in (("address", "query"), ("keyword", "query")):
            try:
                r = requests.get(f"{KAKAO_LOCAL}/search/{endpoint}.json",
                                 headers=self._kakao_headers(), params={key: addr, "size": 1}, timeout=10)
                docs = r.json().get("documents") or []
                if docs:
                    result = (float(docs[0]["y"]), float(docs[0]["x"]))
                    break
            except Exception:
                continue
        self._geo_cache[addr] = result
        return result

    def nearby_schools(self, atpt_code: str, lat: float, lng: float,
                       kinds: tuple[str, ...] = ("초등학교", "중학교"),
                       radius_m: int = 2000, limit_per_kind: int = 5) -> list[SchoolDistance]:
        """
        atpt_code: 시도교육청코드(ATPT_OFCDC_SC_CODE). 학교alarmi 표준코드.
        NEIS는 좌표검색이 없어 카카오 카테고리검색(SC4=학교)으로 후보를 먼저 모으고,
        각 학교급은 카카오 키워드로 필터한다.
        """
        out: list[SchoolDistance] = []
        for kind in kinds:
            try:
                r = requests.get(f"{KAKAO_LOCAL}/search/keyword.json",
                                 headers=self._kakao_headers(),
                                 params={"query": kind, "y": lat, "x": lng, "radius": radius_m,
                                        "size": limit_per_kind, "sort": "distance"}, timeout=10)
                docs = r.json().get("documents") or []
            except Exception:
                docs = []
            for d in docs:
                if kind not in d.get("category_name", "") and kind not in d.get("place_name", ""):
                    continue
                dist = d.get("distance")
                if not dist:
                    dist = round(_haversine(lat, lng, float(d["y"]), float(d["x"])))
                out.append(SchoolDistance(school_kind=kind, school_name=d["place_name"], dist_m=int(dist)))
        return out

    def nearest(self, lat: float, lng: float, kind: str = "초등학교") -> SchoolDistance | None:
        r = self.nearby_schools("", lat, lng, kinds=(kind,), limit_per_kind=1)
        return r[0] if r else None


def _haversine(lat1, lng1, lat2, lng2) -> float:
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))
