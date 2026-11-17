# -*- coding: utf-8 -*-
"""전국 확장 — 02번(경기도 전용)을 일반화한 버전. 시/도 이름을 인자로 받는다.
national_comps.json에서 해당 시/도만 골라 카카오 지오코딩.

사용법: python 08_geocode_region.py "서울특별시"
중단돼도 이어서 돌 수 있도록 진행상황을 매 50건마다 저장한다."""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import json, io, os, time, sys
import requests
from dotenv import load_dotenv
_ENV_CANDIDATES = [
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))), "apartment_notice_analyzer", ".env"),
]
for _p in _ENV_CANDIDATES:
    if os.path.exists(_p):
        load_dotenv(_p)
        break

if len(sys.argv) < 2:
    print("사용법: python 08_geocode_region.py \"시/도 이름(national_comps.json의 sido 필드값 그대로)\"")
    sys.exit(1)
SIDO = sys.argv[1]
SLUG = SIDO.replace("특별시", "").replace("광역시", "").replace("자치도", "").replace("특별자치시", "").replace("도", "").strip() or SIDO

SC = os.path.join(_HERE, "data")
SRC = f"{SC}/national_comps.json"
DST = f"{SC}/{SLUG}_geocoded.json"
LOG = io.open(f"{SC}/geocode_{SLUG}_log.txt", "a", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

KAKAO = os.getenv("KAKAO_REST_API_KEY")
if not KAKAO:
    P("KAKAO_REST_API_KEY 없음 — 중단")
    sys.exit(1)

data = json.load(io.open(SRC, encoding="utf-8"))
targets = [x for x in data if x.get("sido") == SIDO]
P(f"{SIDO} 대상 {len(targets)}건")
if not targets:
    P(f"경고: sido=='{SIDO}' 매칭 0건. national_comps.json의 실제 sido 값 목록을 확인할 것.")
    sys.exit(1)

done = {}
if os.path.exists(DST):
    prev = json.load(io.open(DST, encoding="utf-8"))
    done = {(d["sgg"], d["umd"], d["jibun"]): d for d in prev if d.get("lat")}
    P(f"기존 진행분 {len(done)}건 이어서 진행")

def geocode(query):
    try:
        r = requests.get("https://dapi.kakao.com/v2/local/search/address.json",
                          headers={"Authorization": f"KakaoAK {KAKAO}"},
                          params={"query": query}, timeout=10)
        docs = r.json().get("documents") or []
        if not docs:
            r2 = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json",
                               headers={"Authorization": f"KakaoAK {KAKAO}"},
                               params={"query": query}, timeout=10)
            docs = r2.json().get("documents") or []
        if docs:
            d = docs[0]
            return float(d["y"]), float(d["x"]), d.get("address_name") or d.get("road_address_name") or query
    except Exception:
        pass
    return None

out = list(done.values())
n_ok = n_fail = 0
for i, c in enumerate(targets):
    key = (c["sgg"], c["umd"], c["jibun"])
    if key in done:
        continue
    q = f"{SIDO} {c['umd']} {c['jibun']}"
    geo = geocode(q)
    rec = dict(c)
    if geo:
        rec["lat"], rec["lng"], rec["geoAddr"] = geo
        n_ok += 1
    else:
        n_fail += 1
    out.append(rec)
    if (i + 1) % 50 == 0:
        json.dump(out, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
        P(f"  진행 {i+1}/{len(targets)} (성공 {n_ok} 실패 {n_fail})")
    time.sleep(0.08)

json.dump(out, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
P(f"완료: 성공 {n_ok} 실패 {n_fail} / 총 {len(targets)}")
print("DONE", n_ok, n_fail, len(targets))
