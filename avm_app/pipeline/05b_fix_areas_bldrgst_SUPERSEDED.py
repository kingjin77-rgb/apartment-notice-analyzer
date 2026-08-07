# -*- coding: utf-8 -*-
"""화성 파일럿 거래0건 단지(est=1)의 '인근단지 최빈면적' 임시방편을
건축물대장 실제 전유면적(getBrHsprcInfo)으로 교체."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import sys, io, json, re, os, time
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
load_dotenv(os.path.join(_REPO, "apartment_notice_analyzer", ".env"))
import requests
from modules.building_registry import BuildingRegistryClient

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
LOG = io.open(f"{SC}/fix_areas_log.txt", "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush())

KAKAO = os.getenv("KAKAO_REST_API_KEY")
brc = BuildingRegistryClient()
P("건축HUB 설정됨:", brc.is_configured)

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)

targets = [c for c in data if c.get("est") == 1 and c.get("scope") != "gg"]
P(f"대상(화성 파일럿 거래0건) {len(targets)}건")

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

def split_jibun(jibun):
    jibun = (jibun or "").strip()
    if "-" in jibun:
        a, b = jibun.split("-", 1)
        return a or "0", b or "0"
    return jibun or "0", "0"

fixed = skipped = failed = 0
for i, c in enumerate(targets):
    bc = bcode(c["addr"])
    if not bc or len(bc) != 10:
        failed += 1
        P(f"  [실패:b_code] {c['nm']}")
        continue
    sgg, bjd = bc[:5], bc[5:]
    bun, ji = split_jibun(c.get("jibun"))
    try:
        hs = brc.get_unit_areas(sgg, bjd, bun, ji)
    except Exception as e:
        failed += 1
        P(f"  [실패:API] {c['nm']}: {e}")
        continue
    areas = brc.summarize_unit_areas(hs)
    if not areas:
        skipped += 1
        P(f"  [스킵:대장자료없음] {c['nm']}")
        continue
    top4 = areas[:4]
    c["areas"] = [{"a": a["a"], "n": 0, "u": c.get("unit", 0)} for a in top4]
    c["areaSrc"] = "bldrgst"
    fixed += 1
    if (i + 1) % 25 == 0:
        P(f"  진행 {i+1}/{len(targets)} (수정 {fixed} 스킵 {skipped} 실패 {failed})")
        json.dump(data, io.open(DATA_JS.replace(".js", ".partial.json"), "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.12)

P(f"\n완료: 수정 {fixed} / 스킵(대장없음) {skipped} / 실패(주소매칭) {failed} / 총 {len(targets)}")

new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P("data.js 저장 완료")
print("DONE", fixed, skipped, failed, len(targets))
