"""
주변환경 조사 - 카카오맵 로컬 API

신청: https://developers.kakao.com -> 애플리케이션 생성 -> REST API 키 발급 (무료, 일일 쿼터 있음)
문서: https://developers.kakao.com/docs/latest/ko/local/dev-guide

카테고리 코드 예시:
  MT1 대형마트 / CS2 편의점 / SC4 학교 / PS3 어린이집,유치원
  HP8 병원 / PM9 약국 / SW8 지하철역 / AT4 관광명소
혐오시설(장례식장, 소각장 등)은 카테고리 코드가 없어 키워드 검색으로 대체.
"""
import os
import requests

BASE_URL = "https://dapi.kakao.com/v2/local"

CATEGORY_CODES = {
    "대형마트": "MT1",
    "편의점": "CS2",
    "학교": "SC4",
    "어린이집/유치원": "PS3",
    "병원": "HP8",
    "약국": "PM9",
    "지하철역": "SW8",
}

NUISANCE_KEYWORDS = ["장례식장", "쓰레기 소각장", "폐기물 처리장", "축사", "화장장"]


class KakaoLocalClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("KAKAO_REST_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict:
        return {"Authorization": f"KakaoAK {self.api_key}"}

    def geocode_address(self, address: str) -> tuple[float, float] | None:
        """주소 -> (경도, 위도). 카카오 로컬 API는 x=경도, y=위도."""
        if not self.is_configured:
            return None
        resp = requests.get(
            f"{BASE_URL}/search/address.json",
            headers=self._headers(),
            params={"query": address},
            timeout=15,
        )
        resp.raise_for_status()
        docs = resp.json().get("documents", [])
        if not docs:
            return None
        return float(docs[0]["x"]), float(docs[0]["y"])

    def search_category_nearby(self, x: float, y: float, category: str, radius_m: int = 1000) -> list[dict]:
        code = CATEGORY_CODES.get(category)
        if not code or not self.is_configured:
            return []
        resp = requests.get(
            f"{BASE_URL}/search/category.json",
            headers=self._headers(),
            params={"category_group_code": code, "x": x, "y": y, "radius": radius_m, "sort": "distance"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("documents", [])

    def search_keyword_nearby(self, x: float, y: float, keyword: str, radius_m: int = 2000) -> list[dict]:
        if not self.is_configured:
            return []
        resp = requests.get(
            f"{BASE_URL}/search/keyword.json",
            headers=self._headers(),
            params={"query": keyword, "x": x, "y": y, "radius": radius_m, "sort": "distance"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("documents", [])

    def full_survey(self, address: str) -> dict:
        """편의시설 + 혐오시설을 한 번에 조사."""
        coords = self.geocode_address(address)
        if coords is None:
            return {"error": "주소 좌표 변환 실패 (주소 형식 확인 또는 API 키 확인)"}
        x, y = coords

        survey = {"편의시설": {}, "유의시설": {}}
        for category in CATEGORY_CODES:
            survey["편의시설"][category] = self.search_category_nearby(x, y, category)

        for keyword in NUISANCE_KEYWORDS:
            hits = self.search_keyword_nearby(x, y, keyword, radius_m=2000)
            if hits:
                survey["유의시설"][keyword] = hits

        return survey
