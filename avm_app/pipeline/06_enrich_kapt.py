# -*- coding: utf-8 -*-
"""화성 파일럿 단지에 K-APT 실측(복도구조·주차대수)을 배치로 붙인다.
어제/오늘 확인된 대로 41590은 죽은 코드라 41597(동탄구)+41595(화성시 나머지)로 조회."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import sys, io, json, re, time
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
load_dotenv(os.path.join(_REPO, "apartment_notice_analyzer", ".env"))
from modules.kapt_complex import KaptClient

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
LOG = io.open(f"{SC}/enrich_kapt_log.txt", "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush())

client = KaptClient()
CODES = ["41597", "41595"]
kapt_list = []
for code in CODES:
    kapt_list += client.list_by_sigungu(code)
P(f"K-APT 단지목록 {len(kapt_list)}건 확보")

def norm(s):
    return re.sub(r"[\s()]|아파트$", "", s or "")

kapt_by_norm = {}
for k in kapt_list:
    kapt_by_norm.setdefault(norm(k.get("kaptName", "")), []).append(k)

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)

targets = [c for c in data if c.get("scope") != "gg"]
P(f"화성파일럿 대상 {len(targets)}건")

enriched = skipped = failed = 0
for i, c in enumerate(targets):
    key = norm(c["nm"])
    cands = kapt_by_norm.get(key)
    if not cands:
        cands = [k for nk, ks in kapt_by_norm.items() if nk and (nk in key or key in nk) for k in ks]
    if not cands:
        skipped += 1
        continue
    try:
        info = client.basis_info(cands[0]["kaptCode"], with_detail=True)
    except Exception as e:
        failed += 1
        P(f"  [실패] {c['nm']}: {e}")
        continue
    if not info:
        skipped += 1
        continue
    c["hallType"] = info.hall_type or ""
    c["parkingTotal"] = info.parking_total
    c["parkingPerHh"] = round(info.parking_per_household, 2) if info.households else None
    c["kaptEnriched"] = True
    enriched += 1
    if (i + 1) % 50 == 0:
        P(f"  진행 {i+1}/{len(targets)} (성공 {enriched} 스킵 {skipped} 실패 {failed})")
    time.sleep(0.05)

P(f"\n완료: 성공 {enriched} / 스킵(매칭실패) {skipped} / 실패(API) {failed} / 총 {len(targets)}")
new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P("data.js 저장 완료")
print("DONE", enriched, skipped, failed, len(targets))
