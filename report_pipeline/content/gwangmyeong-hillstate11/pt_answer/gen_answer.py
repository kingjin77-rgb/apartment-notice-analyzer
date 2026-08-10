# -*- coding: utf-8 -*-
"""힐스테이트 광명 입예협 추가질의 회신 — 보고서체 (구호 배제, 분석 중심)
   모든 사실: ①공고문 원문 ②공개 보도(본문 확인) ③JL 실물 산출물. 추정은 '분석'으로 명시 구분."""
import os

OUT = "/tmp/gm/slides"
os.makedirs(OUT, exist_ok=True)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1332px;height:750px;overflow:hidden}
body{font-family:"S-Core Dream","NanumSquare","Malgun Gothic",sans-serif;background:#fff;color:#16202E;position:relative;
 word-break:keep-all;line-break:strict}
.pad{position:absolute;left:56px;right:56px;top:40px;bottom:62px;display:flex;flex-direction:column}
.crumb{font-size:13.5px;font-weight:800;color:#3E6CB5;letter-spacing:.4px;margin-bottom:6px}
h1{font-size:28px;font-weight:800;color:#0F2548;letter-spacing:-1px;line-height:1.25;border-bottom:2.5px solid #0F2548;padding-bottom:9px}
.bar{position:absolute;left:0;right:0;bottom:0;height:44px;background:#0F2548;display:flex;align-items:center;
  justify-content:space-between;padding:0 56px}
.bar .l{color:#fff;font-size:12.5px;font-weight:800}.bar .l span{color:#7FA9E8}
.bar .r{color:#8FA3C0;font-size:11px}
.pg{position:absolute;right:56px;top:36px;font-size:12px;font-weight:800;color:#B9C4D2}
.src{position:absolute;left:56px;right:56px;bottom:52px;font-size:9.3px;color:#98A4B3;font-weight:600;line-height:1.4}
table.t{width:100%;border-collapse:collapse;font-size:12.8px;background:#fff;margin-top:12px}
table.t th{background:#0F2548;color:#fff;font-size:12px;font-weight:800;padding:8px 10px;text-align:left}
table.t td{padding:8px 10px;border-bottom:1px solid #E5EAF0;font-weight:600;color:#31404F;line-height:1.45;vertical-align:top}
table.t td.n{white-space:nowrap;font-weight:800}
table.t td.red{color:#C0392B;font-weight:800}
table.t tr.alt td{background:#F9FBFD}
.quote{font-size:12.3px;color:#5B6673;font-weight:600;background:#F7F9FC;border-left:3px solid #C0392B;
  padding:8px 11px;border-radius:0 6px 6px 0;line-height:1.5}
.sec{font-size:15px;font-weight:800;color:#0F2548;margin:13px 0 6px}
.sec small{font-weight:700;color:#98A4B3;font-size:11px;margin-left:6px}
p.body{font-size:13px;font-weight:600;color:#31404F;line-height:1.62}
p.body b{color:#0F2548}
.an{background:#FFFDF2;border:1px solid #E8DCA8;border-radius:8px;padding:9px 12px;font-size:12.5px;font-weight:600;
 color:#5B5233;line-height:1.55;margin-top:8px}
.an b{color:#8A6D1F}
.fix{background:#EDF2FA;border:1px solid #C9D6E8;border-radius:8px;padding:9px 12px;font-size:12.5px;font-weight:600;
 color:#1B3A6B;line-height:1.55;margin-top:8px}
.fix b{color:#0F2548}
.tagF{display:inline-block;font-size:9.5px;font-weight:800;padding:1.5px 7px;border-radius:10px;background:#E8F5EE;color:#0F7B6C;vertical-align:1.5px}
.tagD{display:inline-block;font-size:9.5px;font-weight:800;padding:1.5px 7px;border-radius:10px;background:#EDF2FA;color:#3E6CB5;vertical-align:1.5px}
.tagA{display:inline-block;font-size:9.5px;font-weight:800;padding:1.5px 7px;border-radius:10px;background:#FFF3D6;color:#8A6D1F;vertical-align:1.5px}
"""

BAR = ('<div class="bar"><div class="l">법무법인 <span>JL</span> 제이엘</div>'
      '<div class="r">힐스테이트 광명 입주예정자협의회 · 추가 질의 회신서 · 2026.08</div></div>')

pages=[]
def page(body, pg=None, style=""):
    pgh=f'<div class="pg">{pg}</div>' if pg else ""
    name=f"g{len(pages)+1:02d}"
    open(f"{OUT}/{name}.html","w",encoding="utf-8").write(
      f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}{style}</style></head>'
      f'<body>{pgh}{body}{BAR}</body></html>')
    pages.append(name)

# ═══ 1. 표지 (사무적) ═══
page("""
<style>
body{background:#0F2548}
.cv{position:absolute;left:80px;top:110px;right:80px}
.cv .to{color:#7FA9E8;font-size:16px;font-weight:800;letter-spacing:.5px}
.cv h1{color:#fff;font-size:42px;letter-spacing:-1.6px;margin-top:14px;line-height:1.3;border:0;padding:0}
.cv .rule{width:100%;height:1px;background:rgba(255,255,255,.25);margin:26px 0}
.meta{display:grid;grid-template-columns:150px 1fr;gap:9px 18px;font-size:15px;color:#DCE7F7;font-weight:700;line-height:1.5}
.meta .k{color:#8FA3C0;font-weight:800}
.pr{margin-top:30px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.18);border-radius:12px;
 padding:16px 20px;font-size:13.5px;color:#B9C8DE;font-weight:600;line-height:1.65}
.pr b{color:#fff}
.bar{background:rgba(0,0,0,.3)}
</style>
<div class="cv">
  <div class="to">힐스테이트 광명 입주예정자협의회 귀중</div>
  <h1>법무법인 선임 관련 추가 질의에 대한 회신</h1>
  <div class="rule"></div>
  <div class="meta">
    <span class="k">회신 항목</span><span>① 본 아파트 맞춤형 현안 분석 및 대응 전략 &nbsp;② 재개발 조합사업의 일반분양자 대상 주요 분쟁 사례 및 해결 방안 &nbsp;③ 일반분양자 권익 보호 수행 사례 및 시나리오</span>
    <span class="k">대상 단지</span><span>힐스테이트 광명 (광명제11R구역 재개발 · 총 4,291세대 중 일반분양 652세대 · 현대건설㈜·HDC현대산업개발㈜)</span>
    <span class="k">검토 자료</span><span>입주자모집공고(정정 2025.11.07.) 원문 전문 — 당 법인이 2026.7월 전수 검토를 완료하여 검토보고서를 기보유</span>
    <span class="k">작성</span><span>법무법인 제이엘 · 전담변호사 [성명] &nbsp;|&nbsp; 제출: 2026.08.14. 13:00 기한 내</span>
  </div>
  <div class="pr"><b>작성 원칙.</b> 본 회신서의 사실관계는 ① 공고문 원문 ② 언론 보도(본문 확인분에 한함, 출처 병기) ③ 당 법인이 실물로 보유한 산출물의 세 가지에만 근거하였습니다.
  당 법인의 해석·전망은 본문에 <b>[분석]</b>으로 별도 표시하여 사실과 구분하였고, 확인되지 않은 사항은 확인이 필요하다고 기재하였습니다.</div>
</div>
""")

# ═══ 2. 질의① 현안 개관 ═══
page("""
<div class="pad">
  <div class="crumb">질의 ① 본 아파트 맞춤형 현안 분석 및 대응 전략 — 1/4</div>
  <h1>당 단지 특화 현안 개관</h1>
  <p class="body" style="margin-top:10px">당 법인은 귀 단지 입주자모집공고(정정 2025.11.07.) 원문을 전수 검토한 결과, 일반분양자 관점에서 관리가 필요한
  현안을 아래와 같이 식별하였습니다. 어느 단지에나 있는 일반 조항은 제외하고 <b>귀 단지 공고문에 특유한 사항</b>만 수록하였으며,
  각 현안의 상세 분석과 해결 방안은 3~5면에 기술합니다.</p>
  <table class="t">
    <tr><th style="width:210px">현안</th><th style="width:295px">근거 (공고문 원문 기재)</th><th style="width:118px">성격</th><th>대응 방향 (요지)</th></tr>
    <tr><td class="n">1. 조합원·일반분양 마감사양 차등</td><td>무상제공품목·마감재·창호(업체·브랜드·사양·성능·방충망) 상이함을 원문이 명시</td><td class="red">조합-일반분양자 간</td><td>품목별 사양 비교표 서면 공개 → 공급계약서 별지 편철 (3면)</td></tr>
    <tr class="alt"><td class="n">2. 제12R구역 진행에 따른 교통 변동</td><td>진출입로 폐쇄 시 버스노선 '오리로' 우회 가능성을 원문이 직접 고지</td><td class="red">인근 단지 연계</td><td>사업주체·광명시 이원 대응, 정보공개청구 병행 (4면)</td></tr>
    <tr><td class="n">3. 광명뉴타운 동시 개발 부하</td><td>— (공고문 외 사항: 12개 구역 약 2.8만 세대 개발 보도)</td><td class="red">인근 단지 연계</td><td>구역별 준공 시차·기반시설 계획 조회 및 대응 (4면)</td></tr>
    <tr class="alt"><td class="n">4. 동별 리스크 — 지하철·소화수조·중계기</td><td>7호선 인접 5개동, 옥탑 소화수조 2개동, 중계기 16개동을 원문이 지목</td><td>물리적·세대별</td><td>해당 동 계약자 개별 고지 요구, 호수 단위 관리 (5면)</td></tr>
    <tr><td class="n">5. 내진능력 동군 간 편차</td><td>301~303동 Ⅶ-0.158g — 타 동군(0.197~0.204g) 대비 낮으나 사유 미기재</td><td>물리적·세대별</td><td>산정 근거(지반·구조형식) 서면 확인 요구 (5면)</td></tr>
    <tr class="alt"><td class="n">6. 입주 후 소음 이의제기 제한</td><td>입주 후 교통량 증가로 소음 심화 시 행정청 이의제기·보상요구 불가 취지 기재</td><td>계약 조항</td><td>사용검사 시점 소음 측정치 입주 전 공개 요구</td></tr>
    <tr><td class="n">7. 부대시설 장기 무상사용</td><td>입주지원센터·A/S센터로 최대 27개월 무상사용, 임대료·이전 요구 금지</td><td>계약 조항</td><td>사용 위치·면적 사전 공개, 상응 보상 협의</td></tr>
    <tr class="alt"><td class="n">8. 공사비 증액 이력</td><td>— (공고문 외 사항: 8,720억→1조 3,154억, +50.9% 보도)</td><td class="red">조합-일반분양자 간</td><td>준공 정산 국면 분쟁 가능성 상시 모니터링 (4·6면)</td></tr>
  </table>
</div>
<div class="src">근거 — 현안 1·2·4·5·6·7: 입주자모집공고(정정 2025.11.07.) 원문 조항(당 법인 검토보고서에 조항 원문 전문 수록) / 현안 3: 에너지경제 2025.11.10. / 현안 8: 뉴스핌 2025.6.10. "광명11R구역 착공… 공사비 50.9% 인상"</div>
""", "02")

# ═══ 3. 현안 1 상세 ═══
page("""
<div class="pad">
  <div class="crumb">질의 ① — 2/4</div>
  <h1>현안 1. 조합원 분양분과 일반분양분 간 마감사양 차등</h1>
  <div class="sec">가. 사실관계 <span class="tagD">공고문 원문</span></div>
  <div class="quote">"동일 주택형에 아파트라도 조합원 분양분과 일반 분양분에 대해 무상제공품목 및 마감재 등이 상이한 부분에 대하여 확인 후 청약하시기 바랍니다" /
  "창호는 조합원 분양세대와 일반 분양세대에 대해 창호 업체, 브랜드, 사양, 성능, 디자인, 방충망의 형태 등 상이한 부분이 있습니다"</div>
  <div class="sec">나. 분석 <span class="tagA">당 법인 분석</span></div>
  <p class="body">위 조항의 문제는 차등의 존재가 아니라 <b>차등의 내용이 특정되어 있지 않다는 점</b>입니다. "상이하다"는 고지만으로는 계약자가
  무엇을 포기하고 계약하는지 알 수 없어, 입주 후 사양 분쟁 시 "확인 후 청약하라고 고지했다"는 항변의 근거로 기능하게 됩니다.
  실제로 재건축 단지에서 조합원 세대에 알루미늄 단창, 일반분양 세대에 PVC 이중창이 적용되어 외관 차이까지 발생한 사례가 보도된 바 있으며(개포 프레지던스 자이, 2020),
  분양가 규제 하에서 일반분양분 사양을 낮추는 방식은 구조적으로 반복될 수 있습니다. 귀 단지는 착공 전 공사비가 이미 50.9% 증액된 사업이므로(2면 현안 8),
  원가 압박이 일반분양분 사양으로 전가될 유인이 상대적으로 큰 조건입니다.</p>
  <div class="sec">다. 해결 방안 (실행 순서대로)</div>
  <div class="fix"><b>제1단계 — 특정.</b> 사업주체에 조합원분·일반분양분의 품목별 사양 비교표(창호 제조사·유리 구성·프레임 재질·방충망 형태, 주방가구·위생도기·바닥재 제조사 및 모델 포함) 서면 공개를 요구합니다.
  요구 근거는 공고문 스스로 "확인 후 청약"을 요구하고 있다는 점 — 확인 대상을 특정해 달라는 요구이므로 거부 명분이 약합니다.<br>
  <b>제2단계 — 고정.</b> 공개된 비교표를 공급계약서 별지 또는 확약서로 편철할 것을 요구합니다. 이로써 향후 하향 시공 시 채무불이행 청구의 근거 문서가 확보됩니다.<br>
  <b>제3단계 — 검증.</b> 견본주택 전시 세대가 일반분양 사양인지 서면 확인을 받고, 사전점검 시 비교표와 실제 시공을 세대별로 대조합니다(당 법인 체크리스트 체계, 8면).<br>
  <b>제4단계 — 기록.</b> 공개 거부·불완전 회신 시 그 자체를 회신 대장에 기록화합니다. 거부 기록은 향후 표시·광고 및 설명의무 관련 다툼에서 협의회 측 정황 증거가 됩니다.</div>
</div>
<div class="src">출처 — 공고문 인용: 정정공고(2025.11.07.) 원문 / 개포 프레지던스 자이: 한국경제 2020.11.2.(hankyung.com/realestate/article/2020110256781, 본문 확인) / 공사비 증액: 뉴스핌 2025.6.10.</div>
""", "03")

# ═══ 4. 현안 2·3 상세 (인근 연계) ═══
page("""
<style>
.tl{display:flex;gap:0;margin-top:8px;border:1.5px solid #E1E7EE;border-radius:10px;overflow:hidden}
.tl .c{flex:1;padding:10px 12px;border-right:1px solid #E5EAF0;font-size:11.8px;font-weight:600;color:#31404F;line-height:1.45}
.tl .c:last-child{border-right:0}
.tl .c b{display:block;font-size:12.5px;color:#0F2548;font-weight:800;margin-bottom:3px}
.tl .c.hot{background:#FDF6F5}.tl .c.hot b{color:#C0392B}
</style>
<div class="pad">
  <div class="crumb">질의 ① — 3/4</div>
  <h1>현안 2·3. 제12R구역 진행 및 광명뉴타운 동시 개발에 따른 연계 영향</h1>
  <div class="sec">가. 사실관계 <span class="tagD">공고문 원문</span> <span class="tagF">보도 확인</span></div>
  <div class="quote">"제12R구역 재개발사업계획에 따라 차량 진출입로가 막힌 도로가 될 수 있으며 … 기존 운행 중인 버스노선이 사업구역을 벗어나 '오리로'로 우회할 수 밖에 없는 상황입니다.
  따라서 입주 후 버스노선 서비스를 받기 위해서는 '오리로' 도로변까지 도보 등으로 이동해야 할 수 있습니다" — 공고문 원문(11-2R구역 관련)</div>
  <p class="body" style="margin-top:6px">보도 기준으로 12R구역은 사업시행계획 수정 확정 및 이주 관련 보도가 있고(2025), 광명뉴타운 전체로는
  2030년까지 12개 구역 약 2만 8천 세대의 순차 입주가 전망되고 있습니다(에너지경제 2025.11.10.).</p>
  <div class="sec">나. 분석 — 시간표 중첩 <span class="tagA">당 법인 분석</span></div>
  <div class="tl">
    <div class="c"><b>현재(2026)</b>귀 단지 착공(2025.6.) 후 시공 중 · 12R구역 이주 단계 보도</div>
    <div class="c hot"><b>귀 단지 입주(2029.06 예정)</b>12R구역이 통상적 철거·착공 경로를 밟을 경우 입주 시점에 12R 공사가 진행 중일 개연성 — 진출입로 폐쇄·버스 우회가 <b style="display:inline">입주 초기와 겹칠 수 있음</b></div>
    <div class="c"><b>~2030 전후</b>뉴타운 구역별 순차 준공 — 기반시설(도로) 확충이 입주 총량을 따라가는지가 관건</div>
  </div>
  <p class="body" style="margin-top:8px">유사 선례로, 이문·휘경뉴타운은 약 1.3만 세대 순차 입주에도 간선도로가 정비 전 상태(편도 2차선)로 유지되어 상시 정체가
  보도되었습니다(2025). 단지 단위가 아닌 <b>구역 전체 입주 총량 대비 도로·학교 계획</b>을 확인해야 하는 이유입니다. 위 시간표는 보도된 단계를 전제로 한
  당 법인의 분석이며, 12R구역의 실제 일정은 아래 다-②의 조회로 확정해야 합니다.</p>
  <div class="sec">다. 해결 방안</div>
  <div class="fix"><b>① 사업주체 상대.</b> 12R구역 진행 단계별 교통 영향과 대응 계획을 협의회에 정기 공유하도록 서면 확약을 요구하고, 진출입로 폐쇄가 확정되는 경우
  대체 교통수단(마을버스 노선·정류장) 협의에 착수할 의무를 요구합니다 — 공고문이 스스로 리스크를 고지한 사항이므로 후속 정보 제공을 거부할 명분이 약합니다.<br>
  <b>② 행정청 상대.</b> 광명시에 12R구역 사업 일정, 우회 시 버스노선 계획, 구역별 준공 시차와 도로 개통 연동 계획에 대한 정보공개청구를 협의회 명의로 제기합니다.
  학군 배정(광명교육지원청 추후 결정으로 공고문에 기재)도 같은 경로로 진행 상황을 조회합니다.<br>
  <b>③ 기록화.</b> 회신 내용을 대장으로 관리하여, 입주 후 교통 민원 국면에서 "사전에 어떤 계획이 고지되었는가"의 근거 자료로 축적합니다.</div>
</div>
<div class="src">출처 — 공고문 인용: 정정공고(2025.11.07.) 원문 / 12R구역: 아유경제·위클리한국주택경제신문 보도(제목 수준 확인 — 정확한 단계는 정보공개청구로 확정 필요 명시) / 뉴타운 규모: 에너지경제 2025.11.10. / 이문·휘경: 리버티이코노미데스크(본문 확인)</div>
""", "04")

# ═══ 5. 현안 4·5 상세 (동별) ═══
page("""
<div class="pad">
  <div class="crumb">질의 ① — 4/4</div>
  <h1>현안 4·5. 동별 리스크 및 내진능력 동군 간 편차</h1>
  <div class="sec">가. 사실관계 — 공고문이 동 번호를 직접 지목한 사항 전수 <span class="tagD">공고문 원문</span></div>
  <table class="t">
    <tr><th style="width:235px">대상 동</th><th style="width:130px">유형</th><th>원문 기재 내용</th></tr>
    <tr><td class="n">104·105·204·205·212동</td><td class="n red">지하철 진동</td><td>지하철 7호선(광명사거리역) 인접 운행 — 지하층 구조·흙막이 설계가 실시설계 시 변경될 수 있음</td></tr>
    <tr class="alt"><td class="n">103·203동</td><td class="n red">옥탑 소화수조</td><td>소화수조 인접 세대에 소음·진동 등 환경권 침해 발생 가능</td></tr>
    <tr><td class="n">16개동(101~211동 중)</td><td class="n">통신 중계기</td><td>옥상층 이동통신 중계기·옥외안테나 설치 — "추후 이의제기 불가" 기재</td></tr>
    <tr class="alt"><td class="n">301~303동</td><td class="n red">내진능력 편차</td><td>Ⅶ-0.158g 공개 — 타 동군 0.197~0.204g 대비 낮으나 사유 기재 없음</td></tr>
  </table>
  <div class="sec">나. 분석 <span class="tagA">당 법인 분석</span></div>
  <p class="body">내진능력 수치는 건축법 제48조·제48조의3에 따른 법정 공개사항으로 세 수치 모두 그 자체로 위법·부실을 의미하지 않습니다. 문제는 <b>동군 간 차이의 사유가 어디에도 설명되어 있지 않다</b>는 점입니다.
  당 법인이 공개 데이터(국토지반정보포털·건축HUB·기상청)를 조사한 결과 세 경로 모두 분양 단계 건축물의 산정 근거를 제공하지 않음을 확인했습니다 — 구조계산서·지반조사보고서 등
  비공개 자료의 영역이므로, <b>사업주체에 대한 서면 확인 요구가 사실상 유일한 확인 경로</b>입니다. 한편 지하철 인접 5개동은 "실시설계 시 구조 변경 가능"이 함께 기재되어 있어,
  변경 발생 시 해당 동 계약자에 대한 개별 통지가 확보되어야 합니다.</p>
  <div class="sec">다. 해결 방안</div>
  <div class="fix"><b>① 개별 고지.</b> 위 표에 해당하는 동의 계약(예정)자에게 해당 동 특수사항을 계약 전 개별 안내문으로 고지할 것을 요구합니다 — 공고문 본문에 산재한 고지를 계약자가 놓친 채 계약하는 상황을 차단합니다.<br>
  <b>② 서면 확인.</b> 301~303동 내진능력 편차의 산정 근거(지반조건·구조형식·층수 차이 여부)에 대한 서면 회신을 요구합니다.<br>
  <b>③ 변경 통지 의무화.</b> 지하철 인접 동의 구조·흙막이 설계가 실시설계에서 실제 변경되는 경우 해당 동 계약자에게 변경 내용을 개별 통지하도록 요구합니다.<br>
  <b>④ 호수 단위 관리.</b> 당 법인은 위 매트릭스를 배치도에 표시한 자료를 기보유하고 있으며, 수임 시 전 세대 호수 단위 유의사항 자료로 확장하여 계약 전 확인 → 사전점검 → 하자 대응에 동일 자료 체계로 사용합니다(8면).</div>
</div>
<div class="src">출처 — 표 전체: 정정공고(2025.11.07.) 원문에서 동 번호 직접 언급 조항 전수 추출(당 법인 검토보고서 수록) / 내진 공개데이터 조사: 국토지반정보포털·건축HUB(세움터)·기상청 — 분양 단계 조회 불가 확인(2026.7.)</div>
""", "05")

# ═══ 6. 질의② 사례 ═══
page("""
<div class="pad">
  <div class="crumb">질의 ② 재개발 조합사업의 일반분양자 대상 주요 분쟁 사례 — 1/2</div>
  <h1>주요 분쟁 사례 (언론 보도 본문 확인분에 한함)</h1>
  <p class="body" style="margin-top:8px">재개발·재건축 일반분양자 분쟁은 사업 단계별로 상이한 형태로 나타납니다. 아래 5건은 당 법인이 기사 본문까지 확인한 사례이며,
  각 사례의 발생 지점이 곧 귀 단지에서 예방 조치를 배치할 지점입니다(7면).</p>
  <table class="t">
    <tr><th style="width:118px">발생 단계</th><th style="width:190px">사례</th><th>사실관계 (보도 내용)</th><th style="width:295px">일반분양자 관점 시사점</th></tr>
    <tr><td class="n">착공~분양</td><td class="n">둔촌주공<br>(2022)</td><td>조합-시공사업단 공사비 분쟁으로 공사 약 6개월 전면 중단 — 일반분양 4,786가구 일정 표류, 지연 비용이 분양가에 반영</td><td>계약 전 조합-시공사 간 소송·가처분 유무 확인. 공급계약상 지체상금·중도금 연장 조건 점검</td></tr>
    <tr class="alt"><td class="n">시공 중</td><td class="n">은평 대조1구역<br>(2024)</td><td>조합 내분 → 일반분양 지연 → 공사비 미수금 약 1,800억 → 시공사 공사 중단, 준공 일정 반복 표류</td><td>조합 집행부 소송 이력·공사비 미지급 여부가 곧 일반분양자의 입주 리스크</td></tr>
    <tr><td class="n">준공 직전</td><td class="n">서초 메이플자이<br>(2025)</td><td>시공사 3,000억대 증액 요구·유치권 예고로 입주 지연 위기 — 서울시 코디네이터 중재로 합의, 입주 지연 모면</td><td>준공 6개월 전부터 정산 협상 동향 추적. 지자체 중재 제도가 실효적 수단으로 확인된 사례</td></tr>
    <tr class="alt"><td class="n">입주 후</td><td class="n">송파 헬리오시티<br>(2020)</td><td>조합 분쟁으로 1년 넘게 보존등기 지연 — 일반분양자 528명이 조합 상대 집단소송 (주담대 불가·양도세 비과세 요건 위험 보도)</td><td>이전고시·등기 일정은 조합 소관 — 지연 시 손해배상 청구 기준을 계약 단계부터 인지</td></tr>
    <tr><td class="n">입주 후</td><td class="n">장위자이 레디언트<br>(2026)</td><td>임시사용승인 입주 후 준공승인 지연으로 등기 불가 — 대응 소송 방식을 두고 조합원-일반분양자 간 의견 대립 보도</td><td>임시사용승인 입주는 등기·대출·매매 제약 수반. 권리구제 국면에서 조합원과 이해가 갈릴 수 있음을 전제로 별도 대응 체계 필요</td></tr>
  </table>
  <div class="an"><b>[분석]</b> 다섯 사례의 공통점은 분쟁의 원인(조합 거버넌스·공사비)이 일반분양자의 통제 밖에 있는데 비용(입주·등기·자금 일정)은 일반분양자에게 귀속되었다는 점입니다.
  따라서 해결 방안의 축은 소송 이전에 ① 정보 접근의 확보(모니터링·정보공개청구) ② 시점별 예방 조치 ③ 지연·분쟁 발생 시 신속한 채권 보전으로 구성되어야 합니다.</div>
</div>
<div class="src">출처 — 둔촌: 비즈워치 2022.4.14. 외 복수(본문 확인) / 대조1: 파이낸셜뉴스 2024.1.14. 외(본문 확인) / 메이플자이: 뉴스1 2025.4.18. 외(본문 확인) / 헬리오시티: 파이낸셜뉴스 2020.5.26. 외(본문 확인) / 장위자이: 머니투데이 2026.3.18.(본문 확인) — URL 일람 별첨 가능</div>
""", "06")

# ═══ 7. 질의② 해결방안 ═══
page("""
<div class="pad">
  <div class="crumb">질의 ② — 2/2</div>
  <h1>해결 방안 — 사업 단계별 조치 체계</h1>
  <table class="t" style="margin-top:10px">
    <tr><th style="width:128px">단계</th><th style="width:420px">조치 내용</th><th style="width:210px">예방 대상 선례</th><th>비고</th></tr>
    <tr><td class="n">계약 전</td><td>공고문 전수 검토(완료) · 마감사양 비교표 공개 및 계약서 별지화 요구(3면) · 조합-시공사 정산 구조 및 소송 유무 확인 · 동별 리스크 개별 고지 요구(5면)</td><td>개포(사양 차등)<br>둔촌(공사비 분쟁)</td><td>귀 단지는 검토가 기완료 상태</td></tr>
    <tr class="alt"><td class="n">공사 중</td><td>협의회 명의 개선요구서 제출, 항목별 회신 대장 운영 · 12R구역·공사비 정산 동향 분기 모니터링 보고 · 설계변경(특히 지하철 인접 동 구조 변경) 통지 요구 · 광명시 정보공개청구 병행(4면)</td><td>대조1(조합 리스크 방치)</td><td>모니터링 보고서 분기 1회</td></tr>
    <tr><td class="n">준공 전후</td><td>정산 분쟁 조짐 시 경기도·광명시 중재 절차 활용 검토 · 사용승인/임시사용승인 여부 확인 및 임시승인 입주 시 제약사항 사전 안내 · 사전점검을 사양 비교표와 대조하는 방식으로 수행</td><td>메이플자이(유치권)<br>장위자이(임시승인)</td><td>입주 6개월 전 집중 관리 구간</td></tr>
    <tr class="alt"><td class="n">입주 후<br>~조합 해산 전</td><td>이전고시·보존등기 일정 관리, 지연 시 손해배상 청구 검토 · 입주자대표회의 구성 즉시 하자보수보증금 채권 확보 · 조합 해산 전 하자조사 완료 — 조합 무자력 대비 채권자대위·채권양도 방식의 시공사 직접 청구 경로 확보</td><td>헬리오시티(등기 지연)</td><td>하자 청구는 조합 해산 전 착수가 원칙</td></tr>
  </table>
  <div class="sec">보충 — 조합 해산 이후 하자담보책임 청구의 처리</div>
  <p class="body">재개발 단지의 분양자 지위는 조합에 있어, 조합이 이전고시 후 해산·청산하면 무자력 문제가 발생합니다. 실무상 입주자대표회의가
  조합의 시공사에 대한 채권을 대위행사하거나 양도받아 시공사에 직접 청구하는 방식이 사용되며(전문지 법률기고로 소개된 실무),
  이 경로를 확보하려면 <b>조합 해산 전에 하자조사와 채권 보전 조치가 완료되어 있어야 합니다.</b> 당 법인은 이를 위 표의 4단계 조치에 포함하여
  입주 직후부터 역산 일정으로 관리합니다. 개별 사안에의 적용은 수임 후 사실관계 확인을 전제로 합니다.</p>
</div>
<div class="src">근거 — 단계별 조치: 6면 검증 사례의 발생 지점 역산 / 채권자대위·채권양도 실무: 한국아파트신문 법률기고(hapt.co.kr/news/articleView.html?idxno=161342, 본문 확인) / 지자체 중재: 메이플자이 사례에서 서울시 코디네이터 중재로 합의된 보도 사실에 기초</div>
""", "07")

# ═══ 8. 질의③ 수행 실적·시나리오 ═══
page("""
<div class="pad">
  <div class="crumb">질의 ③ 일반분양자 권익 보호 수행 사례 및 시나리오</div>
  <h1>수행 실적(실물 보유분) 및 당 단지 적용 시나리오</h1>
  <div class="sec">가. 수행 실적 — 당 법인이 실물 문서로 보유하여 대면 PT 시 원본 제시가 가능한 것</div>
  <table class="t">
    <tr><th style="width:280px">수행 내용</th><th>세부</th></tr>
    <tr><td class="n">힐스테이트 광명 검토보고서 (기완료)</td><td>귀 단지 정정공고(2025.11.07.) 원문 161,867자 전수 대조 — 확인·개선요구 지점 14건 이상을 조항 원문과 함께 정리 (검토기준일 2026.7.27.). 본 회신서 2~5면이 그 요약입니다</td></tr>
    <tr class="alt"><td class="n">분양공고문 검토 체계 (8개 단지)</td><td>수도권·지방 8개 단지 입주자모집공고 검토보고서 작성 — 전면 통독, 일반 조항 배제, 원문 재대조를 표준 절차로 운영</td></tr>
    <tr><td class="n">입주예정자협의회 개선요구 실무</td><td>수원 소재 단지 입예협 개선요구사항 문서 작성 수행 — 조항별 원문 인용·요구 문안·회신 관리 구조 (의뢰인 관계상 단지명 익명)</td></tr>
    <tr class="alt"><td class="n">공공데이터 교차검증</td><td>카카오맵·V-World 용도지역·법제처 현행법 API 실측 대조 — 귀 단지 입지·조망권(반경 500m 내 준주거·일반상업지역 확인) 분석에 기적용</td></tr>
    <tr><td class="n">정비사업 수임 사례 상세</td><td>대면 PT 시 전담변호사가 사건 단위로 직접 설명 [상세 자료 별도 지참]</td></tr>
  </table>
  <div class="sec">나. 선정 시 30일 이행 시나리오</div>
  <table class="t">
    <tr><th style="width:110px">시점</th><th>이행 사항</th></tr>
    <tr><td class="n">D+7</td><td>기보유 검토보고서 전문 및 개선요구서 초안을 협의회에 제출 — 신규 착수 기간이 소요되지 않습니다</td></tr>
    <tr class="alt"><td class="n">D+14</td><td>개선요구서 확정본을 사업주체·시공사·감리에 발송(마감사양 비교표 공개, 동별 개별 고지, 내진 편차 서면 확인 포함), 회신 대장 개설</td></tr>
    <tr><td class="n">D+21</td><td>광명시 정보공개청구 제기(12R구역 일정·버스노선·도로 계획·학군 배정)</td></tr>
    <tr class="alt"><td class="n">D+30</td><td>제1차 동향 보고(회신 현황·12R구역·공사비 정산) 및 향후 분기 모니터링 계획 확정</td></tr>
  </table>
</div>
<div class="src">위 실적은 전부 실물 문서 기준이며 과장·각색이 없습니다. 타 단지 자료의 익명 처리는 의뢰인 보호 목적입니다.</div>
""", "08")

# ═══ 9. 요약 ═══
page("""
<div class="pad">
  <div class="crumb">요약</div>
  <h1>회신 요지</h1>
  <table class="t" style="margin-top:12px">
    <tr><th style="width:250px">질의</th><th>회신 요지</th></tr>
    <tr><td class="n">① 당 단지 맞춤형 현안 분석<br>및 대응 전략</td><td>공고문 전수 검토(기완료)로 단지 특화 현안 8건을 식별했습니다(2면). 핵심은 ▲조합원·일반분양 마감사양 차등의 '특정→계약서 편철'(3면)
    ▲12R구역·뉴타운 동시 개발에 대한 사업주체·광명시 이원 대응(4면) ▲동별 리스크의 계약 전 개별 고지와 내진 편차 서면 확인(5면)이며,
    각 조치는 공고문이 스스로 고지한 조항을 근거로 하므로 사업주체가 거부할 명분이 약한 순서로 설계했습니다.</td></tr>
    <tr class="alt"><td class="n">② 재개발 일반분양자<br>주요 분쟁 사례 및 해결 방안</td><td>보도 본문까지 확인된 5개 사례(둔촌·대조1·메이플자이·헬리오시티·장위자이)를 단계별로 분석했습니다(6면).
    분쟁 원인은 일반분양자 통제 밖에 있으나 비용은 일반분양자에게 귀속되는 구조이므로, 해결 방안을 소송 중심이 아닌
    '단계별 예방 조치 + 지연 시 신속한 채권 보전'(등기 지연 손배, 조합 해산 전 하자조사·채권 확보)으로 제시했습니다(7면).</td></tr>
    <tr><td class="n">③ 권익 보호 수행 사례<br>및 시나리오</td><td>귀 단지 검토보고서를 이미 완료·보유하고 있어 선정 시 D+7에 보고서 전문과 개선요구서 초안 제출이 가능하며,
    D+30까지의 이행 일정을 특정하여 제시했습니다(8면). 실적은 실물 보유분만 기재했고, 수임 사건 상세는 대면 PT에서 전담변호사가 직접 설명합니다.</td></tr>
  </table>
  <p class="body" style="margin-top:14px">본 회신서는 사실(공고문 원문·확인된 보도·실물 산출물)과 당 법인의 분석([분석] 표시)을 구분하여 작성했으며,
  모든 인용에 출처를 병기했습니다. 사실관계 출처 일람과 검토보고서 목차는 요청 시 즉시 제출하겠습니다.</p>
  <p class="body" style="margin-top:8px">법무법인 제이엘 · 전담변호사 [성명] · [연락처] — 대면 PT(2026.8.22.)에는 계약 시 실제 전담할 변호사가 직접 발표합니다.</p>
</div>
""", "09")

print("pages:", len(pages))
import json; open(f"{OUT}/_list.json","w").write(json.dumps(pages))
