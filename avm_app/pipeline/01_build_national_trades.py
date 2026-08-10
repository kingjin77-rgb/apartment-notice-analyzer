# -*- coding: utf-8 -*-
"""전국 224개 시군구 실거래 수집·정제·단지 집계 (최근 12개월)."""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import io, json, time, statistics, collections
import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import dotenv_values

SC = os.path.join(_HERE, "data")
# 2026-08-10 수정: keys.env 절대경로가 박혀 있어 다른 머신/클론에서 죽었다.
# 다른 스크립트들과 같은 후보경로 폴백 방식으로 통일한다.
_KEY_CANDIDATES = [
    os.path.join(_REPO, "avm_app", "keys.env"),
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))),
                 "apartment_notice_analyzer", ".env"),
]
V = {}
for _p in _KEY_CANDIDATES:
    if os.path.exists(_p):
        V = dotenv_values(_p)
        if V.get("DATA_GO_KR_KEY") or V.get("MOLIT_API_KEY"):
            break
MOLIT = V.get("DATA_GO_KR_KEY") or V.get("MOLIT_API_KEY")
if not MOLIT:
    raise SystemExit("DATA_GO_KR_KEY / MOLIT_API_KEY 없음 — .env 또는 keys.env 확인")
U = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
log = io.open(f"{SC}/national_log.txt", "w", encoding="utf-8"); P = lambda *a: print(*a, file=log)

# 2026-08-10 수정: `regions.json`은 리포에 존재하지 않는다(이 스크립트를 지금
# 그대로 재실행하면 FileNotFoundError로 죽는다). 실제로 남아 있는 목록 파일은
# regions_gyeonggi_224sgg.json이다 — 이름은 경기 파일럿 때 붙었지만 내용은
# 전국 224개 시군구다. 제주 누락 원인을 추적하다 발견했다: 이 224개 목록에는
# 50110(제주시)·50130(서귀포시)이 멀쩡히 들어 있고 MOLIT·K-APT API도 정상인데
# national_comps.json에만 제주가 0건이다. 즉 당시 실행에 쓰인 목록 파일은
# 지금 없는 다른 파일이었고 거기에 제주가 빠져 있었던 것으로 보인다.
regions = json.load(io.open(f"{SC}/regions_gyeonggi_224sgg.json", encoding="utf-8"))
codes = sorted(regions)
P("regions:", len(codes))

YMS = [f"2025{m:02d}" for m in range(9, 13)] + [f"2026{m:02d}" for m in range(1, 9)]
P("months:", YMS)

def fetch(code_ym, tries=3):
    code, ym = code_ym
    for t in range(tries):
        try:
            r = requests.get(U, params={"serviceKey": MOLIT, "LAWD_CD": code, "DEAL_YMD": ym,
                                        "numOfRows": "999", "pageNo": "1"}, timeout=25)
            if r.status_code != 200: time.sleep(0.8*(t+1)); continue
            import re
            items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
            rows = []
            for it in items:
                d = {}
                for m in re.finditer(r"<(\w+)>([^<]*)</\1>", it):
                    d[m.group(1)] = m.group(2)
                d["_sgg"] = code; d["_sido"] = regions[code]["sido"]
                rows.append(d)
            return code, ym, rows
        except Exception:
            time.sleep(0.8*(t+1))
    return code, ym, []

jobs = [(c, y) for c in codes for y in YMS]
P("total jobs:", len(jobs))

all_rows = []
done = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    for code, ym, rows in ex.map(fetch, jobs):
        all_rows += rows
        done += 1
        if done % 200 == 0:
            P(f"  {done}/{len(jobs)}  rows={len(all_rows)}")

P(f"\n원본 수집: {len(all_rows)}건")

def g(d, *ks):
    for k in ks:
        if k in d and d[k].strip(): return d[k].strip()
    return ""

