"""
school_analysis.py
아파트 모집공고문 분석 — 2순위 모듈: 학군

전략:
  NEIS(보유)        → 반경 내 학교 목록 + 좌표/주소  (기본정보)
  학교알리미(신규)   → 학급당 학생수·학생수·교원수     (과밀 판정 = 협상 근거)
  카카오 로컬(보유)  → 통학 도보거리 실측

핵심 산출:
  '초등학교 도보 N분 / 학급당 M명(과밀)' — 입예협이 시행사·교육청에
  학교 신설·통학로 개선을 요구할 때 쓰는 정량 근거.

인증키:
  NEIS_API_KEY        (보유)
  SCHOOLINFO_API_KEY  (신규 — schoolinfo.go.kr 소셜로그인 후 발급)
"""

from __future__ import annotations

import os
import math
import logging
from dataclasses import dataclass, field, asdict
from typing import Any

import requests

log = logging.getLogger(__name__)

NEIS_API_KEY = os.getenv("NEIS_API_KEY", "")
SCHOOLINFO_API_KEY = os.getenv("SCHOOLINFO_API_KEY", "")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

NEIS_BASE = "https://open.neis.go.kr/hub"
SCHOOLINFO_BASE = "https://www.schoolinfo.go.kr/openApi.do"

# 학교알리미 실제 요청인자(공식 개발자가이드 확인, 2026-07-27):
#   apiKey(필수) / apiType(필수, Api종류) / sidoCode(필수, 시도코드)
#   sggCode(필수, 시군구코드) / schulKndCode(필수, 02:초 03:중 04:고 05:특수 06:그외 07:각종)
# schulNm/pbanYr 파라미터는 존재하지 않는다 — 예전 코드의 가정이 틀렸음.
# apiType=0 은 "학교기본정보"로 확인됨(경기도 시도코드=41, 부천시 원미구=41194로 실측).
# "학년별·학급별 학생수" 항목의 apiType 값은 아직 미확정 — 0 이외 후보(1,2)는
# 모두 "해당 연도에 공시되지 않음" 응답만 반환했다. 학교알리미 OpenAPI > API
# 제공목록에서 해당 항목 상세 명세서를 직접 열어 apiType 기본값을 확인할 것.
SCHOOLINFO_API_TYPE_BASIC = "0"        # 학교기본정보 (확인됨)
SCHOOLINFO_API_TYPE_CLASS = os.getenv("SCHOOLINFO_API_TYPE_CLASS", "")  # 학년별·학급별 학생수 (미확정)

# 시도코드(행정표준코드 앞 2자리) — 학교알리미는 NEIS의 B10/J10 체계가 아니라
# 구 법정동코드 체계(서울=11, 경기=41 등)를 쓴다.
SCHOOLINFO_SIDO_CODE = {
    "서울": "11", "부산": "26", "대구": "27", "인천": "28", "광주": "29",
    "대전": "30", "울산": "31", "세종": "36", "경기": "41", "강원": "42",
    "충북": "43", "충남": "44", "전북": "45", "전남": "46", "경북": "47",
    "경남": "48", "제주": "50",
}

TIMEOUT = 12

# 학급당 학생수 과밀 기준 (교육부 학급편성 기준 참고)
CROWD_LIMIT = {"초등학교": 24, "중학교": 26, "고등학교": 26}

# 통학 적정 거리 (초등학교 통학구역 설정 기준 통상 1.5km)
WALK_OK_M = {"초등학교": 800, "중학교": 1500, "고등학교": 2500}


@dataclass
class School:
    name: str
    level: str                    # 초등학교 / 중학교 / 고등학교
    address: str = ""
    lat: float | None = None
    lon: float | None = None
    straight_m: int | None = None    # 직선거리
    walk_m: int | None = None        # 도보거리
    walk_min: int | None = None
    students: int | None = None
    classes: int | None = None
    per_class: float | None = None
    crowded: bool = False
    severity: str = "하"
    note: str = ""


@dataclass
class SchoolReport:
    address: str
    lat: float | None = None
    lon: float | None = None
    radius_m: int = 2000
    schools: list[School] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────────────────────

def _haversine_m(lat1, lon1, lat2, lon2) -> int:
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return int(2 * R * math.asin(math.sqrt(a)))


def geocode(address: str) -> tuple[float, float] | None:
    if not KAKAO_REST_API_KEY:
        return None
    try:
        r = requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
            params={"query": address}, timeout=TIMEOUT,
        )
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if docs:
            return float(docs[0]["y"]), float(docs[0]["x"])
    except Exception as e:  # noqa: BLE001
        log.warning("지오코딩 실패: %s", e)
    return None


