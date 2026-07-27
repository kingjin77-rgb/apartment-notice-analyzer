"""
environment_analysis.py
아파트 모집공고문 분석 — 1순위 모듈: 환경권(소음·악취·대기)

목적:
  입주 전(사용승인 전) 사업장도 조회 가능한 데이터만 사용한다.
  - EIASS(환경영향평가정보지원시스템): 사업 착공 전 '예측치'가 존재 → 입주 전에도 유효
  - 에어코리아: 인근 측정소 실측 → 현재 대기질 baseline

산출:
  EnvironmentReport (dict) — 공고문 유의사항 리포트의 '환경권' 섹션 근거자료

EIASS 조회 흐름 (실제 API는 좌표·반경 직접조회가 아니라 mgtNo(사업코드) 필수):
  단지 좌표 → BsnsAreaService/getInfoWFS (bbox) → mgtNo 확보
            → NoiseVibrationService/getInfo(mgtNo)  → 소음·진동 조사/예측치
            → AirqualityService/getInfo(mgtNo)      → 대기질 예측치
  서비스 4종(사업구역/소음진동/대기질/악취) 모두 기관코드 B090026 고정,
  인증키는 MOLIT_API_KEY(data.go.kr 통합키)와 동일. bbox는 EPSG:32652(UTM 52N,
  m 단위)로 투영해야 한다. 오퍼레이션명은 서비스별로 다르다 —
  NoiseVibrationService는 getInfo, Airquality/Foulsmell(악취)Service는
  getIvstg(조사)/getPredict(예측) (eiass.go.kr 오픈API가이드로 확인, 2026-07-27).
"""

from __future__ import annotations

import os
import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Any

import requests
import xmltodict
from pyproj import Transformer

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────────────────────

MOLIT_API_KEY = os.getenv("MOLIT_API_KEY", "")  # data.go.kr 일반인증키 (공용, EIASS 3종 서비스 공용)
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

# 에어코리아 (실측 baseline — EIASS와 별개, 엔드포인트 확인됨)
AIRKOREA_MSRSTN = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc"
AIRKOREA_ARPLTN = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"

# EIASS — 기관코드 B090026 고정 (data.go.kr 개발계정 자동승인, 트래픽 10,000건/일)
# eiass.go.kr 오픈API 가이드(chapter04_03/13/15)로 확인 완료 (2026-07-27)
EIASS_BSNSAREA = "http://apis.data.go.kr/B090026/BsnsAreaService"
EIASS_NOISE = "http://apis.data.go.kr/B090026/NoiseVibrationService"
EIASS_AIR = "http://apis.data.go.kr/B090026/AirqualityService"
EIASS_ODOR_BASE = "http://apis.data.go.kr/B090026/FoulsmellService"

TIMEOUT = 12
DEFAULT_RADIUS_M = 1000

# WGS84(위경도) → EPSG:32652(UTM 52N, m) — bbox 조회용
_TO_UTM52N = Transformer.from_crs("EPSG:4326", "EPSG:32652", always_xy=True)


# ─────────────────────────────────────────────────────────────
# 데이터 모델
# ─────────────────────────────────────────────────────────────

@dataclass
class EnvItem:
    """개별 환경 이슈 1건"""
    category: str            # 소음 / 악취 / 대기
    name: str                # 시설·사업명
    distance_m: int | None   # 단지로부터 거리
    value: str | None        # 측정·예측치
    unit: str | None
    severity: str            # 상 / 중 / 하
    source: str              # 출처(API명)
    note: str = ""


@dataclass
class EnvironmentReport:
    address: str
    lat: float | None = None
    lon: float | None = None
    radius_m: int = DEFAULT_RADIUS_M
    items: list[EnvItem] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


# ─────────────────────────────────────────────────────────────
# 공통 유틸
# ─────────────────────────────────────────────────────────────

def _get_json_or_xml(url: str, params: dict) -> dict | None:
    """data.go.kr 계열 JSON/XML 응답 파싱"""
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        if r.text.lstrip().startswith("{"):
            return r.json()
        return xmltodict.parse(r.text)
    except Exception as e:  # noqa: BLE001
        log.warning("API 호출 실패 %s : %s", url, e)
        return None


def _items_of(parsed: dict | None) -> list[dict]:
    """response.body.items.item 을 안전하게 리스트로 뽑는다"""
    if not parsed:
        return []
    try:
        body = parsed["response"]["body"]
        items = body.get("items")
        if not items:
            return []
        item = items.get("item") if isinstance(items, dict) else items
        if item is None:
            return []
        return item if isinstance(item, list) else [item]
    except Exception:  # noqa: BLE001
        return []


