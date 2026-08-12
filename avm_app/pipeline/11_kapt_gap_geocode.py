# -*- coding: utf-8 -*-
"""10번이 모은 K-APT 전수목록(20,638건, 거래여부 무관) 중 현재 data.js(14,798건,
전부 hasT=1 실거래 기반이거나 화성파일럿 comps보유)에 아직 없는 '거래0건 갭' 단지를
골라 카카오로 지오코딩한다. 다음 단계(12번)가 이 결과로 인근비준 comps를 만든다.
사용법: python 11_kapt_gap_geocode.py"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, time
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

SC = os.path.join(_HERE, "data")
APP = os.path.join(_REPO, "avm_app")
DATA_JS = os.path.join(APP, "data.js")
SRC = os.path.join(SC, "kapt_full_list.json")
DST = os.path.join(SC, "kapt_gap_geocoded.json")
LOG = io.open(os.path.join(SC, "kapt_gap_geocode_log.txt"), "a", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

KAKAO = os.getenv("KAKAO_REST_API_KEY")
if not KAKAO:
    P("KAKAO_REST_API_KEY 없음 — 중단")
    sys.exit(1)

SUFFIX = re.compile(r"(아파트|APT|apt)$")
BRANDPAD = re.compile(r"[\s\(\)\[\]·,\.:：\-_/]")
def norm(s):
    s = BRANDPAD.sub("", s or "")
    s = SUFFIX.sub("", s)
    return s

kapt = json.load(io.open(SRC, encoding="utf-8"))
gap_raw = []
for code, v in kapt.items():
    for it in v["items"]:
        nm = (it.get("kaptName") or "").strip()
        if not nm:
            continue
        gap_raw.append({
            "nm": nm, "sido": it.get("as1") or v["sido"], "sgg": it.get("as2") or v.get("sgg_nm", ""),
            "umd": it.get("as3") or "", "bjdCode": it.get("bjdCode") or "", "kaptCode": it.get("kaptCode") or "",
        })
P(f"K-APT 전수 원본 {len(gap_raw)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
existing = json.loads(m.group(2))
existing_keys = {(norm(e["nm"]), e.get("umd", "")) for e in existing}
P(f"기존 data.js {len(existing)}건")

seen = set()
gap = []
for g in gap_raw:
    key = (norm(g["nm"]), g["umd"])
    if key in existing_keys or key in seen:
        continue
    seen.add(key)
    gap.append(g)
P(f"갭(미보유) 단지 {len(gap)}건 — 지오코딩 시작")

done = {}
if os.path.exists(DST):
    prev = json.load(io.open(DST, encoding="utf-8"))
    done = {(d["nm"], d["umd"]): d for d in prev}
    P(f"기존 진행분 {len(done)}건 이어서 진행")

def geocode(query):
    try:
        r = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json",
                          headers={"Authorization": f"KakaoAK {KAKAO}"},
                          params={"query": query}, timeout=10)
        docs = r.json().get("documents") or []
        if docs:
            d = docs[0]
            return float(d["y"]), float(d["x"]), d.get("address_name") or d.get("road_address_name") or query
    except Exception:
        pass
    return None

out = list(done.values())
n_ok = n_fail = 0
for i, g in enumerate(gap):
    key = (g["nm"], g["umd"])
    if key in done:
        continue
    q = f"{g['sido']} {g['sgg']} {g['umd']} {g['nm']}"
    geo = geocode(q)
    rec = dict(g)
    if geo:
        rec["lat"], rec["lng"], rec["geoAddr"] = geo
        n_ok += 1
    else:
        n_fail += 1
    out.append(rec)
    if (i + 1) % 100 == 0:
        json.dump(out, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
        P(f"  진행 {i+1}/{len(gap)} (성공 {n_ok} 실패 {n_fail})")
    time.sleep(0.08)

json.dump(out, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
P(f"완료: 성공 {n_ok} 실패 {n_fail} / 총 {len(gap)}")
print("DONE", n_ok, n_fail, len(gap))
