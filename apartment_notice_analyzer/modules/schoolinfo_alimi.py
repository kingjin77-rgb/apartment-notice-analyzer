"""
학교알리미(schoolinfo.go.kr) Open API - 학교기본정보(좌표 포함)

신청: https://www.schoolinfo.go.kr (네이버/카카오 소셜로그인 후 OPENAPI > 마이페이지에서 인증키 발급, 최초 1회)
개발자 가이드: https://www.schoolinfo.go.kr/download/OpenAPI_Developer_Guide.pdf

호출: GET https://www.schoolinfo.go.kr/openApi.do
  ?apiKey=인증키(필수) &apiType=0(학교기본정보) &sidoCode=시도코드(필수)
  &sggCode=시군구코드(필수) &schulKndCode=학교급구분(필수: 02초등 03중등 04고등 05특수 06그외 07각종)

sidoCode/sggCode는 표준 행정구역코드(법정동코드 앞자리)와 동일 체계 —
국토부 실거래가 API(market_analysis.py)의 LAWD_CD와 같은 코드를 그대로 사용 가능
(예: 부산광역시 강서구 = sidoCode "26", sggCode "26440").

NEIS(school_district.py)와 달리 위경도(LTTUD/LGTUD)를 제공하므로,
카카오 지오코딩 좌표 기준 haversine 거리 계산으로 반경 내 최근접 학교를
학교급(초/중/고)별로 정확히 뽑아낼 수 있다. 학업성취도 등 서열 데이터는
동일하게 정책상 비공개이므로 이 모듈도 취급하지 않는다.
"""
import os
import math
import requests

BASE_URL = "https://www.schoolinfo.go.kr/openApi.do"

SCHUL_KND_CODES = {
    "초등학교": "02",
    "중학교": "03",
    "고등학교": "04",
    "특수학교": "05",
    "그외": "06",
    "각종학교": "07",
}


class SchoolInfoClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SCHOOLINFO_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_schools(self, sido_code: str, sgg_code: str, school_level: str) -> list[dict]:
        """school_level: SCHUL_KND_CODES의 키(예: '초등학교') 또는 코드값('02') 둘 다 허용."""
        if not self.is_configured:
            return []
        code = SCHUL_KND_CODES.get(school_level, school_level)
        resp = requests.get(
            BASE_URL,
            params={
                "apiKey": self.api_key,
                "apiType": "0",
                "sidoCode": sido_code,
                "sggCode": sgg_code,
                "schulKndCode": code,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [s for s in data.get("list", []) if s.get("CLOSE_YN") != "Y"]


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 좌표간 직선거리(미터)."""
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def nearest_schools(schools: list[dict], site_lat: float, site_lon: float, top_n: int = 5) -> list[dict]:
    """학교 목록을 site 좌표 기준 거리순 정렬. 각 dict에 'distance_m' 필드 추가해서 반환."""
    ranked = []
    for s in schools:
        try:
            lat, lon = float(s["LTTUD"]), float(s["LGTUD"])
        except (KeyError, ValueError, TypeError):
            continue
        d = haversine_m(site_lat, site_lon, lat, lon)
        ranked.append({**s, "distance_m": round(d)})
    ranked.sort(key=lambda x: x["distance_m"])
    return ranked[:top_n]
