# -*- coding: utf-8 -*-
"""data.js의 lh(임대추정) 플래그를 K-APT codeSaleNm(공식 분양/임대 구분)로 재검증.
이름 키워드 매칭(merge_data.py)의 한계를 실측 API로 교정한다."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))  # avm_app/pipeline -> avm_app -> repo root
import sys, io, json, re, time
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
load_dotenv(os.path.join(_REPO, "apartment_notice_analyzer", ".env"))
from modules.kapt_complex import KaptClient

SC = os.path.join(_HERE, "data")
out = io.open(f"{SC}/rental_verify_log.txt", "w", encoding="utf-8")
P = lambda *a: (print(*a, file=out), out.flush())

DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)
P(f"전체 {len(data)}건")

# 화성시 4개구 전부 시군구코드 41590 (동탄/병점/봉담/남양 모두 화성시 관할)
client = KaptClient()
sigungu = "41590"
all_kapt = client.list_by_sigungu(sigungu)
P(f"K-APT 화성시 단지목록 {len(all_kapt)}건 확보")

def norm(s):
    return re.sub(r"[\s()]|아파트$|아파트(?=\d|$)", "", s or "")

kapt_by_norm = {}
for k in all_kapt:
    kapt_by_norm.setdefault(norm(k.name), []).append(k)

targets = [c for c in data if c.get("est") == 1 and not c.get("lh") and not c.get("hasT")]
P(f"재검증 대상(자체거래0·키워드미탐지) {len(targets)}건")

changed = 0
checked = 0
unmatched = []
for c in targets:
    key = norm(c["nm"])
    cands = kapt_by_norm.get(key)
    if not cands:
        # 부분일치 폴백
        cands = [k for nk, ks in kapt_by_norm.items() if nk and (nk in key or key in nk) for k in ks]
    if not cands:
        unmatched.append(c["nm"])
        continue
    checked += 1
    try:
        info = client.basis_info(cands[0].kapt_code, with_detail=False)
    except Exception as e:
        P(f"  ERROR {c['nm']}: {e}")
        continue
    is_rental = info.is_rental if info else False
    if is_rental and not c.get("lh"):
        c["lh"] = 1
        c["lhVerified"] = "kapt"
        changed += 1
        P(f"  [수정] {c['nm']} -> lh=1 (K-APT 확인)")
    time.sleep(0.05)

P(f"\nK-APT 매칭 성공 {checked}건 / 미매칭 {len(unmatched)}건")
P(f"임대 재분류(lh 0->1) {changed}건")
P(f"\n[미매칭 목록 상위 30]")
for n in unmatched[:30]:
    P(" ", n)

new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P("\ndata.js 갱신 완료")
out.close()
print("done", changed, "changed of", checked, "checked,", len(unmatched), "unmatched")
