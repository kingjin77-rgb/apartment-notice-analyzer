# -*- coding: utf-8 -*-
"""data.js 용량 축소. 12번 병합 후 17MB가 되면서 브라우저 파싱·전송이 무거워졌다.

줄이는 항목(전부 index.html에서 실제로 안 쓰는 것만 — grep으로 확인):
  1. comps[].areas / fadj / maxfl 제거
     — 비준표(index.html 556행)와 사례표(772행)가 쓰는 건 nm·d·yr·n·unit 뿐.
       areas/fadj는 병합 시점에 부모 레코드의 unit/fadj/areas를 만드는 데만 쓰이고
       이후엔 죽은 데이터다.
  2. comps 상위 5개 -> 3개
     — 보고서가 "음영 3건의 ㎡단가 중위값을 기준단가로 채택"이라 명시. 4·5번째는
       화면에 나열만 되고 계산에 안 들어간다.
  3. lat/lng 소수 6자리 반올림(약 0.1m 해상도) — 지오코딩 원본이 15자리로 들어와 있었다.

사용법: python 13_slim_data.py"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re

DATA_JS = os.path.join(_REPO, "avm_app", "data.js")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)
before = len(arr)
print(f"기존 {len(data)}건 / {before/1048576:.2f}MB")

KEEP = ("nm", "d", "yr", "n", "unit")
for c in data:
    cs = c.get("comps")
    if cs:
        c["comps"] = [{k: x[k] for k in KEEP if k in x} for x in cs[:3]]
    for k in ("lat", "lng"):
        if isinstance(c.get(k), float):
            c[k] = round(c[k], 6)

new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
print(f"축소 후 {len(new_json)/1048576:.2f}MB ({(1-len(new_json)/before)*100:.1f}% 절감)")
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
print("DONE")
