# -*- coding: utf-8 -*-
"""
예상 감정평가액 산정 엔진

감정평가사가 거래사례비교법으로 하는 판단을 코드로 옮긴다.
감칙 제16조(구분소유 부동산은 거래사례비교법)와 실무기준 [610-3.1.3],
[400-3.3.1.2~5], [400-4]의 절차를 그대로 따른다.

    비준가액 = 사례가격 × 사정보정 × 시점수정 × 지역요인 × 개별요인

이 모듈이 기존 통계 방식과 다른 점은 세 가지다.

1. 노후도를 별도 요인으로 분리한다.
   분양전환·임대 단지는 5~10년간 임차인이 실제 거주한 물건이라 같은 연식의
   자가 단지와 물리적 상태가 다르다. 경과연수 감가곡선을 실거래에서 회귀로
   추정하고, 임대 사용분을 추가 감가로 얹는다.

2. 단일 값이 아니라 판단 범위를 낸다.
   실제 감정평가는 사례 선정과 보정 판단에 따라 결과가 달라진다. 법이 두 곳
   법인의 산술평균을 쓰도록 정한 이유이기도 하다(공공주택 특별법 시행규칙
   별표7 제2호 나목). 같은 방법론 안에서 방어 가능한 상·하단을 함께 낸다.

3. 이해관계 방향을 명시한다.
   분양전환가격은 낮을수록, 담보 대출한도는 높을수록 입주민에게 유리하다.
   목적에 따라 어느 쪽이 입주민에게 유리한지 표시하되, 사례를 임의로 배제하거나
   보정률을 근거 없이 조작하지 않는다. 채택 근거를 전부 노출하는 것이 전제다.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field, asdict

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------

# 층대 구간 — 최고층 대비 상대위치
FLOOR_BANDS = [
    ("저층", 0.00, 0.18),
    ("중층", 0.18, 0.35),
    ("중상층", 0.35, 0.62),
    ("고층", 0.62, 1.01),
]

# 평가목적별 이해관계 방향.
#  -1 : 값이 낮을수록 입주민에게 유리 (분양전환가격은 감정가로 정해진다)
#  +1 : 값이 높을수록 입주민에게 유리 (담보 대출한도가 커진다)
PURPOSE_DIRECTION = {
    "분양전환": -1,
    "담보평가": +1,
    "시가참고": 0,
    "경매참고": 0,
}

# 임대 사용에 따른 추가 감가.
# 공공주택 특별법상 임대의무기간(5·6·10년) 동안 임차인이 실제 거주한 물건은
# 마감재·설비 마모가 자가 단지보다 크다. 임대기간에 비례해 얹되, 상한을 둔다.
RENTAL_WEAR_PER_YEAR = 0.004   # 연 0.4%
RENTAL_WEAR_CAP = 0.05         # 최대 5%


# ---------------------------------------------------------------------------
# 노후도
# ---------------------------------------------------------------------------

@dataclass
class AgeCurve:
    """경과연수 → 가격배율. 지역 실거래 회귀로 추정한다."""

    base_year: int                     # 기준연도 (배율 1.0)
    coef: float                        # 로그선형 회귀계수 (연당)
    n: int                             # 추정에 쓰인 거래 수
    r2: float = 0.0
    region: str = ""

    def ratio(self, build_year: int) -> float:
        """해당 건축년도의 기준연도 대비 가격배율."""
        if not build_year:
            return 1.0
        return math.exp(self.coef * (build_year - self.base_year))

    def between(self, subject_year: int, case_year: int) -> float:
        """사례 대비 대상물건의 연식 격차율."""
        if not subject_year or not case_year:
            return 1.0
        return self.ratio(subject_year) / self.ratio(case_year)


def fit_age_curve(trades: list[dict], region: str = "") -> AgeCurve | None:
    """
    실거래에서 경과연수 감가곡선을 추정한다.

    ln(㎡단가) = a + b·건축년도 형태의 단순 로그선형 회귀.
    b가 양수면 신축일수록 비싸다는 뜻이고, 연 감가율은 대략 b에 해당한다.
    면적·층 효과가 섞이지만 단지 다양성이 충분하면 연식 신호가 지배적이다.
    """
    pts = []
    for t in trades:
        try:
            y = int(t["yr"]); u = float(t["unit"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (1970 <= y <= 2030) or u <= 0:
            continue
        pts.append((y, math.log(u)))

    if len(pts) < 30:
        return None

    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if sxx == 0:
        return None
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    b = sxy / sxx
    a = my - b * mx

    ss_tot = sum((p[1] - my) ** 2 for p in pts)
    ss_res = sum((p[1] - (a + b * p[0])) ** 2 for p in pts)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    # 회귀계수가 비현실적이면(연 8% 초과) 신뢰하지 않는다
    if not (0 < b < 0.08):
        return None

    base = int(round(mx))
    return AgeCurve(base_year=base, coef=b, n=n, r2=round(r2, 3), region=region)


def rental_wear(rental_years: float) -> float:
    """임대 사용 마모에 따른 추가 감가율(0~CAP)."""
    if rental_years <= 0:
        return 0.0
    return min(RENTAL_WEAR_PER_YEAR * rental_years, RENTAL_WEAR_CAP)


# ---------------------------------------------------------------------------
# 비교사례
# ---------------------------------------------------------------------------

@dataclass
class Case:
    """선정된 거래사례 한 건과 그 보정 내역."""

    label: str
    price: float                  # 사례 거래금액 (원)
    area: float                   # 사례 전용면적
    unit: float                   # 사례 ㎡단가
    dist_m: int = 0               # 대상과의 거리
    build_year: int = 0
    deal_ym: int = 0
    same_complex: bool = False

    adj_sajeong: float = 1.000    # 사정보정  [400-3.3.1.3]
    adj_time: float = 1.000       # 시점수정  [400-3.3.1.4]

    # 가치형성요인 4계층 — 실제 감정평가서(지우 1-230619-301, 청암 CA2308-004) 체계.
    # adj_region/adj_age/adj_floor/adj_etc 는 아래 4계층으로 환산해 사용한다.
    adj_outer: float = 1.000      # 단지외부요인 (교통·교육·상업·자연환경)
    adj_inner: float = 1.000      # 단지내부요인 (브랜드·세대수·노후도·전용률)
    adj_ho: float = 1.000         # 호별요인 (층·향·위치·면적·소음) [610-3.1.3]②
    adj_misc: float = 1.000       # 기타요인

    # 하위 호환 — adj_age/adj_floor 는 adj_inner/adj_ho 로 각각 합성된다.
    adj_region: float = 1.000     # (구) 지역요인 → adj_outer 로 이관
    adj_age: float = 1.000        # (구) 연식 → adj_inner 구성요소
    adj_floor: float = 1.000      # (구) 층별효용 → adj_ho 구성요소
    adj_etc: float = 1.000        # (구) 기타 개별요인 → adj_ho 구성요소

    @property
    def factor_total(self) -> float:
        """가치형성요인 비교치 = 외부 × 내부 × 호별 × 기타 (감정평가서 '누계')."""
        return (self.adj_outer * self.adj_region
                * self.adj_inner * self.adj_age
                * self.adj_ho * self.adj_floor * self.adj_etc
                * self.adj_misc)

    @property
    def adj_total(self) -> float:
        return self.adj_sajeong * self.adj_time * self.factor_total

    def bijun_unit(self) -> float:
        """비준 ㎡단가."""
        return self.unit * self.adj_total

    def bijun(self, subject_area: float) -> float:
        """
        비준가액. 실제 감정평가서 산식과 동일하다.
            사례가격 × 사정보정 × 시점수정 × 가치형성요인비교 × (대상면적/사례면적)
        ㎡단가 기준으로 계산하므로 면적비는 subject_area 를 곱하는 것으로 대체된다.
        """
        return self.bijun_unit() * subject_area

    def worksheet_row(self, subject_area: float) -> dict:
        """감정평가서 '비준가격' 표 1행 형태로 산출내역을 펼친다."""
        return {
            "사례": self.label,
            "사례단가(원/㎡)": round(self.unit),
            "사정보정": round(self.adj_sajeong, 4),
            "시점수정": round(self.adj_time, 5),
            "가치형성요인비교": round(self.factor_total, 4),
            "  단지외부요인": round(self.adj_outer * self.adj_region, 4),
            "  단지내부요인": round(self.adj_inner * self.adj_age, 4),
            "  호별요인": round(self.adj_ho * self.adj_floor * self.adj_etc, 4),
            "  기타요인": round(self.adj_misc, 4),
            "면적비": f"{subject_area}/{self.area}",
            "비준가격(원)": round(self.bijun(subject_area), -4),
        }


# ---------------------------------------------------------------------------
# 산정 결과
# ---------------------------------------------------------------------------

@dataclass
class Estimate:
    """
    감정평가 산정 결과.

    mid    : 방어 가능한 중앙 추정치
    low/high : 같은 방법론 안에서 방어 가능한 하단/상단
    favorable : 평가목적상 입주민에게 유리한 쪽 값
    """

    mid: float
    low: float
    high: float
    unit_mid: float
    cases: list[Case] = field(default_factory=list)
    grade: int = 3
    grade_reason: str = ""
    purpose: str = "분양전환"
    direction: int = -1
    age_note: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def favorable(self) -> float:
        if self.direction < 0:
            return self.low
        if self.direction > 0:
            return self.high
        return self.mid

    @property
    def adverse(self) -> float:
        if self.direction < 0:
            return self.high
        if self.direction > 0:
            return self.low
        return self.mid

    @property
    def spread(self) -> float:
        return (self.high - self.low) / self.mid if self.mid else 0.0

    def favorable_label(self) -> str:
        if self.direction < 0:
            return "입주민 유리 (분양전환가격은 낮을수록 유리)"
        if self.direction > 0:
            return "입주민 유리 (담보한도는 높을수록 유리)"
        return "중립"

    def to_dict(self) -> dict:
        d = asdict(self)
        d.update(favorable=self.favorable, adverse=self.adverse,
                 spread=round(self.spread, 4),
                 favorable_label=self.favorable_label())
        return d


# ---------------------------------------------------------------------------
# 엔진
# ---------------------------------------------------------------------------

def floor_band_index(floor: int, top_floor: int) -> int:
    if not top_floor or top_floor <= 0:
        return 2
    rel = floor / top_floor
    for i, (_, lo, hi) in enumerate(FLOOR_BANDS):
        if lo <= rel < hi:
            return i
    return len(FLOOR_BANDS) - 1


def appraise(
    *,
    subject_area: float,
    subject_floor: int,
    subject_top_floor: int,
    subject_build_year: int,
    cases: list[Case],
    age_curve: AgeCurve | None = None,
    floor_ratios: list[float | None] | None = None,
    rental_years: float = 0.0,
    purpose: str = "분양전환",
    own_trades: int = 0,
) -> Estimate:
    """
    거래사례비교법으로 예상 감정평가액을 산정한다.

    cases 는 이미 [400-3.3.1.2] 3요건으로 선별된 사례여야 한다.
    이 함수는 보정(사정·시점·지역·개별)을 적용하고 시산가액을 조정한다.
    """
    if not cases:
        raise ValueError("비교사례가 없습니다. [400-3.3.1.2] 요건 충족 사례를 먼저 선정하십시오.")

    bi = floor_band_index(subject_floor, subject_top_floor)
    warnings: list[str] = []

    # ---- 개별요인 보정 ----
    for c in cases:
        # 연식
        if age_curve and subject_build_year and c.build_year:
            c.adj_age = round(age_curve.between(subject_build_year, c.build_year), 4)
        # 층별효용 — 사례가 동일 단지가 아니면 층 정보를 신뢰하기 어려워 1.0
        if floor_ratios and c.same_complex:
            r = floor_ratios[bi]
            if r:
                c.adj_floor = round(r, 4)

    # ---- 임대 사용 마모 ----
    wear = rental_wear(rental_years)
    if wear:
        for c in cases:
            c.adj_etc = round(c.adj_etc * (1 - wear), 4)

    # ---- 비준가액 ----
    bijuns = sorted(c.bijun(subject_area) for c in cases)
    mid = statistics.median(bijuns)

    # ---- 판단 범위 ----
    # 사례 간 산포가 곧 감정평가사 간 판단차의 하한이다.
    # 사례가 적을수록 추가 불확실성을 얹는다.
    if len(bijuns) >= 3:
        disp = (bijuns[-1] - bijuns[0]) / mid / 2
    elif len(bijuns) == 2:
        disp = abs(bijuns[1] - bijuns[0]) / mid / 2 + 0.02
    else:
        disp = 0.05

    if own_trades >= 100:
        floor_disp = 0.020
    elif own_trades >= 20:
        floor_disp = 0.030
    elif own_trades >= 3:
        floor_disp = 0.045
    else:
        floor_disp = 0.075
        warnings.append(
            "대상 단지에 자체 거래사례가 없어 인근 유사단지로 비준하였다. "
            "확정 감정평가액은 감정평가법인의 평가를 받아야 한다."
        )

    band = max(disp, floor_disp)
    if not any(c.same_complex for c in cases):
        band += 0.015
    nearest = min((c.dist_m for c in cases if c.dist_m), default=0)
    if nearest > 1500:
        band += 0.015
        warnings.append(f"최근접 비교사례가 {nearest}m로 멀어 지역요인 격차가 커질 수 있다.")

    band = min(band, 0.16)
    low, high = mid * (1 - band), mid * (1 + band)

    # ---- 신뢰등급 ----
    if own_trades >= 100 and band <= 0.03:
        grade, why = 5, "동일 단지 거래가 충분하고 사례 간 산포가 작다."
    elif own_trades >= 50:
        grade, why = 4, "동일 단지 거래로 비준하였다."
    elif own_trades >= 20:
        grade, why = 3, "동일 단지 거래가 있으나 사례 수가 제한적이다."
    elif own_trades >= 3:
        grade, why = 2, "동일 단지 거래가 소수여서 인근 사례를 병용하였다."
    else:
        grade, why = 1, "자체 거래가 없어 전적으로 인근 유사단지에 의존하였다."

    # ---- 노후도 설명 ----
    if age_curve:
        yearly = (math.exp(age_curve.coef) - 1) * 100
        age_note = (f"{age_curve.region or '해당 지역'} 실거래 {age_curve.n:,}건 회귀 결과 "
                    f"연식 1년당 약 {yearly:.2f}% (R²={age_curve.r2}).")
        if wear:
            age_note += f" 임대 {rental_years:.0f}년 사용분 {wear*100:.1f}% 추가 감가."
    else:
        age_note = "연식 감가곡선을 추정할 표본이 부족하여 연식 보정을 적용하지 않았다."
        warnings.append("연식 보정 미적용 — 사례와 대상의 준공연차 차이를 확인할 것.")

    return Estimate(
        mid=round(mid, -4), low=round(low, -4), high=round(high, -4),
        unit_mid=mid / subject_area if subject_area else 0.0,
        cases=cases, grade=grade, grade_reason=why,
        purpose=purpose, direction=PURPOSE_DIRECTION.get(purpose, 0),
        age_note=age_note, warnings=warnings,
    )


# ---------------------------------------------------------------------------
# 분양전환가격 역산
# ---------------------------------------------------------------------------

def conversion_base_date(move_in_end: str, lease_years: int = 10) -> str | None:
    """
    분양전환 감정평가의 기준시점을 산출한다.

    "최초 입주지정기간 종료일이 속하는 달의 다음 달 1일"을 기산점으로 삼아
    임대의무기간이 경과한 시점이 기준시점이 된다.

    move_in_end: 최초 입주지정기간 종료일 (YYYYMMDD 또는 YYYY-MM-DD)
    반환: 기준시점 YYYYMMDD

    주의: 이 계산은 분양전환 '시기' 판단용이다. 감칙 제9조 제2항상 실제
    기준시점은 가격조사를 완료한 날이므로, 실제 감정평가서의 기준시점과는
    며칠 차이가 날 수 있다. 사전 예측 단계에서 시점수정 목표월을 잡는 데 쓴다.
    """
    s = str(move_in_end).replace("-", "").strip()
    if len(s) < 6 or not s[:6].isdigit():
        return None
    y, m = int(s[:4]), int(s[4:6])
    # 종료일이 속한 달의 다음 달 1일
    m += 1
    if m > 12:
        y, m = y + 1, 1
    return f"{y + lease_years}{m:02d}01"


def conversion_price(*, appraised: float, build_cost: float | None = None,
                     lease_type: str = "10년") -> dict:
    """
    감정평가금액에서 분양전환가격을 산출한다.
    공공주택 특별법 시행규칙 제40조 [별표7] / [별표7의2].

    10년 : 분양전환가격 ≤ 감정평가금액
    5년  : (건설원가 + 감정평가금액) ÷ 2
    6년  : (입주시감정가 + 분양시감정가) ÷ 2  — 여기서는 분양시감정가만 받는다
    """
    lt = lease_type.replace("임대", "").strip()
    if lt.startswith("10"):
        return {"lease_type": "10년 임대", "price": appraised,
                "basis": "[별표7] 1.가 — 분양전환가격은 감정평가금액을 초과할 수 없다.",
                "note": (
                    "실무상 감정평가금액이 곧 분양전환가격이 된다. 두 곳의 감정평가법인이 "
                    "각각 평가한 금액의 산술평균으로 확정하며(시행규칙 제42조), 택지비+건축비 "
                    "원가방식이 아니라 분양전환 시점의 시장가치를 반영한다. 따라서 임대기간 중 "
                    "주변 시세가 상승하면 분양전환가격도 그대로 상승한다 — 입주민 부담이 "
                    "커지는 구조이므로 사전 예측의 실익이 가장 큰 유형이다.\n"
                    "장기수선충당금은 분양 시 별도 정산 대상이며 분양전환가격에 포함되지 않는다."
                )}
    if lt.startswith("5"):
        if build_cost is None:
            return {"lease_type": "5년 임대", "price": None,
                    "basis": "[별표7] 1.나 — (건설원가 + 감정평가금액) ÷ 2",
                    "note": "건설원가(최초 입주자 모집 공고 당시 주택가격 + 자기자금이자 − 감가상각비)가 있어야 산출된다."}
        return {"lease_type": "5년 임대", "price": (build_cost + appraised) / 2,
                "basis": "[별표7] 1.나 — (건설원가 + 감정평가금액) ÷ 2",
                "note": "산정가격에서 감가상각비를 뺀 금액을 초과할 수 없다는 상한이 별도로 적용된다."}
    if lt.startswith("6"):
        return {"lease_type": "6년 임대", "price": None,
                "basis": "[별표7의2] 1 — (입주시감정가 + 분양시감정가) ÷ 2",
                "note": "입주시감정가가 있어야 산출된다. 분양전환가격은 분양시감정가를 초과할 수 없다."}
    return {"lease_type": lease_type, "price": None,
            "basis": "", "note": (
                "민간임대(민간임대주택법 본법)는 분양전환가격 법정기준이 없다. "
                "'확정분양가'로 홍보하더라도 모집공고문 원문에 그 표현·산정기준이 실제로 있는지 "
                "먼저 원문 전수검색으로 확인할 것. 원문에 없으면 사업주체 재량 사항이며, "
                "국토교통부는 '장래 분양전환가를 미리 약정하는 행위는 법에 근거가 없어 "
                "법에 저촉될 수 있다'는 경고문구를 실제 공고문에서 사업주체 스스로 인용한 사례가 있다 "
                "(동탄 파라곤3차, 2026.08 조사)."
            )}


def installment_conversion_schedule(*, initial_price: float, early_appraised: float | None = None,
                                    lh_rate: float = 0.028, year4_rate: float | None = None,
                                    early_year: int = 5) -> dict:
    """
    분납 공공임대(10년/분납) 조기분양전환의 4회 납부 스케줄.
    「공공주택특별법 시행규칙」[별표8] 근거 — 실제 LH 계약안내문(하남감일B5,
    2026.06 조기분양전환) 원문 대조로 확인한 구조.

    최초주택가격(입주자모집공고 당시 산정가격) 기준으로 앞 3회는 LH 할부이자율
    복리 적용, 마지막 30%만 조기분양전환 시점의 실제 감정평가금액(두 법인 평균)에
    연동된다 — 즉 4회차만 '예측이 필요한' 항목이고 나머지는 확정 계산이다.

    initial_price: 최초주택가격 (입주자모집공고 당시)
    early_appraised: 조기분양전환 시점 감정평가금액 산술평균 (모르면 4회차 None)
    lh_rate: LH 할부이자율 (연리, 변동금리 — 2026.06.01 기준 3.0%가 아니라
             입주시~4년차 구간엔 보통 기본금리 2.8% 별도 적용되므로 계약안내문 확인 필수)
    year4_rate: 4년차 이자율이 입주시와 다를 경우 별도 지정. None이면 lh_rate 사용.
    early_year: 조기분양전환 시행 연차 (하남감일B5 사례는 5년차)
    """
    r4 = year4_rate if year4_rate is not None else lh_rate
    year1 = initial_price * 0.30
    year4 = initial_price * ((1 + r4) ** 4) * 0.20
    early_fixed = initial_price * ((1 + lh_rate) ** early_year) * 0.20
    early_final = None if early_appraised is None else early_appraised * 0.30
    total = None if early_final is None else year1 + year4 + early_fixed + early_final
    return {
        "basis": "「공공주택특별법 시행규칙」[별표8] — LH 계약안내문(하남감일B5 감일스윗시티10단지, "
                 "2026.06 조기분양전환) 원문 대조",
        "note": (
            "1~3회차(80%)는 최초주택가격에 LH 할부이자율 복리를 적용한 확정 금액이라 "
            "사전예측이 정확히 맞는다. 4회차(30%)만 '조기분양전환 시점 감정평가금액'에 "
            "연동되므로 이 앱의 예측이 실제로 효력을 갖는 구간은 사실상 4회차뿐이다."
        ),
        "회차별": {
            "1_입주시_30%": round(year1),
            "2_4년차_20%": round(year4),
            "3_조기분전시_20%_확정분": round(early_fixed),
            "4_조기분전시_30%_감정가연동": None if early_final is None else round(early_final),
        },
        "합계": None if total is None else round(total),
    }


# ---------------------------------------------------------------------------
# 공공건설임대주택 표준건축비 (국토교통부고시 제2023-64호, 시행 2023-02-01)
#
# 5년 임대 분양전환가격 상한(산정가격)의 건축비 항이다.
# 단위: 원/㎡. 고시 원문은 천원/㎡이며 부가가치세가 포함된 금액이다.
# 적용 면적은 '주택공급면적'(주택공급규칙 제21조⑤ 공급면적 중 그 밖의
# 공용면적을 제외한 면적)이지 전용면적이 아니다 — 혼동 주의.
#
# 구간 기준은 '주거전용면적'이고, 단가는 '주택공급면적'에 곱한다.
# 층수 구간별로 단가가 다르며 6~10층이 가장 비싸다(저층·초고층보다 비효율).
# ---------------------------------------------------------------------------

STD_BUILD_COST_2023 = {
    "5층 이하":    {40: 1_126_700, 50: 1_145_200, 60: 1_109_500, 999: 1_120_800},
    "6~10층":      {40: 1_209_800, 50: 1_226_100, 60: 1_188_500, 999: 1_192_300},
    "11~20층":     {40: 1_143_000, 50: 1_154_100, 60: 1_119_300, 999: 1_118_800},
    "21층 이상":   {40: 1_162_600, 50: 1_173_800, 60: 1_139_200, 999: 1_138_400},
}

STD_BUILD_COST_META = {
    "고시": "국토교통부고시 제2023-64호 「공공건설임대주택 표준건축비」",
    "시행": "2023-02-01",
    "단위": "원/㎡ (부가가치세 포함)",
    "적용면적": "주택공급면적 (주택공급에 관한 규칙 제21조제5항의 공급면적 중 "
                "그 밖의 공용면적을 제외한 면적)",
    "구간기준": "주거전용면적",
    "적용시점": "2023년 고시 이후 최초로 입주자모집공고 승인을 신청하는 분 또는 "
                "분양전환에 관한 승인을 신청하는 분부터 적용",
    "행정규칙일련번호": "2100000218618",
}


def standard_build_cost(*, floors: int, exclusive_area: float,
                        supply_area: float | None = None) -> dict:
    """
    표준건축비 단가와 총액을 구한다.

    floors          : 해당 동의 층수 (구간 판정용)
    exclusive_area  : 주거전용면적 (단가 구간 판정 기준)
    supply_area     : 주택공급면적 (단가를 곱할 면적). 생략하면 총액을 내지 않는다.
    """
    if floors <= 5:
        band = "5층 이하"
    elif floors <= 10:
        band = "6~10층"
    elif floors <= 20:
        band = "11~20층"
    else:
        band = "21층 이상"

    table = STD_BUILD_COST_2023[band]
    for cap in (40, 50, 60, 999):
        if exclusive_area <= cap:
            rate = table[cap]
            area_band = (f"{cap}㎡ 이하" if cap != 999 else "60㎡ 초과")
            break

    out = {
        "층수구간": band, "면적구간": area_band,
        "단가(원/㎡)": rate,
        "전용면적": exclusive_area,
        "basis": STD_BUILD_COST_META["고시"],
        "note": f"단가는 {STD_BUILD_COST_META['적용면적']}에 곱한다. 전용면적이 아님에 주의.",
    }
    if supply_area:
        out["주택공급면적"] = supply_area
        out["표준건축비 총액"] = round(rate * supply_area)
    return out


def build_cost(*, initial_price: float, land_price: float,
               fund_loan: float = 0.0, deposit: float = 0.0,
               rate_start: float = 0.0, rate_end: float = 0.0,
               lease_years: float = 0.0, useful_life: int = 40) -> dict:
    """
    건설원가를 산출한다. 공공주택 특별법 시행규칙 [별표7] 제2호 가목.

        건설원가 = 최초 입주자모집공고 당시 주택가격 + 자기자금이자 − 감가상각비

        자기자금이자 = (최초 주택가격 − 주택도시기금 융자금 − 임대보증금)
                       × 이자율 × 임대기간
          이자율 = 임대시작일과 분양전환일의 1년만기 정기예금 평균이자율의 산술평균
        감가상각비 = 법인세법 시행령 제26조 정액법
          철근콘크리트 주택 내용연수 40년, 건축비(건물분)를 상각 대상으로 한다.

    5년 임대의 분양전환가격 = (건설원가 + 감정평가금액) ÷ 2 에 들어가는 항이다.
    10년 임대는 건설원가를 쓰지 않는다(감정평가금액이 곧 상한).
    """
    building_price = max(0.0, initial_price - land_price)   # 건축비 = 주택가격 − 택지비
    rate = (rate_start + rate_end) / 2
    own_fund = max(0.0, initial_price - fund_loan - deposit)
    own_interest = own_fund * rate * lease_years
    depreciation = (building_price / useful_life) * lease_years if useful_life else 0.0
    total = initial_price + own_interest - depreciation
    return {
        "건설원가": round(total),
        "최초주택가격": round(initial_price),
        "택지비": round(land_price),
        "건축비(건물분)": round(building_price),
        "자기자금이자": round(own_interest),
        "  자기자금": round(own_fund),
        "  적용이자율": round(rate, 5),
        "  임대기간(년)": lease_years,
        "감가상각비": round(depreciation),
        "  내용연수": useful_life,
        "basis": "공공주택 특별법 시행규칙 [별표7] 제2호 가목",
        "note": "표준건축비·정기예금 금리는 추정치이므로 실제 분양전환 통보서 수치로 보정할 것.",
    }


def ceiling_price_5yr(*, std_build_cost: float, land_price: float,
                      land_interest: float = 0.0,
                      depreciation: float = 0.0) -> dict:
    """
    5년 임대 분양전환가격의 상한(산정가격 − 감가상각비).
    [별표7] 제1호 나목 단서 및 제2호 다목.

        산정가격 = 분양전환 당시 표준건축비 + 최초 택지비 + 택지비이자
    """
    calc = std_build_cost + land_price + land_interest
    return {
        "산정가격": round(calc),
        "상한": round(calc - depreciation),
        "  표준건축비": round(std_build_cost),
        "  최초택지비": round(land_price),
        "  택지비이자": round(land_interest),
        "  감가상각비": round(depreciation),
        "basis": "공공주택 특별법 시행규칙 [별표7] 제1호 나목 단서, 제2호 다목",
        "note": "5년 임대는 (건설원가+감정평가금액)÷2가 이 상한을 초과할 수 없다.",
    }


def sampling_rule(total_units: int) -> dict:
    """
    분양전환 감정평가의 표본 산정 규칙.
    공공주택 특별법 시행규칙 제42조 제2항 (시행 2026.6.22. 국토교통부령 제1599호).

    "같은 단지에서 30세대 이상의 공공임대주택을 분양전환하는 경우에는
     분양전환대상 세대수의 10퍼센트 범위에서 동·규모·층 및 방향 등을 고려하여
     감정평가의 대상 주택을 정할 수 있다."

    실무상 함의가 크다. 전 세대를 평가하지 않고 표본만 평가한 뒤 나머지는
    그 표본에서 유추한다. 즉 '어떤 세대가 표본으로 뽑히느냐'가 단지 전체
    분양전환가격을 좌우한다. 표본 선정 기준이 동·규모·층·방향이므로
    우리 엔진의 층별효용·향·면적 분석이 그대로 표본 검증 논리가 된다.
    """
    if total_units < 30:
        return {"applies": False, "max_sample": total_units,
                "basis": "시행규칙 제42조 제2항 — 30세대 미만은 표본평가 규정 미적용",
                "note": "전 세대 평가가 원칙이다."}
    cap = int(total_units * 0.10)
    return {
        "applies": True, "total_units": total_units, "max_sample": cap,
        "basis": "공공주택 특별법 시행규칙 제42조 제2항",
        "criteria": ["동", "규모(면적)", "층", "방향"],
        "note": (
            f"분양전환대상 {total_units:,}세대의 10% 이내, 즉 최대 {cap:,}세대만 "
            f"감정평가 대상으로 정할 수 있다. 표본이 단지 전체 가격을 좌우하므로 "
            f"표본이 동·규모·층·방향을 대표하는지 검증할 실익이 크다."
        ),
    }


def revaluation_trigger(appraisals: list[float]) -> dict:
    """
    재감정 요건 판정.
    공공주택 특별법 시행규칙 제42조 제3항.

    "감정평가금액 중 최고 평가액이 최저 평가액의 100분의 110을 초과하는 경우에는
     ... 감정평가를 다시 의뢰하여야 한다."

    입주민 입장에서 결정적인 조항이다. 두 평가액 격차가 10%를 넘으면 재감정이
    강제되고, 종전 감정평가에 대한 타당성 조사도 요구할 수 있다.
    """
    vals = [v for v in appraisals if v and v > 0]
    if len(vals) < 2:
        return {"triggered": False, "note": "평가액이 2건 미만이라 판정 불가"}
    lo, hi = min(vals), max(vals)
    ratio = hi / lo
    triggered = ratio > 1.10
    return {
        "triggered": triggered, "min": lo, "max": hi, "ratio": round(ratio, 4),
        "threshold": 1.10,
        "basis": "공공주택 특별법 시행규칙 제42조 제3항",
        "note": (
            f"최고 {hi:,.0f}원 / 최저 {lo:,.0f}원 = {ratio:.1%}. "
            + ("110%를 초과하므로 시장·군수·구청장은 재감정을 의뢰하여야 한다. "
               "공공주택사업자 또는 임차인은 종전 감정평가에 대한 타당성 조사를 "
               "요구할 수 있다(감정평가법 제46조①1호)."
               if triggered else
               "110% 이내이므로 재감정 사유에 해당하지 않는다.")
        ),
    }


def reverse_appraised(*, conversion: float, build_cost: float,
                      lease_type: str = "5년") -> float | None:
    """
    분양전환가격과 건설원가로 감정평가금액을 역산한다.
    5년 임대에서만 성립한다.  감정가 = 2 × 분양전환가 − 건설원가
    """
    if not lease_type.replace("임대", "").strip().startswith("5"):
        return None
    return 2 * conversion - build_cost


# ---------------------------------------------------------------------------
# 시공사 브랜드 — 국가가 공시하지 않는 항목. 단지명에 박힌 브랜드명으로 매칭한 뒤
# 우리가 가진 실거래 데이터에서 지역 통제(같은 시군구 내 비교) 잔차로 프리미엄을 추정한다.
# 참고: LH 공공임대 분양전환 감정평가 실무 사례(구경백 감정평가사 블로그, 2026) —
# "시공업체의 브랜드, 시장선호도"가 단지내부요인으로 실제 반영됨.
# ---------------------------------------------------------------------------

# 단지명 부분일치 -> (브랜드, 시공사) . 순서가 곧 매칭 우선순위(긴 키워드부터 위에 둘 것).
BRAND_KEYWORDS: list[tuple[str, str, str]] = [
    ("아크로", "아크로", "DL이앤씨"), ("디에이치", "디에이치", "현대건설"),
    ("래미안", "래미안", "삼성물산"), ("힐스테이트", "힐스테이트", "현대건설"),
    ("자이", "자이", "GS건설"), ("푸르지오", "푸르지오", "대우건설"),
    ("아이파크", "아이파크", "HDC현대산업개발"), ("롯데캐슬", "롯데캐슬", "롯데건설"),
    ("e편한세상", "이편한세상", "DL이앤씨"), ("이편한세상", "이편한세상", "DL이앤씨"),
    ("호반써밋", "호반써밋", "호반건설"), ("호반베르디움", "호반베르디움", "호반건설"),
    ("데시앙", "데시앙", "태영건설"), ("위브", "위브", "두산건설"),
    ("우미린", "우미린", "우미건설"), ("반도유보라", "반도유보라", "반도건설"),
    ("보라매", "반도유보라", "반도건설"),
    ("서희스타힐스", "서희스타힐스", "서희건설"), ("중흥", "중흥에스클래스", "중흥토건"),
    ("모아엘가", "모아엘가", "모아건설"), ("금강펜테리움", "금강펜테리움", "금강주택"),
    ("대광로제비앙", "로제비앙", "대광건영"), ("동양엔파트", "엔파트", "동양건설산업"),
    ("한신더휴", "한신더휴", "한신공영"), ("계룡리슈빌", "리슈빌", "계룡건설"),
    ("포레나", "포레나", "한화건설"), ("한화포레나", "포레나", "한화건설"),
    ("신동아파밀리에", "파밀리에", "신동아건설"), ("동원로얄듀크", "로얄듀크", "동원개발"),
    ("코오롱하늘채", "하늘채", "코오롱글로벌"), ("하늘채", "하늘채", "코오롱글로벌"),
    ("SK뷰", "SK뷰", "SK에코플랜트"), ("자연앤스카이", "자연앤", "SK에코플랜트"),
    ("금호어울림", "어울림", "금호산업"), ("우남퍼스트빌", "우남퍼스트빌", "우남건설"),
]


def detect_brand(complex_name: str) -> tuple[str, str] | None:
    """단지명에서 브랜드·시공사를 추정. 못 찾으면 None(중소 지역건설사 추정)."""
    for kw, brand, builder in BRAND_KEYWORDS:
        if kw in complex_name:
            return brand, builder
    return None


def brand_premium_table(complexes: list[dict], *, min_group: int = 5,
                        min_baseline: int = 8) -> dict[str, dict]:
    """
    같은 시군구(sgg) 안에서 브랜드별 ㎡단가 중앙값을, 무브랜드(중소사) 단지 중앙값과 비교한다.
    지역 자체의 가격수준 차이를 통제하기 위해 "같은 시군구 안에서"만 비교하고,
    그 격차율(브랜드/무브랜드)을 시군구별로 구한 뒤 최종적으로 전체 중앙값을 취한다.

    complexes: [{"nm":..., "sgg":..., "unit":...}, ...] — 실거래 보유 단지만 넣을 것.
    반환: {브랜드: {"n":..., "ratio":..., "note":...}}
    """
    import statistics
    import collections

    by_sgg = collections.defaultdict(list)
    for c in complexes:
        if not c.get("sgg") or not c.get("unit"):
            continue
        by_sgg[c["sgg"]].append(c)

    brand_ratios: dict[str, list[float]] = collections.defaultdict(list)
    for sgg, items in by_sgg.items():
        base = [c["unit"] for c in items if not detect_brand(c["nm"])]
        if len(base) < min_baseline:
            continue
        base_med = statistics.median(base)
        grouped = collections.defaultdict(list)
        for c in items:
            hit = detect_brand(c["nm"])
            if hit:
                grouped[hit[0]].append(c["unit"])
        for brand, units in grouped.items():
            if len(units) < 2:
                continue
            brand_ratios[brand].append(statistics.median(units) / base_med)

    out = {}
    for brand, ratios in brand_ratios.items():
        if len(ratios) < min_group:
            continue
        out[brand] = {
            "n_sgg": len(ratios),
            "ratio": round(statistics.median(ratios), 4),
            "note": f"{len(ratios)}개 시군구에서 무브랜드 단지 대비 ㎡단가 중앙값 비율",
        }
    return out


# ---------------------------------------------------------------------------
# 지역요인 6조건 — 「표준지공시지가 조사・평가 기준」(국토부훈령, 2023-01-30)
# [별표 2] 주택지대의 지역요인 및 개별요인. 감칙 제9조가 정한 법정 비교틀이다.
# 토지 표준지 비교용이지만, 아파트 감정평가에서도 "단지가 속한 위치"의
# 지역요인 비교(인근 비준단지가 다른 위치일 때) 체크리스트로 그대로 쓸 수 있다.
# 세대 개별요인(층·향·동위치)은 별도로 실무기준 [610-3.1.3]②를 따른다.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# ★ 아파트(구분건물) 전용 가치형성요인 4계층
#
# 실제 감정평가서 2건에서 동일한 체계가 확인되었다 (2026-08-06 원문 대조):
#   - 지우감정평가법인 1-230619-301 (서울중앙지법 경매, 2023.07.26)
#   - 청암감정평가사사무소 CA2308-004 (수원지법 경매, 2023.08.29)
#
# 위 REGIONAL_FACTOR_ITEMS(토지 표준지 6조건)는 나지(裸地) 비교용이고,
# 아파트는 이 4계층을 쓴다. 각 계층의 격차율을 곱해 최종 비교치를 낸다.
#     비준가격 = 사례가격 × 사정보정 × 시점수정 × 가치형성요인비교 × 면적비
#
# CA2308-004 실제 산출 예: 880,000,000 × 1.00 × 1.00792 × 1.030 × (84.949/84.949)
#                          = 913,600,000  (호별요인에서 층별효용 우세로 1.03)
# ---------------------------------------------------------------------------

APARTMENT_FACTOR_ITEMS = {
    "단지외부요인": [
        "대중교통의 편의성",
        "교육시설 등의 배치",
        "도심지 및 상업·업무시설과의 접근성",
        "차량이용의 편리성",
        "공공시설 및 편익시설과의 배치",
        "자연환경(조망·풍치·경관 등)",
    ],
    "단지내부요인": [
        "시공업체의 브랜드",
        "단지내 총세대수 및 최고층수",
        "건물의 구조 및 마감상태",
        "경과연수에 따른 노후도",
        "단지내 면적구성(대형·중형·소형)",
        "단지내 통로구조(복도식/계단식)",
        "공용시설의 규모·구성·상태",
        "전용률",
    ],
    "호별요인": [
        "층별 효용",
        "향별 효용",
        "위치별 효용(동별 및 라인별)",
        "전유부분의 면적 및 대지사용권의 크기",
        "내부 평면방식(베이)",
        "베란다의 유무 및 면적의 대소",
        "주차장 등의 유무",
        "간선도로 및 철도 등에 의한 소음",
        "관리상태",
    ],
    "기타요인": ["기타 가치에 영향을 미치는 요인"],
    "_출처": "실제 감정평가서 원문 대조 — 지우감정평가법인 1-230619-301(2023.07.26), "
             "청암감정평가사사무소 CA2308-004(2023.08.29). 감칙 제16조 구분소유 부동산 "
             "일괄 거래사례비교법 적용 사례.",
}


def apartment_factor_worksheet(*, subject: dict, case: dict) -> dict:
    """
    아파트 가치형성요인 4계층 비교표를 생성한다.

    자동으로 채울 수 있는 것(층별효용·경과연수·브랜드·세대수·전용률)은 값을 넣고,
    임장·현황확인이 필요한 것(마감상태·관리상태·소음·조망)은 확인란으로 남긴다.
    감정평가사가 실제로 각 계층에 단일 격차율을 부여하므로, 계층별 산출근거를
    항목 단위로 노출해 그 격차율이 어디서 왔는지 추적 가능하게 만든다.

    subject / case 예:
      {"nm":..., "build_year":..., "floor":..., "top_floor":..., "hhld":..., "area":...}
    """
    def _brand(d):
        hit = detect_brand(d.get("nm", ""))
        return hit[0] if hit else "무브랜드(중소사)"

    sheet = {
        "단지외부요인": {"items": list(APARTMENT_FACTOR_ITEMS["단지외부요인"]),
                    "자동산출": {}, "확인필요": ["대중교통·상업시설 접근성", "조망·풍치"]},
        "단지내부요인": {"items": list(APARTMENT_FACTOR_ITEMS["단지내부요인"]),
                    "자동산출": {
                        "시공업체 브랜드": {"대상": _brand(subject), "사례": _brand(case)},
                        "총세대수": {"대상": subject.get("hhld"), "사례": case.get("hhld")},
                        "최고층수": {"대상": subject.get("top_floor"), "사례": case.get("top_floor")},
                        "준공연도": {"대상": subject.get("build_year"), "사례": case.get("build_year")},
                    },
                    "확인필요": ["마감상태", "공용시설 상태", "통로구조(복도식/계단식)"]},
        "호별요인": {"items": list(APARTMENT_FACTOR_ITEMS["호별요인"]),
                  "자동산출": {
                      "층": {"대상": subject.get("floor"), "사례": case.get("floor")},
                      "전유면적": {"대상": subject.get("area"), "사례": case.get("area")},
                  },
                  "확인필요": ["향", "동·라인 위치", "베이(평면방식)", "간선도로·철도 소음", "관리상태"]},
        "기타요인": {"items": list(APARTMENT_FACTOR_ITEMS["기타요인"]),
                  "자동산출": {}, "확인필요": ["기타 가치영향요인"]},
        "_출처": APARTMENT_FACTOR_ITEMS["_출처"],
        "_주의": "확인필요 항목은 임장(실지조사) 없이는 확정할 수 없다. "
                 "감칙 제10조는 실지조사를 원칙으로 하며, 미실시 시 그 사유를 "
                 "감정평가서에 적어야 한다.",
    }
    return sheet


REGIONAL_FACTOR_ITEMS = {
    "가로조건": ["가로의 폭ㆍ구조 등의 상태(포장ㆍ보도ㆍ계통 및 연속성)"],
    "접근조건": [
        "도심과의 거리 및 교통시설의 상태(인근교통시설 편의성ㆍ도시중심 접근성)",
        "상가의 배치상태(인근상가 편의성ㆍ품격)",
        "공공 및 편익시설의 배치상태(유치원ㆍ초등학교ㆍ공원ㆍ병원ㆍ관공서 등)",
    ],
    "환경조건": [
        "기상조건(일조ㆍ습도ㆍ온도ㆍ통풍 등)",
        "자연환경(조망ㆍ경관ㆍ지반ㆍ지질 등)",
        "사회환경(거주자의 직업ㆍ연령 등, 학군 등)",
        "획지의 상태(표준적 면적ㆍ정연성ㆍ건물 소밀도ㆍ주변 이용상황)",
        "공급 및 처리시설의 상태(상수도ㆍ하수도ㆍ도시가스 등)",
        "위험 및 혐오시설(변전소ㆍ가스탱크ㆍ오수처리장 등의 유무, 특별고압선 통과 유무)",
        "재해발생의 위험성(홍수ㆍ사태ㆍ절벽붕괴 등)",
    ],
    "획지조건": ["면적ㆍ접면너비ㆍ깊이ㆍ형상(부정형지ㆍ삼각지ㆍ자루형획지ㆍ맹지 등), 방위ㆍ고저"],
    "행정적조건": ["행정상의 조장 및 규제정도 등"],
    "기타조건": ["장래의 동향, 기타"],
    "_출처": "표준지공시지가 조사・평가 기준 [별표2] 주택지대의 지역요인 및 개별요인 "
             "(국토교통부훈령, 행정규칙일련번호 2100000218574, 시행 2023-01-30)",
}


def regional_factor_checklist(*, subject_addr: str = "", comp_addr: str = "",
                              nearest_school_m: int | None = None,
                              hazard_flags: list[str] | None = None) -> dict:
    """
    대상-사례 지역요인 비교 체크리스트를 생성한다. 값을 자동 산정하지 않고
    확인이 필요한 항목을 구조화해 반환한다 — 임의로 격차율을 매기면 §근거없는
    보정이 되므로, 실측 가능한 것(학교거리)만 수치를 채우고 나머지는 확인란으로 둔다.
    """
    checklist = {k: list(v) for k, v in REGIONAL_FACTOR_ITEMS.items() if not k.startswith("_")}
    result = {"subject": subject_addr, "comp": comp_addr, "items": checklist,
             "출처": REGIONAL_FACTOR_ITEMS["_출처"]}
    if nearest_school_m is not None:
        result["학교거리_실측"] = f"최근접 초등학교 {nearest_school_m}m (배정학구 아님, 참고용)"
    if hazard_flags:
        result["위험혐오시설_확인"] = hazard_flags
    return result
