# -*- coding: utf-8 -*-
"""거래0건 비준 추정의 정확도를 실측한다.

왜 필요한가 — 지금 앱은 10,446개 단지(est)에 대해 "인근 3km 실거래 앵커의 ㎡단가
중위값"으로 감정가를 낸다. 그런데 이 추정이 실제로 얼마나 맞는지 숫자가 하나도
없었다. 근거 없는 수치를 내지 말라는 원칙을 지키려면 추정 자체의 오차도 알아야 한다.
또 15번의 연식보정(APPLY_AGE)을 켤지 말지도 이 측정 없이는 정할 수 없다.

방법 — 홀드아웃 검증.
  실거래를 가진 단지(hasT=1)를 "거래0건인 척" 가리고, 자기 자신을 제외한 인근
  단지만으로 ㎡단가를 추정한 뒤 실제 ㎡단가와 대조한다. 거래0건 단지가 처하는
  상황을 그대로 재현하는 것이다.

  자기 자신뿐 아니라 **같은 지번의 다른 레코드도 제외**한다. 같은 단지가 이름
  변형으로 두 번 들어가 있으면(중복 2,634건 확인됨) 자기 답을 보고 맞히는 셈이라
  정확도가 실제보다 좋게 나온다.

측정 지표는 MdAPE(중위 절대백분율오차). 목표는 3%다.

사용법: python 19_backtest_comps.py
"""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
import io, json, re, math, statistics, collections, random

