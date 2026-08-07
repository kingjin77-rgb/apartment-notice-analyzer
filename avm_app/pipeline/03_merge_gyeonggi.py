# -*- coding: utf-8 -*-
"""지오코딩된 경기도 4,278개 단지(실거래 기반)를 기존 화성시 파일럿 604개에 병합.
화성시 파일럿과 이름 중복되는 건 파일럿 쪽(더 정제됨)을 우선하고 스킵한다.
경기도 전역 건은 전부 hasT=1(실거래 기반)이라 거래0건 비준(comps)은 없다 —
아직 안 만든 전국 POI 수집이 선행돼야 하는 부분이라 정직하게 비워둔다."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import json, re, io

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")

gg = json.load(io.open(f"{SC}/gyeonggi_geocoded.json", encoding="utf-8"))
gg = [g for g in gg if g.get("lat") and g.get("lng")]
print(f"지오코딩 성공 {len(gg)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
existing = json.loads(arr)
existing_names = {e["nm"] for e in existing}
print(f"기존(화성 파일럿) {len(existing)}건")

FUT = re.compile(r"예정|입주예정")
LH = re.compile(r"LH|엘에이치|행복주택|국민임대|공공임대|뉴스테이|영구임대")

added = []
skipped_dup = 0
for g in gg:
    nm = g["nm"]
    if nm in existing_names:
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
        "scope": "gg",  # 경기도 전역 확장분 — 화성 파일럿과 품질 다름을 구분하는 태그
    }
    added.append(rec)

print(f"중복 스킵 {skipped_dup}건, 신규 추가 {len(added)}건")
merged = existing + added
new_json = json.dumps(merged, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
print(f"총 {len(merged)}건 저장 완료")