recs = []
stat = collections.Counter()
for t in all_rows:
    stat["total"] += 1
    if g(t, "cdealType") == "O": stat["cancel"] += 1; continue
    if "직거래" in g(t, "dealingGbn"): stat["direct"] += 1; continue
    try:
        area = float(g(t, "excluUseAr")); amt = float(g(t, "dealAmount").replace(",", "")) * 10000
        fl = int(g(t, "floor")); y = int(g(t, "dealYear")); m = int(g(t, "dealMonth"))
    except Exception:
        stat["parse"] += 1; continue
    if area <= 0 or amt <= 0 or fl <= 0: stat["parse"] += 1; continue
    recs.append({"nm": g(t, "aptNm"), "umd": g(t, "umdNm"), "jibun": g(t, "jibun"),
                "seq": g(t, "aptSeq"), "yr": g(t, "buildYear"), "area": area, "amt": amt,
                "fl": fl, "ym": y*100+m, "unit": amt/area, "reg": bool(g(t, "registrationDate")),
                "sgg": t["_sgg"], "sido": t["_sido"]})
P("정제:", len(recs), dict(stat))

by = collections.defaultdict(list)
for r in recs: by[(r["nm"], r["umd"], r["sgg"])].append(r)

def mad_filter(vals):
    if len(vals) < 4: return vals
    med = statistics.median(vals)
    dev = [abs(v-med) for v in vals]
    mad = statistics.median(dev) or 1
    return [v for v in vals if abs(v-med)/(1.4826*mad) < 3.5]

comps = []
for (nm, umd, sgg), rs in by.items():
    if len(rs) < 3: continue
    units = [r["unit"] for r in rs]
    keep = set(mad_filter(units))
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
    areas = []
    for a, cnt in ac.most_common(6):
        sub = [r["unit"] for r in rs2 if round(r["area"], 2) == a]
        areas.append({"a": a, "n": cnt, "u": round(statistics.median(sub))})
    comps.append({"nm": nm, "umd": umd, "jibun": rs2[0]["jibun"], "seq": rs2[0]["seq"],
                 "yr": rs2[0]["yr"], "sido": rs2[0]["sido"], "sgg": sgg,
                 "n": len(rs2), "nRaw": len(rs), "maxfl": maxfl, "unit": round(med_unit),
                 "fadj": fadj, "areas": areas,
                 "regRate": round(sum(1 for r in rs2 if r["reg"])/len(rs2), 3)})
comps.sort(key=lambda c: -c["n"])
P("\n단지 집계:", len(comps))

bysido = collections.Counter(c["sido"] for c in comps)
P("\n=== 시도별 단지 수 ===")
for s, n in bysido.most_common(): P(f"  {s}: {n}개")

# 전국 노후도 회귀 (지역 계수 참고용)
import math
pts = [(int(c["yr"]), math.log(c["unit"])) for c in comps if c["yr"] and c["unit"] > 0]
if len(pts) >= 30:
    n = len(pts); mx = sum(p[0] for p in pts)/n; my = sum(p[1] for p in pts)/n
    sxx = sum((p[0]-mx)**2 for p in pts); sxy = sum((p[0]-mx)*(p[1]-my) for p in pts)
    b = sxy/sxx if sxx else 0; a = my - b*mx
    ss_tot = sum((p[1]-my)**2 for p in pts); ss_res = sum((p[1]-(a+b*p[0]))**2 for p in pts)
    r2 = 1 - ss_res/ss_tot if ss_tot else 0
    P(f"\n전국 노후도 회귀: n={n} coef={b:.5f} r2={r2:.3f} base={round(mx)} 연간={( (2.718281828**b)-1)*100:.2f}%")
    json.dump({"baseYear": round(mx), "coef": round(b,5), "n": n, "r2": round(r2,3), "region": "전국"},
              io.open(f"{SC}/age_curve_national.json", "w", encoding="utf-8"), ensure_ascii=False)

json.dump(comps, io.open(f"{SC}/national_comps.json", "w", encoding="utf-8"), ensure_ascii=False)
log.close(); print("ok", len(comps))