DATA_JS = os.path.join(_REPO, "avm_app", "data.js")
LOG = io.open(os.path.join(_HERE, "data", "backtest_log.txt"), "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

txt = io.open(DATA_JS, encoding="utf-8").read()
data = json.loads(re.search(r"const COMPLEX_DATA = (\[.*\]);", txt, re.S).group(1))

def sido_of(c):
    a = (c.get("addr") or "").strip()
    return a.split()[0] if a else ""

# 신뢰할 만한 정답만 검증 대상으로 삼는다. 거래 3~4건짜리는 정답 자체가 흔들려서
# 추정오차인지 정답오차인지 구분이 안 된다.
anchors = [c for c in data if c.get("hasT") and c.get("unit") and c.get("lat")
           and str(c.get("yr", "")).isdigit()]
truth = [c for c in anchors if (c.get("n") or 0) >= 8]
P(f"앵커(실거래 보유) {len(anchors)}건 / 정답 후보(거래 8건+) {len(truth)}건")

R = 6371000.0
def hav(a1, o1, a2, o2):
    p = math.radians
    dφ = p(a2 - a1); dλ = p(o2 - o1)
    x = math.sin(dφ/2)**2 + math.cos(p(a1))*math.cos(p(a2))*math.sin(dλ/2)**2
    return 2*R*math.asin(math.sqrt(x))

GRID = 0.01
grid = collections.defaultdict(list)
for a in anchors:
    grid[(int(a["lat"]/GRID), int(a["lng"]/GRID))].append(a)

def fit(pts):
    n = len(pts)
    if n < 8: return None
    mx = sum(p[0] for p in pts)/n; my = sum(p[1] for p in pts)/n
    sxx = sum((p[0]-mx)**2 for p in pts)
    if not sxx: return None
    b = sum((p[0]-mx)*(p[1]-my) for p in pts)/sxx
    a = my - b*mx
    sst = sum((p[1]-my)**2 for p in pts)
    ssr = sum((p[1]-(a+b*p[0]))**2 for p in pts)
    return b, n, (1-ssr/sst if sst else 0)

# 시/도 폴백 계수 (15번과 동일 규칙)
MIN_R2, MIN_LOCAL_N, CAP, MAXD = 0.15, 8, 0.30, 3000
by_sido = collections.defaultdict(list)
for c in anchors:
    y = int(c["yr"])
    if 1970 <= y <= 2026 and c["unit"] > 0:
        by_sido[sido_of(c)].append((y, math.log(c["unit"])))
nat = fit([p for v in by_sido.values() for p in v])
NAT = nat[0] if nat and nat[2] >= MIN_R2 else 0.0
COEF = {}
for s, pts in by_sido.items():
    f = fit(pts) if len(pts) >= 100 else None
    COEF[s] = f[0] if (f and f[2] >= MIN_R2) else NAT

random.seed(20260811)
sample = random.sample(truth, min(3000, len(truth)))
P(f"표본 {len(sample)}건 (재현 가능하도록 seed 고정)\n")

def estimate(c, apply_age):
    """c를 거래0건 취급하고 인근 앵커만으로 ㎡단가를 추정한다."""
    gi, gj = int(c["lat"]/GRID), int(c["lng"]/GRID)
    cand = []
    for di in range(-3, 4):
        for dj in range(-3, 4):
            for a in grid.get((gi+di, gj+dj), ()):
                # 자기 자신 + 같은 지번의 다른 레코드(중복 등록분) 제외
                if a is c: continue
                if a.get("umd") == c.get("umd") and a.get("jibun") == c.get("jibun"): continue
                if a.get("nm") == c.get("nm"): continue
                d = hav(c["lat"], c["lng"], a["lat"], a["lng"])
                if d <= MAXD: cand.append((d, a))
    if len(cand) < 3: return None, None
    ty = int(c["yr"])
    local = fit([(int(a["yr"]), math.log(a["unit"])) for _, a in cand
                 if str(a.get("yr","")).isdigit() and a["unit"] > 0])
    if local and len(cand) >= MIN_LOCAL_N and local[2] >= MIN_R2:
        coef, csrc = local[0], "local"
    else:
        coef, csrc = COEF.get(sido_of(c), NAT), "sido"

    def score(d, a):
        s = d/1000.0
        dy = abs(int(a["yr"]) - ty)
        s += dy/10.0
        if dy > 20: s += 2.0
        return s
    cand.sort(key=lambda x: score(x[0], x[1]))
    top = cand[:3]
    adj = []
    for d, a in top:
        u = a["unit"]
        if apply_age and coef:
            f_age = math.exp(coef*(ty - int(a["yr"])))
            u *= max(1-CAP, min(1+CAP, f_age))
        adj.append(u)
    return statistics.median(adj), csrc

def report(title, errs):
    if not errs:
        P(f"{title}: 표본 없음"); return None
    errs = sorted(errs)
    md = statistics.median(errs)
    within = lambda t: sum(1 for e in errs if e <= t)/len(errs)*100
    P(f"{title}")
    P(f"   MdAPE {md:.2f}%  |  평균 {statistics.mean(errs):.2f}%  |  n={len(errs)}")
    P(f"   ±3% 이내 {within(3):.1f}%  ±5% {within(5):.1f}%  ±10% {within(10):.1f}%  ±20% {within(20):.1f}%")
    return md

res = {}
for apply_age in (False, True):
    errs, bysrc = [], collections.defaultdict(list)
    for c in sample:
        est, src = estimate(c, apply_age)
        if est is None: continue
        e = abs(est - c["unit"])/c["unit"]*100
        errs.append(e); bysrc[src].append(e)
    lbl = "연식보정 ON " if apply_age else "연식보정 OFF"
    res[apply_age] = report(f"■ {lbl}", errs)
    for s in sorted(bysrc):
        P(f"     계수출처 {s}: MdAPE {statistics.median(bysrc[s]):.2f}% (n={len(bysrc[s])})")
    P("")

if res.get(False) is not None and res.get(True) is not None:
    d = res[False] - res[True]
    P(f"■ 판정: 연식보정을 켜면 MdAPE가 {res[False]:.2f}% -> {res[True]:.2f}% "
      f"({'개선' if d>0 else '악화'} {abs(d):.2f}%p)")
    P("   -> " + ("15번의 APPLY_AGE=True로 켤 근거가 된다."
                 if d > 0.3 else
                 "개선폭이 미미하거나 악화된다. 끈 상태를 유지할 것."))
print("DONE")
