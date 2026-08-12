# -*- coding: utf-8 -*-
"""19번이 측정한 비준 추정 오차(MdAPE 11.35%)를 줄일 수 있는지 파라미터를 훑는다.

19번과 동일한 홀드아웃 표본·동일한 제외규칙을 쓰되, 사례 개수·거리와 연식의
가중비·집계방식·면적유사도 반영을 바꿔가며 MdAPE를 비교한다. 감정평가에서
'사례를 몇 건 어떻게 고르느냐'가 곧 방법론이므로, 이걸 실측으로 정하는 것이
임의 상수를 쓰는 것보다 방어 가능하다.

사용법: python 20_tune_comps.py
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
LOG = io.open(os.path.join(_HERE, "data", "tune_log.txt"), "w", encoding="utf-8")
P = lambda *a: (print(*a, file=LOG), LOG.flush(), print(*a))

txt = io.open(DATA_JS, encoding="utf-8").read()
data = json.loads(re.search(r"const COMPLEX_DATA = (\[.*\]);", txt, re.S).group(1))
sido_of = lambda c: ((c.get("addr") or "").strip().split() or [""])[0]

anchors = [c for c in data if c.get("hasT") and c.get("unit") and c.get("lat")
           and str(c.get("yr","")).isdigit()]
truth = [c for c in anchors if (c.get("n") or 0) >= 8]

R=6371000.0
def hav(a1,o1,a2,o2):
    p=math.radians; dφ=p(a2-a1); dλ=p(o2-o1)
    x=math.sin(dφ/2)**2+math.cos(p(a1))*math.cos(p(a2))*math.sin(dλ/2)**2
    return 2*R*math.asin(math.sqrt(x))
GRID=0.01
grid=collections.defaultdict(list)
for a in anchors: grid[(int(a["lat"]/GRID),int(a["lng"]/GRID))].append(a)

def fit(pts):
    n=len(pts)
    if n<8: return None
    mx=sum(p[0] for p in pts)/n; my=sum(p[1] for p in pts)/n
    sxx=sum((p[0]-mx)**2 for p in pts)
    if not sxx: return None
    b=sum((p[0]-mx)*(p[1]-my) for p in pts)/sxx
    a=my-b*mx
    sst=sum((p[1]-my)**2 for p in pts); ssr=sum((p[1]-(a+b*p[0]))**2 for p in pts)
    return b,n,(1-ssr/sst if sst else 0)

MIN_R2, CAP = 0.15, 0.30
by_sido=collections.defaultdict(list)
for c in anchors:
    y=int(c["yr"])
    if 1970<=y<=2026 and c["unit"]>0: by_sido[sido_of(c)].append((y,math.log(c["unit"])))
nat=fit([p for v in by_sido.values() for p in v])
NAT=nat[0] if nat and nat[2]>=MIN_R2 else 0.0
COEF={}
for s,pts in by_sido.items():
    f=fit(pts) if len(pts)>=100 else None
    COEF[s]=f[0] if (f and f[2]>=MIN_R2) else NAT

random.seed(20260811)
sample=random.sample(truth, min(3000,len(truth)))

def area_of(c):
    ar=c.get("areas") or []
    return statistics.median([a["a"] for a in ar]) if ar else None

# 후보 수집은 한 번만 하고 재사용 (파라미터 스윕이 빨라진다)
PRE=[]
for c in sample:
    gi,gj=int(c["lat"]/GRID),int(c["lng"]/GRID)
    cand=[]
    for di in range(-4,5):
        for dj in range(-4,5):
            for a in grid.get((gi+di,gj+dj),()):
                if a is c: continue
                if a.get("umd")==c.get("umd") and a.get("jibun")==c.get("jibun"): continue
                if a.get("nm")==c.get("nm"): continue
                d=hav(c["lat"],c["lng"],a["lat"],a["lng"])
                if d<=4000: cand.append((d,a))
    if len(cand)>=3: PRE.append((c,cand))
P(f"표본 {len(PRE)}건 (사례 3건 이상 확보)\n")

def run(k=3, yw=10.0, far_pen=2.0, maxd=3000, agg="median", aw=0.0, apply_age=True):
    errs=[]
    for c,cand0 in PRE:
        cand=[(d,a) for d,a in cand0 if d<=maxd]
        if len(cand)<3: continue
        ty=int(c["yr"]); ta=area_of(c)
        local=fit([(int(a["yr"]),math.log(a["unit"])) for _,a in cand
                   if str(a.get("yr","")).isdigit() and a["unit"]>0])
        coef = local[0] if (local and len(cand)>=8 and local[2]>=MIN_R2) else COEF.get(sido_of(c),NAT)
        def score(d,a):
            s=d/1000.0
            dy=abs(int(a["yr"])-ty); s+=dy/yw
            if dy>20: s+=far_pen
            if aw and ta:
                aa=area_of(a)
                if aa: s += aw*abs(aa-ta)/max(ta,1)
            return s
        cand.sort(key=lambda x:score(x[0],x[1]))
        top=cand[:k]
        vals=[]; wts=[]
        for d,a in top:
            u=a["unit"]
            if apply_age and coef:
                u*=max(1-CAP,min(1+CAP,math.exp(coef*(ty-int(a["yr"])))))
            vals.append(u); wts.append(1.0/max(d,50)**2)
        if agg=="median": est=statistics.median(vals)
        elif agg=="mean": est=statistics.mean(vals)
        else: est=sum(v*w for v,w in zip(vals,wts))/sum(wts)
        errs.append(abs(est-c["unit"])/c["unit"]*100)
    return statistics.median(errs), len(errs)

P("■ 기준선 (현재 15번 설정: k=3, 연식가중 10년/km, 3km, median)")
base,n=run(); P(f"   MdAPE {base:.2f}%  n={n}\n")

P("■ 사례 개수 k")
for k in (3,4,5,7,10):
    m,n=run(k=k); P(f"   k={k:<3} MdAPE {m:.2f}%  {'<-- 기준' if k==3 else ''}")
P("")
P("■ 연식 가중 (작을수록 연식을 더 중시)")
for yw in (3,5,10,20,1e9):
    m,n=run(yw=yw); P(f"   1km≈{yw if yw<1e8 else '∞'}년  MdAPE {m:.2f}%")
P("")
P("■ 반경")
for md in (1500,2000,3000,4000):
    m,n=run(maxd=md); P(f"   {md}m  MdAPE {m:.2f}%  n={n}")
P("")
P("■ 집계 방식")
for agg in ("median","mean","idw"):
    m,n=run(agg=agg); P(f"   {agg:<7} MdAPE {m:.2f}%")
P("")
P("■ 면적 유사도 가중")
for aw in (0,0.5,1.0,2.0):
    m,n=run(aw=aw); P(f"   aw={aw:<4} MdAPE {m:.2f}%")
P("")
P("■ 조합 탐색 (상위 후보)")
best=[]
for k in (3,5,7):
    for yw in (3,5,10):
        for md in (1500,2000,3000):
            for agg in ("median","idw"):
                m,n=run(k=k,yw=yw,maxd=md,agg=agg,aw=0.5)
                best.append((m,k,yw,md,agg,n))
best.sort()
for m,k,yw,md,agg,n in best[:8]:
    P(f"   MdAPE {m:.2f}%  k={k} yw={yw} r={md}m {agg} n={n}")
P(f"\n   기준선 {base:.2f}% -> 최적 {best[0][0]:.2f}% (개선 {base-best[0][0]:.2f}%p)")
print("DONE")
