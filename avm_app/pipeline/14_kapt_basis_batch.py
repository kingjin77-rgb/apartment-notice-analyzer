# -*- coding: utf-8 -*-
"""12번으로 들어온 K-APT 갭 단지(거래0건)의 단지 기본정보를 전수 수집.

왜 필요한가 — 12번 결과를 브라우저에서 검증하다 발견한 문제:
  경희궁의아침4단지(2004년 주상복합)의 비교사례 1순위가 1981년 준공 빌딩이었다.
  갭 단지는 yr(준공년)이 비어 있어서 노후도 보정이 원천적으로 불가능하고,
  거리만으로 비준하면 서울 도심처럼 연식 편차가 큰 곳에서 사례 선정이 무너진다.
  화성 파일럿은 단지 연식이 고른 신도시라 이 결함이 안 드러났던 것.

같이 해결되는 것:
  codeSaleNm(분양/임대/혼합)이 공부상 임대구분을 준다. 지금 lh 플래그는 단지명
  정규식 추정이라 26,948건 중 341건밖에 못 잡는다(임대인데 시세가 뜨는 문제의 원인).

K-APT는 일 트래픽 한도가 있어(2026-08-07 소진 확인) 진행분을 계속 저장한다.
중단되면 그냥 다시 실행하면 이어서 돈다.
사용법: python 14_kapt_basis_batch.py
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import sys, io, json, re, time, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
_ENV_CANDIDATES = [
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))), "apartment_notice_analyzer", ".env"),
]
for _p in _ENV_CANDIDATES:
    if os.path.exists(_p):
        load_dotenv(_p)
        break
from modules.kapt_complex import KaptClient

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
DST = os.path.join(SC, "kapt_basis.json")
LOG = io.open(os.path.join(SC, "kapt_basis_log.txt"), "a", encoding="utf-8")
_lk = threading.Lock()
def P(*a):
    with _lk:
        print(*a, file=LOG); LOG.flush(); print(*a)

client = KaptClient()
if not client.is_configured:
    P("KAPT_API_KEY / MOLIT_API_KEY 없음 — 중단")
    sys.exit(1)

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"const COMPLEX_DATA = (\[.*\]);", txt, re.S)
data = json.loads(m.group(1))
codes = [c["kaptCode"] for c in data if c.get("kaptCode")]
P(f"대상 kaptCode {len(codes)}개")

done = {}
if os.path.exists(DST):
    done = json.load(io.open(DST, encoding="utf-8"))
    P(f"기존 진행분 {len(done)}건 이어서 진행")

todo = [c for c in codes if c not in done]
P(f"남은 {len(todo)}건")

n_ok = n_fail = 0
def fetch(code):
    global n_ok, n_fail
    try:
        info = client.basis_info(code, with_detail=True)
    except Exception as e:
        with _lk:
            n_fail += 1
        return code, None
    if not info:
        with _lk:
            n_fail += 1
        return code, None
    with _lk:
        n_ok += 1
    return code, {
        "yr": info.build_year or "",
        "useDate": info.use_date,
        "units": info.households,
        "topFloor": info.top_floor,
        "hallType": info.hall_type,
        "saleType": info.sale_type,          # 분양 / 임대 / 혼합 — 공부상 임대구분
        "kind": info.kind,
        "builder": info.builder,
        "parkingTotal": info.parking_total,
        "parkingPerHh": round(info.parking_per_household, 2) if info.households else None,
        "heatType": info.heat_type,
        "subwayStation": info.subway_station,
        "subwayTime": info.subway_time,
        "eduFacility": info.education_facility,
        "area60": info.area_60, "area85": info.area_85,
        "area135": info.area_135, "area136": info.area_136,
    }

with ThreadPoolExecutor(max_workers=6) as ex:
    for i, (code, rec) in enumerate(ex.map(fetch, todo)):
        if rec:
            done[code] = rec
        if (i + 1) % 200 == 0:
            with _lk:
                json.dump(done, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
            P(f"  진행 {i+1}/{len(todo)} (성공 {n_ok} 실패 {n_fail})")

json.dump(done, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
P(f"완료: 확보 {len(done)} / 대상 {len(codes)} (이번 성공 {n_ok} 실패 {n_fail})")
print("DONE", len(done), n_ok, n_fail)
