# -*- coding: utf-8 -*-
"""거래0건 단지의 전용면적을 V-World 세대별 공시가격으로 실측 교체 — 전국판.

왜 — 19번 백테스트로 비준 추정 오차가 MdAPE 9.38%로 측정됐고, 파라미터 조정으로는
여기가 한계였다. 남은 오차의 큰 부분이 "전용면적을 인근 단지에서 빌려온다"는 데서
온다고 본다. 지금 거래0건 단지의 areas는 12번이 인근 3개 단지 면적을 그대로 복사한
값이고, 15번이 K-APT 면적구성으로 불가능한 것 11,963개를 지웠을 뿐 맞는 값을 채운
것이 아니다. 감정가 = 단가 × 면적이므로 면적이 틀리면 단가가 맞아도 결과가 틀린다.

방법 — 05번(화성 파일럿)을 전국으로 일반화. V-World 세대별 공시가격은 같은 단지에서
1,135/1,135 정확히 일치하는 것이 검증돼 있다(건축HUB는 대형단지에서 12건만 반환).

05번 대비 바뀐 점:
  - b_code를 K-APT bjdCode에서 먼저 찾는다. 카카오 지오코딩을 단지마다 한 번씩
    더 때릴 필요가 없고 공부상 코드라 더 정확하다. 없을 때만 카카오로 폴백.
  - 지번을 addr 문자열 끝에서 파싱한다(K-APT 목록에는 지번이 없다).
  - 체크포인트를 읽어서 재개한다. 05번은 쓰기만 하고 읽지 않아 재개가 안 됐다.
  - 병렬 6스레드.

사용법: python 21_fix_areas_national.py   (중단되면 그냥 다시 실행)
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import sys, io, json, re, time, threading, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import load_dotenv
_ENV_CANDIDATES = [
    os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_REPO))), "apartment_notice_analyzer", ".env"),
]
for _p in _ENV_CANDIDATES:
    if os.path.exists(_p):
        load_dotenv(_p); break
import requests
from modules.housing_price import HousingPriceClient, make_pnu

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
CKPT = os.path.join(SC, "areas_vworld_national.json")
LOG = io.open(os.path.join(SC, "fix_areas_national_log.txt"), "a", encoding="utf-8")
_lk = threading.Lock()
def P(*a):
    with _lk:
        print(*a, file=LOG); LOG.flush(); print(*a)

KAKAO = os.getenv("KAKAO_REST_API_KEY")
hp = HousingPriceClient()

# kaptCode -> bjdCode (10자리 법정동코드)
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

targets = [c for c in data
           if not c.get("hasT") and c.get("addr") and c.get("areaSrc") != "vworld"]
P(f"대상(거래0건·미보정) {len(targets)}건")

done = {}
if os.path.exists(CKPT):
    done = json.load(io.open(CKPT, encoding="utf-8"))
    P(f"체크포인트 {len(done)}건 — 이어서 진행")

JIBUN = re.compile(r"(\d+)(?:-(\d+))?\s*$")
def parse_jibun(addr):
    """주소 끝의 지번을 본번/부번으로 쪼갠다. '내수동 73' -> (73,0), '월계동 943-2' -> (943,2)"""
    mm = JIBUN.search((addr or "").strip())
    if not mm:
        return None, None
    return mm.group(1), (mm.group(2) or "0")

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
    """±0.6㎡ 안은 같은 타입으로 묶는다. 안 묶으면 84.97/84.98이 다른 평형이 된다."""
    vals = sorted(vals)
    cl = []
    for v in vals:
        if cl and v - cl[-1][-1] <= tol:
            cl[-1].append(v)
        else:
            cl.append([v])
    return sorted([{"a": round(sum(c)/len(c), 2), "n": len(c)} for c in cl],
                  key=lambda x: -x["n"])

KEY = lambda c: f"{c.get('nm','')}|{c.get('umd','')}|{c.get('jibun','')}|{c.get('addr','')}"
stat = collections.Counter()

def work(c):
    k = KEY(c)
    if k in done:
        stat["캐시"] += 1
        return
    bc = bjd.get(c.get("kaptCode") or "") or kakao_bcode(c["addr"])
    if not bc or len(str(bc)) != 10:
        done[k] = None; stat["실패_법정동코드"] += 1
        return
    bun, ji = parse_jibun(c["addr"])
    if not bun:
        done[k] = None; stat["실패_지번파싱"] += 1
        return
    try:
        units = hp.fetch(make_pnu(str(bc), bun, ji))
    except Exception:
        done[k] = None; stat["실패_API"] += 1
        return
    areas = [u.area for u in units if u.area and u.area > 0]
    if len(areas) < 5:
        done[k] = None; stat["자료부족"] += 1
        return
    done[k] = {"areas": cluster(areas)[:4], "n": len(areas)}
    stat["성공"] += 1

with ThreadPoolExecutor(max_workers=6) as ex:
    for i, _ in enumerate(ex.map(work, targets)):
        if (i + 1) % 300 == 0:
            with _lk:
                json.dump(done, io.open(CKPT, "w", encoding="utf-8"), ensure_ascii=False)
            P(f"  진행 {i+1}/{len(targets)}  {dict(stat)}")

json.dump(done, io.open(CKPT, "w", encoding="utf-8"), ensure_ascii=False)
P(f"\n조회 완료: {dict(stat)}")

# ---------- 반영 ----------
applied = 0
for c in data:
    if c.get("hasT"):
        continue
    r = done.get(KEY(c))
    if not r:
        continue
    c["areas"] = [{"a": a["a"], "n": 0, "u": c.get("unit", 0)} for a in r["areas"]]
    c["areaSrc"] = "vworld"
    c["areaN"] = r["n"]
    c["areaOk"] = 1          # 실측이므로 K-APT 구간 검증 결과를 덮는다
    applied += 1
P(f"data.js 반영 {applied}건")

nj = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
io.open(DATA_JS, "w", encoding="utf-8").write(txt[:m.start()] + m.group(1) + nj + m.group(3) + txt[m.end():])
P(f"저장 완료 {len(nj)/1048576:.2f}MB")
print("DONE", applied, dict(stat))
