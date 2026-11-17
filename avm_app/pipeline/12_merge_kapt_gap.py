# -*- coding: utf-8 -*-
"""11번이 지오코딩한 K-APT 갭(거래0건) 단지를 data.js에 병합.
00번(화성파일럿)의 인근비준 로직을 전국으로 일반화한 것:
반경 3km 내 실거래 보유(hasT=1) 단지 최대 5개를 comps로 저장,
상위 3개의 중앙값으로 unit/fadj/areas를 추정(est=1).
비준 불가(반경 내 앵커 없음) 단지는 지도에 안 올린다 — 추정 근거가 없으면
표기하지 않는다는 원칙(감정평가 필요로 표시되게 hasT=0 est=0은 제외).
사용법: python 12_merge_kapt_gap.py"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, math, statistics, collections

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
SRC = os.path.join(SC, "kapt_gap_geocoded.json")
LOG = io.open(os.path.join(SC, "merge_kapt_gap_log.txt"), "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

gap = json.load(io.open(SRC, encoding="utf-8"))
gap = [g for g in gap if g.get("lat") and g.get("lng")]
P(f"지오코딩 성공 갭 단지 {len(gap)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
existing = json.loads(arr)
P(f"기존 data.js {len(existing)}건")

SUFFIX = re.compile(r"(아파트|APT|apt)$")
BRANDPAD = re.compile(r"[\s\(\)\[\]·,\.:：\-_/]")
def norm(s):
    return SUFFIX.sub("", BRANDPAD.sub("", s or ""))

existing_keys = {(norm(e["nm"]), e.get("umd", "")) for e in existing}

# 실거래 앵커: hasT=1 단지만. 위경도 그리드 인덱스(0.03도 ≈ 3km)로 탐색 가속.
anchors = [e for e in existing if e.get("hasT")]
P(f"실거래 앵커 {len(anchors)}건")
GRID = 0.03
grid = collections.defaultdict(list)
for a in anchors:
    grid[(int(a["lat"] / GRID), int(a["lng"] / GRID))].append(a)

def hav(a, b, c, d):
    R = 6371000; p = math.radians
    x = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))

def near(lat, lng, radius=3000):
    gi, gj = int(lat / GRID), int(lng / GRID)
    cand = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for a in grid.get((gi + di, gj + dj), ()):
                d = hav(lat, lng, a["lat"], a["lng"])
                if d <= radius:
                    cand.append((d, a))
    cand.sort(key=lambda x: x[0])
    return cand[:5]

FUT = re.compile(r"예정|입주예정")
LH = re.compile(r"LH|엘에이치|행복주택|국민임대|공공임대|뉴스테이|영구임대")

added = []
n_dup = n_nocomp = 0
for g in gap:
    key = (norm(g["nm"]), g.get("umd", ""))
    if key in existing_keys:
        n_dup += 1
        continue
    top = near(g["lat"], g["lng"])
    if not top:
        n_nocomp += 1
        continue
    us = [a["unit"] for _, a in top[:3] if a.get("unit")]
    if not us:
        n_nocomp += 1
        continue
    unit = round(statistics.median(us))
    fs = []
    for i in range(4):
        vals = [a["fadj"][i] for _, a in top[:3]
                if a.get("fadj") and len(a["fadj"]) > i and a["fadj"][i] is not None]
        fs.append(round(statistics.median(vals), 3) if vals else None)
    ac = collections.Counter()
    for _, a in top[:3]:
        for ar in a.get("areas", []):
            ac[ar["a"]] += max(ar.get("n", 0), 1)
    areas = [{"a": a_, "n": 0, "u": unit} for a_, _ in ac.most_common(4)]
    maxfl = max((a.get("maxfl", 0) for _, a in top[:3]), default=0) or 15
    rec = {
        "nm": g["nm"], "lat": g["lat"], "lng": g["lng"],
        "addr": g.get("geoAddr", ""), "road": "",
        "hasT": 0, "n": 0, "umd": g.get("umd", ""), "jibun": "",
        "yr": "", "maxfl": maxfl,
        "comps": [{"nm": a["nm"], "d": round(d), "unit": a.get("unit", 0),
                   "yr": a.get("yr", ""), "n": a.get("n", 0), "maxfl": a.get("maxfl", 0),
                   "areas": [x["a"] for x in a.get("areas", [])[:4]],
                   "fadj": a.get("fadj", [1, 1, 1, 1])} for d, a in top],
        "unit": unit, "fadj": fs, "areas": areas,
        "est": 1,
        "future": 1 if FUT.search(g["nm"]) else 0,
        "lh": 1 if LH.search(g["nm"]) else 0,
        "kaptCode": g.get("kaptCode", ""),
        "scope": "kapt",  # K-APT 전수목록발 갭 단지 — 인근비준 기반 추정
    }
    added.append(rec)
    existing_keys.add(key)

P(f"중복 스킵 {n_dup} / 비준불가 제외 {n_nocomp} / 신규 추가 {len(added)}")
merged = existing + added
new_json = json.dumps(merged, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P(f"총 {len(merged)}건 저장 완료")
print("DONE", len(added), len(merged))
