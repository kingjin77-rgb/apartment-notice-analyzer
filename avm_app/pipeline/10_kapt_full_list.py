# -*- coding: utf-8 -*-
"""전국 224개 시군구 K-APT 단지 '전수' 목록(getSigunguAptList3) 수집.
01번(MOLIT 실거래)은 거래 있는 단지만 잡는다 — 거래0건 단지를 지도에 올리려면
이 전수 목록이 선행돼야 한다(README '다음에 이어서 할 것' 2번).
K-APT는 하루 트래픽 한도가 있어(2026-08-07 확인) 시군구별로 진행분을 저장,
중단돼도 이어서 돌 수 있게 한다.
사용법: python 10_kapt_full_list.py"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import sys, io, json, time
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
from modules.kapt_complex import KaptClient

SC = os.path.join(_HERE, "data")
REGIONS = os.path.join(SC, "regions_gyeonggi_224sgg.json")  # 실제로는 전국 224개 시군구 목록(이름만 경기파일럿때 명명)
DST = os.path.join(SC, "kapt_full_list.json")
LOG = io.open(os.path.join(SC, "kapt_full_list_log.txt"), "a", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

client = KaptClient()
if not client.is_configured:
    P("KAPT_API_KEY / MOLIT_API_KEY 없음 — 중단")
    sys.exit(1)

regions = json.load(io.open(REGIONS, encoding="utf-8"))
codes = sorted(regions)
P(f"대상 시군구 {len(codes)}개")

done = {}
if os.path.exists(DST):
    done = json.load(io.open(DST, encoding="utf-8"))
    P(f"기존 진행분 {len(done)}개 시군구 이어서 진행")

n_new = n_fail = 0
for i, code in enumerate(codes):
    if code in done:
        continue
    try:
        items = client.list_by_sigungu(code)
    except Exception as e:
        P(f"  [실패] {code}: {e}")
        n_fail += 1
        continue
    meta = regions[code]
    done[code] = {"sido": meta["sido"], "sgg_nm": meta.get("sgg_nm", ""), "items": items}
    n_new += 1
    P(f"  {code} {meta['sido']} {meta.get('sgg_nm','')}: {len(items)}건 ({i+1}/{len(codes)})")
    if n_new % 10 == 0:
        json.dump(done, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
    time.sleep(0.15)

json.dump(done, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
total_items = sum(len(v["items"]) for v in done.values())
P(f"\n완료: 시군구 {len(done)}/{len(codes)} (신규 {n_new} 실패 {n_fail}), 단지 합계(중복포함) {total_items}")
print("DONE", len(done), len(codes), total_items)