# ─────────────────────────────────────────────────────────────
# 1) NEIS — 학교 목록 (시도/시군구 단위 조회 후 반경 필터)
# ─────────────────────────────────────────────────────────────

NEIS_SIDO_CODE = {
    "서울": "B10", "부산": "C10", "대구": "D10", "인천": "E10", "광주": "F10",
    "대전": "G10", "울산": "H10", "세종": "I10", "경기": "J10", "강원": "K10",
    "충북": "M10", "충남": "N10", "전북": "P10", "전남": "Q10", "경북": "R10",
    "경남": "S10", "제주": "T10",
}


def _sido_code(address: str) -> str | None:
    for k, v in NEIS_SIDO_CODE.items():
        if address.startswith(k):
            return v
    return None


def fetch_schools_neis(address: str, lat: float, lon: float,
                       radius_m: int = 2000) -> tuple[list[School], str | None]:
    code = _sido_code(address)
    if not code:
        return [], f"시도코드 판별 실패: {address}"

    out: list[School] = []
    page = 1
    while page <= 10:
        try:
            r = requests.get(
                f"{NEIS_BASE}/schoolInfo",
                params={
                    "KEY": NEIS_API_KEY, "Type": "json",
                    "pIndex": page, "pSize": 1000,
                    "ATPT_OFCDC_SC_CODE": code,
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:  # noqa: BLE001
            return out, f"NEIS 조회 실패: {e}"

        body = data.get("schoolInfo")
        if not body or len(body) < 2:
            break
        rows = body[1].get("row", [])
        if not rows:
            break

        for row in rows:
            level = row.get("SCHUL_KND_SC_NM", "")
            if level not in CROWD_LIMIT:
                continue
            try:
                slat = float(row.get("LAT") or 0)
                slon = float(row.get("LOT") or 0)
            except (TypeError, ValueError):
                continue
            if not slat or not slon:
                continue
            d = _haversine_m(lat, lon, slat, slon)
            if d > radius_m:
                continue
            out.append(School(
                name=row.get("SCHUL_NM", ""),
                level=level,
                address=row.get("ORG_RDNMA", ""),
                lat=slat, lon=slon, straight_m=d,
            ))
        if len(rows) < 1000:
            break
        page += 1

    out.sort(key=lambda s: (s.level, s.straight_m or 99999))
    return out, None


# ─────────────────────────────────────────────────────────────
# 2) 학교알리미 — 학급당 학생수
# ─────────────────────────────────────────────────────────────

def enrich_schoolinfo(schools: list[School], address: str, sgg_code: str | None = None) -> str | None:
    """
    학교알리미 공시정보로 학생수·학급수를 채운다.

    ※ 학교알리미 API는 schulNm(학교명) 필터를 지원하지 않는다 — sidoCode/sggCode/
      schulKndCode 조합으로 해당 시군구·학교급 전체 목록을 받아온 뒤 이름으로
      매칭한다. sgg_code(5자리 구 법정동코드, 예: 부천시 원미구=41194)는 호출자가
      알고 있어야 한다 — 공식 시도시군구코드.xlsx 없이는 자동 산출 불가.
    """
    if not SCHOOLINFO_API_KEY:
        return "SCHOOLINFO_API_KEY 미설정 — 과밀 판정 생략"
    if not SCHOOLINFO_API_TYPE_CLASS:
        return "SCHOOLINFO_API_TYPE_CLASS 미확정 — 학년별·학급별 학생수 항목의 apiType 값을 schoolinfo.go.kr > API 제공목록에서 확인 후 환경변수로 지정할 것"
    if not sgg_code:
        return "sgg_code 미제공 — 시도시군구코드.xlsx(API이용안내)에서 대상 시군구 코드 확인 필요"

    sido_code = SCHOOLINFO_SIDO_CODE.get(address.split()[0] if address else "")
    if not sido_code:
        return f"시도코드 판별 실패: {address}"

    by_level: dict[str, list[School]] = {}
    for s in schools:
        by_level.setdefault(s.level, []).append(s)

    for level, kind_code in (("초등학교", "02"), ("중학교", "03"), ("고등학교", "04")):
        targets = by_level.get(level)
        if not targets:
            continue
        try:
            r = requests.get(
                SCHOOLINFO_BASE,
                params={
                    "apiKey": SCHOOLINFO_API_KEY,
                    "apiType": SCHOOLINFO_API_TYPE_CLASS,
                    "sidoCode": sido_code,
                    "sggCode": sgg_code,
                    "schulKndCode": kind_code,
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:  # noqa: BLE001
            log.debug("학교알리미 조회 실패 (%s): %s", level, e)
            continue

        if data.get("resultCode") != "success":
            log.debug("학교알리미 응답 실패 (%s): %s", level, data.get("resultMsg"))
            continue

        rows = data.get("list") or []
        by_name = {row.get("SCHUL_NM") or row.get("schulNm"): row for row in rows}
        for s in targets:
            row = by_name.get(s.name)
            if not row:
                continue
            try:
                s.students = int(row.get("총학생수") or row.get("student_cnt") or 0) or None
                s.classes = int(row.get("총학급수") or row.get("class_cnt") or 0) or None
            except (TypeError, ValueError):
                pass
            if s.students and s.classes:
                s.per_class = round(s.students / s.classes, 1)
                s.crowded = s.per_class > CROWD_LIMIT[s.level]
    return None


# ─────────────────────────────────────────────────────────────
# 3) 카카오 — 도보거리 실측 (가장 가까운 초등학교만)
# ─────────────────────────────────────────────────────────────

def enrich_walking(schools: list[School], lat: float, lon: float,
                   limit: int = 3) -> None:
    """도보 경로 API 미사용 시 직선거리 × 1.3 보정치를 쓴다."""
    for s in schools[:limit]:
        if s.straight_m is None:
            continue
        s.walk_m = int(s.straight_m * 1.3)
        s.walk_min = max(1, round(s.walk_m / 67))   # 도보 4km/h


# ─────────────────────────────────────────────────────────────
# 심각도 판정
# ─────────────────────────────────────────────────────────────

def judge(s: School) -> None:
    reasons = []
    sev = "하"

    limit = WALK_OK_M.get(s.level, 1500)
    dist = s.walk_m or s.straight_m
    if dist and dist > limit:
        reasons.append(f"통학거리 {dist}m (기준 {limit}m 초과)")
        sev = "중"

    if s.crowded and s.per_class:
        reasons.append(f"학급당 {s.per_class}명 (기준 {CROWD_LIMIT[s.level]}명 초과)")
        sev = "상" if sev == "중" else "중"

    if s.level == "초등학교" and dist and dist > 1000:
        reasons.append("초등 통학안전 — 통학로·횡단보도 개선 요구 대상")
        sev = "상"

    s.severity = sev
    s.note = " / ".join(reasons) if reasons else "특이사항 없음"


# ─────────────────────────────────────────────────────────────
# 메인 엔트리
# ─────────────────────────────────────────────────────────────

def analyze_schools(address: str, radius_m: int = 2000, sgg_code: str | None = None) -> SchoolReport:
    """
    >>> rep = analyze_schools("경기도 의왕시 삼동 191-1")
    >>> [s.name for s in rep.schools if s.level == "초등학교"]
    """
    rep = SchoolReport(address=address, radius_m=radius_m)

    coord = geocode(address)
    if not coord:
        rep.errors.append("지오코딩 실패")
        return rep
    rep.lat, rep.lon = coord

    schools, err = fetch_schools_neis(address, coord[0], coord[1], radius_m)
    if err:
        rep.errors.append(err)
    rep.schools = schools

    if e := enrich_schoolinfo(schools, address, sgg_code):
        rep.errors.append(e)

    enrich_walking(schools, coord[0], coord[1], limit=len(schools))

    for s in schools:
        judge(s)

    # 종합 소견
    elem = [s for s in schools if s.level == "초등학교"]
    if not elem:
        rep.findings.append("[상] 반경 내 초등학교 없음 — 학교 신설·통학버스 요구 근거")
    else:
        nearest = min(elem, key=lambda s: s.straight_m or 99999)
        rep.findings.append(
            f"최근접 초등학교: {nearest.name} 도보 약 {nearest.walk_min or '?'}분"
        )
        crowded = [s for s in elem if s.crowded]
        if crowded:
            rep.findings.append(
                f"[상] 과밀 초등학교 {len(crowded)}곳 — 입주 후 학급 부족 우려, "
                f"교육지원청 학급증설 협의 필요"
            )
    return rep


def to_docx_rows(rep: SchoolReport) -> list[list[str]]:
    rows = [["학교급", "학교명", "직선거리", "도보", "학급당", "심각도", "비고"]]
    for s in rep.schools:
        rows.append([
            s.level, s.name,
            f"{s.straight_m}m" if s.straight_m else "-",
            f"{s.walk_min}분" if s.walk_min else "-",
            f"{s.per_class}명" if s.per_class else "-",
            s.severity, s.note,
        ])
    return rows


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import json, sys
    addr = sys.argv[1] if len(sys.argv) > 1 else "경기도 의왕시 삼동"
    print(json.dumps(analyze_schools(addr).to_dict(), ensure_ascii=False, indent=2))
