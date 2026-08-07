# -*- coding: utf-8 -*-
"""화성 파일럿 거래0건 단지 평형 보정 — 2차 시도.
건축HUB(getBrExposPubuseAreaInfo)는 대형단지에서 필지분할 때문에 세대 일부만
돌아오는 게 확인됨(1135세대 단지에서 12건만 옴). V-World 세대별 공시가격
(HousingPriceClient)이 같은 단지에서 1135/1135 정확히 일치하는 걸로 검증됨 —
이걸로 교체."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import sys, io, json, re, os, time, collections
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
load_dotenv(os.path.join(_REPO, "apartment_notice_analyzer", ".env"))
import requests
from modules.housing_price import HousingPriceClient, make_pnu

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
LOG = io.open(f"{SC}/fix_areas_v2_log.txt", "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush())

KAKAO = os.getenv("KAKAO_REST_API_KEY")
hp = HousingPriceClient()
P("V-World 설정 확인 시도")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)

targets = [c for c in data if c.get("est") == 1 and c.get("scope") != "gg"]
P(f"대상 {len(targets)}건")

def bcode(addr):
    try:
        r = requests.get("https://dapi.kakao.com/v2/local/search/address.json",
                          headers={"Authorization": f"KakaoAK {KAKAO}"},
                          params={"query": addr}, timeout=10)
        docs = r.json().get("documents") or []
        if docs:
            return docs[0]["address"]["b_code"]
    except Exception:
        pass
    return None

def cluster(vals, tol=0.6):
    vals = sorted(vals)
    clusters = []
    for v in vals:
        if clusters and v - clusters[-1][-1] <= tol:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    out = [{"a": round(sum(c) / len(c), 2), "n": len(c)} for c in clusters]
    return sorted(out, key=lambda x: -x["n"])

fixed = skipped = failed = 0
for i, c in enumerate(targets):
    bc = bcode(c["addr"])
    if not bc or len(bc) != 10:
        failed += 1
        P(f"  [실패:b_code] {c['nm']}")
        continue
    pnu = make_pnu(bc, c.get("jibun", ""))
    try:
        units = hp.fetch(pnu)
    except Exception as e:
        failed += 1
        P(f"  [실패:API] {c['nm']}: {e}")
        continue
    areas_raw = [u.area for u in units if u.area and u.area > 0]
    if len(areas_raw) < 5:
        skipped += 1
        P(f"  [스킵:공시가격자료부족({len(areas_raw)})] {c['nm']}")
        continue
    clustered = cluster(areas_raw)[:4]
    c["areas"] = [{"a": a["a"], "n": 0, "u": c.get("unit", 0)} for a in clustered]
    c["areaSrc"] = "vworld"
    c["areaN"] = len(areas_raw)
    fixed += 1
    if (i + 1) % 25 == 0:
        P(f"  진행 {i+1}/{len(targets)} (수정 {fixed} 스킵 {skipped} 실패 {failed})")
        json.dump(data, io.open(f"{SC}/areas_v2.partial.json", "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.1)

P(f"\n완료: 수정 {fixed} / 스킵 {skipped} / 실패 {failed} / 총 {len(targets)}")
new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P("data.js 저장 완료")
print("DONE", fixed, skipped, failed, len(targets))
