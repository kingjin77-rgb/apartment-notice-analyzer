# -*- coding: utf-8 -*-
"""화성시 실거래 수집기간을 12개월에서 36개월로 확장.

2026-08-07 재확인: 어제 "MOLIT 할당량 소진"이라 판단했던 원인이 실은
LAWD_CD 41590이 화성시 행정구 개편(동탄구 신설)으로 폐지된 죽은 코드였던
것으로 밝혀짐 — 41597(동탄구)+41595(화성시 나머지)가 현재 코드.
강남구(11680)·부산 코드로는 정상 응답이 왔던 게 그 증거.
새로 실거래가 확인된 단지는 기존 proxied(est=1) 항목을 hasT=1로 승격시킨다."""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import io, json, os, re, time, statistics, collections
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
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
LOG = io.open(f"{SC}/widen_window_log.txt", "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush())

MOLIT = os.getenv("MOLIT_API_KEY") or os.getenv("DATA_GO_KR_KEY")
U = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"

YMS = []
y, m = 2023, 9
while (y, m) <= (2026, 8):
    YMS.append(f"{y}{m:02d}")
    m += 1
    if m > 12:
        y, m = y + 1, 1
P(f"수집 대상 {len(YMS)}개월: {YMS[0]}~{YMS[-1]}")

CODES = ["41597", "41595"]  # 동탄구 / 화성시 나머지(구 41590 폐지분 대체)
raw = []
for code in CODES:
 for ym in YMS:
    for page in range(1, 6):
        r = requests.get(U, params={"serviceKey": MOLIT, "LAWD_CD": code, "DEAL_YMD": ym,
                                     "numOfRows": 1000, "pageNo": page, "_type": "json"}, timeout=20)
        try:
            body = r.json()["response"]["body"]
        except Exception:
            break
        items = (body.get("items") or {}).get("item") or []
        if isinstance(items, dict):
            items = [items]
        if not items:
            break
        raw += items
        if len(raw) >= int(body.get("totalCount") or 0) or page * 1000 >= int(body.get("totalCount") or 1e9):
            pass
        if len(items) < 1000:
            break
    time.sleep(0.05)
P(f"원본 수집 {len(raw)}건")

def f(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None

clean = []
for it in raw:
    if str(it.get("cdealType") or "").strip() == "O":
        continue  # 계약해제
    if str(it.get("dealingGbn") or "").strip() == "직거래":
        continue
    amt = f(it.get("dealAmount"))
    area = f(it.get("excluUseAr"))
    floor = f(it.get("floor"))
    nm = str(it.get("aptNm") or "").strip()
    if not (amt and area and nm):
        continue
    clean.append({"nm": nm, "amt": amt * 10000, "area": area, "floor": int(floor or 0),
                  "yr": str(it.get("buildYear") or ""), "umd": str(it.get("umdNm") or "").strip(),
                  "jibun": str(it.get("jibun") or "").strip()})
P(f"정제 {len(clean)}건 (계약해제·직거래 제외)")

by_nm = collections.defaultdict(list)
for c in clean:
    by_nm[c["nm"]].append(c)
P(f"단지 수(이름기준) {len(by_nm)}")

def mad_filter(vals):
    if len(vals) < 4:
        return vals
    med = statistics.median(vals)
    mad = statistics.median([abs(v - med) for v in vals]) or 1
    return [v for v in vals if abs(v - med) / mad < 5]

FLOOR_BANDS = [(0, 0.18), (0.18, 0.35), (0.35, 0.62), (0.62, 1.01)]

agg = {}
for nm, deals in by_nm.items():
    if len(deals) < 3:
        continue
    unit_prices = [d["amt"] / d["area"] for d in deals]
    kept_idx = set(id(v) for v in mad_filter(unit_prices))
    kept = [d for d, up in zip(deals, unit_prices) if id(up) in kept_idx]
    if len(kept) < 3:
        kept = deals
    maxfl = max((d["floor"] for d in kept if d["floor"]), default=0)
    unit_med = statistics.median(d["amt"] / d["area"] for d in kept)
    by_area = collections.defaultdict(list)
    for d in kept:
        by_area[round(d["area"], 2)].append(d["amt"] / d["area"])
    areas = sorted(
        [{"a": a, "n": len(v), "u": round(statistics.median(v))} for a, v in by_area.items()],
        key=lambda x: -x["n"],
    )[:4]
    fadj = []
    if maxfl:
        for lo, hi in FLOOR_BANDS:
            band_ups = [d["amt"] / d["area"] for d in kept if lo <= (d["floor"] / maxfl) < hi]
            fadj.append(round(statistics.median(band_ups) / unit_med, 4) if band_ups else None)
    else:
        fadj = [1, 1, 1, 1]
    agg[nm] = {"n": len(kept), "unit": round(unit_med), "areas": areas, "fadj": fadj,
               "maxfl": int(maxfl), "yr": kept[0]["yr"], "umd": kept[0]["umd"], "jibun": kept[0]["jibun"]}

P(f"3건+ 실거래 확보 단지 {len(agg)}개 (기존 12개월 기준 48개 대비)")

txt = io.open(DATA_JS, encoding="utf-8").read()
mm = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = mm.group(1), mm.group(2), mm.group(3)
data = json.loads(arr)

upgraded = 0
for c in data:
    if c.get("scope") == "gg":
        continue
    a = agg.get(c["nm"])
    if a and not c.get("hasT"):
        c.update({"hasT": 1, "n": a["n"], "unit": a["unit"], "fadj": a["fadj"],
                  "areas": a["areas"], "maxfl": a["maxfl"] or c.get("maxfl", 0),
                  "yr": a["yr"] or c.get("yr", ""), "est": 0})
        c.pop("areaSrc", None)
        c.pop("comps", None)
        upgraded += 1

P(f"기존 proxied(est=1) -> 실거래(hasT=1) 승격 {upgraded}건")

new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:mm.start()] + prefix + new_json + suffix + txt[mm.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P("data.js 저장 완료")
print("DONE", len(agg), upgraded)
