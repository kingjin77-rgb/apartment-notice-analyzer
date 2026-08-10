# -*- coding: utf-8 -*-
"""힐스테이트 광명 입예협 추가질의 회신 — PPT 10슬라이드 이내 (16:9)
   원칙: 모든 사실은 ①공고문 원문(자체 전수분석) ②공개 보도(URL 검증) ③JL 실물 산출물 중 하나에 근거.
   추정·창작 금지. 미확보 정보는 [확인 중] 표기."""
import os

OUT = "/tmp/gm/slides"
os.makedirs(OUT, exist_ok=True)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1332px;height:750px;overflow:hidden}
body{font-family:"S-Core Dream","NanumSquare","Malgun Gothic",sans-serif;background:#fff;color:#16202E;position:relative;
 word-break:keep-all;line-break:strict}
.pad{position:absolute;left:56px;right:56px;top:42px;bottom:64px;display:flex;flex-direction:column}
.eyebrow{font-size:14px;font-weight:800;color:#3E6CB5;letter-spacing:1px;margin-bottom:7px}
h1{font-size:37px;font-weight:800;color:#0F2548;letter-spacing:-1.5px;line-height:1.18}
h1 em{font-style:normal;color:#C0392B}
h1 u{text-decoration:none;background:linear-gradient(transparent 62%,#FFE08A 62%)}
.lead{font-size:15px;color:#5B6673;font-weight:700;margin-top:8px;line-height:1.55}
.bar{position:absolute;left:0;right:0;bottom:0;height:46px;background:#0F2548;display:flex;align-items:center;
  justify-content:space-between;padding:0 56px}
.bar .l{color:#fff;font-size:13px;font-weight:800}.bar .l span{color:#7FA9E8}
.bar .r{color:#8FA3C0;font-size:11px}
.pg{position:absolute;right:56px;top:36px;font-size:12px;font-weight:800;color:#B9C4D2}
.src{position:absolute;left:56px;right:56px;bottom:54px;font-size:9.5px;color:#98A4B3;font-weight:600;line-height:1.4}
table.t{width:100%;border-collapse:collapse;font-size:13.5px;background:#fff;margin-top:14px}
table.t th{background:#0F2548;color:#fff;font-size:12.5px;font-weight:800;padding:9px 11px;text-align:left}
table.t td{padding:8.5px 11px;border-bottom:1px solid #E5EAF0;font-weight:600;color:#31404F;line-height:1.45;vertical-align:top}
table.t td.n{white-space:nowrap;font-weight:800}
table.t td.red{color:#C0392B;font-weight:800}
.quote{font-size:13px;color:#5B6673;font-weight:700;background:#F7F9FC;border-left:4px solid #C0392B;
  padding:9px 12px;border-radius:0 8px 8px 0;line-height:1.5}
.tag-fact{display:inline-block;font-size:10px;font-weight:800;padding:2px 8px;border-radius:12px;background:#E8F5EE;color:#0F7B6C;vertical-align:2px}
.tag-doc{display:inline-block;font-size:10px;font-weight:800;padding:2px 8px;border-radius:12px;background:#EDF2FA;color:#3E6CB5;vertical-align:2px}
"""

BAR = ('<div class="bar"><div class="l">법무법인 <span>JL</span> 제이엘</div>'
      '<div class="r">힐스테이트 광명 입주예정자협의회 추가 질의 회신 · 2026.08</div></div>')

pages=[]
def page(body, pg=None, style=""):
    pgh=f'<div class="pg">{pg}</div>' if pg else ""
    name=f"g{len(pages)+1:02d}"
    open(f"{OUT}/{name}.html","w",encoding="utf-8").write(
      f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}{style}</style></head>'
      f'<body>{pgh}{body}{BAR}</body></html>')
    pages.append(name)

# ═══ 1. 표지 ═══
page("""
<style>
body{background:linear-gradient(155deg,#0F2548 0%,#16305C 55%,#1B3A6B 100%)}
body:before{content:"";position:absolute;inset:auto -6% -30% 52%;height:500px;
 background:repeating-linear-gradient(90deg,rgba(255,255,255,.055) 0 2px,transparent 2px 30px);transform:skewY(-9deg)}
.cv{position:absolute;left:70px;top:96px;right:70px}
.cv .tag{display:inline-block;border:1px solid rgba(255,255,255,.34);background:rgba(255,255,255,.12);
 color:#DCE7F7;font-size:14.5px;font-weight:800;padding:7px 16px;border-radius:24px}
.cv h1{color:#fff;font-size:50px;letter-spacing:-2px;margin-top:18px;line-height:1.16}
.cv h1 em{color:#8FBBFF}
.cv p{color:#B9C8DE;font-size:17px;font-weight:700;margin-top:14px;line-height:1.6}
.cv .rule{width:84px;height:5px;background:#C0392B;margin-top:20px;border-radius:3px}
.kpi{display:flex;gap:13px;margin-top:34px}
.k{flex:1;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.09);border-radius:13px;padding:15px 17px}
.k b{display:block;color:#fff;font-size:26px;font-weight:800;letter-spacing:-1px;line-height:1.05}
.k small{display:block;color:#B9C8DE;font-size:12px;font-weight:700;margin-top:6px;line-height:1.35}
.bar{background:rgba(0,0,0,.28)}
.note{margin-top:26px;color:#8FA3C0;font-size:12.5px;font-weight:700;line-height:1.5}
</style>
<div class="cv">
  <span class="tag">추가 질의 회신 · 힐스테이트 광명 입주예정자협의회 귀중</span>
  <h1>귀 단지 공고문 161,867자,<br><em>저희는 이미 전수 분석을 마쳤습니다</em></h1>
  <div class="rule"></div>
  <p>광명제11R구역 재개발 · 4,291세대(일반분양 652세대) · 현대건설·HDC현대산업개발<br>
  본 회신의 모든 사실관계는 ①공고문 원문 ②공개 보도(출처 병기) ③당 법인 실물 산출물에만 근거하며, 추정·각색을 배제했습니다.</p>
  <div class="kpi">
    <div class="k"><b>2025.11.07</b><small>정정공고 원문 전수 대조 완료<br>(당 법인 기검토 · 실물 보고서 보유)</small></div>
    <div class="k"><b>652 / 4,291</b><small>일반분양 15.2% — 소수파 구조가<br>모든 현안의 출발점</small></div>
    <div class="k"><b>14건+</b><small>공고문에서 확인한 단지 고유<br>확인·개선요구 지점</small></div>
    <div class="k"><b>9건</b><small>공개 보도로 검증한 재개발<br>일반분양 분쟁 선례</small></div>
  </div>
  <div class="note">작성 : 법무법인 제이엘 · 전담변호사 [성명 기재 예정] &nbsp;|&nbsp; 제출기한(2026.08.14 13:00) 내 회신</div>
</div>
""")

# ═══ 2. 질의① 총론: 이 단지의 구도 ═══
page("""
<style>
.duo{display:flex;gap:18px;margin-top:14px;flex:1}
.box{flex:1;background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:13px;padding:16px 18px;display:flex;flex-direction:column}
.box h3{font-size:16.5px;font-weight:800;color:#0F2548;margin-bottom:8px}
.box p{font-size:13px;color:#43525F;font-weight:600;line-height:1.6}
.donut{display:flex;align-items:center;gap:14px;margin:10px 0}
.dn{width:110px;height:110px;border-radius:50%;background:conic-gradient(#C0392B 0 54.7deg,#1B3A6B 54.7deg 360deg);
 display:flex;align-items:center;justify-content:center;flex:none}
.dn i{width:66px;height:66px;border-radius:50%;background:#F6F9FC;display:flex;align-items:center;justify-content:center;
 font-style:normal;font-size:13px;font-weight:800;color:#C0392B;text-align:center;line-height:1.2}
.leg{font-size:12.5px;font-weight:700;color:#43525F;line-height:1.7}
.leg b{color:#C0392B}
</style>
<div class="pad">
  <div class="eyebrow">질의 ① 본 아파트 맞춤형 현안 분석 — 총론</div>
  <h1>모든 현안의 뿌리는 하나입니다 —<br><em>일반분양자는 이 단지의 15.2% 소수파</em>입니다</h1>
  <div class="duo">
    <div class="box">
      <h3>구조적 위치 <span class="tag-doc">공고문 원문</span></h3>
      <div class="donut">
        <div class="dn"><i>일반<br>652세대<br>15.2%</i></div>
        <div class="leg">총 4,291세대 중<br><b>일반분양 652세대</b><br>나머지는 조합원분 등<br>— 총회 의결권도, 정보 접근도<br>조합원 중심으로 설계된 사업</div>
      </div>
      <p>재개발 일반분양자는 조합 총회에 참석할 수 없고, 관리처분·공사비 정산·설계변경 정보에서 구조적으로 소외됩니다. 그런데 그 결정들의 결과(마감 사양·입주 일정·등기 시점)는 그대로 떠안습니다. 이 비대칭을 좁히는 것이 자문의 핵심입니다.</p>
    </div>
    <div class="box">
      <h3>이미 확인된 재무 신호 <span class="tag-fact">공개 보도 검증</span></h3>
      <p style="font-size:14px;margin-bottom:8px">공사비 <b style="color:#C0392B;font-size:19px">8,720억 → 1조 3,154억 (+50.9%)</b><br>
      2021.6 수주 당시 대비 착공(2025.6) 시점 기준 — 공사기간 연장에 따른 금융비용 증가 등이 사유로 보도되었습니다.</p>
      <p>공사비가 착공 전에 이미 절반 넘게 증액된 사업은, 준공 정산 국면에서 조합-시공사 분쟁이 재점화될 개연성을 안고 갑니다. 뒤에서 보듯(5면) 그 분쟁의 비용은 번번이 일반분양자의 입주·등기 일정으로 전가되어 왔습니다. <b>계약 전부터 정산 동향을 추적하는 체계</b>가 필요한 이유입니다.</p>
    </div>
  </div>
</div>
<div class="src">출처 — 세대수·구역: 입주자모집공고(정정 2025.11.07.) 원문 / 공사비: 뉴스핌 2025.6.10. "광명11R구역 착공… 공사비 50.9% 인상" (newspim.com/news/view/20250610000852)</div>
""", "02")

# ═══ 3. 현안 1: 마감재·창호 차등 ═══
page("""
<style>
.duo{display:flex;gap:18px;margin-top:12px;flex:1}
.l{flex:1.15;display:flex;flex-direction:column;gap:10px}
.r{flex:1;display:flex;flex-direction:column;gap:10px}
.case{background:#FDF6F5;border:1.5px solid #F0C6C0;border-radius:13px;padding:14px 16px}
.case h3{font-size:15px;font-weight:800;color:#C0392B;margin-bottom:6px}
.case p{font-size:12.5px;color:#43525F;font-weight:600;line-height:1.55}
.act{background:#0F2548;color:#fff;border-radius:13px;padding:14px 17px;flex:1;display:flex;flex-direction:column;justify-content:center}
.act h3{font-size:15px;font-weight:800;color:#7FA9E8;margin-bottom:8px}
.act ol{list-style:none;font-size:13px;font-weight:700;line-height:1.55}
.act ol li{padding:4px 0;border-bottom:1px solid rgba(255,255,255,.12)}
.act ol li:last-child{border-bottom:0}
.act b{color:#FFD479}
</style>
<div class="pad">
  <div class="eyebrow">질의 ① 현안 1 — 조합원 · 일반분양 마감 차등</div>
  <h1>사양 차등을 <u>공고문이 스스로 자인</u>하고 있습니다</h1>
  <div class="duo">
    <div class="l">
      <div class="quote">"동일 주택형에 아파트라도 조합원 분양분과 일반 분양분에 대해 무상제공품목 및 마감재 등이 상이한 부분에 대하여 확인 후 청약하시기 바랍니다" — 공고문 원문</div>
      <div class="quote">"창호는 조합원 분양세대와 일반 분양세대에 대해 창호 업체, 브랜드, 사양, 성능, 디자인, 방충망의 형태 등 상이한 부분이 있습니다" — 공고문 원문</div>
      <div class="case">
        <h3>선례 — 개포 프레지던스 자이 (2020) <span class="tag-fact">보도 검증</span></h3>
        <p>조합원 세대는 알루미늄 단창, 일반분양 세대는 PVC 이중창을 적용해 외관까지 달라진 사례가 보도되었습니다(한국경제 2020.11.2.). "확인 후 청약하라"는 문구만으로 차등의 범위가 무한정 열리는 것이 문제입니다.</p>
      </div>
    </div>
    <div class="r">
      <div class="act">
        <h3>JL의 대응 — 계약 전이 골든타임입니다</h3>
        <ol>
          <li><b>①</b> 조합원분·일반분양분 <b>품목별 사양 비교표</b>(창호 업체·유리 사양·방충망 포함) 서면 공개 요구 — "상이하다"가 아니라 "무엇이 어떻게 다른지"를 특정</li>
          <li><b>②</b> 공개된 비교표를 <b>공급계약서 별지로 편철</b> 요구 — 분쟁 시 청구 근거 확보</li>
          <li><b>③</b> 견본주택 전시 세대가 일반분양 사양인지 확인 서면 징구 — 조합원 사양 전시 후 하향 시공 방지</li>
          <li><b>④</b> 회신 거부·형식 회신 시 그 자체를 기록화 — 향후 설명의무 위반 다툼의 근거</li>
        </ol>
      </div>
    </div>
  </div>
</div>
<div class="src">출처 — 공고문 인용 2건: 힐스테이트 광명 입주자모집공고(정정 2025.11.07.) 원문 / 선례: 한국경제 2020.11.2. "강남 재건축, 조합원과 일반분양자 집 창문 왜 다른가요" (hankyung.com/realestate/article/2020110256781)</div>
""", "03")

# ═══ 4. 현안 2: 12R 교통 + 뉴타운 동시개발 ═══
page("""
<style>
.duo{display:flex;gap:18px;margin-top:12px;flex:1}
.l{flex:1.1;display:flex;flex-direction:column;gap:10px}
.r{flex:1;display:flex;flex-direction:column;gap:10px}
.case{background:#FDF6F5;border:1.5px solid #F0C6C0;border-radius:13px;padding:13px 16px}
.case h3{font-size:14.5px;font-weight:800;color:#C0392B;margin-bottom:5px}
.case p{font-size:12.3px;color:#43525F;font-weight:600;line-height:1.5}
.act{background:#0F2548;color:#fff;border-radius:13px;padding:14px 17px;flex:1;display:flex;flex-direction:column;justify-content:center}
.act h3{font-size:15px;font-weight:800;color:#7FA9E8;margin-bottom:8px}
.act ol{list-style:none;font-size:12.8px;font-weight:700;line-height:1.5}
.act ol li{padding:4px 0;border-bottom:1px solid rgba(255,255,255,.12)}
.act ol li:last-child{border-bottom:0}
.act b{color:#FFD479}
</style>
<div class="pad">
  <div class="eyebrow">질의 ① 현안 2 — 인근 단지 연계 이슈 (12R구역 · 광명뉴타운 동시 개발)</div>
  <h1>버스가 단지를 떠날 수 있다고 <u>공고문이 미리 적었습니다</u></h1>
  <div class="duo">
    <div class="l">
      <div class="quote">"제12R구역 재개발사업계획에 따라 차량 진출입로가 막힌 도로가 될 수 있으며 … 기존 운행 중인 버스노선이 사업구역을 벗어나 '오리로'로 우회할 수 밖에 없는 상황입니다. 따라서 입주 후 버스노선 서비스를 받기 위해서는 '오리로' 도로변까지 도보 등으로 이동해야 할 수 있습니다" — 공고문 원문(11-2R구역)</div>
      <div class="case">
        <h3>규모 인식 — 광명뉴타운 약 2.8만 세대 동시 개발 <span class="tag-fact">보도 검증</span></h3>
        <p>2030년까지 12개 구역 약 2만 8천 세대가 순차 입주 예정으로 보도되고 있습니다(에너지경제 2025.11.10.). 12R구역은 사업시행계획 수정 확정·이주 단계 보도가 있어, 공고문이 예고한 진출입로 폐쇄가 현실화되는 시간표 위에 있습니다.</p>
      </div>
      <div class="case">
        <h3>선례 — 이문·휘경뉴타운 (2025) <span class="tag-fact">보도 검증</span></h3>
        <p>약 1.3만 세대가 순차 입주했으나 간선도로는 재개발 전 편도 2차선 그대로 — 상시 정체가 보도되었습니다. 단지 하나가 아니라 <b>구역 전체의 입주 총량 대비 도로 계획</b>을 봐야 한다는 선례입니다.</p>
      </div>
    </div>
    <div class="r">
      <div class="act">
        <h3>JL의 대응 — 상대는 사업주체와 광명시, 둘입니다</h3>
        <ol>
          <li><b>①</b> 사업주체에 12R구역 진행 단계별 <b>교통 영향과 대응 계획 정기 공유</b>를 서면 확약 요구</li>
          <li><b>②</b> 진출입로 폐쇄 확정 시 <b>대체 교통(마을버스 노선 신설·정류장 위치)</b>을 광명시와 사전 협의하도록 요구 — 협의회 명의 민원·정보공개청구 병행</li>
          <li><b>③</b> 광명시에 <b>구역별 준공 시차와 도로 개통 연동 계획</b> 정보공개청구 — 공고문 밖의 사실관계를 협의회가 직접 확보</li>
          <li><b>④</b> 학군 배정(광명교육지원청 추후 결정 사항) 진행 상황 조회 및 대응</li>
        </ol>
      </div>
    </div>
  </div>
</div>
<div class="src">출처 — 공고문 인용: 정정공고(2025.11.07.) 원문 / 광명뉴타운 규모: 에너지경제 2025.11.10.(m.ekn.kr/view.php?key=20251110027575620) / 12R구역: 아유경제·위클리한국주택경제신문 보도 / 이문·휘경: 리버티이코노미데스크(ledesk.co.kr/view.php?uid=15197)</div>
""", "04")

# ═══ 5. 현안 3: 동별 리스크 ═══
page("""
<style>
table.t td{font-size:12.8px}
.note2{margin-top:10px;background:#FDF3F2;border:1.5px solid #F0C6C0;border-radius:11px;padding:11px 14px;
 font-size:12.8px;font-weight:700;color:#43525F;line-height:1.55}
.note2 b{color:#C0392B}
</style>
<div class="pad">
  <div class="eyebrow">질의 ① 현안 3 — 동별 · 세대별 리스크 (공고문이 동 번호를 직접 지목한 것만)</div>
  <h1>같은 단지 안에서도 <em>내 동이 어디냐</em>에 따라 다릅니다</h1>
  <table class="t">
    <tr><th style="width:250px">대상 동</th><th style="width:150px">유형</th><th>공고문이 적은 내용</th></tr>
    <tr><td class="n">104·105·204·205·212동</td><td class="n red">지하철 진동</td><td>지하철 7호선(광명사거리역)이 인접 운행 중 — 지하층 구조·흙막이 설계가 실시설계 시 변경될 수 있음</td></tr>
    <tr><td class="n">103·203동</td><td class="n red">옥탑 소화수조</td><td>옥탑 소화수조 인접 세대는 소음·진동 등 환경권 침해 발생 가능</td></tr>
    <tr><td class="n">16개동 (101~211 중)</td><td class="n">이동통신 설비</td><td>옥상층 중계기·옥외안테나 설치 예정 — "추후 이의제기 불가" 명시</td></tr>
    <tr><td class="n">301~303동</td><td class="n red">내진능력 편차</td><td>Ⅶ-0.158g로 공개 — 다른 동군(0.197~0.204g)보다 낮은 사유가 원문에 없음. 공개 데이터(지반정보포털·건축HUB·기상청) 조사로도 확인 불가 — 서면 확인이 유일한 경로</td></tr>
    <tr><td class="n">11-2R구역 전체</td><td class="n">교통</td><td>12R구역 진행 시 버스노선 '오리로' 우회 가능(4면 참조)</td></tr>
  </table>
  <div class="note2"><b>JL의 대응 :</b> 위 동 해당 입주예정자에게 <b>계약 전 개별 안내문 발송</b>을 사업주체에 요구하고, 301~303동 내진 편차 사유(지반·구조형식)의 <b>서면 회신</b>을 요구합니다. 당 법인은 이미 이 매트릭스를 배치도 위에 표시한 자료로 보유하고 있으며, 수임 시 <b>전 세대 호수 단위 유의사항 지도</b>로 확장해 계약 전 확인 → 사전점검 → 하자 대응까지 같은 자료로 연결합니다.</div>
</div>
<div class="src">출처 — 전 항목: 힐스테이트 광명 입주자모집공고(정정 2025.11.07.) 원문에서 동 번호가 직접 언급된 조항 전수 추출(법무법인 제이엘 검토보고서, 검토기준일 2026.7.27.) / 내진 공개데이터 조사: 국토지반정보포털·건축HUB·기상청 확인 결과</div>
""", "05")

# ═══ 6. 질의② 분쟁 유형: 검증 사례 ═══
page("""
<style>
.tl{display:flex;flex-direction:column;gap:0;margin-top:12px;flex:1;justify-content:space-evenly}
.ev{display:flex;gap:14px;align-items:flex-start;padding:7px 0;border-bottom:1px solid #EDF1F6}
.ev:last-child{border-bottom:0}
.ev .when{flex:none;width:150px;font-size:12.5px;font-weight:800;color:#0F2548;padding-top:2px}
.ev .what{flex:1;font-size:12.8px;font-weight:600;color:#31404F;line-height:1.5}
.ev .what b{color:#C0392B}
.ev .les{flex:none;width:330px;font-size:12px;font-weight:700;color:#1B3A6B;background:#EDF2FA;border-radius:9px;padding:8px 11px;line-height:1.45}
</style>
<div class="pad">
  <div class="eyebrow">질의 ② 재개발 조합사업의 일반분양자 주요 분쟁 — 전부 공개 보도로 검증된 실제 사례입니다</div>
  <h1>분쟁은 <u>계약 후 입주 전후의 전 구간</u>에서 터졌습니다</h1>
  <div class="tl">
    <div class="ev"><div class="when">착공~분양<br><span style="color:#98A4B3;font-size:11px">둔촌주공 · 2022</span></div>
      <div class="what">조합-시공사업단 공사비 분쟁으로 <b>공사 전면 중단 6개월</b> — 일반분양 4,786가구 일정이 수년 단위로 표류, 지연 기간의 비용이 분양가에 반영</div>
      <div class="les">계약 전 조합-시공사 소송·가처분 유무 확인, 지체상금·중도금 연장 조항 점검</div></div>
    <div class="ev"><div class="when">시공 중<br><span style="color:#98A4B3;font-size:11px">은평 대조1구역 · 2024</span></div>
      <div class="what">조합 내분 → 일반분양 지연 → 공사비 미수금 약 1,800억 → <b>시공사 공사 중단</b> — 준공 일정 반복 표류</div>
      <div class="les">조합 집행부 소송 이력·공사비 미지급 여부가 곧 일반분양자 리스크</div></div>
    <div class="ev"><div class="when">준공 직전<br><span style="color:#98A4B3;font-size:11px">서초 메이플자이 · 2025</span></div>
      <div class="what">시공사 3,000억대 증액 요구·<b>유치권 예고로 입주 지연 위기</b> — 서울시 코디네이터 중재로 합의, 입주 지연 모면</div>
      <div class="les">준공 6개월 전부터 정산 협상 동향 추적 — 지자체 중재 제도가 실효적 수단</div></div>
    <div class="ev"><div class="when">입주 후<br><span style="color:#98A4B3;font-size:11px">송파 헬리오시티 · 2020</span></div>
      <div class="what">조합 분쟁으로 <b>1년 넘게 보존등기 지연</b> — 일반분양자 528명이 조합 상대 집단소송(주담대 불가·양도세 비과세 요건 위험)</div>
      <div class="les">이전고시·등기 일정은 조합 소관 — 지연 손해배상 기준을 계약 단계부터 인지</div></div>
    <div class="ev"><div class="when">입주 후<br><span style="color:#98A4B3;font-size:11px">장위자이 레디언트 · 2026</span></div>
      <div class="what">임시사용승인 입주 후 <b>준공승인 지연으로 등기 불가</b> — 소송 방식을 두고 조합원과 일반분양자 간 의견 대립까지 보도</div>
      <div class="les">'임시사용승인 입주'는 미완성 입주 — 권리구제 국면에서 조합원과 이해가 갈릴 수 있음을 전제로 전략 수립</div></div>
  </div>
</div>
<div class="src">출처 — 둔촌주공: 비즈워치 2022.4.14. 외 복수 / 대조1구역: 파이낸셜뉴스 2024.1.14. 외 / 메이플자이: 뉴스1 2025.4.18. 외 / 헬리오시티: 파이낸셜뉴스 2020.5.26. 외 / 장위자이: 머니투데이 2026.3.18. — 전 사례 기사 본문 확인 완료(URL 목록 별첨 가능)</div>
""", "06")

# ═══ 7. 질의② 해결 시나리오 ═══
page("""
<style>
.rm{display:flex;gap:12px;margin-top:14px;flex:1}
.st{flex:1;background:#fff;border:1.5px solid #E1E7EE;border-radius:13px;padding:16px 15px;display:flex;flex-direction:column}
.st .no{font-size:24px;font-weight:800;color:#3E6CB5;opacity:.3;line-height:1}
.st b{display:block;font-size:15px;font-weight:800;color:#0F2548;margin:6px 0 7px;line-height:1.3}
.st ul{list-style:none;font-size:12px;font-weight:700;color:#43525F;line-height:1.5;flex:1}
.st ul li{padding:3px 0;border-bottom:1px solid #F0F3F7}
.st ul li:last-child{border-bottom:0}
.st .why{margin-top:8px;font-size:10.5px;font-weight:700;color:#98A4B3}
.st.hot{border-color:#F0C6C0;background:#FDFAF9}
.st.hot .no{color:#C0392B;opacity:.35}
</style>
<div class="pad">
  <div class="eyebrow">질의 ② 해결 방안 — 시점별 실행 시나리오 (앞 면의 실제 분쟁이 터진 지점마다 예방 조치를 배치)</div>
  <h1>이기는 방법은 소송이 아니라 <u>시점을 놓치지 않는 것</u>입니다</h1>
  <div class="rm">
    <div class="st hot"><div class="no">01</div><b>계약 전<br>(지금)</b>
      <ul><li>공고문 전수 검토 — <b style="display:inline;color:#C0392B">완료</b></li>
      <li>마감 사양 비교표 공개·계약서 별지화 요구</li><li>조합-시공 공사비 정산 구조 파악</li><li>동별 리스크 개별 고지 요구</li></ul>
      <div class="why">개포·둔촌 선례의 예방 지점</div></div>
    <div class="st"><div class="no">02</div><b>공사 중</b>
      <ul><li>협의회 명의 개선요구서 제출 · 항목별 회신 대장 운영</li><li>12R구역·공사비 동향 분기 모니터링</li><li>설계변경·구조형식 변경 통지 요구</li><li>광명시 정보공개청구 병행</li></ul>
      <div class="why">대조1구역 선례의 예방 지점</div></div>
    <div class="st"><div class="no">03</div><b>준공 전후</b>
      <ul><li>정산 분쟁 조짐 시 지자체 중재(코디네이터) 신청 검토</li><li>'사용승인 vs 임시사용승인' 확인</li><li>사전점검 — 동·호수별 체크리스트(사양 비교표와 대조)</li></ul>
      <div class="why">메이플자이·장위자이 선례의 예방 지점</div></div>
    <div class="st hot"><div class="no">04</div><b>입주 후<br>~조합 해산 전</b>
      <ul><li>이전고시·보존등기 일정 관리, 지연 시 손해배상 검토</li><li>입대의 구성 즉시 하자보수보증금 채권 확보</li><li>조합 해산 전 하자조사 완료 — 채권자대위·채권양도로 시공사 직접 청구 경로 확보</li></ul>
      <div class="why">헬리오시티 선례 + 조합 무자력 대비 실무</div></div>
  </div>
</div>
<div class="src">근거 — 각 단계 실무: 공개 보도 검증 사례(6면)의 발생 시점 역산 / 조합 해산 후 청구 실무(채권자대위·채권양도): 한국아파트신문 법률기고(hapt.co.kr/news/articleView.html?idxno=161342) — 개별 사안 적용은 수임 후 사실관계 확인을 전제로 합니다</div>
""", "07")

# ═══ 8. 수행 실적 (실물 기반) ═══
page("""
<style>
.duo{display:flex;gap:16px;margin-top:12px;flex:1}
.big{flex:1.2;background:#0F2548;border-radius:14px;padding:18px 20px;color:#fff;display:flex;flex-direction:column;justify-content:center}
.big h3{font-size:17px;font-weight:800;color:#7FA9E8;margin-bottom:10px}
.big p{font-size:13.5px;font-weight:700;line-height:1.65;color:#DCE7F7}
.big b{color:#FFD479}
.r{flex:1;display:flex;flex-direction:column;gap:10px}
.itm{background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:12px;padding:12px 15px}
.itm h4{font-size:13.5px;font-weight:800;color:#0F2548;margin-bottom:4px}
.itm p{font-size:12px;font-weight:600;color:#5B6673;line-height:1.5}
.itm.wait{border-style:dashed;background:#FFFDF5;border-color:#E8D9A8}
.itm.wait h4{color:#8A6D1F}
</style>
<div class="pad">
  <div class="eyebrow">수행 실적 · 방법론 — 실물이 있는 것만 적었습니다</div>
  <h1>일반론이 아니라, <em>귀 단지 분석 실물</em>로 답합니다</h1>
  <div class="duo">
    <div class="big">
      <h3>힐스테이트 광명 — 이미 검토를 마친 상태에서 이 회신을 드립니다</h3>
      <p>정정공고(2025.11.07.) 원문 161,867자를 전수 대조한 <b>검토보고서를 이미 작성·보유</b>하고 있습니다(검토기준일 2026.7.27.). 조합원·일반분양 사양 차등, 12R구역 교통, 동별 유의사항(지하철 진동 5개동·소화수조 2개동·중계기 16개동), 내진 동별 편차, 입주 후 소음 포괄면책, 27개월 부대시설 무상사용 등 <b>14건 이상의 확인·개선요구 지점</b>을 조항 원문과 함께 정리해 두었습니다.<br><br>
      선정 즉시 이 보고서 전문과 <b>개선요구서 초안</b>을 협의회에 제출할 수 있습니다 — 착수까지의 공백이 없습니다.</p>
    </div>
    <div class="r">
      <div class="itm"><h4>분양공고문 전수 검토 체계 (실물 보유)</h4>
        <p>수도권·지방 8개 단지 입주자모집공고 검토보고서 작성 — 공고문 전면 통독, 상투 조항 배제, 원문 재대조를 표준 절차로 운영</p></div>
      <div class="itm"><h4>입주예정자협의회 개선요구 실무 (실물 보유)</h4>
        <p>수원 소재 단지 입예협 개선요구사항 문서 작성 수행 — 조항별 원문 인용·요구 문안·회신 관리 구조</p></div>
      <div class="itm"><h4>공공데이터 교차검증</h4>
        <p>카카오맵·V-World 용도지역·법제처 현행법 API 실측 대조 — 귀 단지 입지·조망권 분석에 이미 적용</p></div>
      <div class="itm wait"><h4>정비사업 수임 사례 상세</h4>
        <p>대면 PT 시 전담변호사가 사건 단위로 직접 설명드립니다 [상세 자료 준비 중]</p></div>
    </div>
  </div>
</div>
<div class="src">위 실적은 전부 당 법인이 실물 문서로 보유한 것이며, 대면 PT 시 원본 제시가 가능합니다. 타 단지 자료는 의뢰인 관계를 고려해 단지명을 일부 익명 처리했습니다.</div>
""", "08")

# ═══ 9. 클로징 ═══
page("""
<style>
.duo{display:flex;gap:18px;margin-top:14px;flex:1}
.box{flex:1;background:#F6F9FC;border:1.5px solid #E1E7EE;border-radius:13px;padding:17px 19px;display:flex;flex-direction:column;justify-content:center}
.box h3{font-size:18px;font-weight:800;color:#0F2548;margin-bottom:11px}
.box ul{list-style:none;font-size:14.5px;font-weight:700;color:#43525F;line-height:1.75}
.box ul li{padding:7px 0;border-bottom:1px solid #E9EEF4}.box ul li:last-child{border-bottom:0}
.box ul b{color:#0F2548}
.close{margin-top:12px;background:#FDF3F2;border:1.5px solid #F0C6C0;border-radius:13px;padding:15px 19px}
.close b{font-size:19px;font-weight:800;color:#C0392B}
.close p{font-size:14px;color:#43525F;font-weight:700;margin-top:5px;line-height:1.6}
</style>
<div class="pad">
  <div class="eyebrow">맺음말</div>
  <h1>약속드릴 수 있는 것만 <u>약속드립니다</u></h1>
  <div class="duo">
    <div class="box">
      <h3>선정 시 30일 내 이행 사항</h3>
      <ul>
        <li><b>①</b> 기보유 검토보고서 전문 + 개선요구서 초안 즉시 제출 (착수 공백 없음)</li>
        <li><b>②</b> 조합원·일반분양 사양 비교표 공개 요구 발송 및 회신 대장 개설</li>
        <li><b>③</b> 동별 리스크 개별 고지 요구 (지목 동 입주예정자 대상)</li>
        <li><b>④</b> 12R구역·공사비 정산 동향 첫 분기 모니터링 보고</li>
      </ul>
    </div>
    <div class="box">
      <h3>일하는 원칙</h3>
      <ul>
        <li><b>·</b> 모든 주장에 공고문 면수 또는 공개 출처를 병기합니다 — 본 회신서가 그 방식 그대로입니다</li>
        <li><b>·</b> 어느 단지에나 있는 상투 조항은 문제 삼지 않습니다 — 이 단지에만 있는 것에 집중합니다</li>
        <li><b>·</b> 확인되지 않은 것은 "확인이 필요하다"고 말씀드립니다</li>
        <li><b>·</b> 검토 자료는 사전점검·하자 대응까지 같은 체계로 이어집니다</li>
      </ul>
    </div>
  </div>
  <div class="close">
    <b>"공고문에 다 적혀 있었다"는 말을, 입주 후가 아니라 지금 들으시게 하겠습니다.</b>
    <p>법무법인 제이엘 · 전담변호사 [성명] · 연락처 [기재] — 대면 PT(2026.8.22.)에는 계약 시 실제 전담할 변호사가 직접 발표합니다.</p>
  </div>
</div>
<div class="src">본 회신서의 사실관계 출처 일람과 검토보고서 목차는 요청 시 즉시 제출 가능합니다.</div>
""", "09")

print("pages:", len(pages))
import json; open(f"{OUT}/_list.json","w").write(json.dumps(pages))
