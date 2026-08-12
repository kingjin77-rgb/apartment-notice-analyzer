# -*- coding: utf-8 -*-
"""03번(경기도 전용 병합)을 일반화. 08번이 만든 {SLUG}_geocoded.json을 data.js에 병합.
사용법: python 09_merge_region.py 서울"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import json, re, io, sys

if len(sys.argv) < 2:
    print("사용법: python 09_merge_region.py <SLUG>  (예: 서울, 인천 — 08번이 만든 파일명과 맞출 것)")
    sys.exit(1)
SLUG = sys.argv[1]

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
SRC = f"{SC}/{SLUG}_geocoded.json"

gg = json.load(io.open(SRC, encoding="utf-8"))
gg = [g for g in gg if g.get("lat") and g.get("lng")]
print(f"지오코딩 성공 {len(gg)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
existing = json.loads(arr)
# 이름만으로 중복판정하면 동명이지만 실제로 다른 지역인 단지가 통째로
# 스킵된다(서울 확장 1차 때 442건 실손실로 확인됨) — 이름+동 조합으로 판정.
existing_keys = {(e["nm"], e.get("umd", "")) for e in existing}
print(f"기존 {len(existing)}건")

FUT = re.compile(r"예정|입주예정")
LH = re.compile(r"LH|엘에이치|행복주택|국민임대|공공임대|뉴스테이|영구임대")

added = []
skipped_dup = 0
for g in gg:
    nm = g["nm"]
    key = (nm, g.get("umd", ""))
    if key in existing_keys:
        skipped_dup += 1
        continue
    addr = g.get("geoAddr") or f"{g.get('sido','')} {g.get('umd','')} {g.get('jibun','')}"
    rec = {
        "nm": nm, "lat": g["lat"], "lng": g["lng"], "addr": addr, "road": "",
        "hasT": 1, "n": g.get("n", 0), "umd": g.get("umd", ""), "jibun": g.get("jibun", ""),
        "yr": g.get("yr", ""), "maxfl": g.get("maxfl", 0),
        "comps": [],
        "unit": g.get("unit", 0), "fadj": g.get("fadj", [1, 1, 1, 1]),
        "areas": [{"a": a["a"], "n": a.get("n", 0), "u": a.get("u", g.get("unit", 0))}
                  for a in g.get("areas", [])],
        "est": 0,
        "future": 1 if FUT.search(nm) else 0,
        "lh": 1 if LH.search(nm) else 0,
        "scope": "gg",
    }
    added.append(rec)
    existing_keys.add(key)

print(f"중복 스킵 {skipped_dup}건, 신규 추가 {len(added)}건")
merged = existing + added
new_json = json.dumps(merged, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
print(f"총 {len(merged)}건 저장 완료")
