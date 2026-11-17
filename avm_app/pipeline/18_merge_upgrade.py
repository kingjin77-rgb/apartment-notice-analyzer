# -*- coding: utf-8 -*-
"""17번이 재수집한 결손 시군구 단지를 data.js에 병합한다.

09번을 그대로 쓰면 안 되는 이유 — 09번은 (이름, 동)이 이미 있으면 무조건 스킵한다.
그런데 결손 시군구 단지들은 이미 K-APT 갭 경로(12번)로 들어와 있다. 그것들은
자기 지역 실거래가 없어서 인접 지역 시세로 비준된 est=1 레코드다. 09번 규칙대로면
"중복"으로 판정돼 새로 받은 진짜 실거래(hasT=1)가 통째로 버려지고, 추정치가
실측을 이긴 채로 남는다.

그래서 여기서는 키가 겹칠 때 스킵이 아니라 승격시킨다.
  기존 est=1(추정) + 신규 hasT=1(실거래)  -> 실거래로 교체. 비준 흔적(comps 등) 제거
  기존 hasT=1 + 신규 hasT=1               -> 기존 유지 (재수집분이 더 좁은 기간일 수 있음)
  키 없음                                  -> 신규 추가

기존 레코드의 K-APT 보강분(saleType·units·hallType·area60 등 15번 산출물)은
실거래로 덮어써도 살려둔다 — 출처가 다르고 서로 보완하는 정보다.

사용법: python 18_merge_upgrade.py
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
SRC = os.path.join(SC, "missing_sgg_geocoded.json")
LOG = io.open(os.path.join(SC, "merge_upgrade_log.txt"), "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

new = [g for g in json.load(io.open(SRC, encoding="utf-8")) if g.get("lat") and g.get("lng")]
P(f"재수집분(지오코딩 성공) {len(new)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)
P(f"기존 data.js {len(data)}건")

idx = {}
for i, e in enumerate(data):
    idx.setdefault((e["nm"], e.get("umd", "")), i)

FUT = re.compile(r"예정|입주예정")
# 15번이 채운 공부상 정보 — 실거래로 승격해도 유지한다
KEEP_FIELDS = ("saleType", "mixed", "units", "hallType", "parkingPerHh", "builder",
               "heatType", "subwayStation", "eduFacility",
               "area60", "area85", "area135", "area136", "kaptCode", "lh")

n_up = n_add = n_keep = 0
for g in new:
    key = (g["nm"], g.get("umd", ""))
    addr = g.get("geoAddr") or f"{g.get('sido','')} {g.get('umd','')} {g.get('jibun','')}"
    base = {
        "nm": g["nm"], "lat": round(g["lat"], 6), "lng": round(g["lng"], 6),
        "addr": addr, "road": "", "hasT": 1, "n": g.get("n", 0), "nRaw": g.get("nRaw", 0),
        "umd": g.get("umd", ""), "jibun": g.get("jibun", ""), "seq": g.get("seq", ""),
        "yr": g.get("yr", ""), "maxfl": g.get("maxfl", 0), "regRate": g.get("regRate"),
        "comps": [], "unit": g.get("unit", 0), "fadj": g.get("fadj", [1, 1, 1, 1]),
        "areas": [{"a": a["a"], "n": a.get("n", 0), "u": a.get("u", g.get("unit", 0))}
                  for a in g.get("areas", [])],
        "est": 0, "future": 1 if FUT.search(g["nm"]) else 0, "lh": 0, "scope": "resweep",
    }
    if key in idx:
        old = data[idx[key]]
        if old.get("hasT"):
            n_keep += 1
            continue
        # 추정 -> 실거래 승격. 공부상 보강분은 살린다.
        carried = {k: old[k] for k in KEEP_FIELDS if k in old}
        base.update(carried)
        # 평형은 실거래 실측이 인근 복사본을 이긴다. areaOk/areaSrc는 의미가 없어진다.
        for dead in ("areaOk", "areaSrc", "areaN", "ageCoef", "ageSrc", "ageApplied"):
            old.pop(dead, None)
        data[idx[key]] = base
        n_up += 1
    else:
        data.append(base)
        idx[key] = len(data) - 1
        n_add += 1

P(f"추정->실거래 승격 {n_up}건 / 신규 추가 {n_add}건 / 기존 실거래 유지 {n_keep}건")
P(f"총 {len(data)}건")
P(f"  hasT=1: {sum(1 for c in data if c.get('hasT'))}건")

new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P(f"저장 완료 {len(new_json)/1048576:.2f}MB")
print("DONE", n_up, n_add, n_keep)
