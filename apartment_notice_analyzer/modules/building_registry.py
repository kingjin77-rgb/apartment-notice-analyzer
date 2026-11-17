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
import time
import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://apis.data.go.kr/1613000/BldRgstHubService"


def _to_int(v) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


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
        for attempt in range(3):
            resp = requests.get(f"{BASE_URL}/{operation}", params=query, timeout=20)
            if resp.status_code < 500:
                break
            time.sleep(0.8 * (attempt + 1))  # data.go.kr는 502/503이 간헐적으로 발생함
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

    def get_unit_areas(self, sigungu_cd: str, bjdong_cd: str, bun: str, ji: str = "0000") -> list[dict]:
        """전유공용면적 조회(getBrExposPubuseAreaInfo) — 세대별 실제 전유면적 원부.

        거래사례가 없는 단지의 '평형(타입) 구성'을 인근 단지에서 빌려오는 임시방편 대신,
        이 단지 자체의 건축물대장 공부에서 직접 가져오기 위한 것이다.
        (getBrHsprcInfo는 이름과 달리 동별 주택가격 공시이력이라 전유면적이 없다 — 실측 확인함)
        """
        return self._call("getBrExposPubuseAreaInfo", {
            "sigunguCd": sigungu_cd,
            "bjdongCd": bjdong_cd,
            "platGbCd": "0",
            "bun": bun.zfill(4),
            "ji": ji.zfill(4),
            "numOfRows": 3000,
        })

    def summarize_unit_areas(self, hsprc_info: list[dict]) -> list[dict]:
        """get_unit_areas() 원본(호별 1행)을 전유면적 타입별로 집계.

        exposPubuseGbCdNm(전유/공용 구분)이 '전유'인 행만 세대로 간주하고,
        area 필드(exclusPrvatArea, ㎡)를 반올림해 타입으로 묶는다.
        """
        units = [r for r in hsprc_info if "전유" in (r.get("exposPubuseGbCdNm") or "")]
        raw: list[float] = []
        for r in units:
            a = r.get("area")
            try:
                a = float(a)
            except (TypeError, ValueError):
                continue
            if a > 0:
                raw.append(a)
        if not raw:
            return []

        # 같은 타입이라도 세대마다 대장상 전유면적이 소수점 이하 몇 g 단위로
        # 흔들려서(59.94 vs 59.70 등) 그대로 세면 진짜 타입 하나가 두세 개
        # 잡음값으로 쪼개지고, 그 틈에 희소한 특수세대(펜트하우스 등)가
        # "주요 타입"으로 잘못 끼어든다. ±0.6㎡ 이내는 같은 타입으로 묶는다.
        raw.sort()
        clusters: list[list[float]] = []
        for a in raw:
            if clusters and a - clusters[-1][-1] <= 0.6:
                clusters[-1].append(a)
            else:
                clusters.append([a])
        out = [{"a": round(sum(c) / len(c), 2), "n": len(c)} for c in clusters]
        return sorted(out, key=lambda x: -x["n"])

    def summarize_complex(self, title_info: list[dict]) -> dict:
        """
        get_title_info() 원본(동별 1행)을 단지 단위 통계로 집계.

        표제부는 경로당·관리사무소·기계실·지하주차장 등 비주거 동도 함께 내려오므로
        hhldCnt(세대수) > 0 인 행만 "주거동"으로 간주해 집계 대상으로 삼는다.
        평가 실무상 개별요인(감칙 610-3.1.3②) 판단에 쓰이는 단지 특성치가 여기서 나온다.
        """
        if not title_info:
            return {}
        dongs = [r for r in title_info if _to_int(r.get("hhldCnt")) > 0]
        if not dongs:
            dongs = title_info  # 세대수 필드가 비어있는 예외 케이스 대비

        def isum(field):
            return sum(_to_int(r.get(field)) for r in dongs)

        def imax(field):
            vals = [_to_int(r.get(field)) for r in dongs]
            return max(vals) if vals else 0

        grades = [r.get("engrGrade") for r in dongs if (r.get("engrGrade") or "").strip()]
        quake = [r.get("rserthqkDsgnApplyYn") for r in dongs]

        return {
            "동수": len(dongs),
            "총세대수": isum("hhldCnt"),
            "최고층": imax("grndFlrCnt"),
            "최저동층수": min((_to_int(r.get("grndFlrCnt")) for r in dongs if _to_int(r.get("grndFlrCnt"))), default=0),
            "승강기_승용": isum("rideUseElvtCnt"),
            "승강기_비상": isum("emgenUseElvtCnt"),
            "내진설계여부": "Y" in quake,
            "내진설계등급": next((r.get("rserthqkAblty") for r in dongs if r.get("rserthqkAblty")), ""),
            "에너지효율등급": grades[0] if grades else "",
            "친환경인증등급": next((r.get("gnBldGrade") for r in dongs if r.get("gnBldGrade")), ""),
            "주구조": next((r.get("strctCdNm") for r in dongs if r.get("strctCdNm")), ""),
            "사용승인일": next((r.get("useAprDay") for r in dongs if r.get("useAprDay")), ""),
            "연면적_합계": round(isum("totArea"), 1),
            "옥내기계식주차": isum("indrMechUtcnt"),
            "옥내자주식주차": isum("indrAutoUtcnt"),
            "옥외기계식주차": isum("oudrMechUtcnt"),
            "옥외자주식주차": isum("oudrAutoUtcnt"),
            "raw_동목록": [r.get("dongNm") for r in dongs],
        }

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
