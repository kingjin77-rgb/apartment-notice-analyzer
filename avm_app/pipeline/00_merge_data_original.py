# -*- coding: utf-8 -*-
"""POI 단지(거래0건 포함) + 실거래 통계를 병합해 앱용 data.js 생성.
   거래 0건 단지는 '인근 유사단지 비준' 근거를 함께 저장한다."""
import sys, io as _io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import os, sys, json, io, math, re, statistics, collections

SC=r"C:\Users\corncake\AppData\Local\Temp\claude\D--DDownloads-apartment-notice-analyzer--claude-worktrees-apartment-appraisal-ai-9c689d\999ed042-521f-471e-892b-b4d7900ac313\scratchpad"
APP=r"D:\DDownloads\apartment_notice_analyzer\.claude\worktrees\apartment-appraisal-ai-9c689d\avm_app"
log=io.open(f"{SC}/merge_log.txt","w",encoding="utf-8"); P=lambda *a: print(*a,file=log)

poi=json.load(io.open(f"{SC}/poi_all.json",encoding="utf-8"))
txt=io.open(f"{APP}/data.js",encoding="utf-8").read()
tr=json.loads(txt[txt.index("["):txt.rindex("]")+1])
P("poi",len(poi),"trade-complexes",len(tr))

# ---------- 이름 정규화 강화 ----------
SUFFIX=re.compile(r"(아파트|APT|apt)$")
BRANDPAD=re.compile(r"[\s\(\)\[\]·,\.:：\-_/]")
def norm(s):
    s=BRANDPAD.sub("",s)
    s=SUFFIX.sub("",s)
    return s
def toks(s):
    return set(re.findall(r"[가-힣A-Za-z0-9]{2,}", s))

tr_idx=[(norm(c["nm"]),c) for c in tr]

def match(nm):
    n=norm(nm)
    for k,c in tr_idx:
        if k==n: return c,"exact"
    best=None;bs=0
    for k,c in tr_idx:
        if len(k)>=5 and (k in n or n in k):
            sc=min(len(k),len(n))/max(len(k),len(n))
            if sc>bs: bs, best = sc, c
    if best and bs>=0.62: return best,f"sub{bs:.2f}"
    # 토큰 자카드
    tn=toks(nm)
    for k,c in tr_idx:
        tk=toks(c["nm"])
        if not tk or not tn: continue
        j=len(tk&tn)/len(tk|tn)
        if j>bs and j>=0.6: bs,best=j,c
    if best and bs>=0.6: return best,f"jac{bs:.2f}"
    return None,""

def hav(a,b,c,d):
    R=6371000;p=math.radians
    dφ=p(c-a);dλ=p(d-b)
    x=math.sin(dφ/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(dλ/2)**2
    return 2*R*math.asin(math.sqrt(x))

# ---------- 1차: 매칭 ----------
out=[]
mc=collections.Counter()
for p_ in poi:
    hit,how=match(p_["nm"])
    mc[how.split("0")[0] if how else "none"]+=1
    r={"nm":p_["nm"],"lat":p_["lat"],"lng":p_["lng"],
       "addr":p_["addr"],"road":p_.get("road","")}
    if hit:
        r.update({"hasT":1,"n":hit["n"],"nRaw":hit["nRaw"],"unit":hit["unit"],
                  "fadj":hit["fadj"],"areas":hit["areas"],"yr":hit["yr"],
                  "maxfl":hit["maxfl"],"regRate":hit["regRate"],
                  "umd":hit["umd"],"jibun":hit["jibun"],"seq":hit["seq"],
                  "match":how})
    else:
        parts=p_["addr"].split()
        r.update({"hasT":0,"n":0,
                  "umd":parts[-2] if len(parts)>=2 else "",
                  "jibun":parts[-1] if parts else "","yr":"","maxfl":0})
    out.append(r)
P("match:",dict(mc))
withT=[o for o in out if o["hasT"]]
P("hasT",len(withT),"noT",len(out)-len(withT))

# ---------- 2차: 거래0건 -> 인근 비준 ----------
# 건축연도 추정 불가하므로 거리 + 단가중앙값으로 비준
for o in out:
    if o["hasT"]: continue
    cand=[]
    for w in withT:
        d=hav(o["lat"],o["lng"],w["lat"],w["lng"])
        if d<=3000:
            cand.append((d,w))
    cand.sort(key=lambda x:x[0])
    top=cand[:5]
    o["comps"]=[{"nm":w["nm"],"d":round(d),"unit":w["unit"],"yr":w["yr"],
                 "n":w["n"],"maxfl":w["maxfl"],
                 "areas":[a["a"] for a in w["areas"][:4]],"fadj":w["fadj"]}
                for d,w in top]
    if top:
        us=[w["unit"] for _,w in top[:3]]
        o["unit"]=round(statistics.median(us))
        # 층효용은 인근 단지 평균
        fs=[[w["fadj"][i] for _,w in top[:3] if w["fadj"][i] is not None] for i in range(4)]
        o["fadj"]=[round(statistics.median(f),3) if f else None for f in fs]
        # 평형은 인근 단지 최빈 면적 사용 (실제는 건축물대장/K-APT 필요)
        ac=collections.Counter()
        for _,w in top[:3]:
            for a in w["areas"]: ac[a["a"]]+=a["n"]
        o["areas"]=[{"a":a,"n":0,"u":o["unit"]} for a,_ in ac.most_common(4)]
        o["maxfl"]=max((w["maxfl"] for _,w in top[:3]),default=25)
        o["est"]=1
    else:
        o["est"]=0

noT=[o for o in out if not o["hasT"]]
P("비준 가능:",sum(1 for o in noT if o.get("est")),"/ 불가:",sum(1 for o in noT if not o.get("est")))

# 미준공/예정 단지 태깅
FUT=re.compile(r"예정|입주\s*예정|20\d\d년\s*\d+월")
for o in out:
    o["future"]=1 if FUT.search(o["nm"]) else 0
    o["lh"]=1 if re.search(r"LH|엘에이치|행복주택|국민임대|공공임대|뉴스테이|영구임대", o["nm"]) else 0
P("예정단지",sum(o["future"] for o in out),"임대추정",sum(o["lh"] for o in out))

# 용량 축소: 비준 가능한 것 + 실거래 있는 것만
keep=[o for o in out if o["hasT"] or o.get("est")]
P("최종",len(keep))
for o in keep[:1]: P("sample:",json.dumps(o,ensure_ascii=False)[:400])

io.open(f"{APP}/data.js","w",encoding="utf-8").write(
 "// 단지목록: 카카오 로컬 POI (실거래 0건 단지 포함)\n"
 "// 가격: 국토교통부 실거래가 오픈API (화성 4개구, 2025.01~2026.08)\n"
 f"// 총 {len(keep)}곳 = 실거래보유 {len(withT)} + 인근비준 {len(keep)-len(withT)}\n"
 "const COMPLEX_DATA = "+json.dumps(keep,ensure_ascii=False,separators=(",",":"))+";\n")
log.close(); print("ok",len(keep))