def _haversine_m(lat1, lon1, lat2, lon2) -> int:
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return int(2 * R * math.asin(math.sqrt(a)))


def _bbox_utm(lat: float, lon: float, radius_m: int) -> str:
    """중심좌표(WGS84) + 반경(m) → EPSG:32652 bbox 문자열 (minx,miny,maxx,maxy)"""
    x, y = _TO_UTM52N.transform(lon, lat)
    return f"{x - radius_m},{y - radius_m},{x + radius_m},{y + radius_m}"


# ─────────────────────────────────────────────────────────────
# 지오코딩 (카카오)
# ─────────────────────────────────────────────────────────────

def geocode(address: str) -> tuple[float, float] | None:
    if not KAKAO_REST_API_KEY:
        log.warning("KAKAO_REST_API_KEY 없음 — 지오코딩 생략")
        return None
    try:
        r = requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
            params={"query": address},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if not docs:
            # 도로명 실패 시 키워드 검색으로 재시도
            r = requests.get(
                "https://dapi.kakao.com/v2/local/search/keyword.json",
                headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
                params={"query": address},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            docs = r.json().get("documents", [])
        if not docs:
            return None
        return float(docs[0]["y"]), float(docs[0]["x"])
    except Exception as e:  # noqa: BLE001
        log.warning("지오코딩 실패: %s", e)
        return None


# ─────────────────────────────────────────────────────────────
# 심각도 판정 — 소음·진동 관리기준(주거지역) 기준
# ─────────────────────────────────────────────────────────────

# 환경정책기본법 시행령 [별표] 소음 환경기준(일반지역 '가' 주거지역)
#   낮(06~22) 55 dB / 밤(22~06) 45 dB
NOISE_LIMIT_DAY = 55
NOISE_LIMIT_NIGHT = 45


def noise_severity(db_value: float | None, is_night: bool = False) -> str:
    if db_value is None:
        return "하"
    limit = NOISE_LIMIT_NIGHT if is_night else NOISE_LIMIT_DAY
    over = db_value - limit
    if over >= 10:
        return "상"
    if over > 0:
        return "중"
    return "하"


def distance_severity(dist_m: int | None) -> str:
    """혐오시설 거리 기반 기본 심각도"""
    if dist_m is None:
        return "하"
    if dist_m <= 300:
        return "상"
    if dist_m <= 800:
        return "중"
    return "하"


# ─────────────────────────────────────────────────────────────
# 0) 사업구역정보 — bbox 조회로 인근 사업코드(mgtNo) 확보 (소음·대기 조회의 선행 단계)
# ─────────────────────────────────────────────────────────────

def find_nearby_mgtno(lat: float, lon: float, radius_m: int) -> tuple[list[dict], str | None]:
    """
    반경 내 환경영향평가 사업구역을 찾아 (mgtNo, 사업명, 구분) 목록을 반환한다.
    NoiseVibrationService / AirqualityService 조회는 이 mgtNo가 있어야 가능하다.
    """
    if not MOLIT_API_KEY:
        return [], "MOLIT_API_KEY 미설정 — 사업구역 조회 생략"
    try:
        r = requests.get(
            f"{EIASS_BSNSAREA}/getInfoWFS",
            params={
                "serviceKey": MOLIT_API_KEY,
                "srsName": "EPSG:32652",
                "bbox": _bbox_utm(lat, lon, radius_m),
                "maxFeatures": 50,
                "resultType": "result",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        parsed = xmltodict.parse(r.text) if not r.text.lstrip().startswith("{") else r.json()
    except Exception as e:  # noqa: BLE001
        return [], f"사업구역정보 조회 실패: {e}"

    # WFS GetFeature 응답 구조: featureMember 반복
    try:
        members = parsed.get("wfs:FeatureCollection", parsed).get("gml:featureMember")
        if members is None:
            return [], None
        if not isinstance(members, list):
            members = [members]
    except Exception:  # noqa: BLE001
        return [], "사업구역정보 응답 구조 파싱 실패 (typeName·네임스페이스 확인 필요)"

    out: list[dict] = []
    for m in members:
        feat = next(iter(m.values()), {})
        out.append({
            "mgtNo": feat.get("MGTNO") or feat.get("mgtNo"),
            "bsnsNm": feat.get("BSNS_NM") or feat.get("bsnsNm") or "사업명 미상",
            "bsnsOd": feat.get("BSNS_OD") or feat.get("bsnsOd"),
        })
    return [o for o in out if o.get("mgtNo")], None


# ─────────────────────────────────────────────────────────────
# 1) 소음·진동 조사·예측 (mgtNo 필수)
# ─────────────────────────────────────────────────────────────

def fetch_noise(mgt_no: str, bsns_nm: str = "") -> tuple[list[EnvItem], str | None]:
    parsed = _get_json_or_xml(
        f"{EIASS_NOISE}/getInfo",
        {"serviceKey": MOLIT_API_KEY, "mgtNo": mgt_no, "numOfRows": 100, "pageNo": 1, "type": "xml"},
    )
    rows = _items_of(parsed)
    if not rows:
        return [], None  # 해당 사업구역에 소음·진동 조사자료 없음 (정상적인 경우)

    out: list[EnvItem] = []
    for r in rows:
        val = r.get("noiseVal") or r.get("value")
        try:
            fval = float(val)
        except (TypeError, ValueError):
            fval = None
        out.append(EnvItem(
            category="소음",
            name=r.get("ivstgSpotNm") or bsns_nm or "사업장",
            distance_m=None,
            value=str(val) if val is not None else None,
            unit="dB(A)",
            severity=noise_severity(fval),
            source="EIASS 소음·진동 조사·예측",
            note=f"사업코드 {mgt_no} — 환경영향평가서 예측치, 입주 전 사업장 대응 근거",
        ))
    return out, None


# ─────────────────────────────────────────────────────────────
# 2) 악취 예측정보 (FoulsmellService, mgtNo 필수)
# ─────────────────────────────────────────────────────────────

def fetch_odor(mgt_no: str, bsns_nm: str = "") -> tuple[list[EnvItem], str | None]:
    parsed = _get_json_or_xml(
        f"{EIASS_ODOR_BASE}/getPredict",
        {"serviceKey": MOLIT_API_KEY, "mgtNo": mgt_no, "numOfRows": 100, "pageNo": 1, "type": "xml"},
    )
    rows = _items_of(parsed)
    if not rows:
        return [], None

    out: list[EnvItem] = []
    for r in rows:
        out.append(EnvItem(
            category="악취",
            name=r.get("faciltNm") or bsns_nm or "악취배출시설",
            distance_m=None,
            value=r.get("odorValue") or r.get("value"),
            unit="희석배수",
            severity="중",
            source="EIASS 악취정보",
            note=f"사업코드 {mgt_no} — 혐오시설 인접, 조망·환기 관련 개선요구 근거",
        ))
    return out, None


# ─────────────────────────────────────────────────────────────
# 3) EIASS 대기질 예측치 (mgtNo 필수, 착공 전 예측)
# ─────────────────────────────────────────────────────────────

def fetch_air_eiass(mgt_no: str, bsns_nm: str = "") -> tuple[list[EnvItem], str | None]:
    parsed = _get_json_or_xml(
        f"{EIASS_AIR}/getPredict",
        {"serviceKey": MOLIT_API_KEY, "mgtNo": mgt_no, "numOfRows": 100, "pageNo": 1, "type": "xml"},
    )
    rows = _items_of(parsed)
    if not rows:
        return [], None

    out: list[EnvItem] = []
    for r in rows:
        out.append(EnvItem(
            category="대기",
            name=f"{bsns_nm} 환경영향평가 예측치",
            distance_m=None,
            value=r.get("value") or r.get("prdctValue"),
            unit=r.get("unit") or "",
            severity="하",
            source="EIASS 대기질 예측정보",
            note=f"사업코드 {mgt_no} — 착공 전 예측치, 입주 후 실측 대조용",
        ))
    return out, None


# ─────────────────────────────────────────────────────────────
# 4) 에어코리아 — 근접측정소 + 실시간 대기질 (실측 baseline, EIASS와 별개)
# ─────────────────────────────────────────────────────────────

def _tm_coord(address: str) -> tuple[float, float] | None:
    """에어코리아 TM 좌표 변환"""
    parsed = _get_json_or_xml(
        f"{AIRKOREA_MSRSTN}/getTMStdrCrdnt",
        {"serviceKey": MOLIT_API_KEY, "umdName": address, "returnType": "xml", "numOfRows": 1, "pageNo": 1},
    )
    rows = _items_of(parsed)
    if not rows:
        return None
    try:
        return float(rows[0]["tmX"]), float(rows[0]["tmY"])
    except (KeyError, TypeError, ValueError):
        return None


def fetch_air(address: str, sido: str | None = None) -> tuple[list[EnvItem], str | None]:
    """근접 측정소를 찾고, 해당 시도 실시간 측정치를 붙인다"""
    umd = address.split()[-1] if address else ""
    tm = _tm_coord(umd)
    if not tm:
        return [], "에어코리아 TM 좌표 변환 실패"

    parsed = _get_json_or_xml(
        f"{AIRKOREA_MSRSTN}/getNearbyMsrstnList",
        {"serviceKey": MOLIT_API_KEY, "tmX": tm[0], "tmY": tm[1], "returnType": "xml", "numOfRows": 3, "pageNo": 1},
    )
    stations = _items_of(parsed)
    if not stations:
        return [], "근접 측정소 조회 실패"

    st_name = stations[0].get("stationName")
    st_dist = stations[0].get("tm")  # km

    # 실시간 측정치
    if not sido:
        sido = address.split()[0] if address else "경기"
    parsed2 = _get_json_or_xml(
        f"{AIRKOREA_ARPLTN}/getCtprvnRltmMesureDnsty",
        {
            "serviceKey": MOLIT_API_KEY,
            "sidoName": sido,
            "returnType": "xml",
            "numOfRows": 200,
            "pageNo": 1,
            "ver": "1.3",
        },
    )
    measures = _items_of(parsed2)
    target = next((m for m in measures if m.get("stationName") == st_name), None)

    out: list[EnvItem] = []
    if target:
        for key, label, unit, bad in (
            ("pm10Value", "미세먼지(PM10)", "㎍/㎥", 80),
            ("pm25Value", "초미세먼지(PM2.5)", "㎍/㎥", 35),
        ):
            v = target.get(key)
            try:
                fv = float(v)
                sev = "상" if fv >= bad * 1.5 else ("중" if fv >= bad else "하")
            except (TypeError, ValueError):
                fv, sev = None, "하"
            out.append(EnvItem(
                category="대기",
                name=f"{label} @ {st_name}측정소",
                distance_m=int(float(st_dist) * 1000) if st_dist else None,
                value=str(v) if v else None,
                unit=unit,
                severity=sev,
                source="에어코리아 실시간 대기오염정보",
                note="현재 baseline — 입주 후 비교 기준선",
            ))
    else:
        out.append(EnvItem(
            category="대기",
            name=f"근접측정소 {st_name}",
            distance_m=int(float(st_dist) * 1000) if st_dist else None,
            value=None, unit=None, severity="하",
            source="에어코리아 측정소정보",
            note="실시간 측정치 매칭 실패",
        ))
    return out, None


# ─────────────────────────────────────────────────────────────
# 메인 엔트리
# ─────────────────────────────────────────────────────────────

def analyze_environment(address: str, radius_m: int = DEFAULT_RADIUS_M) -> EnvironmentReport:
    """
    공고문에서 추출한 단지 주소를 넣으면 환경권 리포트를 반환한다.

    >>> rep = analyze_environment("경기도 의왕시 삼동 191-1")
    >>> rep.summary
    {'상': 2, '중': 5, '하': 11}
    """
    rep = EnvironmentReport(address=address, radius_m=radius_m)

    coord = geocode(address)
    if coord:
        rep.lat, rep.lon = coord

    if coord:
        mgtnos, err = find_nearby_mgtno(coord[0], coord[1], radius_m)
        if err:
            rep.errors.append(err)
        for proj in mgtnos:
            for fn in (fetch_noise, fetch_odor, fetch_air_eiass):
                items, ferr = fn(proj["mgtNo"], proj.get("bsnsNm", ""))
                rep.items.extend(items)
                if ferr:
                    rep.errors.append(ferr)
    else:
        rep.errors.append("지오코딩 실패 — EIASS 조회 생략")

    air_items, air_err = fetch_air(address)
    rep.items.extend(air_items)
    if air_err:
        rep.errors.append(air_err)

    rep.summary = {
        "상": sum(1 for i in rep.items if i.severity == "상"),
        "중": sum(1 for i in rep.items if i.severity == "중"),
        "하": sum(1 for i in rep.items if i.severity == "하"),
    }
    return rep


def to_docx_rows(rep: EnvironmentReport) -> list[list[str]]:
    """report_generator.py 의 표 삽입용 행 리스트"""
    rows = [["구분", "대상", "거리", "수치", "심각도", "출처"]]
    order = {"상": 0, "중": 1, "하": 2}
    for i in sorted(rep.items, key=lambda x: order.get(x.severity, 3)):
        rows.append([
            i.category,
            i.name,
            f"{i.distance_m}m" if i.distance_m else "-",
            f"{i.value}{i.unit or ''}" if i.value else "-",
            i.severity,
            i.source,
        ])
    return rows


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import json, sys
    addr = sys.argv[1] if len(sys.argv) > 1 else "경기도 의왕시 삼동"
    r = analyze_environment(addr)
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
