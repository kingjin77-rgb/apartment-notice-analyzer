# -*- coding: utf-8 -*-
import os, json, html
OUT = "/tmp/lc/slides"
os.makedirs(OUT, exist_ok=True)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1332px;height:750px;overflow:hidden}
body{font-family:"S-Core Dream","NanumSquare","Malgun Gothic",sans-serif;background:#fff;color:#16202E;position:relative}
.pad{position:absolute;left:64px;right:64px;top:52px;bottom:74px;display:flex;flex-direction:column}
.eyebrow{font-size:16px;font-weight:800;color:#3E6CB5;letter-spacing:1px;margin-bottom:10px}
h1{font-size:52px;font-weight:800;color:#0F2548;letter-spacing:-2px;line-height:1.14}
h1 em{font-style:normal;color:#C0392B}
h1 u{text-decoration:none;background:linear-gradient(transparent 62%,#FFE08A 62%)}
.lead{font-size:19px;color:#5B6673;font-weight:700;margin-top:12px;line-height:1.5}
.bar{position:absolute;left:0;right:0;bottom:0;height:54px;background:#0F2548;display:flex;align-items:center;
  justify-content:space-between;padding:0 64px}
.bar .l{color:#fff;font-size:15px;font-weight:800}.bar .l span{color:#7FA9E8}
.bar .r{color:#8FA3C0;font-size:12px}
.pg{position:absolute;right:64px;top:44px;font-size:13px;font-weight:800;color:#B9C4D2}
/* metric row */
.mrow{display:flex;gap:14px;margin-top:22px}
.m{flex:1;border:1.5px solid #E1E7EE;border-radius:14px;padding:15px 17px;background:#fff}
.m.hot{border-color:#F0C6C0;background:#FDF6F5}
.m b{display:block;font-size:40px;font-weight:800;color:#0F2548;letter-spacing:-1.5px;line-height:1}
.m.hot b{color:#C0392B}
.m small{display:block;font-size:13.5px;color:#5B6673;font-weight:700;margin-top:8px;line-height:1.4}
/* two col */
.two{display:flex;gap:26px;margin-top:24px;align-items:stretch}
.col{flex:1;display:flex;flex-direction:column;gap:12px}
.panel{background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:14px;padding:20px 22px;flex:1;display:flex;flex-direction:column;justify-content:center}
.panel h3{font-size:20px;font-weight:800;color:#0F2548;margin-bottom:9px;letter-spacing:-.6px}
.panel p{font-size:15px;color:#43525F;line-height:1.6;font-weight:600}
.panel.dark{background:#0F2548;border-color:#0F2548}
.panel.dark h3{color:#fff}.panel.dark p{color:#C3D3E8}
.panel.red{background:#FDF3F2;border-color:#F0C6C0}
.panel.red h3{color:#C0392B}
.quote{font-size:14.5px;color:#5B6673;font-weight:700;background:#fff;border-left:4px solid #C0392B;
  padding:11px 14px;border-radius:0 8px 8px 0;line-height:1.5}
.ask{background:#0F2548;color:#fff;border-radius:12px;padding:16px 20px;font-size:16px;font-weight:700;line-height:1.5}
.ask b{color:#FFD479}
.ask .tag{display:inline-block;font-size:12px;font-weight:800;color:#7FA9E8;letter-spacing:1px;margin-bottom:5px}
table.t{width:100%;border-collapse:collapse;font-size:14.5px;background:#fff;margin-top:20px}
table.t th{background:#0F2548;color:#fff;font-size:13.5px;font-weight:800;padding:11px 14px;text-align:left}
table.t td{padding:10.5px 14px;border-bottom:1px solid #E5EAF0;font-weight:600;color:#31404F}
table.t td.n{white-space:nowrap;font-weight:800}
table.t td.red{color:#C0392B;font-weight:800}
"""

BAR = ('<div class="bar"><div class="l">법무법인 <span>JL</span> 제이엘 · 분양공고문 분석팀</div>'
       '<div class="r">번영로 롯데캐슬 센트럴스카이 · 입주자모집공고 69면 전수 통독</div></div>')

def page(name, body, pg=None, bodyclass=""):
    pgh = f'<div class="pg">{pg}</div>' if pg else ""
    h = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body class="{bodyclass}">{pgh}{body}{BAR}</body></html>"""
    open(f"{OUT}/{name}.html", "w", encoding="utf-8").write(h)

# ── 01 표지
page("s01", """
<style>
body{background:linear-gradient(155deg,#0F2548 0%,#16305C 55%,#1B3A6B 100%)}
body:before{content:"";position:absolute;inset:auto -6% -30% 52%;height:520px;
 background:repeating-linear-gradient(90deg,rgba(255,255,255,.055) 0 2px,transparent 2px 30px);transform:skewY(-9deg)}
.cv{position:absolute;left:78px;top:120px;right:78px}
.cv .tag{display:inline-block;border:1px solid rgba(255,255,255,.34);background:rgba(255,255,255,.12);
 color:#DCE7F7;font-size:16px;font-weight:800;padding:8px 18px;border-radius:26px}
.cv h1{color:#fff;font-size:66px;letter-spacing:-2.6px;margin-top:22px}
.cv h1 em{color:#8FBBFF}
.cv p{color:#B9C8DE;font-size:20px;font-weight:700;margin-top:18px;line-height:1.55}
.cv .rule{width:92px;height:5px;background:#C0392B;margin:26px 0 0;border-radius:3px}
.bar{background:rgba(0,0,0,.28)}
.kpi{display:flex;gap:16px;margin-top:52px}
.k{flex:1;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.09);border-radius:14px;padding:18px 20px}
.k b{display:block;color:#fff;font-size:34px;font-weight:800;letter-spacing:-1.4px;line-height:1}
.k small{display:block;color:#B9C8DE;font-size:14px;font-weight:700;margin-top:8px}
</style>
<div class="cv">
  <span class="tag">입주예정자협의회 자문 제안</span>
  <h1>공고문 69면,<br><em>한 면도 빼지 않고</em> 읽었습니다</h1>
  <div class="rule"></div>
  <p>번영로 롯데캐슬 센트럴스카이 · 634세대 · 울산 중구 학산동 167-4 일원<br>
  키워드 검색이 아니라 전면 통독 — 서로 다른 면의 표를 이 단지에만 있는 문제 <b style="color:#fff">13건</b>을 찾았습니다. 여러 아파트 공통의 상투 항목은 처음부터 뺐고, 수치는 모두 원문과 재대조했습니다.</p>
  <div class="kpi">
    <div class="k"><b>69 / 69면</b><small>통독 커버리지 · 미통독 0면</small></div>
    <div class="k"><b>13건</b><small>단지 고유 발견 · 치명 3건</small></div>
    <div class="k"><b>396세대</b><small>21층 이상 · 진입창 없는 구간</small></div>
    <div class="k"><b>1억 1,400만</b><small>103동 21·22층 8세대 초과부담</small></div>
  </div>
</div>
""")

# ── 02 통독 방법
cells = "".join('<div class="cell"></div>' for _ in range(69))
page("s02", f"""
<style>
.cells{{display:grid;grid-template-columns:repeat(23,1fr);gap:7px;margin-top:26px}}
.cell{{height:52px;border-radius:5px;background:#2ECC8F}}
.segs{{display:flex;gap:12px;margin-top:16px}}
.seg{{flex:1;background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:12px;padding:15px 18px}}
.seg b{{display:block;font-size:19px;font-weight:800;color:#0F2548}}
.seg small{{font-size:13px;color:#5B6673;font-weight:700}}
</style>
<div class="pad">
  <div class="eyebrow">HOW WE READ IT</div>
  <h1>69면을 5개 구간으로 나눠 <u>동시에 통독</u>했습니다</h1>
  <p class="lead">"주요 항목을 검토했습니다"가 아니라, 각 구간에 검토자를 따로 두고 처음부터 끝까지 읽었습니다. 못 읽은 면이 있으면 못 읽었다고 적습니다 — 이번 검토의 미통독 면은 <b style="color:#0F2548">0면</b>입니다.</p>
  <div class="cells">{cells}</div>
  <div class="segs">
    <div class="seg"><b>1 – 14면</b><small>청약자격 · 공급금액 · 특별공급</small></div>
    <div class="seg"><b>15 – 28면</b><small>당첨자선정 · 소명 · 계약절차</small></div>
    <div class="seg"><b>29 – 42면</b><small>대금납부 · 보증 · 옵션</small></div>
    <div class="seg"><b>43 – 56면</b><small>건축 · 마감재 · 부대시설 · 피난</small></div>
    <div class="seg"><b>57 – 69면</b><small>세대별 유의사항 · 신탁 · 보증약관</small></div>
  </div>
  <div class="two" style="margin-top:auto">
    <div class="panel"><h3>① 서로 다른 면의 표를 겹칩니다</h3><p>7면 층별가격표 × 52면 설비층 고지 · 6면 면적표 × 7면 가격표 · 9면 배정표 × 11면 추천기관. 한 면만 보면 정상으로 보이는 것이 여기서 갈립니다.</p></div>
    <div class="panel"><h3>② 상투 항목은 처음부터 뺍니다</h3><p>주차 층고, 내진 법정등급, 표준약관 문구처럼 어느 아파트에나 똑같이 있는 것은 문제로 취급하지 않습니다. 남는 것이 이 단지의 진짜 문제입니다.</p></div>
    <div class="panel dark"><h3>③ 적혀 있지 않은 것을 찾습니다</h3><p>총 주차대수 · 신탁재산 잔액 · 실외기 영향 호수 — 이 세 가지는 69면 어디에도 없습니다. 없는 것이 있는 것보다 중요할 때가 있습니다.</p></div>
  </div>
</div>
""", "02")

# ── 03 진단 대시보드
page("s03", """
<div class="pad">
  <div class="eyebrow">DIAGNOSIS</div>
  <h1>상투를 걷어내고 남은 <em>이 단지만의 문제 13건</em></h1>
  <div class="mrow">
    <div class="m hot"><b style="font-size:31px">1억 1,400만</b><small>103동 21·22층 8세대가<br>11~19층보다 더 내는 금액</small></div>
    <div class="m hot"><b>396세대</b><small>21층 이상 62.5% —<br>소방관 진입창 없는 구간</small></div>
    <div class="m hot"><b>4대</b><small>103동만 승강기 1대 적음<br>오피스텔 2대는 사용 불가</small></div>
    <div class="m hot"><b>0세대</b><small>장애인·철거주택 소유자<br>자격만 있고 배정 없음</small></div>
    <div class="m hot"><b>70일</b><small>층간소음 사후확인제<br>시행 직전 승인으로 배제</small></div>
  </div>
  <table class="t">
    <tr><th style="width:150px">분류</th><th>공고문이 말한 것</th><th>두 면을 겹쳐 보면</th><th style="width:120px">근거 면</th></tr>
    <tr><td class="n">동별·세대별</td><td>103동 21층 소화수조 · 22층 제연휀룸 (52면)</td><td>가격표는 21~30층을 한 밴드로 묶음 — 8세대 1억 1,400만원</td><td class="n red">7 ↔ 52</td></tr>
    <tr><td class="n">피난</td><td>"각동 20층이하는 … 소방관진입창" (50면)</td><td>21층 이상 396세대는 그 문장에 없음 · 타입별 위치도 상이</td><td class="n red">50 · 52</td></tr>
    <tr><td class="n">가격 형평</td><td>84B 계약면적 174.73㎡ (6면)</td><td>가장 작은데 가장 넓은 84D보다 1,300만원 비쌈</td><td class="n red">6 ↔ 7</td></tr>
    <tr><td class="n">승강기</td><td>101·102동 5대 / 103동 아파트 4대 (53면)</td><td>오피스텔 2대는 코어 분리로 사용 불가 (50면)</td><td class="n red">50 ↔ 53</td></tr>
    <tr><td class="n">절차·자격</td><td>장애인 추천기관 3곳 지정 (11면)</td><td>기관추천 54세대를 다른 7개 항목이 전부 소진 — 배정 0</td><td class="n red">9 ↔ 11</td></tr>
    <tr><td class="n">공백</td><td>총 주차대수</td><td>69면 어디에도 없음 — 세대당 주차대수 산출 불가</td><td class="n red">전면</td></tr>
  </table>
</div>
""", "03")

# ── 04 21층
page("s04", """
<style>
.wrapx{display:flex;gap:26px;margin-top:22px;align-items:stretch;flex:1}
.tower{width:330px;border:2px solid #0F2548;border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.tower .fl{flex:1}
.fl{padding:9px 14px;font-size:14px;font-weight:700;color:#5B6673;background:#fff;border-bottom:1px solid #E5EAF0;
  display:flex;justify-content:space-between;align-items:center}
.fl.mech{background:#EDF2F9;color:#0F2548;font-weight:800}
.fl.risk{background:#FBEAEA;color:#C0392B;font-weight:800}
.fl .t{font-size:11px;background:#C0392B;color:#fff;border-radius:4px;padding:2px 7px}
.fl.mech .t{background:#0F2548}
.right{flex:1;display:flex;flex-direction:column;gap:14px}
.calc{background:#fff;border:1.5px solid #E1E7EE;border-radius:14px;padding:18px 22px}
.calc table{width:100%;border-collapse:collapse;font-size:16px}
.calc td{padding:8px 0;font-weight:700;color:#43525F}
.calc td.v{text-align:right;font-weight:800;color:#0F2548;font-variant-numeric:tabular-nums}
.calc tr.sum td{border-top:2px solid #0F2548;padding-top:12px;color:#C0392B;font-size:19px}
</style>
<div class="pad">
  <div class="eyebrow">FINDING 01 · 동별 · 세대별</div>
  <h1>103동 21층은 <u>소화수조와 같은 층</u>인데,<br>가격표는 <em>21층부터 30층까지를 한 칸에 묶었습니다</em></h1>
  <div class="wrapx">
    <div class="tower">
      <div class="fl mech"><span>옥탑</span><span>소화수조·기계실</span><span class="t">진동원</span></div>
      <div class="fl"><span>23 ~ 48층</span><span>일반세대</span></div>
      <div class="fl risk"><span>22층</span><span>제연휀룸 + 세대</span><span class="t">동거</span></div>
      <div class="fl risk"><span>21층</span><span>소화수조 + 세대</span><span class="t">동거</span></div>
      <div class="fl mech"><span>20층</span><span>피난안전구역</span><span class="t">공용</span></div>
      <div class="fl"><span>4 ~ 19층</span><span>일반세대</span></div>
      <div class="fl risk"><span>3층</span><span>부대시설 상부</span><span class="t">소음</span></div>
      <div class="fl mech"><span>1~2층</span><span>근생·라운지</span><span class="t">시설</span></div>
    </div>
    <div class="right">
      <div class="quote">"103동 20층에 피난안전구역, 소화수조 및 제연휀룸실이, 21층에 소화수조가, 22층에 제연휀룸 계획되어 있어서 21층, 22층 공동주택 세대 및 아래 위 …" — 공고문 52면이 스스로 적은 문장입니다.</div>
      <div class="calc"><table>
        <tr><td>84B · 11~19층 → 21~30층</td><td class="v">+ 15,000,000 원</td></tr>
        <tr><td>84C · 690,000,000 → 704,000,000</td><td class="v">+ 14,000,000 원</td></tr>
        <tr><td>84D · 693,000,000 → 707,000,000</td><td class="v">+ 14,000,000 원</td></tr>
        <tr><td>84F · 700,000,000 → 714,000,000</td><td class="v">+ 14,000,000 원</td></tr>
        <tr class="sum"><td>103동 21·22층 8세대 합계</td><td class="v">+ 114,000,000 원</td></tr>
      </table></div>
      <div class="ask"><span class="tag">개선요구</span>103동 20~22층 세대에 대해 <b>층별 가격 재산정 또는 방진·방음 보강 시공</b>을 요구하고, 미이행 시 해당 호수에 한해 계약 전 사전고지 확인서를 별도 징구할 것. <span style="color:#8FA3C0;font-size:13px">※ 103동 4개 라인(84B·84C·84D·84F) 전부 원문 대조 완료</span></div>
    </div>
  </div>
</div>
""", "04")

# ── 05 피난
page("s05", """
<style>
.viz{display:flex;gap:26px;margin-top:22px;align-items:stretch;flex:1}
.bars{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:14px;padding:26px 24px;display:flex;flex-direction:column;justify-content:center}
.b{margin-bottom:16px}
.b .lb{display:flex;justify-content:space-between;font-size:15px;font-weight:800;color:#0F2548;margin-bottom:7px}
.b .tr{height:26px;background:#EEF2F7;border-radius:6px;overflow:hidden}
.b .fi{height:100%;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;
  padding-right:10px;color:#fff;font-size:13px;font-weight:800}
</style>
<div class="pad">
  <div class="eyebrow">FINDING 02 · 안전 · 피난</div>
  <h1>소방관 진입창은 <em>20층 이하에만</em> 있습니다<br>21층 이상 <u>396세대</u>가 그 밖에 있습니다</h1>
  <div class="viz">
    <div class="bars">
      <div class="b"><div class="lb"><span>진입창 있는 세대 (20층 이하)</span><span>238세대 · 37.5%</span></div>
        <div class="tr"><div class="fi" style="width:37.5%;background:#3E6CB5">37.5%</div></div></div>
      <div class="b"><div class="lb"><span>진입창 없는 세대 (21층 이상)</span><span style="color:#C0392B">396세대 · 62.5%</span></div>
        <div class="tr"><div class="fi" style="width:62.5%;background:#C0392B">62.5%</div></div>
        <div style="font-size:12px;color:#5B6673;font-weight:700;margin-top:6px">84A 58 + 84B 27 + 84C 83 + 84D 85 + 84E 58 + 84F 27 + 105형 58 = 396세대 (7면 층별 세대수표 합산, 총 634세대 검증 완료)</div></div>
      <div class="b"><div class="lb"><span>최상층(49층)에서 피난안전구역(20층)까지</span><span style="color:#C0392B">29개 층</span></div>
        <div class="tr"><div class="fi" style="width:100%;background:#0F2548">계단으로 29개 층 하강</div></div></div>
      <div class="quote" style="margin-top:20px">"각동 20층이하는 소방관 진입을 위한 소방관진입창이 계획되어져 있으며" — 공고문 50면. 21층 이상은 그 문장에 포함되지 않습니다.</div>
    </div>
    <div style="width:430px;display:flex;flex-direction:column;gap:14px">
      <div class="panel red"><h3>층간소음도 옛 기준입니다</h3>
        <p>사업계획승인 2022.5.26 — 층간소음 사후확인제 시행(2022.8.4)보다 <b>70일 앞섭니다.</b> 2028년 11월 입주 아파트가 2022년 5월 기준으로 지어지는 셈입니다. 법적 의무가 없다는 것이지, 성능을 확인하지 못할 이유는 없습니다.</p></div>
      <div class="ask"><span class="tag">개선요구</span>21층 이상 구간에 <b>피난안전구역 1개소 추가</b> 또는 대체 피난설비(하향식 피난구 전 세대 확대) 설계 반영, 그리고 <b>층간소음 성능검사 자발적 실시·결과 공개</b>를 요구할 것.</div>
    </div>
  </div>
</div>
""", "05")

# ── 06 동·호수별 지도
page("s06", """
<style>
.map{display:flex;gap:16px;margin-top:20px;flex:1}
.bd{flex:1;border:1.5px solid #E1E7EE;border-radius:14px;overflow:hidden;display:flex;flex-direction:column;background:#fff}
.bd .h{background:#0F2548;color:#fff;padding:11px 15px}
.bd .h b{font-size:19px;font-weight:800}
.bd .h small{display:block;font-size:11.5px;color:#B9C8DE;font-weight:700;margin-top:3px;line-height:1.4}
.bd ul{list-style:none;flex:1;display:flex;flex-direction:column;justify-content:space-evenly}
.bd li{display:flex;gap:9px;padding:7px 15px;border-bottom:1px solid #F0F3F7;align-items:baseline}
.bd li:last-child{border-bottom:0}
.bd li i{font-style:normal;flex:none;width:72px;font-size:11.5px;font-weight:800;color:#3E6CB5}
.bd li span{font-size:12.3px;color:#43525F;font-weight:700;line-height:1.4}
.bd li.hot{background:#FDF2F1}.bd li.hot i{color:#C0392B}.bd li.hot span{color:#C0392B;font-weight:800}
.bd li.warn i{color:#B7791F}
</style>
<div class="pad">
  <div class="eyebrow">FINDING 03 · 동별 · 세대별</div>
  <h1>같은 단지여도 <u>동에 따라 겪는 것이 다릅니다</u></h1>
  <p class="lead">공고문 50~54면은 동별로 따로 적어 두었습니다. 흩어져 있어 한 번에 읽히지 않을 뿐, 이미 다 쓰여 있습니다.</p>
  <div class="map">
    <div class="bd"><div class="h"><b>101동</b><small>1·2·3·4·5호 &nbsp;|&nbsp; 승강기 5대 &nbsp;|&nbsp; 번영로 면하지 않음</small></div>
      <ul>
        <li class="warn"><i>옥탑</i><span>소화수조·펌프실·EV기계실 — 최상층 진동</span></li>
        <li class="warn"><i>20층</i><span>피난안전구역 + 제연휀룸실</span></li>
        <li class="hot"><i>1층 3곳</i><span>북동 램프 · 남측 진입구 · 동측 DA+램프</span></li>
        <li><i>2층</i><span>돌봄센터 · 어린이집 · 맘&amp;키즈카페</span></li>
        <li><i>지상</i><span>어린이놀이터 2개소 · 공개공지 · 키즈스테이션</span></li>
        <li><i>지하2층</i><span>급기휀룸</span></li>
        <li><i>5호라인</i><span>2층 필로티 직상부</span></li>
      </ul></div>
    <div class="bd"><div class="h"><b>102동</b><small>1·2·3·4·5호 &nbsp;|&nbsp; 승강기 5대 &nbsp;|&nbsp; 남동측 번영로 직접 면함</small></div>
      <ul>
        <li class="warn"><i>옥탑</i><span>소화수조·펌프실·EV기계실 — 최상층 진동</span></li>
        <li class="warn"><i>20층</i><span>피난안전구역 + 제연휀룸실</span></li>
        <li class="hot"><i>남동 전층</i><span>50M 대로(번영로) — 소음·빛공해</span></li>
        <li class="hot"><i>1층 북측</i><span>재활용보관소 — 소음·냄새</span></li>
        <li><i>1층 서측</i><span>차량 진입구</span></li>
        <li><i>1·2층</i><span>관리사무소 · 경로당 · 다이닝카페 · 게스트하우스</span></li>
        <li><i>5호라인</i><span>2층 필로티 직상부</span></li>
      </ul></div>
    <div class="bd"><div class="h"><b>103동</b><small>1·2·3·4호 + 오피스텔(코어 분리) &nbsp;|&nbsp; 아파트 승강기 4대 &nbsp;|&nbsp; 남동측 번영로 직접 면함</small></div>
      <ul>
        <li class="hot"><i>22층</i><span>제연휀룸이 세대와 같은 층</span></li>
        <li class="hot"><i>21층</i><span>소화수조가 세대와 같은 층 — 감액 없음</span></li>
        <li class="warn"><i>20층</i><span>피난안전구역 + 소화수조 + 제연휀룸</span></li>
        <li class="hot"><i>승강기</i><span>아파트 4대 — 오피스텔 2대는 코어 분리로 사용 불가</span></li>
        <li class="hot"><i>남동 전층</i><span>50M 대로(번영로) — 소음·빛공해</span></li>
        <li><i>1층 서측</i><span>재활용보관소 / 동측 차량 출구</span></li>
        <li><i>2층</i><span>작은도서관 · 독서실 · 오피스텔 라운지</span></li>
      </ul></div>
  </div>
  <div class="ask" style="margin-top:16px"><span class="tag">이것이 우리가 하는 일</span>법무법인 제이엘은 이 표를 <b>634세대 전 호수 단위로</b> 만들어 드립니다. 계약 전에는 호수 선택 기준으로, 사전점검에서는 세대별 확인 항목으로, 하자 대응에서는 근거 자료로 그대로 이어집니다.</div>
</div>
""", "06")

# ── 07 가격역전·자격
page("s07", """
<style>
.three{display:flex;gap:16px;margin-top:22px;flex:1}
.bx{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:14px;padding:20px 22px;display:flex;flex-direction:column;justify-content:center}
.bx h3{font-size:19px;font-weight:800;color:#0F2548;letter-spacing:-.5px;margin-bottom:10px}
.bx .big{font-size:36px;font-weight:800;color:#C0392B;letter-spacing:-1.5px;line-height:1;margin-bottom:8px}
.bx p{font-size:14px;color:#5B6673;font-weight:700;line-height:1.55}
.cmp{display:flex;gap:8px;margin:10px 0}
.cmp .cc{flex:1;border:1.5px solid #E1E7EE;border-radius:10px;padding:10px 12px;text-align:center}
.cmp .cc b{display:block;font-size:15px;font-weight:800;color:#0F2548}
.cmp .cc small{font-size:11.5px;color:#5B6673;font-weight:700}
.cmp .cc.r{border-color:#F0C6C0;background:#FDF6F5}.cmp .cc.r b{color:#C0392B}
</style>
<div class="pad">
  <div class="eyebrow">FINDING 04 · 가격 형평 · 자격</div>
  <h1>작은 집이 더 비싸고, <u>자격은 있는데 자리가 없습니다</u></h1>
  <div class="three">
    <div class="bx">
      <h3>84B — 가장 작은데 가장 비쌉니다 (6↔7면)</h3>
      <div class="cmp">
        <div class="cc r"><b>84B · 174.73㎡</b><small>3층 671,000,000원</small></div>
        <div class="cc"><b>84D · 177.97㎡</b><small>3층 658,000,000원</small></div>
      </div>
      <p>계약면적이 3.24㎡ 작은 84B가 오히려 1,300만원 비쌉니다. ㎡당 3,840,000원 vs 3,697,000원 — 3.9% 차이인데, 향·조망 등 차등 근거는 공고문 어디에도 없습니다.</p>
      <div class="quote" style="margin-top:12px">산정 근거 서면 공개를 요구할 수 있는 지점입니다.</div>
    </div>
    <div class="bx">
      <h3>9인 이상 가구 각주 누락 (14·18면)</h3>
      <div class="big">월 472,926원</div>
      <p>8인 초과 가구는 1인마다 배율을 더하는 각주가 있어야 하는데 표에서 빠졌습니다. 다자녀 가구가 <b>자기 소득기준을 낮게 계산해 자격을 스스로 포기</b>할 수 있는 크기입니다.</p>
      <div class="quote" style="margin-top:12px">정정공고와 재산정 기회 부여를 요구합니다.</div>
    </div>
    <div class="bx">
      <h3>장애인·철거주택 소유자 (9·11면)</h3>
      <div class="big">배정 0세대</div>
      <p>추천기관 3곳(울산·부산·경남 장애인복지과)까지 지정해 두었지만, 기관추천 54세대는 다른 7개 항목이 <b>정확히 전부 소진</b>합니다. 10+7+6+10+10+7+4 = 54. 신청 창구만 열려 있습니다.</p>
      <div class="quote" style="margin-top:12px">실제 배정 세대수와 산정 근거 공개를 요구합니다.</div>
    </div>
  </div>
</div>
""", "07")

# ── 08 옵션 봉쇄·모순
page("s08", """
<style>
.chain{display:flex;align-items:stretch;gap:12px;margin-top:22px}
.node{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:14px;padding:22px 20px;text-align:center;display:flex;flex-direction:column;justify-content:center}
.node b{display:block;font-size:17px;font-weight:800;color:#0F2548;margin-bottom:5px}
.node small{font-size:13.5px;color:#5B6673;font-weight:700;line-height:1.45}
.node.end{background:#C0392B;border-color:#C0392B}
.node.end b,.node.end small{color:#fff}
.arw{font-size:22px;color:#B9C4D2;font-weight:800;align-self:center}
.duo{display:flex;gap:16px;margin-top:18px;flex:1}
.p2{flex:1;background:#FDF3F2;border:1.5px solid #F0C6C0;border-radius:14px;padding:18px 20px;display:flex;flex-direction:column;justify-content:center}
.p2 h3{font-size:18px;font-weight:800;color:#C0392B;margin-bottom:8px}
.p2 p{font-size:14px;color:#43525F;font-weight:700;line-height:1.6}
.p2.g{background:#F6F9FC;border-color:#E1E7EE}.p2.g h3{color:#0F2548}
</style>
<div class="pad">
  <div class="eyebrow">FINDING 05 · 옵션 · 문서 효력</div>
  <h1>에어컨은 <em>고르든 안 고르든</em> 한쪽이 막히고,<br>문서 효력은 <u>세 번 뒤집힙니다</u></h1>
  <div class="chain">
    <div class="node"><b>추가선택 품목의 전제</b><small>"발코니 확장옵션을 선택한<br>세대에 한하여" (42·43·46면)</small></div>
    <div class="arw">→</div>
    <div class="node end"><b>시스템에어컨 미선택</b><small>"냉매 배관은 침실1, 거실에만<br>시공됩니다" — 침실2·3 배관 없음</small></div>
    <div class="arw">또는</div>
    <div class="node end"><b>시스템에어컨 선택</b><small>"기본제공 냉매매립배관 제외 …<br>스탠드형·벽걸이형 추가 설치 불가"</small></div>
  </div>
  <div class="duo">
    <div class="p2"><h3>홍보물 우선? 계약서 우선? (57 ↔ 68 ↔ 69면)</h3>
      <p>57면은 "분양 홍보물을 우선기준으로 함", 68면은 "별도의 확약 등을 근거로 권리를 주장할 수 없음", 69면은 "분양계약서를 우선합니다". 같은 공고문 안에서 우선순위가 세 번 뒤집힙니다. 카탈로그를 믿고 계약해도 분쟁 시 청구 근거가 사라질 수 있는 구조 — <b>우선순위 단일화 재고지를 요구합니다.</b></p></div>
    <div class="p2 g"><h3>총 주차대수 — 69면 어디에도 없음</h3>
      <p>634세대 + 오피스텔 + 근생 복합 단지인데 총 주차대수가 전 69면에 없습니다. '주차대수'라는 단어는 53면 기둥 간섭 안내에 한 번 나올 뿐입니다. 세대당 주차대수를 계산할 수 없으니, <b>주거·오피스텔·근생 구분 주차대수를 공고 정정으로 요구합니다.</b></p></div>
  </div>
</div>
""", "08")

# ── 09 승강기·오피스텔
page("s09", """
<style>
.duo{display:flex;gap:20px;margin-top:22px;flex:1}
.half{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:14px;padding:22px 24px;display:flex;flex-direction:column;justify-content:center}
.half h3{font-size:20px;font-weight:800;color:#0F2548;letter-spacing:-.5px;margin-bottom:12px}
.ev{display:flex;gap:10px;margin-bottom:14px}
.ev .e{flex:1;border:1.5px solid #E1E7EE;border-radius:11px;padding:14px;text-align:center}
.ev .e b{display:block;font-size:30px;font-weight:800;color:#0F2548;letter-spacing:-1px}
.ev .e small{font-size:12px;color:#5B6673;font-weight:700}
.ev .e.r{border-color:#F0C6C0;background:#FDF6F5}.ev .e.r b{color:#C0392B}
.half p{font-size:14.5px;color:#43525F;font-weight:700;line-height:1.6}
</style>
<div class="pad">
  <div class="eyebrow">FINDING 06 · 103동 구조</div>
  <h1>103동은 <em>승강기가 1대 적고</em>,<br>옆의 2대는 <u>쓸 수 없습니다</u></h1>
  <div class="duo">
    <div class="half">
      <h3>승강기 대수 (50 ↔ 53면)</h3>
      <div class="ev">
        <div class="e"><b>5대</b><small>101동 · 102동<br>(비상용·피난용 포함)</small></div>
        <div class="e r"><b>4대</b><small>103동 아파트<br>(비상용·피난용 포함)</small></div>
        <div class="e r"><b>+2대</b><small>오피스텔 전용<br>— 아파트는 사용 불가</small></div>
      </div>
      <p>50면: "103동 오피스텔은 공동주택과 코어가 분리되어 있어서 지하를 포함한 모든 층에서 EV홀이나 로비를 따로 쓰게" — 눈앞의 2대를 쓸 수 없다고 공고문이 직접 적었습니다. 그런데 103동은 21·22층 설비 동거 세대까지 있는 동입니다. <b>세대수 대비 승강기 산정 근거(주택건설기준 제15조) 서면 제시를 요구합니다.</b></p>
    </div>
    <div class="half">
      <h3>오피스텔 혼합의 비대칭 (50 · 52면)</h3>
      <p style="margin-bottom:12px">오피스텔은 커뮤니티 중 <b>비지니스라운지 하나만</b> 쓰는데, 그 라운지가 103동 2층에 있어 <b>103동 아파트 저층세대가 소음을 받습니다.</b> 이용은 못 하고 영향만 받는 구조입니다.</p>
      <p>여기에 주거·오피스텔·근생 간 <b>공용부 관리비 배분과 입주자대표회의 의결권 구조</b>는 69면 어디에도 없습니다. 입주 후 분쟁 1순위 항목이 비어 있습니다 — <b>관리규약 초안 사전 공개를 요구합니다.</b></p>
    </div>
  </div>
</div>
""", "09")

# ── 10 로드맵/클로징
page("s10", """
<style>
.rm{display:flex;gap:14px;margin-top:24px;flex:1}
.st{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:16px;padding:22px 20px;position:relative}
.st .no{font-size:34px;font-weight:800;color:#3E6CB5;opacity:.28;letter-spacing:-2px;line-height:1}
.st b{display:block;font-size:18px;font-weight:800;color:#0F2548;margin:8px 0 7px;letter-spacing:-.5px}
.st small{font-size:13.5px;color:#5B6673;font-weight:700;line-height:1.55;display:block}
.st.now{background:#0F2548;border-color:#0F2548}
.st.now .no{color:#7FA9E8;opacity:.6}.st.now b{color:#fff}.st.now small{color:#B9C8DE}
.close{margin-top:24px;background:#FDF3F2;border:1.5px solid #F0C6C0;border-radius:16px;padding:22px 26px}
.close b{font-size:22px;font-weight:800;color:#C0392B;letter-spacing:-.7px}
.close p{font-size:16px;color:#43525F;font-weight:700;margin-top:8px;line-height:1.6}
</style>
<div class="pad">
  <div class="eyebrow">WHAT WE DO NEXT</div>
  <h1>검토는 시작입니다. <u>입주까지 같은 자료로 이어갑니다</u></h1>
  <div class="rm">
    <div class="st now"><div class="no">01</div><b>공고문 전수 통독</b><small>69면 5개 구간 병렬 통독<br>단지 고유 발견 13건 · 치명 3건<br><b style="color:#FFD479">완료</b></small></div>
    <div class="st"><div class="no">02</div><b>개선요구서 제출</b><small>협의회 명의 공문 작성<br>사업주체·시공사·감리 동시 발송</small></div>
    <div class="st"><div class="no">03</div><b>회신 관리 · 협의</b><small>항목별 회신 대장 운영<br>미회신·형식회신 재요구</small></div>
    <div class="st"><div class="no">04</div><b>사전점검 체크리스트</b><small>발견 항목을 세대별 점검표로<br>21~22층 · 저층부 별도 항목</small></div>
    <div class="st"><div class="no">05</div><b>하자 대응 · 분쟁</b><small>하자담보책임 기간 관리<br>필요 시 조정·소송 대리</small></div>
  </div>
  <div class="close">
    <b>"공고문에 다 적혀 있었다"는 말을, 입주 후가 아니라 지금 듣게 해드립니다.</b>
    <p>이번 검토의 13건은 모두 <b>공고문 원문에 근거</b>하며, 어느 아파트에나 있는 상투 항목은 처음부터 뺐습니다. 남은 것은 이 단지에서만 나오는 문제들입니다.
    법무법인 제이엘은 634세대 전 호수를 같은 방식으로 검토하고, 그 결과를 사전점검과 하자 대응까지 하나의 자료로 연결합니다.</p>
  </div>
</div>
""", "10")

print("slides written:", len(os.listdir(OUT)))
