"""
국토교통부 건축HUB 건축물대장정보 (BldRgstHubService)

용도: 공고문에 적힌 정보(사용승인 예정일, 층수, 세대수, 용도 등)를
실제 건축물대장 공부와 대조 — 착공/준공 단계에서는 대장이 아직 없을 수 있고,
기존 건물(재건축 대상 등)이 있는 사업지라면 기존 대장 정보 확인에 유용합니다.

⚠️ market_analysis.py(국토교통부 실거래가)와 마찬가지로 data.go.kr 도메인이라
이 개발 샌드박스에서는 라이브 호출 테스트가 안 됩니다. 실키는 .env에만
넣고(메모리/리포트에는 남기지 않음), 로컬 환경에서 첫 실행 검증이 필요합니다.

법정동코드(sigunguCd 5자리 + bjdongCd 5자리)가 필요합니다.
조회: https://www.code.go.kr/stdcode/regCodeL.do

주요 오퍼레이션:
- getBrTitleInfo       : 표제부 (사용승인일, 주용도, 연면적, 층수, 세대수 등 핵심 정보)
- getBrFlrOulnInfo     : 층별개요 (층별 용도/면적)
- getBrExposInfo       : 총괄표제부 (여러 동이 있는 단지 전체 개요)
- getBrAtchJibunInfo   : 부속지번
- getBrHsprcInfo       : 호수/전유공용면적
"""
import os
import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://apis.data.go.kr/1613000/BldRgstHubService"


class BuildingRegistryClient:
    def __init__(self, service_key: str | None = None):
        self.service_key = service_key or os.getenv("BLDRGST_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.service_key)

    def _call(self, operation: str, params: dict) -> list[dict]:
        if not self.is_configured:
            return []
        query = {
            "serviceKey": self.service_key,
            "_type": "json",
            "numOfRows": params.pop("numOfRows", 100),
            "pageNo": params.pop("pageNo", 1),
            **params,
        }
        resp = requests.get(f"{BASE_URL}/{operation}", params=query, timeout=20)
        resp.raise_for_status()

        # JSON 우선 시도, 실패하면 XML 파싱 (API가 파라미터 오류 시 XML 에러를 반환하는 경우가 있음)
        try:
            data = resp.json()
            body = data.get("response", {}).get("body", {})
            items = body.get("items", {})
            if not items:
                return []
            item_list = items.get("item", [])
            if isinstance(item_list, dict):
                item_list = [item_list]
            return item_list
        except ValueError:
            root = ET.fromstring(resp.content)
            return [
                {child.tag: (child.text or "").strip() for child in item}
                for item in root.iter("item")
            ]

    def get_title_info(self, sigungu_cd: str, bjdong_cd: str, bun: str, ji: str = "0000") -> list[dict]:
        """표제부 조회 — 사용승인일, 주용도, 연면적, 지상/지하 층수, 세대수 등."""
        return self._call("getBrTitleInfo", {
            "sigunguCd": sigungu_cd,
            "bjdongCd": bjdong_cd,
            "platGbCd": "0",  # 0: 일반대지, 1: 산
            "bun": bun.zfill(4),
            "ji": ji.zfill(4),
        })

    def get_floor_outline(self, sigungu_cd: str, bjdong_cd: str, bun: str, ji: str = "0000") -> list[dict]:
        """층별개요 조회 — 층별 용도/면적."""
        return self._call("getBrFlrOulnInfo", {
            "sigunguCd": sigungu_cd,
            "bjdongCd": bjdong_cd,
            "platGbCd": "0",
            "bun": bun.zfill(4),
            "ji": ji.zfill(4),
        })

    def cross_check_notice_claims(self, notice_claims: dict, title_info: list[dict]) -> dict:
        """
        공고문에서 파싱한 값(예: 층수, 세대수)과 건축물대장 표제부 값을 단순 대조.
        notice_claims 예: {"지상층수": "34", "총세대수": "1857"}
        건축물대장 필드명은 API 스펙 기준 ugrflrCnt(지하층수)/grndFlrCnt(지상층수)/hhldCnt(세대수) 등.
        """
        if not title_info:
            return {"status": "대장 정보 없음 (착공 전이거나 조회 실패)"}

        record = title_info[0]
        result = {}
        field_map = {
            "지상층수": "grndFlrCnt",
            "지하층수": "ugrflrCnt",
            "총세대수": "hhldCnt",
            "연면적": "totArea",
            "주용도": "mainPurpsCdNm",
        }
        for claim_key, registry_field in field_map.items():
            if claim_key in notice_claims:
                registry_value = record.get(registry_field)
                result[claim_key] = {
                    "공고문": notice_claims[claim_key],
                    "건축물대장": registry_value,
                    "일치": str(notice_claims[claim_key]) == str(registry_value) if registry_value else "대장값 없음",
                }
        return result
