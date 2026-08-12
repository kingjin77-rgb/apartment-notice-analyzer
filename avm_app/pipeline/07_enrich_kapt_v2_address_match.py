# -*- coding: utf-8 -*-
"""06_enrich_kapt.py 이름매칭 실패분(422/604)에 법정동코드(bjdCode) 기반
폴백 매칭을 추가. K-APT list_by_sigungu가 주는 bjdCode(10자리)를 카카오
지오코딩 b_code와 대조해 같은 법정동 안에서만 이름을 비교하면 오매칭이
훨씬 줄어든다."""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import sys, io, json, re, os as _os, time
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
_ENV_CANDIDATES = [
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))), "apartment_notice_analyzer", ".env"),
]
for _p in _ENV_CANDIDATES:
    if os.path.exists(_p):
        load_dotenv(_p)
        break
import requests
from modules.kapt_complex import KaptClient

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
LOG = io.open(f"{SC}/enrich_kapt_v2_log.txt", "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush())

KAKAO = _os.getenv("KAKAO_REST_API_KEY")
client = KaptClient()
CODES = ["41597", "41595"]
kapt_list = []
for code in CODES:
    for attempt in range(5):
        rows = client.list_by_sigungu(code)
        if rows:
            kapt_list += rows
            break
        P(f"  [{code}] 목록 0건 — 재시도 {attempt+1}/5")
        time.sleep(3)
P(f"K-APT 단지목록 {len(kapt_list)}건")
if not kapt_list:
    P("치명적: K-APT 목록을 5회 재시도해도 못 가져옴 — 중단")
    print("DONE 0 0 0 0 (kapt list empty after retries)")
    raise SystemExit(1)

by_bjd = {}
for k in kapt_list:
    by_bjd.setdefault(k.get("bjdCode", ""), []).append(k)

def norm(s):
    return re.sub(r"[\s()]|아파트$|\d+단지$|\d+차$", "", s or "")

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

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)

targets = [c for c in data if c.get("scope") != "gg" and not c.get("kaptEnriched")]
P(f"이름매칭 실패분(재시도 대상) {len(targets)}건")

enriched = skipped = failed = 0
for i, c in enumerate(targets):
    bjd = bcode(c["addr"])
    cands = by_bjd.get(bjd) if bjd else None
    if not cands:
        skipped += 1
        continue
    if len(cands) == 1:
        pick = cands[0]
    else:
        key = norm(c["nm"])
        scored = sorted(cands, key=lambda k: -len(set(norm(k.get("kaptName", ""))) & set(key)))
        pick = scored[0]
    try:
        info = client.basis_info(pick["kaptCode"], with_detail=True)
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
    c["kaptMatchedBy"] = "bjdCode" if len(cands) == 1 else "bjdCode+name"
    c["kaptMatchedName"] = pick.get("kaptName", "")
    enriched += 1
    if (i + 1) % 50 == 0:
        P(f"  진행 {i+1}/{len(targets)} (성공 {enriched} 스킵 {skipped} 실패 {failed})")
    time.sleep(0.08)

P(f"\n2차 완료: 성공 {enriched} / 스킵(동 못찾음) {skipped} / 실패(API) {failed} / 총 {len(targets)}")
new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P("data.js 저장 완료")
print("DONE", enriched, skipped, failed, len(targets))
