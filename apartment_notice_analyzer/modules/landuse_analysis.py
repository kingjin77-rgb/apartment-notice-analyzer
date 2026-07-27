"""
landuse_analysis.py
아파트 모집공고문 분석 — 3순위 모듈: 용도지역·주변 개발계획

목적:
  "지금은 뷰가 트여 있으나 앞 필지가 준주거지역이라 향후 고층 신축 가능" 같은,
  공고문에 조망 관련 문구가 붙어 있어도 입주민이 판단할 수 없는 사안을
  용도지역·건폐율·용적률로 정량화한다.

  → 조망·일조 침해 '예고' 근거자료. 입예협이 시행사에 사전 고지 이행 여부를
     따지거나, 조망 프리미엄 세대 배치를 문제 삼을 때 사용.

데이터:
  V-World 2D 데이터 API (api.vworld.kr)
    - LT_C_UQ111 : 용도지역
    - LT_C_UPISUQ151 : 도시계획시설
  토지이음(eum.go.kr) : API 미제공 → 링크 첨부 + 수동확인 안내

인증키:
  VWORLD_API_KEY (신규 — vworld.kr 오픈API 신청, 무료)
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field, asdict
from typing import Any

import requests

log = logging.getLogger(__name__)

VWORLD_API_KEY = os.getenv("VWORLD_API_KEY", "")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

VWORLD_DATA = "https://api.vworld.kr/req/data"
EUM_LINK = "https://www.eum.go.kr/web/ar/lu/luLandDet.jsp"

TIMEOUT = 15

# 국토계획법 시행령 [별표] 용도지역별 건폐율/용적률 상한 (조례로 강화 가능)
ZONE_SPEC: dict[str, dict[str, Any]] = {
    "제1종전용주거지역": {"bcr": 50, "far": 100, "risk": "하"},
    "제2종전용주거지역": {"bcr": 50, "far": 150, "risk": "하"},
    "제1종일반주거지역": {"bcr": 60, "far": 200, "risk": "하"},
    "제2종일반주거지역": {"bcr": 60, "far": 250, "risk": "중"},
    "제3종일반주거지역": {"bcr": 50, "far": 300, "risk": "중"},
    "준주거지역":       {"bcr": 70, "far": 500, "risk": "상"},
    "중심상업지역":     {"bcr": 90, "far": 1500, "risk": "상"},
    "일반상업지역":     {"bcr": 80, "far": 1300, "risk": "상"},
    "근린상업지역":     {"bcr": 70, "far": 900, "risk": "상"},
    "유통상업지역":     {"bcr": 80, "far": 1100, "risk": "상"},
    "전용공업지역":     {"bcr": 70, "far": 300, "risk": "상"},
    "일반공업지역":     {"bcr": 70, "far": 350, "risk": "상"},
    "준공업지역":       {"bcr": 70, "far": 400, "risk": "상"},
    "보전녹지지역":     {"bcr": 20, "far": 80, "risk": "하"},
    "생산녹지지역":     {"bcr": 20, "far": 100, "risk": "하"},
    "자연녹지지역":     {"bcr": 20, "far": 100, "risk": "하"},
    "보전관리지역":     {"bcr": 20, "far": 80, "risk": "하"},
    "생산관리지역":     {"bcr": 20, "far": 80, "risk": "하"},
    "계획관리지역":     {"bcr": 40, "far": 100, "risk": "중"},
    "농림지역":         {"bcr": 20, "far": 80, "risk": "하"},
    "자연환경보전지역": {"bcr": 20, "far": 80, "risk": "하"},
}

# 기피 도시계획시설
AVOID_FACILITY = {
    "화장시설": "상", "장사시설": "상", "봉안시설": "상", "납골당": "상", "공동묘지": "상",
    "폐기물처리시설": "상", "소각장": "상", "소각시설": "상", "자원회수시설": "중",
    "분뇨처리시설": "상", "쓰레기처리장": "상", "재활용시설": "중",
    "하수처리장": "상", "하수종말처리시설": "상", "물재생센터": "상", "하수도": "중",
    "변전소": "중", "송전선로": "상", "고압선": "상", "송전탑": "상",
    "이동통신기지국": "하", "기지국": "하",
    "자동차정류장": "중", "버스차고지": "중", "도축장": "상", "공동구": "하",
    "교정시설": "상", "구치소": "상", "교도소": "상",
    "군사시설": "중", "탄약고": "상",
    "위험물저장및처리시설": "상", "유류저장시설": "상",
}


@dataclass
class ZoneItem:
    kind: str            # 용도지역 / 도시계획시설
    name: str
    bcr: int | None = None      # 건폐율
    far: int | None = None      # 용적률
    distance_m: int | None = None
    severity: str = "하"
    implication: str = ""
    geometry: list | None = None  # GeoJSON MultiPolygon/Polygon coordinates (WGS84) — 지도 시각화용


@dataclass
class LandUseReport:
    address: str
    lat: float | None = None
    lon: float | None = None
    radius_m: int = 500
    site_zone: str | None = None
    items: list[ZoneItem] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    eum_url: str = EUM_LINK
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────────────────────

def geocode(address: str) -> tuple[float, float] | None:
    if not KAKAO_REST_API_KEY:
        return None
    try:
        r = requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
            params={"query": address}, timeout=TIMEOUT,
        )
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if docs:
            return float(docs[0]["y"]), float(docs[0]["x"])
    except Exception as e:  # noqa: BLE001
        log.warning("지오코딩 실패: %s", e)
    return None


def _bbox(lat: float, lon: float, radius_m: int) -> str:
    """대략적 위경도 bbox (위도 1도≈111km)"""
    dlat = radius_m / 111_000
    dlon = radius_m / (111_000 * 0.75)
    return f"{lon - dlon},{lat - dlat},{lon + dlon},{lat + dlat}"


def _vworld(data_id: str, lat: float, lon: float, radius_m: int,
            size: int = 100) -> list[dict]:
    if not VWORLD_API_KEY:
        raise RuntimeError("VWORLD_API_KEY 미설정")
    r = requests.get(
        VWORLD_DATA,
        params={
            "service": "data", "request": "GetFeature", "version": "2.0",
            "key": VWORLD_API_KEY, "format": "json",
            "data": data_id,
            "geomFilter": f"BOX({_bbox(lat, lon, radius_m)})",
            "size": size, "page": 1,
            "domain": os.getenv("VWORLD_DOMAIN", "http://localhost"),
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    j = r.json()
    try:
        return j["response"]["result"]["featureCollection"]["features"]
    except (KeyError, TypeError):
        status = j.get("response", {}).get("status")
        log.warning("V-World 응답 이상 (status=%s, data=%s)", status, data_id)
        return []


def _normalize_zone(name: str) -> str:
    n = (name or "").replace(" ", "")
    for key in ZONE_SPEC:
        if key.replace(" ", "") in n:
            return key
    return name


# ─────────────────────────────────────────────────────────────
# 1) 용도지역
# ─────────────────────────────────────────────────────────────

def fetch_zones(lat: float, lon: float, radius_m: int) -> tuple[list[ZoneItem], str | None]:
    try:
        feats = _vworld("LT_C_UQ111", lat, lon, radius_m)
    except Exception as e:  # noqa: BLE001
        return [], f"V-World 용도지역 조회 실패: {e}"

    by_zone: dict[str, ZoneItem] = {}
    for f in feats:
        props = f.get("properties", {})
        raw = props.get("dgm_nm") or props.get("uname") or props.get("prposArea1Nm") or ""
        z = _normalize_zone(raw)
        if not z:
            continue
        geom = f.get("geometry", {}).get("coordinates")
        if z in by_zone:
            if geom:
                by_zone[z].geometry.append(geom)
            continue
        spec = ZONE_SPEC.get(z)
        by_zone[z] = ZoneItem(
            kind="용도지역",
            name=z,
            bcr=spec["bcr"] if spec else None,
            far=spec["far"] if spec else None,
            severity=spec["risk"] if spec else "하",
            implication=(
                f"용적률 상한 {spec['far']}% — 향후 고층 신축 가능, 조망·일조 침해 여지"
                if spec and spec["risk"] in ("중", "상") else "저층 유지 가능성 높음"
            ) if spec else "용도지역 정보 확인 필요",
            geometry=[geom] if geom else [],
        )
    return list(by_zone.values()), None


# ─────────────────────────────────────────────────────────────
# 2) 도시계획시설 (기피시설)
# ─────────────────────────────────────────────────────────────

def fetch_facilities(lat: float, lon: float, radius_m: int) -> tuple[list[ZoneItem], str | None]:
    try:
        feats = _vworld("LT_C_UPISUQ151", lat, lon, radius_m)
    except Exception as e:  # noqa: BLE001
        return [], f"V-World 도시계획시설 조회 실패: {e}"

    out: list[ZoneItem] = []
    for f in feats:
        props = f.get("properties", {})
        nm = props.get("dgm_nm") or props.get("uname") or ""
        sev = None
        for key, s in AVOID_FACILITY.items():
            if key in nm:
                sev = s
                break
        if not sev:
            continue
        geom = f.get("geometry", {}).get("coordinates")
        out.append(ZoneItem(
            kind="도시계획시설",
            name=nm,
            severity=sev,
            implication="기피시설 도시계획 결정 — 공고문 고지 여부 확인 및 이격·차폐 요구 근거",
            geometry=[geom] if geom else [],
        ))
    return out, None


# ─────────────────────────────────────────────────────────────
# 메인 엔트리
# ─────────────────────────────────────────────────────────────

def analyze_landuse(address: str, radius_m: int = 500) -> LandUseReport:
    """
    >>> rep = analyze_landuse("경기도 의왕시 삼동 191-1", radius_m=500)
    >>> rep.site_zone
    '제3종일반주거지역'
    """
    rep = LandUseReport(address=address, radius_m=radius_m)

    coord = geocode(address)
    if not coord:
        rep.errors.append("지오코딩 실패")
        return rep
    rep.lat, rep.lon = coord

    zones, err = fetch_zones(coord[0], coord[1], radius_m)
    if err:
        rep.errors.append(err)
    rep.items.extend(zones)
    if zones:
        rep.site_zone = zones[0].name

    facs, err2 = fetch_facilities(coord[0], coord[1], radius_m)
    if err2:
        rep.errors.append(err2)
    rep.items.extend(facs)

    # 종합 소견
    high = [z for z in zones if z.severity == "상"]
    if high:
        names = ", ".join(z.name for z in high)
        rep.findings.append(
            f"[상] 반경 {radius_m}m 내 고밀 용도지역 존재({names}) — "
            f"향후 고층 개발 시 조망·일조 침해 가능. 공고문의 조망 관련 면책조항과 "
            f"교차 검토 필요."
        )
    bad_fac = [f for f in facs if f.severity == "상"]
    if bad_fac:
        rep.findings.append(
            f"[상] 기피 도시계획시설 {len(bad_fac)}건 — "
            f"모집공고문 내 고지 여부 확인 후 미고지 시 이의제기 대상."
        )
    if not rep.findings:
        rep.findings.append("주변 용도지역 특이사항 없음 (저·중밀 유지)")

    rep.findings.append(
        "※ 정확한 지구단위계획·개발행위허가 이력은 토지이음(eum.go.kr)에서 "
        "지번 직접 조회 필요 — API 미제공"
    )
    return rep


def to_docx_rows(rep: LandUseReport) -> list[list[str]]:
    rows = [["구분", "명칭", "건폐율", "용적률", "심각도", "시사점"]]
    order = {"상": 0, "중": 1, "하": 2}
    for i in sorted(rep.items, key=lambda x: order.get(x.severity, 3)):
        rows.append([
            i.kind, i.name,
            f"{i.bcr}%" if i.bcr else "-",
            f"{i.far}%" if i.far else "-",
            i.severity, i.implication,
        ])
    return rows


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import json, sys
    addr = sys.argv[1] if len(sys.argv) > 1 else "경기도 의왕시 삼동"
    print(json.dumps(analyze_landuse(addr).to_dict(), ensure_ascii=False, indent=2))
