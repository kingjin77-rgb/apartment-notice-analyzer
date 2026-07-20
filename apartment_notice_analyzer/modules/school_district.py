"""
학군조사 - 나이스(NEIS) 교육정보 개방포털

신청: https://open.neis.go.kr -> 인증키 신청 (무료)

중요: 이 API로 얻을 수 있는 건 "객관적 사실 데이터"뿐입니다.
  - 학교기본정보 (위치, 남녀공학 여부, 학교급)
  - 학급수/학급당 학생수
  - 학사일정
"학업성취도 순위", "학군 좋다/나쁘다" 같은 평가성 데이터는
2010년대 이후 학교 서열화 방지 정책에 따라 개별 학교 단위로 공식 공개되지 않습니다.
따라서 이 모듈은 그런 항목을 자체적으로 만들어내지 않고, 필요하면 웹서치 결과를
"커뮤니티 평판 - 참고용, 공식 데이터 아님"이라고 명시해서 별도 취급해야 합니다.
"""
import os
import requests

BASE_URL = "https://open.neis.go.kr/hub"


class NeisClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("NEIS_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search_school(self, school_name: str, region_code: str | None = None) -> list[dict]:
        """학교기본정보 조회 (schulNm으로 검색)."""
        if not self.is_configured:
            return []
        params = {
            "KEY": self.api_key,
            "Type": "json",
            "pIndex": 1,
            "pSize": 20,
            "SCHUL_NM": school_name,
        }
        if region_code:
            params["ATPT_OFCDC_SC_CODE"] = region_code

        resp = requests.get(f"{BASE_URL}/schoolInfo", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("schoolInfo", [{}, {}])
        if len(rows) < 2:
            return []
        return rows[1].get("row", [])

    def get_class_size(self, school_code: str, office_code: str) -> list[dict]:
        """학급수/학급당 학생수 등 - 통학 관련 참고자료."""
        if not self.is_configured:
            return []
        params = {
            "KEY": self.api_key,
            "Type": "json",
            "SD_SCHUL_CODE": school_code,
            "ATPT_OFCDC_SC_CODE": office_code,
        }
        resp = requests.get(f"{BASE_URL}/classInfo", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("classInfo", [{}, {}])
        if len(rows) < 2:
            return []
        return rows[1].get("row", [])


def build_school_district_report(address: str, nearby_schools: list[dict]) -> dict:
    """
    카카오 로컬 API의 '학교' 카테고리 검색 결과(surrounding_environment.py)와
    NEIS 기본정보를 결합해 학군 리포트 초안 생성.
    """
    return {
        "objective_data": nearby_schools,
        "disclaimer": (
            "학교별 학업성취도·서열 데이터는 정책상 공식 공개되지 않습니다. "
            "위 목록은 통학 가능 거리 내 학교 현황(위치·학교급)이며, "
            "'학군 평판'을 원하실 경우 커뮤니티/부동산 자료 기반 정성적 조사가 "
            "별도로 필요하고 반드시 '참고용, 공식 데이터 아님'으로 표기해야 합니다."
        ),
    }
