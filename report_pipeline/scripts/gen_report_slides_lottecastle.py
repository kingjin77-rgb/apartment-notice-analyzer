# -*- coding: utf-8 -*-
"""검토보고서 가로 슬라이드판 (16:9 · 1332x750) — 발견 31건 + 동별 지도"""
import os, json, html as H

OUT = "/tmp/lc/rslides"
os.makedirs(OUT, exist_ok=True)

F = json.load(open('/tmp/lc/findings.json', encoding='utf-8'))
M = json.load(open('/tmp/lc/unit_matrix.json', encoding='utf-8'))
P = json.load(open('/tmp/lc/price_table.json', encoding='utf-8'))
CAT = {f['id']: c['title'] for c in F['categories'] for f in c['findings']}
ALL = [f for c in F['categories'] for f in c['findings']]
ORD = {'치명': 0, '높음': 1, '중간': 2}
ALL.sort(key=lambda x: ORD[x['grade']])

def esc(s): return H.escape(str(s))

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1332px;height:750px;overflow:hidden}
body{font-family:"S-Core Dream","NanumSquare","Malgun Gothic",sans-serif;background:#fff;color:#16202E;position:relative}
.pad{position:absolute;left:56px;right:56px;top:44px;bottom:66px;display:flex;flex-direction:column}
.eyebrow{font-size:14.5px;font-weight:800;color:#3E6CB5;letter-spacing:1px;margin-bottom:8px}
h1{font-size:40px;font-weight:800;color:#0F2548;letter-spacing:-1.6px;line-height:1.15}
h1 em{font-style:normal;color:#C0392B}
h1 u{text-decoration:none;background:linear-gradient(transparent 62%,#FFE08A 62%)}
.lead{font-size:16px;color:#5B6673;font-weight:700;margin-top:9px;line-height:1.5}
.bar{position:absolute;left:0;right:0;bottom:0;height:48px;background:#0F2548;display:flex;align-items:center;
  justify-content:space-between;padding:0 56px}
.bar .l{color:#fff;font-size:13.5px;font-weight:800}.bar .l span{color:#7FA9E8}
.bar .r{color:#8FA3C0;font-size:11.5px}
.pg{position:absolute;right:56px;top:38px;font-size:12.5px;font-weight:800;color:#B9C4D2}
/* 발견 카드 3열 */
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;flex:1;margin-top:16px}
.cards.four{grid-template-columns:repeat(4,1fr);gap:11px}
.cards.four .c{padding:13px 13px}
.cards.four .c h3{font-size:14px}
.cards.four .c .b{font-size:11.5px}
.cards.four .c .q{font-size:10.8px}
.cards.four .c .n{font-size:10.8px}
.c{border:1.5px solid #E1E7EE;border-radius:13px;padding:15px 16px;display:flex;flex-direction:column;
   background:#fff;position:relative;overflow:hidden}
.c:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:#3E6CB5}
.c.치명:before{background:#C0392B}.c.높음:before{background:#B7791F}
.c .top{display:flex;gap:6px;align-items:center;margin-bottom:8px;flex-wrap:wrap}
.pill{font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:20px}
.pill.g{background:#FBEAEA;color:#C0392B}
.pill.g.높음{background:#FCF3E2;color:#B7791F}
.pill.g.중간{background:#EDF2FA;color:#3E6CB5}
.pill.p{background:#F1F4F8;color:#5B6673}
.pill.k{background:#0F2548;color:#fff}
.c h3{font-size:15.5px;font-weight:800;color:#0F2548;line-height:1.32;letter-spacing:-.4px;margin-bottom:8px}
.c .q{font-size:11.5px;color:#5B6673;background:#F7F9FC;border-left:3px solid #E1E7EE;padding:7px 9px;
  border-radius:0 6px 6px 0;margin-bottom:8px;font-weight:600;line-height:1.45}
.c .b{font-size:12.3px;color:#31404F;line-height:1.55;font-weight:600;margin-bottom:8px}
.c .n{background:#0F2548;color:#fff;border-radius:8px;padding:8px 10px;font-size:11.5px;font-weight:700;
  line-height:1.45;margin-top:auto}
/* 표 */
table.t{width:100%;border-collapse:collapse;font-size:14px;background:#fff;margin-top:16px}
table.t th{background:#0F2548;color:#fff;font-size:13px;font-weight:800;padding:10px 12px;text-align:left}
table.t td{padding:9.5px 12px;border-bottom:1px solid #E5EAF0;font-weight:600;color:#31404F}
table.t td.n{white-space:nowrap;font-weight:800}
table.t td.red{color:#C0392B;font-weight:800}
"""

BAR = ('<div class="bar"><div class="l">법무법인 <span>JL</span> 제이엘 · 분양공고문 분석팀</div>'
       '<div class="r">번영로 롯데캐슬 센트럴스카이 · 입주자모집공고 69면 전수 통독 검토보고서</div></div>')

pages = []
def page(body, pg=None, style=""):
    pgh = f'<div class="pg">{pg}</div>' if pg else ""
    name = f"r{len(pages)+1:02d}"
    h = (f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}{style}</style></head>'
         f'<body>{pgh}{body}{BAR}</body></html>')
    open(f"{OUT}/{name}.html", "w", encoding="utf-8").write(h)
    pages.append(name)

# ── 표지
page("""
<style>
body{background:linear-gradient(155deg,#0F2548 0%,#16305C 55%,#1B3A6B 100%)}
body:before{content:"";position:absolute;inset:auto -6% -30% 52%;height:500px;
 background:repeating-linear-gradient(90deg,rgba(255,255,255,.055) 0 2px,transparent 2px 30px);transform:skewY(-9deg)}
.cv{position:absolute;left:70px;top:130px;right:70px}
.cv .tag{display:inline-block;border:1px solid rgba(255,255,255,.34);background:rgba(255,255,255,.12);
 color:#DCE7F7;font-size:15px;font-weight:800;padding:7px 17px;border-radius:24px}
.cv h1{color:#fff;font-size:58px;letter-spacing:-2.3px;margin-top:20px;line-height:1.14}
.cv h1 em{color:#8FBBFF}
.cv p{color:#B9C8DE;font-size:18px;font-weight:700;margin-top:16px;line-height:1.55}
.cv .rule{width:84px;height:5px;background:#C0392B;margin-top:22px;border-radius:3px}
.kpi{display:flex;gap:14px;margin-top:44px}
.k{flex:1;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.09);border-radius:13px;padding:16px 18px}
.k b{display:block;color:#fff;font-size:30px;font-weight:800;letter-spacing:-1.2px;line-height:1}
.k small{display:block;color:#B9C8DE;font-size:13px;font-weight:700;margin-top:7px}
.bar{background:rgba(0,0,0,.28)}
</style>
<div class="cv">
  <span class="tag">입주자모집공고 전수 검토보고서</span>
  <h1>번영로 롯데캐슬 센트럴스카이<br><em>공고문 69면, 한 면도 빼지 않고</em></h1>
  <div class="rule"></div>
  <p>634세대 · 울산광역시 중구 학산동 167-4 일원 · 관리형 토지신탁<br>
  민영 일반분양 + 주거·오피스텔 혼합 | 단지 고유 발견 13건 · 미통독 0면</p>
  <div class="kpi">
    <div class="k"><b>69 / 69면</b><small>통독 커버리지</small></div>
    <div class="k"><b>13건</b><small>단지 고유 발견 · 치명 3건</small></div>
    <div class="k"><b>396세대</b><small>21층↑ 진입창 없음</small></div>
    <div class="k"><b>4대</b><small>103동 승강기 — 1대 적음</small></div>
    <div class="k"><b>1억1,400만</b><small>103동 21·22층 8세대</small></div>
  </div>
</div>
""")

# ── 요약
page("""
<div class="pad">
  <div class="eyebrow">SUMMARY</div>
  <h1>상투를 걷어내고 남은 <em>이 단지만의 문제</em></h1>
  <p class="lead">여러 아파트에서 반복되는 상투·법정최소·표준약관 항목은 처음부터 배제했습니다. 아래는 이 공고문에만 있는 것들입니다.</p>
  <table class="t">
    <tr><th style="width:140px">분류</th><th>공고문이 말한 것</th><th>두 면을 겹쳐 보면</th><th style="width:110px">근거 면</th></tr>
    <tr><td class="n">동별·세대별</td><td>103동 21층 소화수조 · 22층 제연휀룸</td><td>가격표는 21~30층 한 밴드 — 8세대 1억 1,400만원</td><td class="n red">7 ↔ 52</td></tr>
    <tr><td class="n">피난</td><td>"각동 20층이하는 … 소방관진입창"</td><td>21층 이상 396세대(62.5%)는 그 문장에 없음</td><td class="n red">50 · 52</td></tr>
    <tr><td class="n">피난</td><td>진입창 위치 타입마다 상이</td><td>84A 침실3 · 84E/105 안방발코니 — 가구 놓이는 자리</td><td class="n red">50</td></tr>
    <tr><td class="n">가격 형평</td><td>84B 계약면적 174.73㎡(최소)</td><td>가장 넓은 84D보다 1,300만원 비쌈 — 근거 미제시</td><td class="n red">6 ↔ 7</td></tr>
    <tr><td class="n">승강기</td><td>101·102동 5대 / 103동 아파트 4대</td><td>오피스텔 2대는 코어 분리로 사용 불가</td><td class="n red">50 ↔ 53</td></tr>
    <tr><td class="n">옵션</td><td>시스템에어컨 선택/미선택 조항</td><td>어느 쪽을 골라도 한쪽 냉방 경로가 봉쇄</td><td class="n red">42</td></tr>
    <tr><td class="n">문서 효력</td><td>홍보물 우선(57면)</td><td>68·69면이 이를 두 번 뒤집음</td><td class="n red">57↔68↔69</td></tr>
    <tr><td class="n">절차·자격</td><td>장애인 추천기관 3곳 지정</td><td>기관추천 54세대 전부 소진 — 배정 0세대</td><td class="n red">9 ↔ 11</td></tr>
    <tr><td class="n">공백</td><td>총 주차대수</td><td>69면 어디에도 없음 — 세대당 산출 불가</td><td class="n red">전면</td></tr>
  </table>
</div>
""", "02")

# ── 통독 방법
cells = "".join('<div class="cell"></div>' for _ in range(69))
page(f"""
<style>
.cells{{display:grid;grid-template-columns:repeat(23,1fr);gap:6px;margin-top:20px}}
.cell{{height:46px;border-radius:5px;background:#2ECC8F}}
.segs{{display:flex;gap:11px;margin-top:14px}}
.seg{{flex:1;background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:11px;padding:13px 15px}}
.seg b{{display:block;font-size:17px;font-weight:800;color:#0F2548}}
.seg small{{font-size:12px;color:#5B6673;font-weight:700}}
.two{{display:flex;gap:20px;margin-top:auto}}
.panel{{flex:1;background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:12px;padding:16px 18px;
  display:flex;flex-direction:column;justify-content:center}}
.panel.dark{{background:#0F2548;border-color:#0F2548}}
.panel h3{{font-size:17px;font-weight:800;color:#0F2548;margin-bottom:7px}}
.panel.dark h3{{color:#fff}}
.panel p{{font-size:13px;color:#43525F;line-height:1.55;font-weight:600}}
.panel.dark p{{color:#C3D3E8}}
</style>
<div class="pad">
  <div class="eyebrow">HOW WE READ IT</div>
  <h1>69면을 5개 구간으로 나눠 <u>동시에 통독</u>했습니다</h1>
  <p class="lead">각 구간에 검토자를 따로 두고 처음부터 끝까지 읽었습니다. 이번 검토의 미통독 면은 <b style="color:#0F2548">0면</b>입니다.</p>
  <div class="cells">{cells}</div>
  <div class="segs">
    <div class="seg"><b>1 – 14면</b><small>청약자격 · 공급금액 · 특별공급</small></div>
    <div class="seg"><b>15 – 28면</b><small>당첨자선정 · 소명 · 계약절차</small></div>
    <div class="seg"><b>29 – 42면</b><small>대금납부 · 보증 · 옵션</small></div>
    <div class="seg"><b>43 – 56면</b><small>건축 · 마감재 · 부대시설 · 피난</small></div>
    <div class="seg"><b>57 – 69면</b><small>세대별 유의사항 · 신탁 · 보증약관</small></div>
  </div>
  <div class="two">
    <div class="panel"><h3>① 서로 다른 면의 표를 겹칩니다</h3><p>7면 층별가격표 × 52면 설비층 고지 · 6면 면적표 × 7면 가격표 · 9면 배정표 × 11면 추천기관.</p></div>
    <div class="panel"><h3>② 상투 항목은 처음부터 뺍니다</h3><p>주차 층고 · 내진 법정등급 · 표준약관처럼 어느 아파트에나 똑같이 있는 것은 문제로 취급하지 않습니다.</p></div>
    <div class="panel dark"><h3>③ 적혀 있지 않은 것을 찾습니다</h3><p>총 주차대수 · 신탁재산 잔액 · 실외기 영향 호수 — 이 셋은 69면 어디에도 없습니다.</p></div>
  </div>
</div>
""", "03")

# ── 동별 지도
def bd(b):
    GC = {"critical": ("hot", "#C0392B"), "high": ("warn", "#B7791F"), "mid": ("", "#3E6CB5")}
    lis = ""
    for it in b['items']:
        cls, col = GC[it['risk']]
        lis += (f'<li class="{cls}"><i>{esc(it["floor"])}</i>'
                f'<span>{esc(it["what"])}<em>{esc(it["effect"])} · {it["page"]}면</em></span></li>')
    return (f'<div class="bd"><div class="h"><b>{esc(b["name"])}</b>'
            f'<small>{esc(b["lines"])}<br>승강기 {esc(b["ev"])}<br>{esc(b["road"])}</small></div>'
            f'<ul>{lis}</ul></div>')

page(f"""
<style>
.map{{display:flex;gap:14px;margin-top:16px;flex:1}}
.bd{{flex:1;border:1.5px solid #E1E7EE;border-radius:13px;overflow:hidden;display:flex;flex-direction:column;background:#fff}}
.bd .h{{background:#0F2548;color:#fff;padding:11px 14px}}
.bd .h b{{font-size:18px;font-weight:800}}
.bd .h small{{display:block;font-size:11px;color:#B9C8DE;font-weight:700;margin-top:3px;line-height:1.45}}
.bd ul{{list-style:none;flex:1;display:flex;flex-direction:column;justify-content:space-evenly;padding:4px 0}}
.bd li{{display:flex;gap:8px;padding:5px 14px;align-items:baseline}}
.bd li i{{font-style:normal;flex:none;width:80px;font-size:11px;font-weight:800;color:#3E6CB5}}
.bd li span{{font-size:11.8px;color:#0F2548;font-weight:800;line-height:1.35}}
.bd li span em{{display:block;font-style:normal;font-size:10.8px;color:#5B6673;font-weight:600;margin-top:1px}}
.bd li.hot{{background:#FDF2F1}}.bd li.hot i,.bd li.hot span{{color:#C0392B}}
.bd li.warn i{{color:#B7791F}}
</style>
<div class="pad">
  <div class="eyebrow">동별 · 세대별</div>
  <h1>같은 단지여도 <u>동에 따라 겪는 것이 다릅니다</u></h1>
  <p class="lead">공고문 50~54면이 동별로 따로 적어 둔 것을 한자리에 모았습니다.</p>
  <div class="map">{''.join(bd(b) for b in M['buildings'])}</div>
</div>
""", "04")

# ── 발견 카드 (3장씩)
def card(f):
    return (f'<div class="c {f["grade"]}">'
            f'<div class="top"><span class="pill g {f["grade"]}">{f["grade"]}</span>'
            f'<span class="pill k">{f["level"]}</span>'
            f'<span class="pill p">{"·".join(str(p) for p in f["pages"])}면</span>'
            f'<span class="pill p">{esc(CAT[f["id"]])}</span></div>'
            f'<h3>{esc(f["title"])}</h3>'
            f'<div class="q">"{esc(f["quote"])}"</div>'
            f'<div class="b">{esc(f["problem"])}</div>'
            f'<div class="n">{esc(f["quant"])}</div></div>')

GRP = [ALL[i:i+3] for i in range(0, len(ALL), 3)]
if len(GRP) > 1 and len(GRP[-1]) == 1:          # 마지막이 1장이면 앞과 합쳐 4열로
    GRP[-2] = GRP[-2] + GRP[-1]; GRP.pop()
for i, g in enumerate(GRP, 1):
    lo = (i-1)*3 + 1
    hi = lo + len(g) - 1
    page(f"""
<div class="pad">
  <div class="eyebrow">FINDINGS &nbsp;·&nbsp; {lo} – {hi} / {len(ALL)}</div>
  <h1>발견 항목 <em>{lo}–{hi}</em></h1>
  <div class="cards{' four' if len(g)==4 else ''}">{''.join(card(f) for f in g)}</div>
</div>
""", f"{len(pages)+1:02d}")

# ── 마무리
page("""
<style>
.rm{display:flex;gap:13px;margin-top:20px;flex:1}
.st{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:14px;padding:20px 18px;
  display:flex;flex-direction:column;justify-content:center}
.st .no{font-size:30px;font-weight:800;color:#3E6CB5;opacity:.28;letter-spacing:-2px;line-height:1}
.st b{display:block;font-size:16.5px;font-weight:800;color:#0F2548;margin:7px 0 6px}
.st small{font-size:12.5px;color:#5B6673;font-weight:700;line-height:1.5;display:block}
.st.now{background:#0F2548;border-color:#0F2548}
.st.now .no{color:#7FA9E8;opacity:.6}.st.now b{color:#fff}.st.now small{color:#B9C8DE}
.close{margin-top:16px;background:#FDF3F2;border:1.5px solid #F0C6C0;border-radius:14px;padding:18px 22px}
.close b{font-size:19px;font-weight:800;color:#C0392B}
.close p{font-size:14px;color:#43525F;font-weight:700;margin-top:7px;line-height:1.55}
</style>
<div class="pad">
  <div class="eyebrow">WHAT WE DO NEXT</div>
  <h1>검토는 시작입니다. <u>입주까지 같은 자료로 이어갑니다</u></h1>
  <div class="rm">
    <div class="st now"><div class="no">01</div><b>공고문 전수 통독</b><small>69면 5개 구간 병렬<br>단지 고유 발견 13건 · 치명 3건<br><b style="color:#FFD479;display:inline">완료</b></small></div>
    <div class="st"><div class="no">02</div><b>개선요구서 제출</b><small>협의회 명의 공문<br>사업주체·시공사·감리 동시 발송</small></div>
    <div class="st"><div class="no">03</div><b>회신 관리 · 협의</b><small>항목별 회신 대장 운영<br>미회신·형식회신 재요구</small></div>
    <div class="st"><div class="no">04</div><b>사전점검 체크리스트</b><small>동·호수 단위 점검표<br>103동 21~22층 별도 항목</small></div>
    <div class="st"><div class="no">05</div><b>하자 대응 · 분쟁</b><small>하자담보책임 기간 관리<br>필요 시 조정·소송 대리</small></div>
  </div>
  <div class="close">
    <b>"공고문에 다 적혀 있었다"는 말을, 입주 후가 아니라 지금 듣게 해드립니다.</b>
    <p>이번 검토의 13건은 모두 공고문 원문에 근거합니다. 여러 아파트 공통의 상투 항목은 처음부터 배제했고, 금액·세대수는 원문과 재대조해 계산식을 병기했습니다. 확정 불가 항목은 "사업주체 확인 요망"으로 표시했습니다.</p>
  </div>
</div>
""", f"{len(pages)+1:02d}")

print("pages:", len(pages))
open(f"{OUT}/_list.json", "w").write(json.dumps(pages))
