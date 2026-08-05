"""
국가법령정보 공동활용 API (law.go.kr) 클라이언트

신청: https://open.law.go.kr -> 이메일 인증 후 OC(기관코드) 발급 (무료)
API 문서: https://open.law.go.kr/LSO/openApi/guideList.do

주요 엔드포인트:
- 목록 검색: /DRF/lawSearch.do
- 본문 조회: /DRF/lawService.do

target 값에 따라 다른 법원(法源)을 조회합니다.
- target=law    : 법령 (법률/시행령/시행규칙)   예) 감정평가에 관한 규칙
- target=admrul : 행정규칙 (고시/훈령/예규)     예) 감정평가 실무기준

주의: 이 API는 "검색"보다 "정확한 법령명/조번호를 알고 있을 때 원문 조회"에 최적화되어 있습니다.
따라서 data/law_mapping.json 같은 매핑 테이블을 먼저 구축해두고,
공고문 조항 카테고리 -> 관련 법령명 -> 이 API로 원문 조회, 순서로 사용합니다.
"""
import os
import requests

BASE_URL = "https://www.law.go.kr/DRF"

# 자주 쓰는 법원(法源)의 확정 ID.
# 검색 단계를 건너뛰고 바로 본문을 받기 위한 상수 (2026-08-05 실측 확인).
KNOWN_IDS = {
    # 감정평가 3방식과 물건별 주방식을 정한 부령. 아파트 주방식 근거는 제16조.
    "감정평가에 관한 규칙": {"target": "law", "id": "006140"},
    # 국토교통부 고시 제2023-522호 (시행 2023-09-13). 감칙의 세부 실무기준.
    "감정평가 실무기준": {"target": "admrul", "id": "2100000229230"},
}


class LawApiClient:
    def __init__(self, oc: str | None = None):
        self.oc = oc or os.getenv("LAW_GO_KR_OC")

    @property
    def is_configured(self) -> bool:
        return bool(self.oc)

    # ------------------------------------------------------------------
    # 공통
    # ------------------------------------------------------------------
    def _get(self, endpoint: str, params: dict) -> dict:
        params = {"OC": self.oc, "type": "JSON", **params}
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # 법령 (target=law)
    # ------------------------------------------------------------------
    def search_law(self, law_name: str, num_of_rows: int = 5) -> list[dict]:
        """법령명으로 법령 검색 (법령 ID 확보용)."""
        if not self.is_configured:
            return []
        data = self._get(
            "lawSearch.do",
            {"target": "law", "query": law_name, "display": num_of_rows},
        )
        return data.get("LawSearch", {}).get("law", [])

    def get_law_article(self, law_id: str, article_no: str | None = None) -> dict:
        """법령 본문(조문) 조회."""
        if not self.is_configured:
            return {"error": "LAW_GO_KR_OC 미설정 - .env를 확인하세요."}
        params = {"target": "law", "ID": law_id}
        if article_no:
            params["JO"] = article_no
        return self._get("lawService.do", params)

    # ------------------------------------------------------------------
    # 행정규칙 (target=admrul) - 고시/훈령/예규
    # ------------------------------------------------------------------
    def search_admin_rule(self, rule_name: str, num_of_rows: int = 5) -> list[dict]:
        """행정규칙명으로 검색. 반환 항목의 '행정규칙일련번호'가 본문 조회 ID."""
        if not self.is_configured:
            return []
        data = self._get(
            "lawSearch.do",
            {"target": "admrul", "query": rule_name, "display": num_of_rows},
        )
        items = data.get("AdmRulSearch", {}).get("admrul", [])
        # 결과가 1건이면 dict, 2건 이상이면 list로 오는 API 특성 흡수
        if isinstance(items, dict):
            items = [items]
        return items

    def get_admin_rule(self, rule_seq: str) -> dict:
        """행정규칙 본문 조회. rule_seq는 '행정규칙일련번호'."""
        if not self.is_configured:
            return {"error": "LAW_GO_KR_OC 미설정 - .env를 확인하세요."}
        data = self._get("lawService.do", {"target": "admrul", "ID": rule_seq})
        return data.get("AdmRulService", data)

    def get_admin_rule_text(self, rule_seq: str) -> str:
        """행정규칙 본문 텍스트만 반환."""
        return self.get_admin_rule(rule_seq).get("조문내용", "")

    # ------------------------------------------------------------------
    # 편의 메서드
    # ------------------------------------------------------------------
    def fetch_known(self, name: str) -> dict:
        """KNOWN_IDS에 등록된 법원을 이름만으로 조회."""
        entry = KNOWN_IDS.get(name)
        if entry is None:
            raise KeyError(f"KNOWN_IDS에 없는 이름: {name} (가능: {list(KNOWN_IDS)})")
        if entry["target"] == "admrul":
            return self.get_admin_rule(entry["id"])
        return self.get_law_article(entry["id"])
