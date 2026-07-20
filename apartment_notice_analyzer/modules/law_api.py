"""
국가법령정보 공동활용 API (law.go.kr) 클라이언트

신청: https://open.law.go.kr -> 이메일 인증 후 OC(기관코드) 발급 (무료)
API 문서: https://open.law.go.kr/LSO/openApi/guideList.do

주요 엔드포인트:
- 법령 목록 검색: /DRF/lawSearch.do
- 법령 본문 조회: /DRF/lawService.do

주의: 이 API는 "검색"보다 "정확한 법령명/조번호를 알고 있을 때 원문 조회"에 최적화되어 있습니다.
따라서 data/law_mapping.json 같은 매핑 테이블을 먼저 구축해두고,
공고문 조항 카테고리 -> 관련 법령명 -> 이 API로 원문 조회, 순서로 사용합니다.
"""
import os
import requests

BASE_URL = "https://www.law.go.kr/DRF"


class LawApiClient:
    def __init__(self, oc: str | None = None):
        self.oc = oc or os.getenv("LAW_GO_KR_OC")

    @property
    def is_configured(self) -> bool:
        return bool(self.oc)

    def search_law(self, law_name: str, num_of_rows: int = 5) -> list[dict]:
        """법령명으로 법령 검색 (법령 ID 확보용)."""
        if not self.is_configured:
            return []
        params = {
            "OC": self.oc,
            "target": "law",
            "type": "JSON",
            "query": law_name,
            "display": num_of_rows,
        }
        resp = requests.get(f"{BASE_URL}/lawSearch.do", params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data.get("LawSearch", {}).get("law", [])

    def get_law_article(self, law_id: str, article_no: str | None = None) -> dict:
        """법령 본문(조문) 조회."""
        if not self.is_configured:
            return {"error": "LAW_GO_KR_OC 미설정 - .env를 확인하세요."}
        params = {
            "OC": self.oc,
            "target": "law",
            "type": "JSON",
            "ID": law_id,
        }
        if article_no:
            params["JO"] = article_no
        resp = requests.get(f"{BASE_URL}/lawService.do", params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
