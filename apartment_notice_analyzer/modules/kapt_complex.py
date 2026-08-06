# -*- coding: utf-8 -*-
"""
K-APT 공동주택 단지정보 (AptListService3 + AptBasisInfoServiceV4)

감정평가 가치형성요인 중 '단지내부요인'을 채우는 핵심 소스다.
실제 감정평가서(지우 1-230619-301, 청암 CA2308-004)가 쓰는 단지내부요인
세항목과 이 API 필드가 거의 1:1로 대응한다.

    시공업체의 브랜드          -> kaptBcompany
    단지내 총세대수 및 최고층수  -> kaptdaCnt, kaptTopFloor
    단지내 통로구조(복도식/계단식) -> codeHallNm
    단지내 면적구성(대형/중형/소형) -> kaptMparea60/85/135/136
    전용률                    -> privArea / kaptTarea
    경과연수에 따른 노후도       -> kaptUsedate

여기에 더해 codeSaleNm(분양/임대/혼합)이 분양전환 대상 단지를 확정해준다.
단지명 패턴 추정("LH", "행복주택")이 아니라 공부상 구분이므로 훨씬 정확하다.

주의: kaptCode는 K-APT 고유 코드로 국토부 실거래가의 aptSeq와 다르다.
      단지목록(AptListService3)으로 지역→kaptCode를 먼저 얻어야 한다.
      bjdCode(법정동코드 10자리)가 함께 오므로 PNU 생성·실거래 조인에 쓴다.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, asdict

import requests

LIST_BASE = "https://apis.data.go.kr/1613000/AptListService3"
INFO_BASE = "https://apis.data.go.kr/1613000/AptBasisInfoServiceV4"


@dataclass
class ComplexInfo:
    """단지 기본정보 — 감정평가 단지내부요인 판단용."""

    kapt_code: str
    name: str
    addr: str
    road_addr: str
    bjd_code: str              # 법정동코드 10자리 → PNU 생성에 사용

    sale_type: str             # codeSaleNm — 분양 / 임대 / 혼합
    kind: str                  # codeAptNm — 아파트/연립주택/도시형생활주택
    hall_type: str             # codeHallNm — 계단식 / 복도식 / 혼합식
    heat_type: str             # codeHeatNm — 지역난방 / 개별난방 / 중앙난방
    mgmt_type: str             # codeMgrNm — 위탁관리 / 자치관리

    builder: str               # kaptBcompany — 시공사
    developer: str             # kaptAcompany — 시행사

    households: int            # kaptdaCnt — 총세대수
    dong_count: int            # kaptDongCnt — 동수
    top_floor: int             # kaptTopFloor — 최고층수
    base_floor: int            # kaptBaseFloor — 지하층수

    total_area: float          # kaptTarea — 연면적
    private_area: float        # privArea — 전용면적 합계
    elevator_count: int        # kaptdEcntp — 승강기 대수(주차 아님, 주의)

    # 면적구성 (세대수)
    area_60: int               # 60㎡ 이하 (소형)
    area_85: int               # 60~85㎡ (중형)
    area_135: int              # 85~135㎡ (대형)
    area_136: int              # 135㎡ 초과

    use_date: str              # kaptUsedate — 사용승인일 YYYYMMDD

    # --- 상세정보(getAphusDtlInfoV4)에서 채워지는 항목 ---
    parking_ground: int = 0    # kaptdPcnt — 지상주차
    parking_under: int = 0     # kaptdPcntu — 지하주차
    structure: str = ""        # codeStr — 건물구조
    cctv_count: int = 0        # kaptdCccnt
    bus_time: str = ""         # kaptdWtimebus — 버스정류장 소요시간
    subway_time: str = ""      # kaptdWtimesub — 지하철역 소요시간
    subway_station: str = ""   # subwayStation
    education_facility: str = ""   # educationFacility — 학교명 직접 제공
    convenient_facility: str = ""  # convenientFacility
    welfare_facility: str = ""     # welfareFacility — 부대복리시설
    ev_charger: int = 0        # 전기차충전기 (지상+지하)

    @property
    def exclusive_ratio(self) -> float:
        """전용률 = 전용면적 합계 / 연면적. 감정평가 단지내부요인 세항목."""
        return self.private_area / self.total_area if self.total_area else 0.0

    @property
    def parking_total(self) -> int:
        return self.parking_ground + self.parking_under

    @property
    def parking_per_household(self) -> float:
        return self.parking_total / self.households if self.households else 0.0

    @property
    def is_rental(self) -> bool:
        """임대(분양전환 대상) 여부 — 공부상 구분이므로 단지명 추정보다 정확하다."""
        return "임대" in (self.sale_type or "")

    @property
    def build_year(self) -> int | None:
        s = (self.use_date or "").strip()
        return int(s[:4]) if len(s) >= 4 and s[:4].isdigit() else None

    @property
    def age(self) -> int | None:
        y = self.build_year
        return None if y is None else max(0, 2026 - y)

    @property
    def size_mix(self) -> str:
        """면적구성을 감정평가서 표현으로 요약."""
        parts = []
        for label, n in (("소형", self.area_60), ("중형", self.area_85),
                        ("대형", self.area_135 + self.area_136)):
            if n:
                parts.append(f"{label} {n}세대")
        return " / ".join(parts) if parts else "미상"

    def to_dict(self) -> dict:
        d = asdict(self)
        d.update(전용률=round(self.exclusive_ratio, 4),
                세대당주차=round(self.parking_per_household, 2),
                경과연수=self.age, 면적구성=self.size_mix, 임대여부=self.is_rental)
        return d


class KaptClient:
    def __init__(self, key: str | None = None):
        self.key = key or os.getenv("KAPT_API_KEY") or os.getenv("MOLIT_API_KEY")

    @property
    def is_configured(self) -> bool:
        return bool(self.key)

    def _get(self, url: str, params: dict, tries: int = 3):
        for i in range(tries):
            r = requests.get(url, params={**params, "serviceKey": self.key,
                                         "_type": "json"}, timeout=25)
            if r.status_code < 500:
                try:
                    return r.json()
                except ValueError:
                    return None
            time.sleep(0.8 * (i + 1))  # data.go.kr 502 간헐 발생
        return None

    def list_by_sigungu(self, sigungu_code: str, max_rows: int = 1000) -> list[dict]:
        """시군구 단위 단지 목록. kaptCode·kaptName·bjdCode를 준다."""
        if not self.is_configured:
            return []
        out, page = [], 1
        while True:
            d = self._get(f"{LIST_BASE}/getSigunguAptList3",
                         {"sigunguCode": sigungu_code, "numOfRows": max_rows, "pageNo": page})
            if not d:
                break
            body = (d.get("response") or {}).get("body") or {}
            items = body.get("items") or []
            if isinstance(items, dict):
                items = items.get("item", [])
            if not items:
                break
            out += items
            if len(out) >= int(body.get("totalCount") or 0):
                break
            page += 1
        return out

    def basis_info(self, kapt_code: str, *, with_detail: bool = True) -> ComplexInfo | None:
        """
        kaptCode로 단지 정보를 가져온다.
        with_detail=True면 상세정보(주차·학교·교통·부대시설)까지 합쳐 채운다.
        """
        if not self.is_configured:
            return None
        d = self._get(f"{INFO_BASE}/getAphusBassInfoV4", {"kaptCode": kapt_code})
        if not d:
            return None
        item = ((d.get("response") or {}).get("body") or {}).get("item")
        if not item or not item.get("kaptCode"):
            return None
        info = _to_info(item)
        if with_detail:
            self._merge_detail(info, kapt_code)
        return info

    def _merge_detail(self, info: "ComplexInfo", kapt_code: str) -> None:
        d = self._get(f"{INFO_BASE}/getAphusDtlInfoV4", {"kaptCode": kapt_code})
        if not d:
            return
        it = ((d.get("response") or {}).get("body") or {}).get("item")
        if not it:
            return
        info.parking_ground = _i(it.get("kaptdPcnt"))
        info.parking_under = _i(it.get("kaptdPcntu"))
        info.structure = it.get("codeStr", "") or ""
        info.cctv_count = _i(it.get("kaptdCccnt"))
        info.bus_time = it.get("kaptdWtimebus", "") or ""
        info.subway_time = it.get("kaptdWtimesub", "") or ""
        info.subway_station = it.get("subwayStation") or ""
        info.education_facility = it.get("educationFacility", "") or ""
        info.convenient_facility = it.get("convenientFacility", "") or ""
        info.welfare_facility = it.get("welfareFacility", "") or ""
        info.ev_charger = _i(it.get("groundElChargerCnt")) + _i(it.get("undergroundElChargerCnt"))

    def find(self, sigungu_code: str, name_keyword: str) -> ComplexInfo | None:
        """시군구 + 단지명 키워드로 한 번에 찾는다."""
        for it in self.list_by_sigungu(sigungu_code):
            if name_keyword.replace(" ", "") in (it.get("kaptName") or "").replace(" ", ""):
                return self.basis_info(it["kaptCode"])
        return None


def _i(v) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _f(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _to_info(d: dict) -> ComplexInfo:
    return ComplexInfo(
        kapt_code=d.get("kaptCode", ""), name=d.get("kaptName", ""),
        addr=d.get("kaptAddr", ""), road_addr=d.get("doroJuso", ""),
        bjd_code=d.get("bjdCode", ""),
        sale_type=d.get("codeSaleNm", ""), kind=d.get("codeAptNm", ""),
        hall_type=d.get("codeHallNm", ""), heat_type=d.get("codeHeatNm", ""),
        mgmt_type=d.get("codeMgrNm", ""),
        builder=d.get("kaptBcompany", ""), developer=d.get("kaptAcompany", ""),
        households=_i(d.get("kaptdaCnt")), dong_count=_i(d.get("kaptDongCnt")),
        top_floor=_i(d.get("kaptTopFloor")), base_floor=_i(d.get("kaptBaseFloor")),
        total_area=_f(d.get("kaptTarea")), private_area=_f(d.get("privArea")),
        elevator_count=_i(d.get("kaptdEcntp")),
        area_60=_i(d.get("kaptMparea60")), area_85=_i(d.get("kaptMparea85")),
        area_135=_i(d.get("kaptMparea135")), area_136=_i(d.get("kaptMparea136")),
        use_date=str(d.get("kaptUsedate") or ""),
    )
