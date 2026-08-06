# -*- coding: utf-8 -*-
"""
동별 향(방위) 추정 — V-World 건물통합정보(LT_C_BLDGINFO) 외곽 폴리곤 기반

감정평가 호별요인의 "향별 효용"은 어떤 API도 직접 주지 않는다. 그런데
아파트 판상형은 세대가 건물 장축(長軸)에 직교하는 방향을 바라보도록 배치되므로,
건물 외곽 폴리곤의 장축 방위각을 구하면 그 동의 주된 향을 추정할 수 있다.

    장축 방위각 = 최소외접직사각형의 긴 변 방향
    주향(主向)  = 장축에 직교하는 두 방향 중 남쪽에 가까운 쪽

한계가 분명하다.
  - 타워형(ㅁ자·Y자)은 세대별 향이 제각각이라 장축 추정이 무의미하다.
    종횡비(aspect ratio)가 낮으면 "타워형 추정"으로 표시하고 향을 내지 않는다.
  - 같은 동 안에서도 라인별로 향이 다르다(동/서 양면). 여기서는 동 단위
    주향만 낸다. 세대 단위 향은 공시가격 라인별 역산으로 별도 접근한다.
  - 실제 감정평가는 임장으로 확인한다. 이 값은 사전 추정치다.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass

import requests

VWORLD_DATA = "https://api.vworld.kr/req/data"

# 8방위 — 감정평가서 표기 관행
DIRECTIONS = [
    (0, "북"), (45, "북동"), (90, "동"), (135, "남동"),
    (180, "남"), (225, "남서"), (270, "서"), (315, "북서"),
]

# 향별 선호도 — 국내 아파트 시장의 통상적 서열.
# 실제 격차율은 공시가격 라인별 역산으로 실측해야 하며, 이건 정성 판단용이다.
PREFERENCE = {"남": 1.00, "남동": 0.98, "남서": 0.97, "동": 0.95,
              "서": 0.93, "북동": 0.91, "북서": 0.90, "북": 0.88}


@dataclass
class Orientation:
    dong_name: str
    main_direction: str        # 추정 주향 (8방위)
    azimuth: float             # 주향 방위각 (도, 북=0 시계방향)
    long_axis_deg: float       # 장축 방위각
    aspect_ratio: float        # 종횡비 — 판상형 판단
    shape: str                 # 판상형 / 타워형(추정) / 판단보류
    lat: float = 0.0
    lng: float = 0.0
    note: str = ""

    @property
    def preference(self) -> float | None:
        return PREFERENCE.get(self.main_direction)


class OrientationEstimator:
    def __init__(self, key: str | None = None):
        self.key = key or os.getenv("VWORLD_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.key)

    def fetch_buildings(self, lat: float, lng: float, buffer_m: int = 250,
                       size: int = 100) -> list[dict]:
        """대상 좌표 주변 건물 외곽 폴리곤을 가져온다."""
        if not self.is_configured:
            return []
        out = []
        page = 1
        while page <= 5:
            r = requests.get(VWORLD_DATA, params={
                "key": self.key, "service": "data", "request": "GetFeature",
                "data": "LT_C_BLDGINFO", "format": "json",
                "geomFilter": f"POINT({lng} {lat})", "buffer": buffer_m,
                "size": size, "page": page,
            }, timeout=25)
            if r.status_code != 200:
                break
            try:
                body = r.json()
            except ValueError:
                break
            res = (body.get("response") or {}).get("result") or {}
            fc = res.get("featureCollection") or {}
            feats = fc.get("features") or []
            if not feats:
                break
            out += feats
            pg = (body.get("response") or {}).get("page") or {}
            if int(pg.get("current", 1)) >= int(pg.get("total", 1)):
                break
            page += 1
        return out

    def estimate(self, lat: float, lng: float, buffer_m: int = 250,
                min_area_m2: float = 300.0) -> list[Orientation]:
        """
        주변 건물들의 향을 추정한다.
        min_area_m2 미만은 부속동(경비실·주차장 램프 등)으로 보고 제외한다.
        """
        results: list[Orientation] = []
        for f in self.fetch_buildings(lat, lng, buffer_m):
            props = f.get("properties") or {}
            geom = f.get("geometry") or {}
            ring = _outer_ring(geom)
            if not ring or len(ring) < 4:
                continue
            area = _polygon_area_m2(ring)
            if area < min_area_m2:
                continue
            long_deg, aspect = _long_axis(ring)
            name = (props.get("bldnm") or props.get("BLDNM")
                   or props.get("buld_nm") or "").strip()
            cy = sum(p[1] for p in ring) / len(ring)
            cx = sum(p[0] for p in ring) / len(ring)

            if aspect < 1.4:
                results.append(Orientation(
                    dong_name=name, main_direction="", azimuth=0.0,
                    long_axis_deg=long_deg, aspect_ratio=aspect,
                    shape="타워형(추정)", lat=cy, lng=cx,
                    note="종횡비가 낮아 세대별 향이 제각각일 수 있다. 향 추정을 보류한다.",
                ))
                continue

            az = _facing_from_long_axis(long_deg)
            results.append(Orientation(
                dong_name=name, main_direction=_to_compass(az), azimuth=az,
                long_axis_deg=long_deg, aspect_ratio=aspect, shape="판상형",
                lat=cy, lng=cx,
                note="건물 장축에 직교하는 방향 중 남향에 가까운 쪽을 주향으로 추정.",
            ))
        return results


# ---------------------------------------------------------------------------
# 기하 계산
# ---------------------------------------------------------------------------

def _outer_ring(geom: dict) -> list[tuple[float, float]]:
    """MultiPolygon/Polygon에서 가장 바깥 링을 뽑는다."""
    t = geom.get("type")
    c = geom.get("coordinates") or []
    try:
        if t == "MultiPolygon":
            best, best_n = [], 0
            for poly in c:
                if poly and len(poly[0]) > best_n:
                    best, best_n = poly[0], len(poly[0])
            return [(float(p[0]), float(p[1])) for p in best]
        if t == "Polygon":
            return [(float(p[0]), float(p[1])) for p in c[0]]
    except (IndexError, TypeError, ValueError):
        return []
    return []


def _m_per_deg(lat: float) -> tuple[float, float]:
    """위도에서의 1도당 미터 (경도, 위도)."""
    return 111320.0 * math.cos(math.radians(lat)), 110540.0


def _polygon_area_m2(ring: list[tuple[float, float]]) -> float:
    if len(ring) < 3:
        return 0.0
    lat0 = sum(p[1] for p in ring) / len(ring)
    mx, my = _m_per_deg(lat0)
    pts = [((x - ring[0][0]) * mx, (y - ring[0][1]) * my) for x, y in ring]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def _long_axis(ring: list[tuple[float, float]]) -> tuple[float, float]:
    """
    최소외접직사각형을 회전 캘리퍼스 근사(1도 단위 스캔)로 구해
    장축 방위각(북=0, 시계방향)과 종횡비를 반환한다.
    """
    lat0 = sum(p[1] for p in ring) / len(ring)
    mx, my = _m_per_deg(lat0)
    pts = [((x - ring[0][0]) * mx, (y - ring[0][1]) * my) for x, y in ring]

    best = None
    for deg in range(0, 180):
        th = math.radians(deg)
        cos_t, sin_t = math.cos(th), math.sin(th)
        xs = [p[0] * cos_t + p[1] * sin_t for p in pts]
        ys = [-p[0] * sin_t + p[1] * cos_t for p in pts]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        a = w * h
        if best is None or a < best[0]:
            best = (a, deg, w, h)

    _, deg, w, h = best
    if w >= h:
        long_dir_math = deg          # x축 방향이 장축
        aspect = w / h if h else 999
    else:
        long_dir_math = deg + 90     # y축 방향이 장축
        aspect = h / w if w else 999

    # 수학각(동=0, 반시계) -> 방위각(북=0, 시계)
    az = (90 - long_dir_math) % 360
    return az % 180, round(aspect, 2)


def _facing_from_long_axis(long_az: float) -> float:
    """장축에 직교하는 두 방향 중 남(180도)에 가까운 쪽을 주향으로."""
    a = (long_az + 90) % 360
    b = (long_az - 90) % 360
    return a if _angle_gap(a, 180) <= _angle_gap(b, 180) else b


def _angle_gap(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _to_compass(az: float) -> str:
    best, gap = "북", 999.0
    for deg, name in DIRECTIONS:
        g = _angle_gap(az, deg)
        if g < gap:
            best, gap = name, g
    return best
