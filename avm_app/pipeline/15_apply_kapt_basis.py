# -*- coding: utf-8 -*-
"""14번이 받은 K-APT 단지 기본정보를 data.js에 적용하고, 거래0건 단지의
비준(comps)을 '거리 단독'에서 '거리 + 연식 유사도 + 노후도 보정'으로 재구축한다.

왜 재구축하는가 — 12번 결과를 브라우저에서 검증하다 나온 실제 사례:
  경희궁의아침4단지(서울 종로구, 2004년 준공 주상복합)의 비교사례 1순위가
  1981년 준공 롯데미도파광화문빌딩이었다. 23년 차이 나는 사례를 아무 보정 없이
  기준단가로 썼다는 뜻이다. 원인은 두 가지가 겹친 것:
    (1) 12번의 사례선정이 반경 3km 거리 단독 기준이었다
    (2) 갭 단지는 yr(준공년)이 비어 있어 애초에 연식 비교가 불가능했다
  (2)를 14번이 해결했으므로 이제 (1)을 고칠 수 있다.

바뀌는 것:
  A. 준공년/세대수/최고층/복도구조/주차 — K-APT 실측으로 채움
  B. lh 플래그를 단지명 정규식 추정 -> codeSaleNm(공부상 분양/임대/혼합)으로 교체
     사용자가 반복 지적한 "임대아파트인데 시세가 뜬다"의 근본 원인이 정규식
     추정이었다. 공부상 구분이면 오판이 사라진다.
  C. 사례선정 = 거리 + 연식 유사도 종합점수, 연식 20년 이상 벌어진 사례는 후순위
  D. 기준단가 = 사례단가를 노후도 회귀로 대상 연식에 시점보정한 뒤 중위값
     (거래사례비교법의 '개별요인 비교' 중 경과연수 항목에 해당)

노후도 계수는 '인근지역 국지회귀'로 구한다. 시/도 단위로 먼저 돌려봤더니
서울이 b=-0.0021, r2=0.002로 나왔다 — 연식이 ㎡단가를 전혀 설명하지 못한다는
뜻이고, 강남 구축이 외곽 신축보다 비싼 것처럼 입지가 연식을 압도하기 때문이다
(전국 r2도 0.080에 불과). 시/도 계수를 그대로 쓰면 서울에서는 보정이 0이 되어
정작 고치려던 문제가 안 고쳐진다.

그래서 대상 단지 반경 3km 사례풀 안에서 회귀를 낸다. 좁은 구역 안에서는 입지가
거의 상수이므로 연식 효과가 분리되고, 이는 "사례는 인근지역에서 선정하고
개별요인으로 비교한다"는 감정평가 실무와도 일치한다. 표본이 부족하거나(8건 미만)
설명력이 없으면(r2<0.15) 시/도 -> 전국 순으로 폴백하고, 폴백까지 부실하면
보정을 아예 안 한다(계수 0). 외삽 폭주를 막기 위해 보정배율은 ±30%로 자른다.

사용법: python 15_apply_kapt_basis.py
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, math, statistics, collections

SC = os.path.join(_HERE, "data")
DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
BASIS = os.path.join(SC, "kapt_basis.json")
LOG = io.open(os.path.join(SC, "apply_kapt_basis_log.txt"), "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

basis = json.load(io.open(BASIS, encoding="utf-8"))
P(f"K-APT 기본정보 {len(basis)}건")

txt = io.open(DATA_JS, encoding="utf-8").read()
m = re.search(r"(const COMPLEX_DATA = )(\[.*\])(;)", txt, re.S)
prefix, arr, suffix = m.group(1), m.group(2), m.group(3)
data = json.loads(arr)
P(f"data.js {len(data)}건")

# ---------- A. 기본정보 적용 ----------
def sido_of(c):
    a = (c.get("addr") or "").strip()
    return a.split()[0] if a else ""

n_basis = n_lh_fix = 0
for c in data:
    b = basis.get(c.get("kaptCode") or "")
    if not b:
        continue
    n_basis += 1
    if b.get("yr"):
        c["yr"] = str(b["yr"])
    if b.get("units"):
        c["units"] = b["units"]          # 총세대수 (기존 'unit'은 ㎡단가라 이름 충돌 주의)
    if b.get("topFloor"):
        c["maxfl"] = b["topFloor"]
    for src, dst in (("hallType", "hallType"), ("parkingPerHh", "parkingPerHh"),
                     ("builder", "builder"), ("heatType", "heatType"),
                     ("subwayStation", "subwayStation"), ("eduFacility", "eduFacility"),
                     ("area60", "area60"), ("area85", "area85"),
                     ("area135", "area135"), ("area136", "area136")):
        if b.get(src):
            c[dst] = b[src]
    # B. 공부상 임대구분으로 lh 교체
    #    '혼합'과 '분양 및 임대 등'은 분양분 실거래가 실재하므로 순수 임대와
    #    같이 취급하면 안 된다. lh=1은 순수 임대에만 주고, 혼합은 mixed로 표시해
    #    화면에서 "임대 세대 포함"을 알리되 시세는 살린다.
    st = (b.get("saleType") or "").strip()
    if st:
        c["saleType"] = st
        pure_rental = (st == "임대")
        c["mixed"] = 1 if (not pure_rental and "임대" in st) else 0
        new_lh = 1 if pure_rental else 0
        if new_lh != c.get("lh", 0):
            n_lh_fix += 1
        c["lh"] = new_lh
P(f"기본정보 적용 {n_basis}건 / 임대구분 교정 {n_lh_fix}건")
P(f"  임대(공부상) 총 {sum(1 for c in data if c.get('lh'))}건")

# ---------- A-2. 물리적으로 불가능한 평형 삭제 ----------
# 12번은 인근 3개 단지의 면적을 그대로 대상 단지 areas로 복사했다. 감사 결과
# 대조가능 9,630곳에서 면적 엔트리의 26.1%가 K-APT가 '세대수 0'이라 명시한
# 구간에 배정돼 있었다(나인원한남은 전 세대 135㎡ 초과인데 84.89㎡가 배정됨).
# 감정가 = 단가 x 면적이므로 이건 오차가 아니라 다른 단지 물건을 대상물건으로
# 표시하는 것이다. K-APT는 버킷별 세대수만 주고 정확한 전용면적은 주지 않으므로,
# 여기서 할 수 있는 것은 '틀린 평형 삭제'이지 '맞는 평형 채우기'가 아니다.
def bucket(a):
    if a <= 60: return "area60"
    if a <= 85: return "area85"
    if a <= 135: return "area135"
    return "area136"

n_chk = n_drop = n_empty = 0
for c in data:
    b = basis.get(c.get("kaptCode") or "")
    if not b or not c.get("areas"):
        continue
    buckets = {k: b.get(k, 0) for k in ("area60", "area85", "area135", "area136")}
    if not sum(buckets.values()):
        continue          # 면적구성 자체가 없으면 판정 불가 — 손대지 않는다
    n_chk += 1
    keep = [a for a in c["areas"] if buckets.get(bucket(a["a"]), 0) > 0]
    n_drop += len(c["areas"]) - len(keep)
    c["areas"] = keep
    c["areaOk"] = 1 if keep else 0
    if not keep:
        n_empty += 1
P(f"\n평형 검증: 대조 {n_chk}건 / 불가능 평형 삭제 {n_drop}개 / 전부 탈락 {n_empty}건")

# ---------- 노후도 회귀 (시/도별) ----------
def fit(pts):
    """log(unit) = a + b*yr 단순회귀. (b, n, r2) 반환."""
    n = len(pts)
    if n < 30:
        return None
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if not sxx:
        return None
    b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
    a = my - b * mx
    sst = sum((p[1] - my) ** 2 for p in pts)
    ssr = sum((p[1] - (a + b * p[0])) ** 2 for p in pts)
    return b, n, (1 - ssr / sst if sst else 0)

anchors = [c for c in data if c.get("hasT") and c.get("unit") and str(c.get("yr", "")).isdigit()]
P(f"\n회귀 표본(실거래 보유·연식 확인) {len(anchors)}건")

by_sido = collections.defaultdict(list)
for c in anchors:
    y = int(c["yr"])
    if 1970 <= y <= 2026 and c["unit"] > 0:
        by_sido[sido_of(c)].append((y, math.log(c["unit"])))

MIN_R2 = 0.15          # 이 밑이면 연식이 단가를 설명 못 한다고 보고 폴백
MIN_LOCAL_N = 8        # 국지회귀 최소 표본
CAP = 0.30             # 보정배율 상한 ±30% (외삽 폭주 차단)

# 2026-08-11: 19번(홀드아웃 백테스트)·20번(파라미터 스윕)으로 실측 검증 완료.
# 실거래 보유 단지 3,000건을 "거래0건인 척" 가리고 인근만으로 맞춰본 결과다.
#   연식보정 OFF          MdAPE 11.35%
#   연식보정 ON           MdAPE 10.26%  (1.09%p 개선)
#   + 거리역가중(IDW)      MdAPE  9.99%
#   + 면적유사도 가중       MdAPE  9.38%  (기준선 대비 1.97%p 개선)
# 검증 없이 켜지 않는다는 원칙을 지킨 뒤, 측정으로 근거가 확인되어 켠다.
APPLY_AGE = True

# 아래 3개는 20번 스윕에서 실측으로 정한 값이다(임의 상수가 아니다).
K_COMPS = 3          # 3건이 최적. 5·7·10건으로 늘리면 오히려 나빠진다(10.68·11.08·11.45%)
YEAR_W = 10.0        # 거리 1km ≈ 연식 10년. 3·5년으로 연식을 더 중시하면 나빠진다
AREA_W = 0.5         # 면적 유사도 가중. 0 -> 10.26%, 0.5 -> 9.75%, 1.0 이상은 다시 나빠진다
MAXD = 2000          # 반경. 1.5~3km가 거의 동일하나 2km가 미세 우위 + 사례 확보량 균형

nat = fit([p for v in by_sido.values() for p in v])
NAT_COEF = nat[0] if nat and nat[2] >= MIN_R2 else 0.0
P(f"전국 계수 b={nat[0]:.5f} (연 {(math.exp(nat[0])-1)*100:+.2f}%) n={nat[1]} r2={nat[2]:.3f}"
  + ("" if NAT_COEF else "  -> r2 미달, 전국 폴백은 보정 안 함"))

COEF = {}
for s, pts in sorted(by_sido.items(), key=lambda x: -len(x[1])):
    f = fit(pts) if len(pts) >= 100 else None
    COEF[s] = f[0] if (f and f[2] >= MIN_R2) else NAT_COEF
    if f:
        P(f"  {s}: b={f[0]:.5f} (연 {(math.exp(f[0])-1)*100:+.2f}%) n={f[1]} r2={f[2]:.3f}"
          + ("" if f[2] >= MIN_R2 else "  -> r2 미달, 폴백"))

def target_area(c):
    """대표 전용면적(중위). 면적 유사도 가중에 쓴다."""
    ar = c.get("areas") or []
    return statistics.median([a["a"] for a in ar]) if ar else None

# ---------- C/D. 비준 재구축 ----------
R = 6371000.0
def hav(a1, o1, a2, o2):
    p = math.radians
    dφ = p(a2 - a1); dλ = p(o2 - o1)
    x = math.sin(dφ / 2) ** 2 + math.cos(p(a1)) * math.cos(p(a2)) * math.sin(dλ / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))

# 격자 인덱스(0.01도 ≈ 1.1km) — 전수 비교는 12,150 x 14,248 이라 너무 느리다
GRID = 0.01
grid = collections.defaultdict(list)
for a in anchors:
    grid[(int(a["lat"] / GRID), int(a["lng"] / GRID))].append(a)

targets = [c for c in data if not c.get("hasT") and c.get("lat") and c.get("lng")]
P(f"\n비준 대상(거래0건) {len(targets)}건")

stat = collections.Counter()
for c in targets:
    gi, gj = int(c["lat"] / GRID), int(c["lng"] / GRID)
    cand = []
    for di in range(-3, 4):
        for dj in range(-3, 4):
            for a in grid.get((gi + di, gj + dj), ()):
                d = hav(c["lat"], c["lng"], a["lat"], a["lng"])
                if d <= MAXD:
                    cand.append((d, a))
    if not cand:
        stat["사례없음"] += 1
        continue

    ty = int(c["yr"]) if str(c.get("yr", "")).isdigit() else None

    # 국지회귀: 반경 3km 사례풀 자체에서 연식계수를 낸다. 이 구역 안에서는
    # 입지가 거의 상수라 연식 효과가 분리된다. 부실하면 시/도 -> 전국 폴백.
    local = fit([(int(a["yr"]), math.log(a["unit"]))
                 for _, a in cand
                 if str(a.get("yr", "")).isdigit() and a["unit"] > 0])
    if local and len(cand) >= MIN_LOCAL_N and local[2] >= MIN_R2:
        coef, csrc = local[0], "local"
    else:
        coef = COEF.get(sido_of(c), NAT_COEF)
        csrc = "sido" if coef else "none"
    stat[f"계수_{csrc}"] += 1

    ta = target_area(c)

    def score(d, a):
        """거리·연식·면적 종합점수. 낮을수록 우수. 가중치는 20번 스윕 실측값."""
        s = d / 1000.0
        if ty is not None:
            dy = abs(int(a["yr"]) - ty)
            s += dy / YEAR_W
            if dy > 20:
                s += 2.0        # 20년 초과는 물적 유사성이 깨진다고 보고 강한 후순위
        if AREA_W and ta:
            aa = target_area(a)
            if aa:
                s += AREA_W * abs(aa - ta) / max(ta, 1)
        return s

    cand.sort(key=lambda x: score(x[0], x[1]))
    top = cand[:K_COMPS]

    # 사례단가를 대상 연식으로 시점보정(경과연수 개별요인)
    adj = []
    for d, a in top:
        u = a["unit"]
        if APPLY_AGE and ty is not None and coef and str(a.get("yr", "")).isdigit():
            f_age = math.exp(coef * (ty - int(a["yr"])))
            f_age = max(1 - CAP, min(1 + CAP, f_age))   # 외삽 폭주 차단
            u = u * f_age
        adj.append(u)
    # 거리역가중 평균. 20번 스윕에서 단순중위(10.26%)보다 IDW(9.99%)가 우수했다 —
    # 가까운 사례가 실제로 더 잘 맞는다는 뜻이고 감정평가 실무 감각과도 맞는다.
    wts = [1.0 / max(d, 50) ** 2 for d, _ in top]
    c["unit"] = round(sum(v * w for v, w in zip(adj, wts)) / sum(wts))

    c["comps"] = [{"nm": a["nm"], "d": round(d), "yr": a["yr"], "n": a["n"],
                   "unit": a["unit"], "adj": round(u)}
                  for (d, a), u in zip(top, adj)]
    c["ageCoef"] = round(coef, 5)
    c["ageSrc"] = csrc
    c["ageApplied"] = 1 if APPLY_AGE else 0

    fs = [[a["fadj"][i] for _, a in top if a.get("fadj") and a["fadj"][i] is not None] for i in range(4)]
    c["fadj"] = [round(statistics.median(f), 3) if f else None for f in fs]
    c["ageAdj"] = 1 if ty is not None else 0
    stat["보정적용" if ty is not None else "연식미상"] += 1

    dys = [abs(int(a["yr"]) - ty) for _, a in top] if ty is not None else []
    if dys:
        stat["사례연식차_20년초과"] += sum(1 for x in dys if x > 20)

P(f"비준 결과: {dict(stat)}")
P(f"  연식 보정 적용률 {stat['보정적용']}/{len(targets)} ({stat['보정적용']/max(len(targets),1)*100:.1f}%)")

new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
new_txt = txt[:m.start()] + prefix + new_json + suffix + txt[m.end():]
io.open(DATA_JS, "w", encoding="utf-8").write(new_txt)
P(f"저장 완료 {len(new_json)/1048576:.2f}MB")
print("DONE", n_basis, n_lh_fix, stat["보정적용"])
