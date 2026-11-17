# -*- coding: utf-8 -*-
"""
23. 시점수정치 — 한국부동산원 (월) 매매가격지수_아파트 → avm_app/time_index.js

  시점수정치 = 기준시점 지수 / 거래기간(2025.09~2026.08) 월별 지수 평균

data.js의 단가는 거래별 단가의 중위값이라 거래월을 잃었다. 그래서 거래 하나하나가
아니라 "수집기간 12개월에 거래가 고르게 분포했다"는 가정 아래 기간 평균지수로
나눈다. shortcut: 거래월 분포 무시, 원거래 재수집(01·16·17 rows 보존) 시 거래별 보정으로 교체.
04(화성 확대창)도 같은 창으로 취급한다 — 같은 shortcut.

지역 매칭: 주소의 시군구 토큰(가장 세부부터)을 R-ONE 경로 말단과 대조하되 시도로
범위를 한정한다(중구·동구 등 동명 방지). 13개월 전부에 존재하는 경로만 쓴다
(2026 전남광주 통합으로 경로가 바뀐 지역이 있어서). 없으면 시도 지수.
app은 regKey()를 index.html에서 같은 규칙으로 다시 계산해 이 표를 찾는다.
"""
import io, json, os, re, statistics, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP = os.path.dirname(_HERE)
_REPO = os.path.dirname(_APP)
sys.path.insert(0, os.path.join(_REPO, "apartment_notice_analyzer"))
from dotenv import dotenv_values
from modules.price_index import PriceIndexClient, STATBL

V = {}
for p in (os.path.join(_REPO, "apartment_notice_analyzer", ".env"),
          r"D:\DDownloads\apartment_notice_analyzer\apartment_notice_analyzer\.env"):
    if os.path.exists(p):
        V = dotenv_values(p)
        if V.get("REB_RONE_API_KEY"): break
cli = PriceIndexClient(V.get("REB_RONE_API_KEY"))
assert cli.is_configured, "REB_RONE_API_KEY 없음"

WIN = [f"2025{m:02d}" for m in range(9, 13)] + [f"2026{m:02d}" for m in range(1, 9)]
STAT = STATBL["아파트"]

# 기준시점 = 발표된 가장 최근 월
base_ym = None
y, m = 2026, 12
for _ in range(12):
    if cli._fetch_month(STAT, f"{y}{m:02d}"):
        base_ym = f"{y}{m:02d}"; break
    m -= 1
    if not m: y, m = y - 1, 12
assert base_ym, "R-ONE 최근 지수 없음"

idx = {}   # path -> {ym: val}
for ym in WIN + [base_ym]:
    for r in cli._fetch_month(STAT, ym):
        idx.setdefault(r["CLS_FULLNM"], {})[ym] = float(r["DTA_VAL"])
full = {p: v for p, v in idx.items() if all(ym in v for ym in WIN + [base_ym])}
print("기준시점", base_ym, "경로", len(idx), "13개월 완비", len(full))

ADMIN = ("시", "군", "구", "도")
def reg_key(addr):
    # index.html regKey()와 반드시 같은 규칙
    t = (addr or "").split()
    out = t[:1]
    for w in t[1:]:
        if not w.endswith(ADMIN): break
        out.append(w)
    return " ".join(out)

def match(key):
    toks = key.split()
    if not toks: return None
    s2 = toks[0][:2]
    inside = [p for p in full if s2 in p.split(">")[0]]
    for tok in reversed(toks[1:]):
        c = [p for p in inside if p.split(">")[-1] == tok]
        if c: return min(c, key=lambda p: p.count(">"))
    # 시도 지수: 통합 시도(전남광주)는 하위 '전남'/'광주' 마디를 우선
    c = [p for p in inside if p.split(">")[-1] == s2] or [p for p in inside if ">" not in p]
    return min(c, key=lambda p: p.count(">")) if c else None

txt = io.open(os.path.join(_APP, "data.js"), encoding="utf-8").read()
data = json.loads(re.search(r"const COMPLEX_DATA = (\[.*\]);", txt, re.S).group(1))
keys = sorted({reg_key(c.get("addr")) for c in data if c.get("addr")})

out, lvl, miss = {}, {"시군구": 0, "시도": 0}, []
for k in keys:
    p = match(k)
    if not p: miss.append(k); continue
    v = full[p]
    deal = statistics.mean(v[ym] for ym in WIN)
    out[k] = [round(v[base_ym] / deal, 5), p, round(deal, 2), round(v[base_ym], 2)]
    lvl["시군구" if p.split(">")[-1] in k.split()[1:] else "시도"] += 1

ratios = sorted(x[0] for x in out.values())
print("키", len(keys), "매칭", len(out), lvl, "미매칭", len(miss), miss[:10])
print("시점수정치 분포 min/med/max", ratios[0], statistics.median(ratios), ratios[-1])
assert len(out) >= 0.95 * len(keys), "매칭률 95% 미만 — 규칙 점검 필요"
assert 0.8 < ratios[0] and ratios[-1] < 1.3, "비정상 시점수정치"

meta = {"base": base_ym, "win": f"{WIN[0]}~{WIN[-1]}",
        "src": "한국부동산원 전국주택가격동향조사 (월) 매매가격지수_아파트(A_2024_00045)"}
io.open(os.path.join(_APP, "time_index.js"), "w", encoding="utf-8").write(
    "// 23_time_index.py 생성 — 수정 금지\nconst TIME_INDEX=" +
    json.dumps({**meta, "r": out}, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("time_index.js 저장", len(out))
