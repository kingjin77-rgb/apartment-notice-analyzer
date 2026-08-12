# -*- coding: utf-8 -*-
"""거래0건 단지의 전용면적을 건축물대장으로 실측 교체 — 배치판.

index.html의 클릭 시점 실측(liveAppraise)과 **같은 로직**이다. 화면에서 하나씩
누르는 것과 배치로 미리 채워두는 것이 서로 다른 답을 내면 안 되므로 규칙을 맞춘다.

21번(V-World)을 대체한다. V-World를 쓰던 이유는 README에 "건축HUB는 대형단지에서
12건만 반환된다(필지분할 추정)"고 적혀 있었기 때문인데, 실제로는 numOfRows를 크게
줘도 1페이지만 오는 **페이징 문제**였다. pageNo를 돌리면 totalCount 3,519건·
8,046건이 전부 정상 반환된다. 건축HUB가 더 나은 이유:
  - 브라우저에서 CORS가 열려 있어 클릭 시점 조회와 동일 코드를 쓸 수 있다
    (V-World는 CORS 차단이라 배치로만 가능하다)
  - mainPurpsCdNm으로 주거용만 정확히 거를 수 있다

핵심 두 가지:
1) 용도 필터 — 같은 지번에 아파트·오피스텔·근린생활시설이 섞인 주상복합이 많다.
   경희궁의아침4단지는 전유 425건 중 아파트가 120건뿐이고 나머지가 오피스텔 238·
   근생 37·사무소 14였다. 안 거르면 상가 12.7㎡가 아파트 평형이 된다.
2) K-APT 교차검증 — 대장 주거 전유 세대수를 K-APT 총세대수와 대조한다. 두 출처가
   독립인데 일치하면 이 지번이 대상 단지가 맞다는 강한 근거고, 50% 넘게 어긋나면
   다른 동을 잡았거나 단지가 여러 지번에 걸쳐 있다는 뜻이라 채택하지 않는다.

사용법: python 22_fix_areas_bldrgst.py   (중단되면 그냥 다시 실행 — 체크포인트 재개)
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, time, threading, collections
from concurrent.futures import ThreadPoolExecutor
import requests
from dotenv import dotenv_values

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
CKPT = os.path.join(SC, "areas_bldrgst.json")
LOG = io.open(os.path.join(SC, "fix_areas_bldrgst_log.txt"), "a", encoding="utf-8")
_lk = threading.Lock()
def P(*a):
    with _lk:
        print(*a, file=LOG); LOG.flush(); print(*a)

_ENV = [os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))),
                     "apartment_notice_analyzer", ".env")]
V = {}
for _p in _ENV:
    if os.path.exists(_p):
        V = dotenv_values(_p)
        if V.get("BLDRGST_API_KEY") or V.get("MOLIT_API_KEY"): break
BKEY = V.get("BLDRGST_API_KEY") or V.get("MOLIT_API_KEY")
KAKAO = V.get("KAKAO_REST_API_KEY")
if not BKEY or not KAKAO:
    P("키 없음 — 중단"); sys.exit(1)

HUB = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
_RATE_LK = threading.Lock()
_last_call = [0.0]
MIN_GAP = 0.45   # 실측 안전값(0.5s는 8/8 성공, 1.0s 간격도 앞선 부하가 안 식으면 실패)
def rate_limited_get(url, params, timeout):
    for attempt in range(3):   # 6->3: 페이지당 최대 대기를 줄여 한 단지에 발이 묶이는 걸 막는다
        with _RATE_LK:
            wait = MIN_GAP - (time.time() - _last_call[0])
            if wait > 0:
                time.sleep(wait)
            _last_call[0] = time.time()
        r = requests.get(url, params=params, timeout=timeout)
        if "LIMITED_NUMBER_OF_SERVICE_REQUESTS" in r.text[:300]:
            time.sleep(1.2 * (attempt + 1))   # 초당한도 초과 — 점점 길게 쉬고 재시도
            continue
        return r
    raise RuntimeError("초당 요청한도 재시도 초과")
HOUSING = re.compile(r"^(아파트|공동주택|연립주택|다세대주택|도시형생활주택)")
JIBUN = re.compile(r"(\d+)(?:-(\d+))?\s*$")

# kaptCode -> bjdCode. 카카오 지오코딩을 단지마다 한 번 더 때릴 필요가 없다.
bjd = {}
kf = os.path.join(SC, "kapt_full_list.json")
if os.path.exists(kf):
    for v in json.load(io.open(kf, encoding="utf-8")).values():
        for it in v["items"]:
            if it.get("kaptCode") and it.get("bjdCode"):
                bjd[it["kaptCode"]] = str(it["bjdCode"])
P(f"K-APT bjdCode 매핑 {len(bjd)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
data = json.loads(m.group(2))
targets = [c for c in data if not c.get("hasT") and c.get("addr")
           and c.get("areaSrc") not in ("vworld", "bldrgst", "bldrgst_live")]
P(f"대상(거래0건·미보정) {len(targets)}건")

done = {}
if os.path.exists(CKPT):
    done = json.load(io.open(CKPT, encoding="utf-8"))
    P(f"체크포인트 {len(done)}건 — 이어서 진행")

KEY = lambda c: f"{c.get('nm','')}|{c.get('umd','')}|{c.get('addr','')}"

def kakao_bcode(addr):
    try:
        r = requests.get("https://dapi.kakao.com/v2/local/search/address.json",
                         headers={"Authorization": f"KakaoAK {KAKAO}"},
                         params={"query": addr}, timeout=10)
        docs = r.json().get("documents") or []
        if docs and docs[0].get("address"):
            return docs[0]["address"].get("b_code")
    except Exception:
        pass
    return None

def cluster(vals, tol=0.6):
    vals = sorted(vals); cl = []
    for v in vals:
        if cl and v - cl[-1][-1] <= tol: cl[-1].append(v)
        else: cl.append([v])
    return sorted([{"a": round(sum(g)/len(g), 2), "n": len(g)} for g in cl],
                  key=lambda x: -x["n"])

stat = collections.Counter()
errs = collections.Counter()

def work(c):
    k = KEY(c)
    if done.get(k) is not None:
        # 성공(None이 아닌 값)만 캐시로 스킵한다. 실패는 done[k]=None으로 기록되는데,
        # 이걸 "처리 완료"로 오판해 재시도를 막으면 안 된다 — 실제로 첫 실행에서
        # API 순간부하로 11,591건이 KeyError('response')로 실패했는데, 원인이 풀린
        # 뒤 재실행해도 이 로직 때문에 전부 조용히 스킵될 뻔했다.
        stat["캐시"] += 1; return
    bc = bjd.get(c.get("kaptCode") or "") or kakao_bcode(c["addr"])
    if not bc or len(str(bc)) != 10:
        with _lk: done[k]=None; stat["실패_법정동코드"]+=1
        return
    mm = JIBUN.search(c["addr"].strip())
    if not mm:
        with _lk: done[k]=None; stat["실패_지번파싱"]+=1
        return
    bun, ji = mm.group(1).zfill(4), (mm.group(2) or "0").zfill(4)
    bc = str(bc)
    rows, total = [], None
    try:
        for page in range(1, 91):   # 최대 관측 totalCount 8,046건(81페이지) 커버. 60이면
                                     # 그보다 큰 단지가 페이지 중간에 잘려 K-APT 세대수
                                     # 검증에서 자동 기각된다(안전하지만 커버리지 손실).
            if page % 20 == 0:
                P(f"    ...{c['nm']} 페이지네이션 {page}p 진행중 (누적 {len(rows)}건)")
            r = rate_limited_get(HUB, {"serviceKey": BKEY, "sigunguCd": bc[:5],
                "bjdongCd": bc[5:], "bun": bun, "ji": ji, "numOfRows": "100",
                "pageNo": str(page), "_type": "json"}, 40)
            body = r.json()["response"]["body"]
            if total is None:
                total = int(body.get("totalCount") or 0)
                if not total: break
            it = (body.get("items") or {}).get("item") or []
            if isinstance(it, dict): it = [it]
            if not it: break
            rows += it
            if len(rows) >= total: break
    except Exception as e:
        with _lk:
            done[k] = None
            stat["실패_API"] += 1
            errs[type(e).__name__ + ": " + str(e)[:80]] += 1
        return
    if not rows:
        with _lk: done[k]=None; stat["대장자료없음"]+=1
        return

    expos = [x for x in rows if "전유" in str(x.get("exposPubuseGbCdNm") or "")]
    mix = collections.Counter(str(x.get("mainPurpsCdNm") or "(미상)").strip() for x in expos)
    housing = [x for x in expos if HOUSING.match(str(x.get("mainPurpsCdNm") or "").strip())]
    areas = [float(x["area"]) for x in housing if x.get("area") and float(x["area"]) > 0]
    if len(areas) < 5:
        with _lk: done[k]=None; stat["주거전유부족"]+=1
        return

    if c.get("units"):
        diff = abs(len(areas) - c["units"]) / c["units"]
        if diff > 0.5:
            with _lk: done[k]=None; stat["K-APT세대수불일치"]+=1
            return
        stat["검증일치" if diff <= 0.05 else "검증경고"] += 1

    with _lk:
        done[k] = {"areas": cluster(areas)[:6], "n": len(areas),
                   "mix": dict(mix.most_common(6))}
        stat["성공"] += 1

with ThreadPoolExecutor(max_workers=1) as ex:   # 레이트리미터가 직렬화하므로 1개로 충분   # 6이면 건축HUB가 자주 끊긴다
    for i, _ in enumerate(ex.map(work, targets)):
        if (i + 1) % 200 == 0:
            with _lk:
                snap = dict(done)
            json.dump(snap, io.open(CKPT, "w", encoding="utf-8"), ensure_ascii=False)
            P(f"  진행 {i+1}/{len(targets)}  {dict(stat)}")
            if errs:
                P(f"     오류 상위: {dict(collections.Counter(errs).most_common(3))}")

json.dump(done, io.open(CKPT, "w", encoding="utf-8"), ensure_ascii=False)
P(f"\n조회 완료: {dict(stat)}")

applied = 0
for c in data:
    if c.get("hasT"): continue
    r = done.get(KEY(c))
    if not r: continue
    c["areas"] = [{"a": a["a"], "n": 0, "u": c.get("unit", 0)} for a in r["areas"]]
    c["areaSrc"] = "bldrgst"
    c["areaN"] = r["n"]
    c["areaOk"] = 1
    applied += 1
P(f"data.js 반영 {applied}건")

nj = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
io.open(DATA_JS, "w", encoding="utf-8").write(txt[:m.start()] + m.group(1) + nj + m.group(3) + txt[m.end():])
P(f"저장 완료 {len(nj)/1048576:.2f}MB")
print("DONE", applied, dict(stat))
