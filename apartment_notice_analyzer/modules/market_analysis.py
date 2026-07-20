"""
국토교통부 실거래가 공개시스템 API — 아파트 매매 실거래자료 (상세 자료 기준)

신청: data.go.kr → "국토교통부 아파트 매매 실거래가 자료" 검색 →
     "국토교통부_아파트 매매 실거래가 상세 자료" 활용신청 (무료, 자동승인)
문서: 아파트 매매 실거래가 상세자료 기술문서.hwp (활용신청 페이지에서 다운로드)

기본 자료(RTMSDataSvcAptTrade)와 상세 자료(RTMSDataSvcAptTradeDev) 둘 다 활용신청 승인된
상태라, 필드가 더 많은 상세 자료(Dev) 엔드포인트를 기본값으로 사용합니다.
data.go.kr 계정의 "일반 인증키"는 승인된 모든 API에서 공통으로 재사용됩니다.

⚠️ 이 API는 data.go.kr 도메인이라 이 개발 샌드박스의 네트워크 정책상
호출이 차단되어 있어(허용 도메인: pypi/npm/github 계열만) 라이브 테스트를
못 했습니다. 코드는 공식 API 문서 기준으로 작성했으나, 실제 실행은
보스님 로컬 환경에서 처음 한 번 검증이 필요합니다.

법정동코드는 5자리 시군구코드 필요 (예: 의왕시 = 41630).
전체 코드표: https://www.code.go.kr/stdcode/regCodeL.do

상세 자료 주요 응답 필드(기술문서 기준):
  aptNm(단지명), aptDong(동명), excluUseAr(전용면적), floor(층),
  buildYear(건축년도), dealYear/dealMonth/dealDay(계약일), dealAmount(거래금액, 만원),
  umdNm(법정동), jibun(지번), roadNm(도로명), dealingGbn(중개/직거래 구분),
  cdealType(해제여부 O/공백), cdealDay(해제사유발생일), rgstDate(등기일자)
"""
import os
import requests
import xml.etree.ElementTree as ET

BASE_URL_BASIC = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
BASE_URL_DETAIL = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"


class MolitTradeClient:
    def __init__(self, service_key: str | None = None, use_detail: bool = True):
        self.service_key = service_key or os.getenv("MOLIT_API_KEY")
        self.base_url = BASE_URL_DETAIL if use_detail else BASE_URL_BASIC

    @property
    def is_configured(self) -> bool:
        return bool(self.service_key)

    def get_monthly_trades(self, region_code: str, deal_ym: str) -> list[dict]:
        """
        region_code: 법정동코드 5자리 (예: 의왕시 '41630')
        deal_ym: 'YYYYMM' 형식 (예: '202606')
        반환: 거래 건별 dict 리스트 (단지명, 동명, 전용면적, 거래금액, 층, 건축년도,
             거래일, 해제여부 등 — 필드는 파일 상단 docstring 참고)
        """
        if not self.is_configured:
            return []

        params = {
            "serviceKey": self.service_key,
            "LAWD_CD": region_code,
            "DEAL_YMD": deal_ym,
            "numOfRows": 1000,
        }
        resp = requests.get(self.base_url, params=params, timeout=20)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        items = []
        for item in root.iter("item"):
            row = {child.tag: (child.text or "").strip() for child in item}
            # 해제(취소)된 거래는 시세 비교에서 왜곡을 줄 수 있어 플래그만 남기고 필터링은 호출측 선택
            row["is_cancelled"] = row.get("cdealType", "").strip() == "O"
            items.append(row)
        return items

    def get_price_trend(self, region_code: str, year_months: list[str], exclude_cancelled: bool = True) -> list[dict]:
        """
        여러 달치 데이터를 모아 월별 평균 거래가(만원) 추이를 계산.

        주의: 실제 API 응답의 거래금액 필드명이 '거래금액'(한글) 또는 'dealAmount'(영문)
        중 무엇으로 오는지는 라이브 테스트 전까지 확정할 수 없어 둘 다 시도합니다.
        """
        trend = []
        for ym in year_months:
            trades = self.get_monthly_trades(region_code, ym)
            if exclude_cancelled:
                trades = [t for t in trades if not t.get("is_cancelled")]
            if not trades:
                trend.append({"year_month": ym, "avg_price_manwon": None, "trade_count": 0})
                continue
            prices = []
            for t in trades:
                raw = (t.get("dealAmount") or t.get("거래금액") or "").replace(",", "").strip()
                if raw.isdigit():
                    prices.append(int(raw))
            avg = sum(prices) / len(prices) if prices else None
            trend.append({
                "year_month": ym,
                "avg_price_manwon": avg,
                "trade_count": len(trades),
            })
        return trend
