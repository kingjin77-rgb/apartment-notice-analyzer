# -*- coding: utf-8 -*-
"""제주 누락분 복구 — 수집·집계·지오코딩까지 한 번에. 출력은 08번과 같은 형식이라
그대로 `python 09_merge_region.py 제주`로 병합하면 된다.

원인 규명(README의 기존 추정은 틀렸다):
  README에는 "01번이 처음부터 제주를 수집 안 했다(원인 미확인, 아마 LAWD_CD
  목록에 제주가 빠졌을 것)"고 적혀 있었다. 실제로 확인해보니
    - regions_gyeonggi_224sgg.json 에는 50110(제주시)·50130(서귀포시)이 있다
    - MOLIT API도 정상이다 (202606 기준 제주시 127건 / 서귀포 45건 응답)
    - K-APT 단지목록도 정상이다 (50110: 129개, 50130: 58개)
  그런데 01번이 읽는 파일명은 `data/regions.json`인데 그 파일은 존재하지 않는다.
  즉 01번이 당시 실제로 읽은 목록 파일은 지금 리포에 없고, 제주가 포함된
  224개 목록(regions_gyeonggi_224sgg.json)은 그보다 나중에 만들어진 산출물이다.
  01번을 지금 그대로 재실행하면 FileNotFoundError로 죽는다 — 파일명도 함께 고쳤다.

수집기간은 01번과 동일하게 2025-09 ~ 2026-08(12개월)로 맞춘다.
사용법: python 16_collect_jeju.py  그 다음  python 09_merge_region.py 제주
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, time, math, statistics, collections
import requests
from dotenv import dotenv_values

SC = os.path.join(_HERE, "data")
LOG = io.open(os.path.join(SC, "jeju_log.txt"), "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

_ENV_CANDIDATES = [
    os.path.join(_REPO, "avm_app", "keys.env"),
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))),
                 "apartment_notice_analyzer", ".env"),
]
V = {}
for _p in _ENV_CANDIDATES:
    if os.path.exists(_p):
        V = dotenv_values(_p)
        if V.get("MOLIT_API_KEY") or V.get("DATA_GO_KR_KEY"):
            break
MOLIT = V.get("MOLIT_API_KEY") or V.get("DATA_GO_KR_KEY")
KAKAO = V.get("KAKAO_REST_API_KEY")
if not MOLIT or not KAKAO:
    P("MOLIT / KAKAO 키 없음 — 중단")
    sys.exit(1)

U = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
CODES = {"50110": "제주시", "50130": "서귀포시"}
SIDO = "제주특별자치도"
YMS = [f"2025{m:02d}" for m in range(9, 13)] + [f"2026{m:02d}" for m in range(1, 9)]

# ---------- 수집 ----------
raw = []
for code in CODES:
    for ym in YMS:
        got = 0
        for t in range(3):
            try:
                r = requests.get(U, params={"serviceKey": MOLIT, "LAWD_CD": code,
                                            "DEAL_YMD": ym, "numOfRows": "999", "pageNo": "1"}, timeout=25)
                if r.status_code != 200:
                    time.sleep(0.8 * (t + 1)); continue
                for it in re.findall(r"<item>(.*?)</item>", r.text, re.S):
                    d = {m_.group(1): m_.group(2) for m_ in re.finditer(r"<(\w+)>([^<]*)</\1>", it)}
                    d["_sgg"] = code
                    raw.append(d)
                    got += 1
                break
            except Exception:
                time.sleep(0.8 * (t + 1))
        P(f"  {CODES[code]} {ym}: {got}건")
        time.sleep(0.05)
P(f"원본 수집 {len(raw)}건")

def g(d, *ks):
    for k in ks:
        if k in d and d[k].strip():
            return d[k].strip()
    return ""

recs = []
drop = collections.Counter()
for t in raw:
    if g(t, "cdealType") == "O":
        drop["계약해제"] += 1; continue
    if "직거래" in g(t, "dealingGbn"):
        drop["직거래"] += 1; continue
    try:
        area = float(g(t, "excluUseAr")); amt = float(g(t, "dealAmount").replace(",", "")) * 10000
        fl = int(g(t, "floor"))
    except Exception:
        drop["파싱"] += 1; continue
    if area <= 0 or amt <= 0 or fl <= 0:
        drop["파싱"] += 1; continue
    recs.append({"nm": g(t, "aptNm"), "umd": g(t, "umdNm"), "jibun": g(t, "jibun"),
                 "seq": g(t, "aptSeq"), "yr": g(t, "buildYear"), "area": area, "amt": amt,
                 "fl": fl, "unit": amt / area, "reg": bool(g(t, "registrationDate")),
                 "sgg": t["_sgg"], "sido": SIDO})
P(f"정제 {len(recs)}건 (제외 {dict(drop)})")

# ---------- 집계 (01번과 동일 로직) ----------
def mad_filter(vals):
    if len(vals) < 4:
        return vals
    med = statistics.median(vals)
    mad = statistics.median([abs(v - med) for v in vals]) or 1
    return [v for v in vals if abs(v - med) / (1.4826 * mad) < 3.5]

by = collections.defaultdict(list)
for r in recs:
    by[(r["nm"], r["umd"], r["sgg"])].append(r)

comps = []
for (nm, umd, sgg), rs in by.items():
    if len(rs) < 3:
        continue
    keep = set(mad_filter([r["unit"] for r in rs]))
    rs2 = [r for r in rs if r["unit"] in keep] or rs
    med_unit = statistics.median([r["unit"] for r in rs2])
    maxfl = max(r["fl"] for r in rs2)
    band = collections.defaultdict(list)
    for r in rs2:
        rel = r["fl"] / max(maxfl, 1)
        b = 0 if rel < 0.18 else (1 if rel < 0.35 else (2 if rel < 0.62 else 3))
        band[b].append(r["unit"] / med_unit)
    fadj = [round(statistics.median(band[b]), 3) if band.get(b) else None for b in range(4)]
    ac = collections.Counter(round(r["area"], 2) for r in rs2)
    areas = [{"a": a, "n": cnt,
              "u": round(statistics.median([r["unit"] for r in rs2 if round(r["area"], 2) == a]))}
             for a, cnt in ac.most_common(6)]
    comps.append({"nm": nm, "umd": umd, "jibun": rs2[0]["jibun"], "seq": rs2[0]["seq"],
                  "yr": rs2[0]["yr"], "sido": SIDO, "sgg": sgg,
                  "n": len(rs2), "nRaw": len(rs), "maxfl": maxfl, "unit": round(med_unit),
                  "fadj": fadj, "areas": areas,
                  "regRate": round(sum(1 for r in rs2 if r["reg"]) / len(rs2), 3)})
P(f"3건+ 확보 단지 {len(comps)}개")

# ---------- 지오코딩 (08번과 동일) ----------
def geocode(query):
    for url in ("https://dapi.kakao.com/v2/local/search/address.json",
                "https://dapi.kakao.com/v2/local/search/keyword.json"):
        try:
            r = requests.get(url, headers={"Authorization": f"KakaoAK {KAKAO}"},
                             params={"query": query}, timeout=10)
            docs = r.json().get("documents") or []
            if docs:
                d = docs[0]
                return float(d["y"]), float(d["x"]), d.get("address_name") or d.get("road_address_name") or query
        except Exception:
            pass
    return None

n_ok = n_fail = 0
for c in comps:
    geo = geocode(f"{SIDO} {c['umd']} {c['jibun']}")
    if geo:
        c["lat"], c["lng"], c["geoAddr"] = geo
        n_ok += 1
    else:
        n_fail += 1
    time.sleep(0.08)
P(f"지오코딩 성공 {n_ok} 실패 {n_fail}")

DST = os.path.join(SC, "제주_geocoded.json")
json.dump(comps, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
P(f"저장: {DST}")
P("다음: python 09_merge_region.py 제주")
print("DONE", len(comps), n_ok, n_fail)
