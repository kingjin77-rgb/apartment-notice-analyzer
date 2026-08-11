# -*- coding: utf-8 -*-
"""결손 시군구 재수집 — 224개 중 데이터가 0건인 70개를 찾아 다시 받는다.

발견 경위: 감사 중 national_comps.json의 시군구 분포를 세어보니 224개 중 154개만
있었다. 결손 70개에는 노원구(202606 684건)·고양시덕양구(543)·대전서구(460)·
구리시(430)·구미시(413)·수성구(370)·부산진구(340) 등 대형 지역이 그대로 들어 있고,
합치면 2026년 6월 한 달 전국 거래 43,480건 중 9,901건(22.8%)이다.

원인: 01번의 fetch()가 3회 재시도 후 실패하면 빈 리스트를 반환하고 끝난다.
호출부는 그걸 "이 지역은 거래가 없다"와 구분하지 못한 채 넘어간다. 그래서
수집이 조용히 실패해도 아무 표시가 남지 않았다. 이번 스크립트는 반대로
"수집 0건"을 실패로 간주하고 로그와 결과파일에 남긴다.

이 결손 지역 단지들은 지금 지도에 없거나, K-APT 갭 경로로 들어와 인접 시군구
시세로 비준되고 있다(=자기 지역 실거래 근거 없음). 재수집 후 18번이 est=1
레코드를 실거래 기반 hasT=1로 승격시킨다.

사용법: python 17_collect_missing_sgg.py
        -> data/missing_sgg_geocoded.json
        그 다음 python 18_merge_upgrade.py
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, time, statistics, collections
import requests
from dotenv import dotenv_values

SC = os.path.join(_HERE, "data")
LOG = io.open(os.path.join(SC, "missing_sgg_log.txt"), "a", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

_ENV_CANDIDATES = [
    os.path.join(_REPO, "avm_app", "keys.env"),
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))),
                 "apartment_notice_analyzer", ".env"),
]
V = {}
for _p in _ENV_CANDIDATES:
    if os.path.exists(_p):
        V = dotenv_values(_p)
        if V.get("MOLIT_API_KEY") or V.get("DATA_GO_KR_KEY"):
            break
MOLIT = V.get("MOLIT_API_KEY") or V.get("DATA_GO_KR_KEY")
KAKAO = V.get("KAKAO_REST_API_KEY")
if not MOLIT or not KAKAO:
    P("MOLIT / KAKAO 키 없음 — 중단"); sys.exit(1)

U = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
YMS = [f"2025{m:02d}" for m in range(9, 13)] + [f"2026{m:02d}" for m in range(1, 9)]

regions = json.load(io.open(f"{SC}/regions_gyeonggi_224sgg.json", encoding="utf-8"))
nc = json.load(io.open(f"{SC}/national_comps.json", encoding="utf-8"))
have = collections.Counter(str(x.get("sgg")) for x in nc)
MISSING = [c for c in sorted(regions) if have.get(c, 0) == 0]
P(f"결손 시군구 {len(MISSING)}개 / 전체 {len(regions)}개")

DST = os.path.join(SC, "missing_sgg_geocoded.json")
STATE = os.path.join(SC, "missing_sgg_state.json")
done_codes, out = set(), []
if os.path.exists(STATE):
    st = json.load(io.open(STATE, encoding="utf-8"))
    done_codes = set(st.get("done", []))
    out = json.load(io.open(DST, encoding="utf-8")) if os.path.exists(DST) else []
    P(f"기존 진행분 {len(done_codes)}개 시군구 / 단지 {len(out)}건 — 이어서 진행")

def g(d, *ks):
    for k in ks:
        if k in d and d[k].strip():
            return d[k].strip()
    return ""

def mad_filter(vals):
    if len(vals) < 4:
        return vals
    med = statistics.median(vals)
    mad = statistics.median([abs(v - med) for v in vals]) or 1
    return [v for v in vals if abs(v - med) / (1.4826 * mad) < 3.5]

def geocode(q):
    for url in ("https://dapi.kakao.com/v2/local/search/address.json",
                "https://dapi.kakao.com/v2/local/search/keyword.json"):
        try:
            r = requests.get(url, headers={"Authorization": f"KakaoAK {KAKAO}"},
                             params={"query": q}, timeout=10)
            docs = r.json().get("documents") or []
            if docs:
                d = docs[0]
                return float(d["y"]), float(d["x"]), d.get("address_name") or d.get("road_address_name") or q
        except Exception:
            pass
    return None

still_empty = []
for ci, code in enumerate(MISSING):
    if code in done_codes:
        continue
    meta = regions[code]
    SIDO, SGGNM = meta["sido"], meta.get("sgg_nm", "")
    raw, http_fail = [], 0
    for ym in YMS:
        ok = False
        for t in range(4):
            try:
                r = requests.get(U, params={"serviceKey": MOLIT, "LAWD_CD": code, "DEAL_YMD": ym,
                                            "numOfRows": "999", "pageNo": "1"}, timeout=30)
                if r.status_code != 200:
                    time.sleep(1.0 * (t + 1)); continue
                # 01번은 여기서 에러본문도 그냥 넘겼다. 결과코드를 명시적으로 본다.
                rc = re.search(r"<resultCode>(\d+)</resultCode>", r.text)
                if rc and rc.group(1) not in ("00", "0"):
                    time.sleep(1.0 * (t + 1)); continue
                for it in re.findall(r"<item>(.*?)</item>", r.text, re.S):
                    d = {m_.group(1): m_.group(2) for m_ in re.finditer(r"<(\w+)>([^<]*)</\1>", it)}
                    d["_sgg"] = code
                    raw.append(d)
                ok = True
                break
            except Exception:
                time.sleep(1.0 * (t + 1))
        if not ok:
            http_fail += 1
        time.sleep(0.05)

    recs = []
    for t in raw:
        if g(t, "cdealType") == "O" or "직거래" in g(t, "dealingGbn"):
            continue
        try:
            area = float(g(t, "excluUseAr")); amt = float(g(t, "dealAmount").replace(",", "")) * 10000
            fl = int(g(t, "floor"))
        except Exception:
            continue
        if area <= 0 or amt <= 0 or fl <= 0:
            continue
        recs.append({"nm": g(t, "aptNm"), "umd": g(t, "umdNm"), "jibun": g(t, "jibun"),
                     "seq": g(t, "aptSeq"), "yr": g(t, "buildYear"), "area": area, "amt": amt,
                     "fl": fl, "unit": amt / area, "reg": bool(g(t, "registrationDate"))})

    by = collections.defaultdict(list)
    for r_ in recs:
        by[(r_["nm"], r_["umd"])].append(r_)

    comps = []
    for (nm, umd), rs in by.items():
        if len(rs) < 3:
            continue
        keep = set(mad_filter([x["unit"] for x in rs]))
        rs2 = [x for x in rs if x["unit"] in keep] or rs
        med = statistics.median([x["unit"] for x in rs2])
        maxfl = max(x["fl"] for x in rs2)
        band = collections.defaultdict(list)
        for x in rs2:
            rel = x["fl"] / max(maxfl, 1)
            b = 0 if rel < 0.18 else (1 if rel < 0.35 else (2 if rel < 0.62 else 3))
            band[b].append(x["unit"] / med)
        fadj = [round(statistics.median(band[b]), 3) if band.get(b) else None for b in range(4)]
        ac = collections.Counter(round(x["area"], 2) for x in rs2)
        areas = [{"a": a, "n": cnt,
                  "u": round(statistics.median([x["unit"] for x in rs2 if round(x["area"], 2) == a]))}
                 for a, cnt in ac.most_common(6)]
        comps.append({"nm": nm, "umd": umd, "jibun": rs2[0]["jibun"], "seq": rs2[0]["seq"],
                      "yr": rs2[0]["yr"], "sido": SIDO, "sgg": code,
                      "n": len(rs2), "nRaw": len(rs), "maxfl": maxfl, "unit": round(med),
                      "fadj": fadj, "areas": areas,
                      "regRate": round(sum(1 for x in rs2 if x["reg"]) / len(rs2), 3)})

    n_ok = 0
    for c in comps:
        geo = geocode(f"{SIDO} {c['umd']} {c['jibun']}")
        if geo:
            c["lat"], c["lng"], c["geoAddr"] = geo
            n_ok += 1
        time.sleep(0.08)

    out += comps
    done_codes.add(code)
    flag = ""
    if not comps:
        still_empty.append((code, SIDO, SGGNM, http_fail))
        flag = f"  <== 여전히 0건 (월단위 조회실패 {http_fail}/{len(YMS)})"
    P(f"  [{ci+1}/{len(MISSING)}] {code} {SIDO} {SGGNM}: 원본 {len(raw)} -> 단지 {len(comps)} (지오코딩 {n_ok}){flag}")

    json.dump(out, io.open(DST, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"done": sorted(done_codes)}, io.open(STATE, "w", encoding="utf-8"), ensure_ascii=False)

P(f"\n완료: 신규 단지 {len(out)}건 / 처리 시군구 {len(done_codes)}")
if still_empty:
    P(f"재수집 후에도 0건인 시군구 {len(still_empty)}개:")
    for c, s, nm, hf in still_empty:
        P(f"  {c} {s} {nm} (조회실패 {hf}개월)")
print("DONE", len(out), len(still_empty))
