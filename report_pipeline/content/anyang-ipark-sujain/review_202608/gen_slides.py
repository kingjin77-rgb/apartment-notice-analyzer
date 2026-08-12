# -*- coding: utf-8 -*-
"""안양역 센트럴 아이파크 수자인 — 검토보고서 가로 슬라이드 (16:9 · 1332x750)
   재개발 조합 일반분양(혼합단지) 관점 · 상투 배제 · 발견 16건 + 교육환경 조사"""
import os, html as H

OUT = "/tmp/ay/rslides"
os.makedirs(OUT, exist_ok=True)

def esc(s): return H.escape(str(s))

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1332px;height:750px;overflow:hidden}
body{font-family:"S-Core Dream","NanumSquare","Malgun Gothic",sans-serif;background:#fff;color:#16202E;position:relative}
.pad{position:absolute;left:56px;right:56px;top:40px;bottom:64px;display:flex;flex-direction:column}
.eyebrow{font-size:14px;font-weight:800;color:#3E6CB5;letter-spacing:1px;margin-bottom:7px}
h1{font-size:38px;font-weight:800;color:#0F2548;letter-spacing:-1.5px;line-height:1.16}
h1 em{font-style:normal;color:#C0392B}
h1 u{text-decoration:none;background:linear-gradient(transparent 62%,#FFE08A 62%)}
.lead{font-size:15.5px;color:#5B6673;font-weight:700;margin-top:8px;line-height:1.5}
.lead b{color:#0F2548}
.bar{position:absolute;left:0;right:0;bottom:0;height:46px;background:#0F2548;display:flex;align-items:center;
  justify-content:space-between;padding:0 56px;z-index:5}
.bar .l{color:#fff;font-size:13px;font-weight:800}.bar .l span{color:#7FA9E8}
.bar .r{color:#8FA3C0;font-size:11px}
.pg{position:absolute;right:56px;top:36px;font-size:12.5px;font-weight:800;color:#B9C4D2;z-index:5}
.pill{font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:20px;display:inline-block}
.pill.r{background:#FBEAEA;color:#C0392B}.pill.o{background:#FCF3E2;color:#B7791F}
.pill.b{background:#EDF2FA;color:#3E6CB5}.pill.k{background:#0F2548;color:#fff}
.pill.gy{background:#F1F4F8;color:#5B6673}
.q{font-size:12px;color:#44505E;background:#F7F9FC;border-left:3px solid #C9D4E2;padding:8px 11px;
  border-radius:0 6px 6px 0;font-weight:600;line-height:1.5}
.q mark{background:#FFE08A;color:#16202E;font-weight:800;padding:0 2px}
.q .src{color:#8593A4;font-weight:700;font-size:10.5px}
.navybox{background:#0F2548;color:#fff;border-radius:10px;padding:11px 14px;font-size:12.5px;font-weight:700;line-height:1.5}
.navybox b{color:#FFD98A}
table.t{width:100%;border-collapse:collapse;font-size:13px;background:#fff}
table.t th{background:#0F2548;color:#fff;font-size:12px;font-weight:800;padding:8px 10px;text-align:left}
table.t td{padding:7px 10px;border-bottom:1px solid #E5EAF0;font-weight:600;color:#31404F;line-height:1.4}
table.t td.n{white-space:nowrap;font-weight:800}
table.t td.red{color:#C0392B;font-weight:800}
table.t tr.hl td{background:#FDF6F5}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;flex:1;margin-top:14px;min-height:0}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;flex:1;margin-top:14px;min-height:0}
.panel{border:1.5px solid #E1E7EE;border-radius:12px;padding:13px 15px;display:flex;flex-direction:column;min-height:0}
.panel h3{font-size:14.5px;font-weight:800;color:#0F2548;margin-bottom:8px;letter-spacing:-.3px}
.panel h3 .no{color:#C0392B;margin-right:5px}
.panel .b{font-size:12px;color:#31404F;line-height:1.55;font-weight:600}
.panel .b b{color:#C0392B}
.why3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}
.why3 .w{background:#F7F9FC;border-radius:9px;padding:9px 11px}
.why3 .w h4{font-size:11px;font-weight:800;color:#3E6CB5;margin-bottom:4px}
.why3 .w p{font-size:11.5px;font-weight:600;color:#31404F;line-height:1.45}
.calc{font-family:Consolas,Menlo,monospace;background:#0F2548;color:#CFE0F5;border-radius:8px;
  padding:9px 12px;font-size:11.5px;line-height:1.55}
.calc b{color:#FFD98A;font-weight:800}
.cap{font-size:10.5px;color:#8593A4;font-weight:700;margin-top:6px}
.tag{position:absolute;left:56px;top:36px;z-index:5}
"""

BAR = ('<div class="bar"><div class="l">법무법인 <span>JL</span> 제이엘 · 분양공고문 분석팀</div>'
       '<div class="r">안양역 센트럴 아이파크 수자인 · 입주자모집공고 72면 전수 통독 검토보고서 · 검토기준일 2026.08.12</div></div>')

pages = []
def page(body, pg=None, style=""):
    pgh = f'<div class="pg">{pg}</div>' if pg else ""
    name = f"r{len(pages)+1:02d}"
    h = (f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}{style}</style></head>'
         f'<body>{pgh}{body}{BAR}</body></html>')
    open(f"{OUT}/{name}.html", "w", encoding="utf-8").write(h)
    pages.append(name)

# ══════════════ r01 표지 ══════════════
page("""
<style>
body{background:#0F2548}
.cv{position:absolute;inset:0;padding:70px 76px;display:flex;flex-direction:column}
.cv .brand{font-size:15px;font-weight:800;color:#7FA9E8;letter-spacing:2px}
.cv h1{font-size:56px;color:#fff;letter-spacing:-2.2px;margin-top:26px;line-height:1.18}
.cv h1 em{color:#FFD98A;font-style:normal}
.cv .sub{font-size:19px;color:#B9C9E2;font-weight:700;margin-top:16px;line-height:1.6}
.nums{display:flex;gap:14px;margin-top:auto;margin-bottom:30px}
.nums .n{flex:1;background:rgba(255,255,255,.06);border:1px solid rgba(127,169,232,.35);border-radius:14px;padding:18px 20px}
.nums .n .v{font-size:30px;font-weight:800;color:#fff;letter-spacing:-1px}
.nums .n .v span{font-size:15px;color:#7FA9E8}
.nums .n .k{font-size:12.5px;color:#8FA3C0;font-weight:700;margin-top:5px;line-height:1.4}
.ft{display:flex;justify-content:space-between;color:#8FA3C0;font-size:13px;font-weight:700}
.typ{display:inline-block;background:#C0392B;color:#fff;font-size:14px;font-weight:800;
  padding:6px 14px;border-radius:8px;margin-top:22px}
.axes{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:28px}
.axes .a{border-left:3px solid #3E6CB5;padding:4px 0 4px 16px}
.axes .no{font-size:13px;font-weight:800;color:#7FA9E8}
.axes .tt{font-size:17px;font-weight:800;color:#fff;margin-top:4px}
.axes .dd{font-size:12px;color:#8FA3C0;font-weight:700;margin-top:6px;line-height:1.5}
</style>
<div class="cv">
  <div class="brand">JL LAWFIRM · 분양공고문 분석팀</div>
  <h1>계약서에 없는 위험은,<br>공고문 <em>72면 안에</em> 있었습니다</h1>
  <div class="sub">안양역 센트럴 아이파크 수자인 입주자모집공고(2026.01.) 전수 통독 검토보고서</div>
  <div class="typ">사업유형 판별 — 재개발정비사업 조합 물건 · 조합원분과 일반분양분이 병존하는 혼합단지 (원문 72면: 사업주체 = 안양역세권 지구 재개발정비사업 조합)</div>
  <div class="axes">
    <div class="a"><div class="no">01</div><div class="tt">혼합단지 비대칭</div><div class="dd">중형 물량 선점 · 대지지분 39.5% 격차 · 세대구성 비공개</div></div>
    <div class="a"><div class="no">02</div><div class="tt">재개발 종속 구조</div><div class="dd">이전고시에 묶인 등기 · 기부채납에 묶인 입주 · 조합 모계좌</div></div>
    <div class="a"><div class="no">03</div><div class="tt">계약·옵션 결합 구조</div><div class="dd">이자 부담 모순 · 확장 종속 옵션 · 위약금 요율 공백</div></div>
    <div class="a"><div class="no">04</div><div class="tt">미확정 사양·교육환경</div><div class="dd">주차 재심의 예정 · 방음 미정 · 만안초 수용력</div></div>
  </div>
  <div class="nums">
    <div class="n"><div class="v">853<span>세대</span></div><div class="k">지하4~지상35층 · 8개동<br>일반분양은 407세대뿐</div></div>
    <div class="n"><div class="v">16<span>건</span></div><div class="k">상투 조항 전면 배제 후<br>개선 실익 있는 발견만 선별</div></div>
    <div class="n"><div class="v">75<span>회</span></div><div class="k">"이의를 제기할 수 없다"<br>실측 횟수 (60~61면에만 29회)</div></div>
    <div class="n"><div class="v">2029.04</div><div class="k">입주예정 — 단, 도시계획시설<br>준공·기부채납에 종속 (53면)</div></div>
  </div>
  <div class="ft"><div>작성 · 법무법인 제이엘 분양공고문 분석팀</div><div>여러 단지 공통 상투 조항 18유형은 시작부터 배제하고, 이 단지 고유의 개선 가능 사항만 담았습니다</div></div>
</div>
""")

# ══════════════ r02 사업구조 ══════════════
page("""
<div class="pad">
<div class="eyebrow">01 · 사업구조 — 왜 이 단지는 다른 신축분양과 다른가</div>
<h1>일반분양자는 <em>407/853</em> — 조합이 만든 판에<br><u>뒤에 올라탄 계약자</u>라는 사실이 모든 위험의 출발점입니다</h1>
<div class="grid3" style="margin-top:16px">
  <div class="panel">
    <h3>사업주체가 '회사'가 아니라 '조합'</h3>
    <div class="b">시행 = <b>안양역세권 지구 재개발정비사업 조합</b>, 시공 = HDC현대산업개발·BS한양 (72면).
    조합 총회·관리처분계획이 사업 내용을 결정하며, 일반분양 계약자는 그 의사결정에서 <b>완전히 배제</b>됩니다.</div>
    <div class="q" style="margin-top:9px">"개발계획 및 실시계획은 <mark>사업주체의 사정에 따라 변경, 취소 또는 지연</mark>될 수 있으며, 이에 대해 사업주체 및 시공사는 <mark>일체의 책임을 지지 않습니다</mark>" <span class="src">— 52~53면</span></div>
  </div>
  <div class="panel">
    <h3>853세대 중 비일반분양 446세대의 구성은 공고문에 없음</h3>
    <div class="b">원문은 "총 853세대 중 일반분양 407세대"(7면)라고만 적었습니다. 조합원분·보류지·임대주택이 각각 몇 세대이고 어느 동·층에 있는지 <b>공고문 72면 어디에도 없습니다.</b></div>
    <div class="b" style="margin-top:7px">[분석] 사업주체 공식 홈페이지 평면정보의 타입별 세대수 합계는 653세대 — 나머지 <b>200세대는 홈페이지에도 미게재</b>(임대주택 등 추정, 미확인). 세대구성 공개이 첫 번째 요청사항인 이유입니다.</div>
  </div>
  <div class="panel">
    <h3>이 보고서가 보는 4개의 축</h3>
    <div class="b">① 조합-일반분양 <b>비대칭</b> (물량·대지지분·정보)<br>
    ② 재개발 고유 <b>종속 구조</b> (등기·입주·자금)<br>
    ③ 계약·옵션의 <b>결합 구조</b> (확장 종속·가격 공백)<br>
    ④ 단지 고유 <b>미확정 사양</b> (주차·소음·학교)</div>
    <div class="navybox" style="margin-top:auto">상투 배제 원칙 — 주차 층고·내진 등급·HUG 표준약관·실외기 고지 등 <b>모든 단지에 있는 조항 18유형은 이 보고서에 싣지 않았습니다.</b> 여기 실린 것은 이 단지에서만 확인된 것입니다.</div>
  </div>
</div>
</div>
""", "02")

# ══════════════ r03 종합 진단표 ══════════════
rows = [
 ("01","혼합단지","치명","조합원 선점 구조 — 84형 34세대 중 일반분양 1세대, 59형 200세대 중 37세대","조합원분·보류지·임대 세대구성 공개 요청"),
 ("02","혼합단지","치명","1·2단지 대지지분 39.5% 격차 — 무작위 추첨으로 배정, 격차 고지는 한 줄뿐","타입별 대지지분·원단위 비교표 계약자 고지 요청"),
 ("03","재개발 종속","치명","대지권 등기 '상당 기간' 소요 + 잔금 10% 유예조항 명시적 배제(11·53면)","이전고시 예정 시기 서면 고지 + 지연 시 보호장치 요청"),
 ("04","재개발 종속","치명","도시계획시설 준공·기부채납 이후에야 입주 가능 + 지연·취소 전면 면책","지체상금 적용 명문화·기부채납 시설 목록 고지 요청"),
 ("05","자금관리","치명","분양대금 전액이 조합 모계좌로 — 공동예금주 '(외2)' 정체·대리사무사 정보 공백","예금주 전원·자금관리 방식(신탁 여부) 공개 요청"),
 ("06","계약","치명","중도금 이자 부담 주체가 41면(이자후불제)과 42면(사업주체 부담)에서 상호 모순","정정공고 요구 1순위 — 세대당 수천만원 좌우"),
 ("07","옵션","높음","발코니 확장 사실상 강제 — 확장 전제 설계 + 전 유상옵션이 확장계약에 종속","확장면적·정산내역 공개, 무관 품목 개별 선택 허용 요청"),
 ("08","옵션","높음","시스템에어컨 '기본' 패키지의 배관 함정 — 미포함 침실 냉방 경로 봉쇄","통합 경고문 명기·예비 배관 제공 요청"),
 ("09","옵션","높음","옵션 가격 역전(39형이 59형보다 비쌈)·모델 미특정·해지 위약금 요율 공백","산정내역 공개·위약금 요율 사전 명시 요청"),
 ("10","공고 품질","높음","실재하는 오기 5건+ (없는 주택형 34A1, 계약서 문구 혼입 등) + '전화로 정정, 이의불가' 조항","정정공고(공고 형식) 일괄 요구"),
 ("11","포괄 위임","치명","설계변경 '제반 권리를 사업주체에게 위탁하는 데 동의 간주' + 변경 통보는 재량·최장 6개월","위탁 간주 문구 삭제·변경 즉시 통지 의무화 요청"),
 ("12","미확정 사양","치명","주차계획 이중 미확정 — 착공 후 교통영향평가 재심의 예정 + 무동의 축소 허용 조항","주차대수 하한 명시·재심의 결과 개별 통지 요청"),
 ("13","미확정 사양","높음","1호선·안양역 소음 확정 고지 + 방음시설은 '준공 시 측정에 따라 설치될 수 있음'","소음예측·방음계획 확정본 공개 요청"),
 ("14","동별 중첩","높음","204동 부담시설 5중 중첩(근생 실외기·근생EV·근생·재활용창고·문주) 등 특정 동 집중","동별 부담시설 종합표 제공 요청"),
 ("15","생활 제약","중간","전 세대 이삿짐 사다리차 불가 — 엘리베이터 규격은 미공개","EV 유효 규격 서면 교부 요청"),
 ("16","교육환경","높음","배정 유력 만안초는 16학급 소규모 — 853세대 유입 시 학생 40~60% 급증, 증축 계획 미확인","취학수요 협의 결과·수용 계획 공개 요청"),
]
trs = "".join(
  f'<tr{" class=hl" if g=="치명" else ""}><td class="n">{n}</td><td>{c}</td>'
  f'<td><span class="pill {"r" if g=="치명" else ("o" if g=="높음" else "b")}">{g}</span></td>'
  f'<td>{esc(t)}</td><td style="color:#0F2548">{esc(a)}</td></tr>'
  for n,c,g,t,a in rows)
page(f"""
<div class="pad">
<div class="eyebrow">02 · 종합 진단표</div>
<h1>발견 <em>16건</em> — 치명 8 · 높음 6 · 중간 2</h1>
<div class="lead">여러 단지 공통 상투 18유형 배제 후, 이 단지에서 개선 가능하거나 심각한 문제로 이어질 수 있는 것만 선별했습니다. 전 건 원문 면수·인용 확보.</div>
<div style="flex:1;overflow:hidden;margin-top:12px">
<table class="t" style="font-size:11.8px">
<tr><th style="width:36px">No</th><th style="width:86px">분류</th><th style="width:56px">중요도</th><th>발견 내용</th><th style="width:300px">개선요청 방향</th></tr>
{trs}
</table></div>
</div>
""", "03", style="table.t td{padding:5.2px 9px}")

# ══════════════ r04 조합원 선점 구조 ══════════════
TYPES = [("39A1",48,14),("43A1",215,209),("43A2",104,100),("43B2",52,46),
         ("59A2",90,5),("59B1",50,20),("59B2",60,12),("84A1",34,1)]
bars = ""
x = 70
for t,tot,gen in TYPES:
    co = tot-gen
    W = 96; maxv = 215
    hG = round(gen/maxv*330); hC = round(co/maxv*330)
    yC = 400-hC; yG = yC-hG
    bars += f'''<rect x="{x}" y="{yC}" width="{W}" height="{hC}" fill="#8FA3C0"/>
    <rect x="{x}" y="{yG}" width="{W}" height="{hG}" fill="#C0392B"/>
    <text x="{x+W/2}" y="425" text-anchor="middle" font-size="15" font-weight="800" fill="#0F2548">{t}</text>
    <text x="{x+W/2}" y="{yG-8}" text-anchor="middle" font-size="13.5" font-weight="800" fill="#C0392B">일반 {gen}</text>
    <text x="{x+W/2}" y="{min(yC+18,392)}" text-anchor="middle" font-size="12.5" font-weight="800" fill="#fff">{co}</text>'''
    x += W+42
page(f"""
<div class="pad">
<div class="eyebrow">03 · 발견 01 — 혼합단지 물량 비대칭 (치명)</div>
<h1>전용 84는 34세대를 짓고 <em>일반분양은 단 1세대</em> —<br>중형은 조합원이 가져가고, 일반분양자에게는 <u>초소형만 남았습니다</u></h1>
<div class="grid2" style="grid-template-columns:1.5fr 1fr">
  <div class="panel">
    <h3>타입별 총 세대수 vs 일반분양 세대수</h3>
    <svg viewBox="0 0 1180 435" style="width:100%;flex:1">
      <line x1="50" y1="400" x2="1160" y2="400" stroke="#D5DDE7" stroke-width="2"/>
      {bars}
      <rect x="880" y="10" width="14" height="14" fill="#C0392B"/><text x="900" y="22" font-size="13" font-weight="800" fill="#31404F">일반분양</text>
      <rect x="990" y="10" width="14" height="14" fill="#8FA3C0"/><text x="1010" y="22" font-size="13" font-weight="800" fill="#31404F">조합원분 등(총세대-일반)</text>
    </svg>
    <div class="cap">총 세대수 출처: 사업주체 공식 홈페이지 평면정보(i-park.com/anyangyeok/plane, 2026.08.12. 확인) — 일반분양 세대수는 공고문 7면 공급대상표와 8개 타입 전부 일치 교차검증 완료. 평면표 합계 653세대로 총 853세대와 200세대 차이(임대주택 등 미게재 추정, 미확인).</div>
  </div>
  <div class="panel">
    <h3>계산 — 선점률</h3>
    <div class="calc">59·84형(중형) 총 234세대<br>— 일반분양 38세대 (16.2%)<br>— 조합원분 등 <b>196세대 (83.8%)</b><br><br>43형 총 371세대<br>— 일반분양 355세대 (95.7%)<br>— 조합원분 등 <b>단 16세대</b><br><br>일반분양 407세대 중<br>전용 43㎡ 이하 = 369세대 = <b>90.7%</b></div>
    <div class="b" style="margin-top:10px">[분석] 커뮤니티·주차·관리비는 853세대 전체가 공유하는데, 일반분양자는 사실상 초소형 세대군으로 격리됩니다. 향후 입주자대표회의 의결·하자대응에서 <b>일반분양자가 구조적 소수파</b>가 되는 출발점입니다.</div>
    <div class="navybox" style="margin-top:9px"><b>개선요청</b> — 조합원분·보류지·임대 세대수와 동·층 분포 공개를 요청합니다. 일반분양 세대의 동별 분포 확인이 협의회 구성의 선행 작업입니다.</div>
  </div>
</div>
</div>
""", "04")

# ══════════════ r05 대지지분 격차 ══════════════
page("""
<div class="pad">
<div class="eyebrow">04 · 발견 02 — 대지지분 격차 (치명)</div>
<h1>같은 주택형·같은 추첨인데 대지지분은 <em>39.5% 차이</em> —<br>어느 단지에 배정되느냐로 <u>재산가치의 핵심이 갈립니다</u></h1>
<div class="grid2" style="grid-template-columns:1.15fr 1fr">
  <div class="panel">
    <h3>원문 실측 — 7면 공급대상표</h3>
    <table class="t">
      <tr><th>통합 주택형</th><th>타입(단지)</th><th>세대별 대지지분</th><th>격차</th></tr>
      <tr><td rowspan="2" class="n">043.2386A</td><td>43A1 (1단지)</td><td class="n">19.0858㎡</td><td rowspan="2" class="red">1.395배<br>(+39.5%)</td></tr>
      <tr class="hl"><td>43A2 (2단지)</td><td class="n red">13.6802㎡</td></tr>
      <tr><td rowspan="2" class="n">059.8628B</td><td>59B1 (1단지 102동)</td><td class="n">26.8023㎡</td><td rowspan="2" class="red">1.395배<br>(+39.5%)</td></tr>
      <tr class="hl"><td>59B2 (2단지 202동)</td><td class="n red">19.2136㎡</td></tr>
    </table>
    <div class="calc" style="margin-top:10px">대지비 원단위 [분석]<br>43A1(21층+) 267,567,800원 ÷ 19.0858㎡ = <b>1,402만원/㎡</b><br>43A2(21층+) 252,516,600원 ÷ 13.6802㎡ = <b>1,846만원/㎡ (+31.7%)</b><br>→ 2단지 배정자는 대지지분 ㎡당 약 3할 더 비싸게 사는 셈</div>
  </div>
  <div class="panel">
    <h3>왜 문제인가</h3>
    <div class="q">"단지 및 동·호수는 주택형 내에서 <mark>무작위 추첨으로 결정</mark>되오니 착오 없으시기 바랍니다" <span class="src">— 7면</span><br>
    "동일 통합 주택형 내 <mark>단지별 면적과 공급금액 등이 상이</mark>하오니 청약 신청 전에 반드시 확인" <span class="src">— 8면</span></div>
    <div class="b" style="margin-top:10px">[분석] 두 주택형의 격차 비율이 <b>정확히 1.395배로 일치</b> — 개별 세대 사정이 아니라 1·2단지 간 체계적 대지 배분 차이입니다. 공고문은 "상이할 수 있다"고만 적고 <b>격차의 크기(39.5%)와 원인은 어디에도 밝히지 않았습니다.</b> 대지지분은 재산세·담보가치·먼 훗날의 재건축 가치까지 좌우하는 항목입니다.</div>
    <div class="why3" style="grid-template-columns:1fr 1fr">
      <div class="w"><h4>권리로 주장 가능</h4><p>계약 전 대지지분 고지 — 이미 계약한 세대에는 격차 사유 소명 요구</p></div>
      <div class="w"><h4>요청·협의 사항</h4><p>1·2단지 필지 분리 여부, 향후 관리단 분리 가능성 서면 확인</p></div>
    </div>
    <div class="navybox" style="margin-top:9px"><b>개선요청</b> — 타입별 대지지분·대지비 원단위 비교표와 배분 기준(관리처분계획상 근거) 공개를 요청합니다.</div>
  </div>
</div>
</div>
""", "05")

# ══════════════ r06 층별 가격 절벽 ══════════════
pts = [("4층",878.4),("5층",949.7),("6~10층",900.0),("11~15층",942.4)]
page("""
<div class="pad">
<div class="eyebrow">05 · 발견 03 — 층별 가격 산정근거 공백 (높음)</div>
<h1>59A2는 4층에서 5층으로 <em>한 층에 7,130만원</em>이 뜁니다 —<br>산정근거는 공고문 어디에도 없습니다</h1>
<div class="grid2" style="grid-template-columns:1.2fr 1fr">
  <div class="panel">
    <h3>원문 실측 — 10면 공급금액표 (단위: 원)</h3>
    <table class="t">
      <tr><th>타입</th><th>층 구간</th><th>공급금액</th><th>인접 구간 격차</th></tr>
      <tr class="hl"><td rowspan="2" class="n">59A2<br>(202동 1·2호)</td><td>4층 (최하층)</td><td class="n">878,400,000</td><td rowspan="2" class="red">+71,300,000<br>(+8.1%)</td></tr>
      <tr class="hl"><td>5층</td><td class="n red">949,700,000</td></tr>
      <tr><td rowspan="2" class="n">59B1</td><td>6~10층</td><td class="n">900,000,000</td><td rowspan="2" class="n">+42,400,000<br>(+4.7%)</td></tr>
      <tr><td>11~15층</td><td class="n">942,400,000</td></tr>
      <tr><td rowspan="2" class="n">43A1 (비교)</td><td>16~20층</td><td class="n">644,400,000</td><td rowspan="2" class="n">+9,800,000<br>(+1.5%)</td></tr>
      <tr><td>21층 이상</td><td class="n">654,200,000</td></tr>
    </table>
    <div class="cap">계산식: 949,700,000 − 878,400,000 = 71,300,000원. 59형 층간 격차는 43형 인접 구간 격차(1.5%)의 3~5배.</div>
  </div>
  <div class="panel">
    <h3>왜 문제인가</h3>
    <div class="b">[분석] 청약은 주택형 단위(층·타입 선택 불가)로만 가능했습니다. 같은 주택형 안에서 <b>배정 층 하나로 7천만원 이상</b>이 갈리는데, 조망·일조 등 차등 사유가 공고문에 전혀 없습니다.</div>
    <div class="b" style="margin-top:8px">[분석] 59A2 일반분양분은 4~5층 5세대뿐이고, 최하층 우선배정 3세대가 4층분과 겹칩니다 — 고령자·장애인·다자녀 배정층과 가격 절벽이 만나는 구조로, 산정근거 불투명성의 방증입니다.</div>
    <div class="why3" style="grid-template-columns:1fr 1fr">
      <div class="w"><h4>권리로 주장 가능</h4><p>분양가 산정내역(층별 차등 기준) 정보 요구</p></div>
      <div class="w"><h4>요청·협의 사항</h4><p>통합 주택형 판매 시 최저~최고 금액 범위 표 명시 관행화</p></div>
    </div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — 59형 층별 가격 급등 구간의 산정근거(조망·일조·구조 사유) 공개를 요청합니다.</div>
  </div>
</div>
</div>
""", "06")

# ══════════════ r07 등기·입주 종속 ══════════════
page("""
<div class="pad">
<div class="eyebrow">06 · 발견 04·05 — 재개발 종속 구조 (치명)</div>
<h1>돈은 100% 내고 입주해도, <u>대지권 등기는 조합의 시간표</u>를<br>기다려야 합니다 — 보호장치는 괄호 한 줄로 배제됐습니다</h1>
<div style="display:flex;gap:14px;flex:1;margin-top:14px;min-height:0">
  <div class="panel" style="flex:1.35">
    <h3>원문이 만든 종속의 사슬 (모식도)</h3>
    <svg viewBox="0 0 640 300" style="width:100%;flex:1">
      <defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#C0392B"/></marker></defs>
      <rect x="10" y="20" width="180" height="64" rx="10" fill="#0F2548"/><text x="100" y="46" text-anchor="middle" font-size="14" font-weight="800" fill="#fff">조합 사정</text><text x="100" y="66" text-anchor="middle" font-size="11" fill="#B9C9E2">변경·취소·지연 전면 면책 (52~53면)</text>
      <rect x="230" y="20" width="180" height="64" rx="10" fill="#fff" stroke="#C0392B" stroke-width="2"/><text x="320" y="46" text-anchor="middle" font-size="13.5" font-weight="800" fill="#C0392B">도시계획시설 준공·기부채납</text><text x="320" y="66" text-anchor="middle" font-size="11" fill="#5B6673">공원·주차장·치안센터 등 (55면)</text>
      <rect x="450" y="20" width="180" height="64" rx="10" fill="#fff" stroke="#E1E7EE" stroke-width="2"/><text x="540" y="46" text-anchor="middle" font-size="14" font-weight="800" fill="#0F2548">입주 가능</text><text x="540" y="66" text-anchor="middle" font-size="11" fill="#5B6673">"준공·기부채납 된 이후에" (53면)</text>
      <line x1="190" y1="52" x2="226" y2="52" stroke="#C0392B" stroke-width="2.5" marker-end="url(#ar)"/>
      <line x1="410" y1="52" x2="446" y2="52" stroke="#C0392B" stroke-width="2.5" marker-end="url(#ar)"/>
      <rect x="10" y="130" width="180" height="64" rx="10" fill="#0F2548"/><text x="100" y="156" text-anchor="middle" font-size="14" font-weight="800" fill="#fff">이전고시 (조합 최종 단계)</text><text x="100" y="176" text-anchor="middle" font-size="11" fill="#B9C9E2">청산·소송으로 수년 지연 사례 다수</text>
      <rect x="230" y="130" width="180" height="64" rx="10" fill="#fff" stroke="#C0392B" stroke-width="2"/><text x="320" y="156" text-anchor="middle" font-size="13.5" font-weight="800" fill="#C0392B">대지권 등기 "상당 기간"</text><text x="320" y="176" text-anchor="middle" font-size="11" fill="#5B6673">건물·대지 분리 등기 (53면)</text>
      <rect x="450" y="130" width="180" height="64" rx="10" fill="#fff" stroke="#E1E7EE" stroke-width="2"/><text x="540" y="150" text-anchor="middle" font-size="12.5" font-weight="800" fill="#0F2548">담보대출·처분 제약</text><text x="540" y="170" text-anchor="middle" font-size="11" fill="#5B6673">대지권 없는 건물 소유 상태</text><text x="540" y="186" text-anchor="middle" font-size="11" fill="#5B6673">면적 정산도 등기 시까지 이연</text>
      <line x1="190" y1="162" x2="226" y2="162" stroke="#C0392B" stroke-width="2.5" marker-end="url(#ar)"/>
      <line x1="410" y1="162" x2="446" y2="162" stroke="#C0392B" stroke-width="2.5" marker-end="url(#ar)"/>
      <rect x="10" y="236" width="620" height="52" rx="10" fill="#FDF6F5" stroke="#C0392B" stroke-width="1.5"/>
      <text x="320" y="258" text-anchor="middle" font-size="12.5" font-weight="800" fill="#C0392B">잔금 10% 유예(주택공급규칙 §60)마저 — "대지권에 대한 등기는 … 본 조항은 적용되지 아니합니다" (11면)</text>
      <text x="320" y="277" text-anchor="middle" font-size="11.5" font-weight="700" fill="#5B6673">건물 사용검사 지연에만 작동하는 유일한 대금 유보 장치를, 대지권 지연에는 괄호 한 줄로 배제</text>
    </svg>
    <div class="navybox" style="margin-top:auto">참고 사례 — 재개발·재건축 단지에서 이전고시 지연으로 입주 후 수년간 대지권 미등기 상태가 지속되어 집단 분쟁이 된 사례가 다수 보도되어 있습니다(예: 송파 헬리오시티 등기지연 집단소송, 2020). 이 단지의 조항 구조는 그 위험을 <b>계약자 부담으로 고정</b>해 둔 형태입니다.</div>
  </div>
  <div class="panel" style="flex:1">
    <h3>원문 인용</h3>
    <div class="q">"보존등기 및 이전등기는 … 다소 지연될 수 있습니다. (특히, <mark>대지에 대한 소유권은 상당 기간이 소요</mark>될 수 있음. 이 경우 <mark>건물등기와 대지권 등기를 별도로 이행</mark>하여야 함)" <span class="src">— 53면</span></div>
    <div class="q" style="margin-top:8px">"도시계획시설이 <mark>준공 및 기부채납 된 이후에 입주가 가능</mark>할 수 있으며 … 지연으로 인해 입주가 지연될 수 있습니다" <span class="src">— 53면</span></div>
    <div class="b" style="margin-top:9px">[분석] 지연의 원인(이전고시·기부채납)은 전부 조합 측 사정인데, 위험(대금 완납+무담보 상태+입주 지연)은 전부 일반분양자가 집니다. "다소 지연"이라는 표현과 괄호 속 "상당 기간"의 낙차가 이 조항의 실체입니다.</div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — ① 이전고시·대지권 등기 예상 시기 서면 고지 ② 기부채납 지연 시에도 지체상금 적용됨을 계약서에 명기 ③ "취소" 문구 삭제 또는 취소 시 계약해제·원상회복 규정 신설.</div>
  </div>
</div>
</div>
""", "07")

# ══════════════ r08 자금관리 ══════════════
page("""
<div class="pad">
<div class="eyebrow">07 · 발견 06 — 자금관리 정보 공백 (치명)</div>
<h1>분양대금 전액이 <u>조합 명의 모계좌</u>로 모이는데 —<br>공동예금주 '(외2)'가 누군지, 관리자가 누군지 <em>공고문에 없습니다</em></h1>
<div class="grid3">
  <div class="panel">
    <h3>① 모계좌의 예금주 "(외2)"</h3>
    <div class="q">"모계좌[국민은행 209701-04-534590, 예금주 : 안양역세권 지구 재개발정비사업 <mark>조합(외2)</mark>]로 이체되어 관리됩니다" <span class="src">— 40면</span></div>
    <div class="b" style="margin-top:8px">[분석] 공동예금주 2인이 시공사인지 신탁사인지 <b>72면 어디에도 특정되지 않습니다.</b> 조합 재정 상태를 알 수 없는 일반분양자에게 대금 관리 주체는 대금 보전의 성립요건에 준하는 정보입니다.</div>
  </div>
  <div class="panel">
    <h3>② 공시를 예고하고 비워둔 표</h3>
    <div class="q">72면 표제 "시행자, 시공업체 및 <mark>자금관리 대리사무사</mark> 현황" — 그러나 표의 열은 <mark>사업주체·시공자뿐</mark>, 대리사무사 정보 없음</div>
    <div class="b" style="margin-top:8px">[분석] 관리계좌 외 납부 시 "주택도시보증공사의 분양보증 대상에 해당되지 않습니다"(40·70면)라고 못 박으면서, 그 관리계좌를 <b>누가 운용하는지는 공란</b>입니다. 스스로 예고한 공시 항목의 누락입니다.</div>
  </div>
  <div class="panel">
    <h3>③ 옵션대금 계좌는 "추후 안내"</h3>
    <div class="q">"발코니 확장 공사비 납부계좌는 분양대금 및 추가 선택품목 납부계좌와 상이하오니 … <mark>추후 별도 안내드릴 예정</mark>입니다" <span class="src">— 45면</span></div>
    <div class="b" style="margin-top:8px">[분석] 계좌 3원화(분양대금/확장비/옵션) 중 확장비·옵션 계좌는 예금주조차 미공개. 84A1 기준 옵션대금 최대 약 4,400만원이 <b>수납 주체 미상 계좌</b>로 납부될 예정 — 이 돈은 HUG 보증 밖입니다(표준약관).</div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — (외2) 예금주 전원·대리사무사(또는 신탁사)·확장비 계좌 예금주를 정정공고 또는 계약안내문으로 명시하고, 분양대금이 조합 사업비와 분리 관리되는지 확인을 요청합니다.</div>
  </div>
</div>
</div>
""", "08")

# ══════════════ r09 중도금 이자 모순 ══════════════
page("""
<div class="pad">
<div class="eyebrow">08 · 발견 07 — 공고문 내 상호 모순 (치명 · 정정 요구 1순위)</div>
<h1>중도금 이자, 41면은 "<em>이자후불제</em>" — 42면은 "<em>사업주체 부담</em>"<br>같은 공고문이 정반대로 말하고 있습니다</h1>
<div class="grid2">
  <div class="panel" style="border-color:#C0392B">
    <h3><span class="pill r">41면</span> 이자후불제 = 계약자가 입주 시 일괄 부담</h3>
    <div class="q">"본 아파트는 중도금 대출 시 <mark>"중도금 이자후불제"</mark> 조건으로 융자 알선을 시행할 예정이며, 총 공급대금의 60%인 중도금 범위 내에서…" <span class="src">— 41면</span></div>
    <div class="b" style="margin-top:10px">이자후불제는 대출기간 중 발생한 이자를 <b>수분양자가 입주 시점에 후납</b>하는 방식의 통용 명칭입니다.</div>
    <h3 style="margin-top:14px"><span class="pill b">42면</span> 사업주체 부담 = 이자지원</h3>
    <div class="q">"중도금 대출이자는 최초 대출이자 발생시부터 사업주체가 지정하는 <mark>최초 입주개시일 전일까지는 사업주체가 부담</mark>하고, 입주지정기간 시작일 이후부터는 … 계약자가 중도금 이자를 부담" <span class="src">— 42면</span></div>
  </div>
  <div class="panel">
    <h3>규모와 파장</h3>
    <div class="calc">[분석 · 가정 명시]<br>59B1 6~10층 900,000,000원 기준<br>중도금 60% = 540,000,000원<br>평균 대출기간 1.5년 · 금리 연 4.5% 가정 시<br>이자 ≒ 540,000,000 × 0.045 × 1.5<br>= <b>약 36,450,000원</b> — 부담 주체가 갈리는 금액</div>
    <div class="b" style="margin-top:10px">[분석] 두 방식은 양립할 수 없습니다. 분쟁 시 사업주체는 유리한 해석(후불제=계약자 부담)을 주장할 수 있고, 48면의 "오기는 계약자가 재확인해야 한다"는 조항이 그 방어논리를 보강합니다. 자금계획의 최대 변수를 이런 상태로 둘 수 없습니다.</div>
    <div class="why3" style="grid-template-columns:1fr 1fr">
      <div class="w"><h4>권리로 주장 가능</h4><p>모순 기재의 명확화 요구 — 약관 해석상 작성자 불이익 원칙(약관규제법 §5②) 원용 가능</p></div>
      <div class="w"><h4>요청·협의 사항</h4><p>"입주개시일 전일까지 사업주체 부담"을 공급계약서 특약으로 확정</p></div>
    </div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — 이자 부담 주체·기간을 단일 조항으로 확정하는 정정공고를 요구합니다. 본 검토의 정정 요구 1순위입니다.</div>
  </div>
</div>
</div>
""", "09")

# ══════════════ r10 옵션 3중 종속 ══════════════
page("""
<div class="pad">
<div class="eyebrow">09 · 발견 08·09 — 옵션 결합 구조 (높음)</div>
<h1>확장 없이는 <u>비데 하나도 못 삽니다</u> — 확장 → 에어컨 → 홈네트워크로<br>이어지는 <em>3중 종속</em>이 설계돼 있습니다</h1>
<div style="display:flex;gap:14px;flex:1;margin-top:12px;min-height:0">
  <div class="panel" style="flex:1.25">
    <h3>종속의 구조 (모식도)</h3>
    <svg viewBox="0 0 620 160" style="width:100%">
      <defs><marker id="a2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#C0392B"/></marker></defs>
      <rect x="5" y="30" width="190" height="100" rx="12" fill="#0F2548"/>
      <text x="100" y="62" text-anchor="middle" font-size="14.5" font-weight="800" fill="#fff">① 발코니 확장</text>
      <text x="100" y="84" text-anchor="middle" font-size="10.5" fill="#B9C9E2">평면 자체가 "확장 전제 설계"(44면)</text>
      <text x="100" y="100" text-anchor="middle" font-size="10.5" fill="#B9C9E2">견본주택도 확장형만 전시</text>
      <text x="100" y="116" text-anchor="middle" font-size="10.5" fill="#FFD98A">856만~1,965만원 · 일괄확장만 허용</text>
      <rect x="215" y="30" width="190" height="100" rx="12" fill="#fff" stroke="#C0392B" stroke-width="2"/>
      <text x="310" y="62" text-anchor="middle" font-size="14.5" font-weight="800" fill="#C0392B">② 전 유상옵션</text>
      <text x="310" y="84" text-anchor="middle" font-size="10.5" fill="#5B6673">"발코니 확장옵션 선택 계약시에만</text>
      <text x="310" y="100" text-anchor="middle" font-size="10.5" fill="#5B6673">추가선택 가능 + 이의 불가"(51면)</text>
      <text x="310" y="116" text-anchor="middle" font-size="10.5" fill="#C0392B">비데·식기세척기·냉장고까지 종속</text>
      <rect x="425" y="30" width="190" height="100" rx="12" fill="#fff" stroke="#E1E7EE" stroke-width="2"/>
      <text x="520" y="62" text-anchor="middle" font-size="14.5" font-weight="800" fill="#0F2548">③ 홈네트워크</text>
      <text x="520" y="84" text-anchor="middle" font-size="10.5" fill="#5B6673">"옵션 에어컨만 월패드·홈앱 연동,</text>
      <text x="520" y="100" text-anchor="middle" font-size="10.5" fill="#5B6673">개별 구매품은 연동 불가·이의</text>
      <text x="520" y="116" text-anchor="middle" font-size="10.5" fill="#5B6673">불가"(48면) — 가격 비교 무력화</text>
      <line x1="195" y1="80" x2="211" y2="80" stroke="#C0392B" stroke-width="2.5" marker-end="url(#a2)"/>
      <line x1="405" y1="80" x2="421" y2="80" stroke="#C0392B" stroke-width="2.5" marker-end="url(#a2)"/>
    </svg>
    <h3 style="margin-top:8px">에어컨 "기본" 패키지의 배관 함정</h3>
    <div class="b">옵션 미선택 시 거실+안방 <b>매립배관 2개소가 기본 제공</b>됩니다(47면). 그런데 "기본(일부 실)" 패키지를 선택하면 ① 그 기본 배관이 <b>제거</b>되고 ② 시스템 실외기에 <b>추가 에어컨 연결 금지</b>(48면) ③ 실외기실은 시스템 실외기가 점유 — 미포함 침실의 냉방 설치 경로가 사실상 봉쇄됩니다. <b>안 산 사람보다 확장성이 나빠지는 역설</b>입니다. [분석]</div>
    <div class="cap">덧붙여: 견본주택 전시품은 냉난방기, 실제 공급품은 "냉방 전용"(48면 명문) — 전시물과 공급 사양이 다릅니다.</div>
  </div>
  <div class="panel" style="flex:1">
    <h3>확장비 원단위 — 검증 불가능한 가격</h3>
    <table class="t" style="font-size:12px">
      <tr><th>타입</th><th>확장비(원)</th><th>㎡당 환산*</th></tr>
      <tr><td class="n">43A1</td><td>9,250,000</td><td class="n">215,116원</td></tr>
      <tr><td class="n">39A1</td><td>8,560,000</td><td class="n">219,487원</td></tr>
      <tr><td class="n">84A1</td><td>19,650,000</td><td class="n">233,929원</td></tr>
      <tr><td class="n">43B2</td><td>10,570,000</td><td class="n">245,814원</td></tr>
      <tr><td class="n">59B1·B2</td><td>15,800,000</td><td class="n">267,797원</td></tr>
      <tr class="hl"><td class="n">59A2</td><td class="red">16,950,000</td><td class="red">287,288원 (+33.6%)</td></tr>
    </table>
    <div class="cap">*전용면적(호칭) 기준 [분석]. 확장비는 확장면적에 비례해야 하나 <b>타입별 실제 확장면적이 공고문에 없어</b> 단가 검증 자체가 불가 — 그 상태에서 "감소·증가비용이 정산된 금액"(44면)이라고만 고지.</div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — ① 타입별 확장면적(㎡)·정산내역 공개 ② 확장과 무관한 품목(비데·가전 등) 개별 선택 허용 ③ "기본 패키지 선택 시 미포함 실 냉방 곤란" 통합 경고문 명기 ④ 동일 규격 제품의 홈네트워크 연동 개방.</div>
  </div>
</div>
</div>
""", "10")

# ══════════════ r11 옵션 가격역전·해지 공백 ══════════════
page("""
<div class="pad">
<div class="eyebrow">10 · 발견 09 — 옵션 가격·해지 조건 공백 (높음)</div>
<h1>39형 주방옵션이 59형보다 <em>120만원 비싸고</em>, 해지하면<br>위약금을 무는데 — <u>요율은 어디에도 없습니다</u></h1>
<div class="grid2">
  <div class="panel">
    <h3>가격 역전 실측 (49면 표)</h3>
    <table class="t">
      <tr><th>품목 (동일 세부내용 표기)</th><th>타입</th><th>가격(원)</th></tr>
      <tr class="hl"><td rowspan="3">주방특화 — 조명형유리플랩장(상하부)<br>+독립형후드</td><td class="n">39A1 (최소형)</td><td class="red">4,760,000</td></tr>
      <tr><td class="n">43A1·43A2</td><td>4,340,000</td></tr>
      <tr class="hl"><td class="n">59B1·59B2</td><td class="red">3,560,000 (−120만원)</td></tr>
      <tr><td rowspan="2">거실아트월(세라믹타일+판넬)<br>확장기본형</td><td class="n">59B1·59B2</td><td class="red">9,630,000</td></tr>
      <tr><td class="n">84A1 (최대형)</td><td>7,800,000 (−183만원)</td></tr>
    </table>
    <div class="b" style="margin-top:8px">[분석] 면적·부재량과 가격이 역방향인 구간이 2곳 이상 — 평면 차이로 설명될 수도 있으나 산정근거가 전무하고, "판매가격 및 사양…에 대해 이의를 제기할 수 없고"(51면)로 봉쇄됩니다.</div>
  </div>
  <div class="panel">
    <h3>계약 조건의 3중 공백</h3>
    <div class="b">① <b>목적물 미특정</b> — 에어컨 옵션(최고 1,397만원)은 모델명 없이 "GRILL TYPE"뿐. 같은 48면 가전 표는 모델명을 명기한 것과 대조적. 게다가 "추후 추가, 삭제되거나 변경(<b>금액 포함</b>)될 수 있으며"(47면).<br><br>
    ② <b>해지 비용 미상</b> — "해지시는 위약금과 원상회복비용(실손해액)을 부담"(51면)인데 위약금 요율·산정 주체가 어디에도 없음.<br><br>
    ③ <b>해지 기한 미상</b> — "별도로 공지하는 일정 시점 이후에는 추가, 해지 또는 변경 계약이 불가"(51면) — 기한을 사업주체가 사후에 정함.</div>
    <div class="why3" style="grid-template-columns:1fr 1fr">
      <div class="w"><h4>권리로 주장 가능</h4><p>위약금 요율 없는 위약금 청구는 약관규제법 §8(과중한 손해배상) 다툼 여지</p></div>
      <div class="w"><h4>요청·협의 사항</h4><p>분양계약 해제 시 옵션계약 자동해제·위약금 면제 특약</p></div>
    </div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — 모델명·사양 확정 명기, 위약금 요율 사전 명시, 해지 가능 기한의 객관적 기준(예: 착공 후 O개월) 특정을 요청합니다.</div>
  </div>
</div>
</div>
""", "11")

# ══════════════ r12 정정공고 요구 목록 ══════════════
page("""
<div class="pad">
<div class="eyebrow">11 · 발견 10 — 공고문 오기 실재 + 정정 방식 조항 (높음)</div>
<h1>없는 주택형 "34A1", 계약서 문구 혼입, 작년 날짜 —<br>오기가 실재하는데 정정은 "<em>전화·문자로, 이의 불가</em>"랍니다</h1>
<div class="grid2" style="grid-template-columns:1.35fr 1fr">
  <div class="panel">
    <h3>실측 오기·모순 목록 — 정정공고 요구 대상</h3>
    <table class="t" style="font-size:12px">
      <tr><th style="width:40px">No</th><th style="width:64px">면수</th><th>내용</th></tr>
      <tr class="hl"><td class="n">1</td><td class="n">41↔42면</td><td><b>중도금 이자 부담 주체 상호 모순</b> (이자후불제 ↔ 사업주체 부담) — 발견 07</td></tr>
      <tr><td class="n">2</td><td class="n">49면</td><td>마루 옵션 표에 존재하지 않는 주택형 <b>"34A1"</b> (39A1의 오기로 추정 — 마루 표에만 39A1 행이 없음)</td></tr>
      <tr><td class="n">3</td><td class="n">49면</td><td>주방특화 표 "43B" ↔ 다른 표 전부 "43B2" — 표기 혼용</td></tr>
      <tr><td class="n">4</td><td class="n">59~60면</td><td>정의 없는 <b>"갑"·"을"·"병"</b> 등장 — 공급계약서 조문이 공고문에 그대로 혼입</td></tr>
      <tr><td class="n">5</td><td class="n">35면</td><td>무직자 각서 기산일 <b>"2024.01.01"</b> — 같은 항목의 소득산정 기준(전년도=2025.1.1.)과 불일치, 전년도 공고 서식 잔재로 추정</td></tr>
      <tr><td class="n">6</td><td class="n">28면</td><td>"서류 상이 시 당첨 취소" ↔ 바로 다음 항목 "소명 기회 부여" — 동일 사실관계에 상충 조항 병존</td></tr>
      <tr><td class="n">7</td><td class="n">35~36면</td><td>오탈자: "불규칙환"(→불규칙한)·"재무재표"(→재무제표)·"주책 외 건축물"(→주택 외)</td></tr>
    </table>
  </div>
  <div class="panel">
    <h3>문제는 '정정 방식' 조항</h3>
    <div class="q">"입주자모집공고 표기항목에 오류가 있을 경우 옵션 계약시 <mark>문자발송, 분양 홈페이지, 현장 상담안내, 전화안내 등 방법을 선택해</mark> 정정고지를 할 수 있으며, 옵션계약시 이에 대해 <mark>이의를 제기할 수 없으므로</mark>" <span class="src">— 52면</span></div>
    <div class="q" style="margin-top:8px">"오기 등에 대하여 <mark>반드시 견본주택 고객센터로 문의하여 확인</mark>하여야 하며" <span class="src">— 48면</span></div>
    <div class="b" style="margin-top:9px">[분석] 입주자모집공고는 법정 공시 문서입니다. 실재하는 오기를 두고 정정 방법을 사업주체가 '전화안내'까지 포함해 선택하고, 확인 책임은 계약자에게 지우는 구조 — 오기의 위험을 통째로 소비자에게 이전하는 장치입니다. 이자 모순(발견 07) 같은 실질 분쟁에서 방어논리로 작동합니다.</div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — 오기 7건의 <b>정정공고(공고 형식)</b> 일괄 요구. 옵션가격표 오기 정정은 전화·문자가 아닌 정정공고 또는 개별 서면 교부로 하도록 조항 수정을 요청합니다.</div>
  </div>
</div>
</div>
""", "12")

# ══════════════ r13 설계변경 위임 ══════════════
page("""
<div class="pad">
<div class="eyebrow">12 · 발견 11 — 포괄 위임 조항 (치명)</div>
<h1>"제반 권리를 사업주체에게 <em>위탁하는 데 동의 간주</em>" —<br>내 집 설계가 바뀌어도 <u>최장 6개월간 모를 수 있습니다</u></h1>
<div class="grid2">
  <div class="panel" style="border-color:#C0392B">
    <h3>원문 인용 — 59면</h3>
    <div class="q" style="font-size:13px">"본 공사 진행 중에 이루어지는 각종 설계의 경미한 변경에 대하여 사업주체의 결정에 따르며, <mark>제반 권리를 사업주체에게 위탁하는데 동의하는 것으로 간주</mark>하며, 이에 대한 이의를 제기할 수 없습니다."</div>
    <div class="q" style="margin-top:9px;font-size:13px">"단, "갑" 및 "병"은 경미한 사항의 변경에 대해서는 <mark>6개월 이하의 기간마다</mark> 그 변경 내용을 취합하여 "을"에게 <mark>통보할 수 있다</mark>." <span class="src">— 59~60면 (갑·을·병 정의 없음 = 계약서 혼입)</span></div>
    <div class="b" style="margin-top:9px">[분석] 통상의 "경미한 변경 이의 불가"를 넘어 <b>권리의 포괄 위탁을 의제</b>하는 문구입니다. 의사표시 의제는 약관규제법 §10, 포괄 면책은 §6·§7 위반 시비 소지가 있는 유형입니다.</div>
  </div>
  <div class="panel">
    <h3>왜 이 단지에서 특히 위험한가</h3>
    <div class="why3" style="grid-template-columns:1fr;gap:9px">
      <div class="w"><h4>① 변경이 예정된 단지</h4><p>착공 후 교통영향평가 재심의 예정(60면) — "변경 가능성"이 아니라 변경 절차가 이미 잡혀 있습니다.</p></div>
      <div class="w"><h4>② 통보는 의무가 아니라 재량</h4><p>"통보할 수 있다" — 안 해도 됩니다. 주기도 "6개월 이하" — 계약자는 자기 집 설계 변경을 최장 6개월간, 재량 불통보 시 입주 때까지 모를 수 있습니다.</p></div>
      <div class="w"><h4>③ 조합 의결에서 배제된 계약자</h4><p>설계변경의 실질 결정권(조합 총회·시행자)에 일반분양자는 참여 경로가 없습니다. 위탁 간주는 그 공백을 '동의'로 메꾸는 장치입니다.</p></div>
    </div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — ① "제반 권리 위탁 간주" 문구 삭제 ② 변경 발생 시마다(최소 분기별) 서면·전자 통지 의무화, "통보할 수 있다"→"통보하여야 한다" ③ 갑·을·병 혼입 문구 정정공고.</div>
  </div>
</div>
</div>
""", "13")

# ══════════════ r14 주차·소음·이사 미확정 ══════════════
page("""
<div class="pad">
<div class="eyebrow">13 · 발견 12·13·15 — 미확정 사양 3종 (치명·높음)</div>
<h1>주차는 <em>재심의 예정</em>, 방음벽은 "<em>설치될 수 있음</em>",<br>사다리차는 <u>전 세대 진입 불가</u> — 확정 안 된 채 계약됐습니다</h1>
<div class="grid3">
  <div class="panel" style="border-color:#C0392B">
    <h3><span class="pill r">치명</span> 주차계획 이중 미확정</h3>
    <div class="q">"착공신고 후 <mark>교통영향평가 재심의가 예정</mark>되어 있어 … 주차계획과 일부 차이가 발생할 수 있으며, 이에 따른 설계변경은 <mark>계약자의 동의 없이</mark> … 어떠한 민원이나 이의도 제기할 수 없습니다" <span class="src">— 60면</span></div>
    <div class="b" style="margin-top:8px">[분석] "주차대수 및 조경면적…축소 또는 증가될 수 있으며"(60면) 조항과 결합 — 주차대수가 (a)재심의 절차 (b)무동의 축소 조항의 <b>이중 경로로</b> 계약 후 변동될 수 있습니다. 가정형 상투가 아니라 <b>재심의가 '예정'된 확정 사실</b>을 스스로 공시한 경우입니다.</div>
    <div class="navybox" style="margin-top:auto;font-size:11.5px"><b>요청</b> — 승인 기준 총 주차대수·세대당 대수를 하한으로 명시, 재심의 결과 개별 통지.</div>
  </div>
  <div class="panel">
    <h3><span class="pill o">높음</span> 소음은 확정, 대책은 미정</h3>
    <div class="q">"동측에는 <mark>안양역 및 지하철 1호선이 인접</mark>해 있어, 해당 시설 이용에 따른 소음 발생…" <span class="src">— 55면</span><br>"<mark>준공 시 소음 측정에 따라</mark> … 방음벽 등의 시설물이 <mark>설치될 수 있으며</mark>" <span class="src">— 56면</span></div>
    <div class="b" style="margin-top:8px">[분석] 소음원(철도)은 확정 고지하면서 방음계획은 예측 소음도·위치·차음사양 없이 '사후 측정 조건부'입니다. 방음벽이 서면 저층 조망 침해가 다시 세대 부담으로 — 양방향 모두 이의 불가.</div>
    <div class="navybox" style="margin-top:auto;font-size:11.5px"><b>요청</b> — 소음예측 결과·방음계획 확정본, 철도 직면 동·라인, 동측 창호 차음등급 공개.</div>
  </div>
  <div class="panel">
    <h3><span class="pill o">높음</span> 이사는 엘리베이터로만</h3>
    <div class="q">"단지 배치 및 창호 형태 상 <mark>이삿짐 사다리차의 진입 및 이용이 불가능</mark>하므로, 이삿짐 운반 시 엘리베이터를 이용하여야" <span class="src">— 57면</span></div>
    <div class="b" style="margin-top:8px">[분석] 예외 없는 전 세대 사다리차 불가는 드문 고지입니다. 대형 가전·가구는 EV 규격 안에서만 반입 가능한데 <b>공고문에 EV 유효 규격(문폭·깊이·적재하중)이 없습니다.</b> "희망 가전 설치 불가할 수 있으니 유의"(57면)와 결합하면 검증 불가능한 위험 전가입니다.</div>
    <div class="navybox" style="margin-top:auto;font-size:11.5px"><b>요청</b> — 동별 EV 유효 규격 서면 교부, 입주기 EV 예약·보양 운영계획 고지.</div>
  </div>
</div>
</div>
""", "14")

# ══════════════ r15 동별 부담 중첩 ══════════════
DONG = [
 ("204동",["근생 실외기(측벽)","근생 엘리베이터","근생 인접","재활용보관창고","문주(저층)"],5),
 ("203동",["근생 실외기(측벽)","근생 엘리베이터","근생 인접"],3),
 ("201동",["근생 엘리베이터","공공보행통로","문주(저층)","옥상 안테나","주차램프(1~3층)"],5),
 ("202동",["근생 엘리베이터","근생 인접","공공보행통로"],3),
 ("104동",["공공보행통로","보호자대기쉼터","문주(저층)","옥상 안테나","주차램프(1~3층)"],5),
 ("103동",["공공보행통로","옥상 안테나"],2),
 ("101동",["문주(저층)","주차램프(1~3층)"],2),
]
cards = "".join(
  f'''<div class="panel" style="border-color:{'#C0392B' if n>=5 else ('#B7791F' if n>=3 else '#E1E7EE')};padding:10px 12px">
  <h3 style="margin-bottom:5px">{d} <span class="pill {'r' if n>=5 else ('o' if n>=3 else 'gy')}">{n}건 중첩</span></h3>
  <div class="b" style="font-size:12.5px;line-height:1.6">{" · ".join(items)}</div></div>'''
  for d,items,n in DONG)
page(f"""
<div class="pad">
<div class="eyebrow">14 · 발견 14 — 동별 부담 중첩 (높음)</div>
<h1>공고문엔 흩어져 있지만, 겹쳐 보면 <em>204·201·104동에</em><br>부담시설이 <u>5중으로 집중</u>됩니다</h1>
<div style="display:flex;gap:14px;flex:1;margin-top:12px;min-height:0">
  <div style="flex:1.35;display:grid;grid-template-columns:repeat(2,1fr);gap:10px;grid-auto-rows:1fr">{cards}</div>
  <div class="panel" style="flex:1">
    <h3>근거 조항 (62~63면·53·55·59면 — 동 지정 원문 집계)</h3>
    <div class="q" style="font-size:11.5px">"근린생활시설#2,#3의 실외기는 <mark>203동, 204동 주동 측벽 인근</mark>에 설치되므로 … 민원을 제기할 수 없습니다"(62면) · "일부 동(<mark>204동</mark>)에 인접하여 재활용보관창고"(62면) · "특히 <mark>101, 104, 201, 204동 저층</mark> 세대의 경우 문주 설치로 인한…환경권 피해"(63면) · "안테나 설치 예정 장소 : 옥상층 <mark>103동, 104동, 201동, 204동</mark>"(53면) · "<mark>101동, 104동, 201동, 204동 1~3층</mark>…주차램프 구조물에 의해 시야간섭, 소음, 빛공해"(59면)</div>
    <div class="b" style="margin-top:9px">[분석] 각 조항은 별개 문장으로 흩어져 있어 문장 단위로 읽으면 개별 리스크로 보입니다. 동별로 집계해야 <b>204동(측벽 실외기+재활용창고+문주 등 5건)</b>과 <b>201·104동(안테나+램프+문주 등 5건)</b>의 집중이 드러납니다. 재개발 단지는 조합원 동·호 배정이 선행되므로, 중첩 동 저층이 일반분양분에 몰렸는지도 점검 대상입니다(공고문만으로 확인 불가).</div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — ① 동·호수별 부담시설 종합표(안테나·램프·근생 실외기·창고·문주) 제공 ② 203·204동 측벽 근생 실외기의 저소음 사양·방음 처리 ③ 일반분양 세대의 동·호 분포 자료 공개.</div>
  </div>
</div>
<div class="cap">※ 상기 집계는 공고문 원문의 동 지정 조항을 겹친 것으로, 배치도 상 위치 관계는 사업주체 공식 자료(배치도 이미지)로 재확인 필요 — 모식적 집계표.</div>
</div>
""", "15")

# ══════════════ r16 교육환경 1 ══════════════
page("""
<div class="pad">
<div class="eyebrow">15 · 발견 16 — 교육환경 조사 ① 배정·현황 (높음)</div>
<h1>배정 유력 만안초는 <em>16학급 353명</em>의 소규모 학교 —<br>이 단지 하나로 학생이 <u>절반 가까이 늘 수 있습니다</u></h1>
<div class="grid3">
  <div class="panel">
    <h3>배정 학교 — "추정"인 이유</h3>
    <table class="t" style="font-size:11.5px">
      <tr><th>구분</th><th>학교</th><th>근거 수준</th></tr>
      <tr class="hl"><td class="n">초등(유력)</td><td><b>만안초</b> (공립)</td><td>복수 언론 "도보 통학" 일치 — <b>추정</b></td></tr>
      <tr><td class="n">초등(차순위)</td><td>안양초 (공립)</td><td>만안구 최대 규모교 — 미확인</td></tr>
      <tr><td class="n">중학(도보권)</td><td>안양여중(사립·여)<br>근명중(사립·공학)</td><td>NEIS 소재지 확정 — 배정방식 미확보</td></tr>
    </table>
    <div class="b" style="margin-top:8px">통학구역은 <b>안양과천교육지원청 고시가 유일한 확정 근거</b>인데 고시 원문을 확보하지 못해 "추정"으로만 표기합니다. 도보권 중학교 2곳이 <b>모두 사립</b>(NEIS 확정)이라는 점, 여학생 외 선택지가 근명중 1곳뿐이라는 점은 확인된 사실입니다.</div>
  </div>
  <div class="panel">
    <h3>만안초 실측 (나이스·학교알리미)</h3>
    <div class="calc">2026학년도 학급수 <b>16학급</b> (특수 3 포함)<br>학생수 <b>353명</b> (남 190 · 여 163)<br><br>학급당 학생수<br>— 전체학급 기준: 353÷16 = <b>22.1명</b><br>— 일반학급 기준: 353÷13 = <b>27.2명</b><br><br>경기 초등 평균 21.2명 · 과밀 기준 28명 초과</div>
    <div class="b" style="margin-top:8px">[분석] 전체학급 기준으론 경기 평균 수준이지만 <b>일반학급 기준으론 과밀 문턱(28명)에 근접</b>합니다. 참고: 2024년 436명 → 최근 353명으로 감소 — 재개발 이주(멸실)에 따른 일시적 공동화 가능성이 있으며, 입주와 함께 되돌아올 수요입니다(추정).</div>
  </div>
  <div class="panel">
    <h3>공고문은 뭐라고 하나</h3>
    <div class="q">"학교, 도로, 공원·녹지 … 사업부지 외의 개발계획 및 기반시설은 인·허가 협의 시 일부 변경, 지연될 수 있고, <mark>학교 및 학군의 경우 교육청의 여건에 따라 분양 당시와 일치하지 않을 수 있으며</mark>, 이에 대해 사업주체 및 시공사에 <mark>이의를 제기할 수 없습니다</mark>" <span class="src">— 53면</span></div>
    <div class="b" style="margin-top:9px">[분석] 학교 변경 가능 고지는 모든 공고문에 있는 상투입니다. 이 단지에서 문제가 되는 것은 조항이 아니라 <b>수치</b>입니다 — 소규모 학교 하나에 853세대가 유입되는데, 수용 계획이 공개된 곳이 없습니다. →</div>
    <div class="navybox" style="margin-top:auto">수용력 시뮬레이션과 개선요청은 다음 장에서 계속됩니다.</div>
  </div>
</div>
</div>
""", "16")

# ══════════════ r17 교육환경 2 ══════════════
page("""
<div class="pad">
<div class="eyebrow">16 · 발견 16 — 교육환경 조사 ② 수용력·개선요청 (높음)</div>
<h1>853세대 유입 추정 <em>171~213명</em> — 현재 학생의 48~60%인데,<br><u>증축·신설 계획은 확인되지 않았습니다</u></h1>
<div class="grid2" style="grid-template-columns:1.2fr 1fr">
  <div class="panel">
    <h3>수용력 시뮬레이션 [분석 · 계수 출처 명시]</h3>
    <svg viewBox="0 0 640 250" style="width:100%">
      <line x1="40" y1="210" x2="620" y2="210" stroke="#D5DDE7" stroke-width="2"/>
      <rect x="80" y="90" width="120" height="120" fill="#8FA3C0"/>
      <text x="140" y="80" text-anchor="middle" font-size="15" font-weight="800" fill="#0F2548">현재 353명</text>
      <rect x="280" y="90" width="120" height="120" fill="#8FA3C0"/>
      <rect x="280" y="32" width="120" height="58" fill="#C0392B"/>
      <text x="340" y="22" text-anchor="middle" font-size="15" font-weight="800" fill="#C0392B">+171명 (계수 0.2)</text>
      <rect x="460" y="90" width="120" height="120" fill="#8FA3C0"/>
      <rect x="460" y="18" width="120" height="72" fill="#C0392B"/>
      <text x="520" y="10" text-anchor="middle" font-size="15" font-weight="800" fill="#C0392B">+213명 (계수 0.25)</text>
      <text x="140" y="232" text-anchor="middle" font-size="12.5" font-weight="700" fill="#5B6673">만안초 현재</text>
      <text x="340" y="232" text-anchor="middle" font-size="12.5" font-weight="700" fill="#5B6673">입주 후(보수적)</text>
      <text x="520" y="232" text-anchor="middle" font-size="12.5" font-weight="700" fill="#5B6673">입주 후(상단)</text>
    </svg>
    <div class="calc">853세대 × 0.20 = 171명 / 853세대 × 0.25 = 213명<br>학급 환산(25명/학급): 171~213 ÷ 25 = <b>7~9개 학급 증설 수요</b><br>계수 출처: 부산시의회 시정질문 보도의 적용 사례(0.2~0.25) — <b>경기도교육청 공식 계수는 미확보</b>(타 시도 사례에 의한 참고 추정). 소형 타입 위주 단지라 실제 유발률은 낮을 수 있음.</div>
  </div>
  <div class="panel">
    <h3>확인된 것 / 확인 안 된 것</h3>
    <table class="t" style="font-size:11.8px">
      <tr><th>항목</th><th>상태</th></tr>
      <tr><td>안양역세권 재개발 학교 신설·만안초 증축 계획</td><td class="red">공개 자료에서 미발견</td></tr>
      <tr><td>인근 재개발로 추가 세대 유입 예정(기사 확인)</td><td class="n">확인 — 수요는 이 단지만이 아님</td></tr>
      <tr><td>통학구역 고시·통학로(안양로 횡단 여부)</td><td class="red">미확보 — 실측 필요</td></tr>
      <tr><td>학교용지부담금·교육청 협의 내용</td><td class="red">사업시행인가 고시문 미확보</td></tr>
    </table>
    <div class="b" style="margin-top:9px">[분석] "미발견"은 "계획 없음 확정"이 아닙니다. 다만 <b>계획이 있다면 공개되지 않을 이유가 없는 정보</b>이고, 없다면 입주 시점(2029.04)의 과밀·원거리 배정 위험은 실재합니다.</div>
    <div class="navybox" style="margin-top:auto"><b>개선요청</b> — ① 사업시행자에게: 학교용지부담금 납부·교육청 취학수요 협의 결과 공개 ② 교육지원청에: 본 단지 취학구역 지정 계획과 만안초 수용 계획(증축·분산배정) 조회 회신 ③ 입주예정자협의회 명의 공식 질의 발송 — 초안은 별도 제공 가능.</div>
  </div>
</div>
</div>
""", "17")

# ══════════════ r18 정량 실측 + 기록 ══════════════
dist = [(42,1),(43,1),(44,1),(45,3),(48,4),(49,3),(51,1),(52,4),(53,2),(54,8),(55,2),(56,2),(57,4),(59,1),(60,17),(61,12),(62,2),(63,2),(65,3),(66,2)]
bx=""
x=30
for pg_,n in dist:
    h=n*11; bx+=f'<rect x="{x}" y="{200-h}" width="20" height="{h}" fill="{"#C0392B" if n>=8 else "#3E6CB5"}"/><text x="{x+10}" y="216" text-anchor="middle" font-size="9.5" font-weight="700" fill="#5B6673">{pg_}</text>'
    if n>=8: bx+=f'<text x="{x+10}" y="{192-h}" text-anchor="middle" font-size="11" font-weight="800" fill="#C0392B">{n}</text>'
    x+=27
page(f"""
<div class="pad">
<div class="eyebrow">17 · 정량 실측 + 절차 경과 기록</div>
<h1>"이의를 제기할 수 없다" <em>75회 실측</em> — 그중 29회가<br>단지여건·설계 유의사항 두 면(60~61면)에 몰려 있습니다</h1>
<div class="grid2" style="grid-template-columns:1.15fr 1fr">
  <div class="panel">
    <h3>면별 분포 (원문 전수 검색 실측)</h3>
    <svg viewBox="0 0 590 225" style="width:100%">{bx}
      <text x="30" y="20" font-size="12" font-weight="800" fill="#0F2548">건수</text>
    </svg>
    <div class="b">청약 절차 면(1~40면대 초반)에는 드물고, <b>계약자가 실제로 살게 될 집의 사양을 다루는 구간(60~61면 29회)</b>에 집중 — 이의 봉쇄가 주거 품질 영역에 몰려 있다는 뜻입니다. "일체의 책임을 지지 않습니다" 유형 문구도 별도로 확인됩니다.</div>
    <div class="cap">검색식: "이의[를·도] 제기할 수 없" 계열 정규식 전수 카운트, 총 75회. 면 배정은 페이지 마커 기준.</div>
  </div>
  <div class="panel">
    <h3>절차 경과 기록 (청약 단계 — 계약자 참고)</h3>
    <div class="b" style="font-size:11.8px;line-height:1.6">
    ① <b>다자녀 특공 10%→3.2% 축소</b>(14면 명시) — 축소분 대부분(25세대)을 "1인가구 위주" 생애최초 추첨형으로 이전. 근거는 2020.02.28.자 국토부 공문 하나 — 2자녀 완화(2023.11.) 이후 유효성은 확인 필요.<br>
    ② <b>생애최초 표제 "9% 범위: 61세대"</b> — 실제 15.0%로 표제와 자기모순(20면).<br>
    ③ <b>서류 미제출 = "계약 포기 간주·일반 당첨자"</b> 분류(28면) — 부적격(통장 부활)보다 불리한 역전 구조. 소명 심사기한 미기재.<br>
    ④ 특공 222세대(54.6%) — 일반공급 185세대, 가점제는 최대 약 74세대(18%) [분석].</div>
    <div class="b" style="margin-top:8px;font-size:11.8px">기타 확인요청 목록: 샘플하우스 세대 사용(53면, 대상·보상 공백) · 부대복리시설 사업주체 무상사용(53면, 기간 미특정) · 견본주택 2개 타입 옵션 시공 상태만 전시(55~56면) · DC전원 조명 하자책임 제조사 전가(65면) · 입주 후 비용 전가 3종(홍보 사인물 유지비·IoT 회선비·영구배수 관리비, 63·66면).</div>
    <div class="navybox" style="margin-top:auto;font-size:11.5px">HUG 분양보증 183,277,010,000원(70면) ÷ 407세대 = 세대 평균 약 4.50억원 — 일반분양 총 분양대금과의 정합 여부는 <b>사업주체 소명 요청 사항</b>으로 분류(공고문만으로 검산 불가).</div>
  </div>
</div>
</div>
""", "18")

# ══════════════ r19 종합 개선요청 ══════════════
page("""
<div class="pad">
<div class="eyebrow">18 · 종합 개선요청 권고</div>
<h1>정정공고 <em>1건</em>, 정보공개 <em>5건</em>, 계약조항 개선 <em>6건</em> —<br>입주예정자협의회 명의로 요구할 수 있는 목록입니다</h1>
<div style="display:flex;gap:14px;flex:1;margin-top:12px;min-height:0">
  <div class="panel" style="flex:1">
    <h3><span class="pill r">권리로 주장 가능</span> 즉시 요구</h3>
    <div class="b" style="font-size:12px;line-height:1.65">
    <b>1. 정정공고 요구</b> — 중도금 이자 모순(41↔42면)·34A1·갑을병 혼입·2024.01.01 등 오기 7건 일괄 (발견 07·10)<br>
    <b>2. 분양가·옵션 산정근거 정보 요구</b> — 59형 층별 격차, 타입별 확장면적·정산내역, 옵션 가격 역전 사유 (발견 03·08·09)<br>
    <b>3. 자금관리 주체 공개</b> — 모계좌 공동예금주 "(외2)"·자금관리 대리사무사·확장비 계좌 예금주 (발견 06)<br>
    <b>4. 하자담보책임 관련</b> — DC조명 "시공사 귀책 없음" 문구는 법정 하자담보책임(공동주택관리법령)을 배제할 수 없음을 확인</div>
  </div>
  <div class="panel" style="flex:1">
    <h3><span class="pill b">요청·협의 사항</span> 협의회 명의 공문</h3>
    <div class="b" style="font-size:12px;line-height:1.65">
    <b>5. 세대구성 공개</b> — 조합원분·보류지·임대 세대수와 동·층 분포, 일반분양 세대 분포 (발견 01·14)<br>
    <b>6. 등기·입주 일정</b> — 이전고시 예정 시기, 기부채납 시설 목록·준공 예정, 지연 시 지체상금 적용 명문화 (발견 04·05)<br>
    <b>7. 설계변경 통지</b> — 위탁 간주 문구 삭제, 변경 발생 시 즉시 서면 통지 의무화 (발견 11)<br>
    <b>8. 미확정 사양 확정</b> — 주차대수 하한·재심의 결과 통지, 소음예측·방음계획, EV 규격 (발견 12·13·15)<br>
    <b>9. 교육환경</b> — 학교용지부담금·취학수요 협의 결과, 만안초 수용 계획 조회 (발견 16)<br>
    <b>10. 옵션 계약 조건</b> — 위약금 요율·해지 기한 특정, 무관 품목 개별 선택 (발견 08·09)</div>
  </div>
  <div class="panel" style="flex:.9;background:#0F2548;border-color:#0F2548">
    <h3 style="color:#fff">검토의 한계와 다음 단계</h3>
    <div class="b" style="color:#B9C9E2;font-size:11.8px;line-height:1.6">
    · 본 보고서는 공고문 원문 72면 전수 통독 + 공개자료 교차검증으로 작성했습니다. 공급계약서·관리처분계획 원문은 미확보 — 확보 시 등기·설계변경 조항 대조를 보강합니다.<br><br>
    · 배치도·평면도는 사업주체가 이미지로만 제공해 원본 확보가 필요합니다(홈페이지 이미지 URL 목록 확보 완료).<br><br>
    · 통학구역 고시·교육청 협의 내용은 정보공개청구 대상입니다.<br><br>
    <b style="color:#FFD98A">법무법인 제이엘은 위 요구 목록의 공문 초안 작성과 사업주체·교육지원청 대응을 지원합니다.</b></div>
  </div>
</div>
</div>
""", "19")

print("\n".join(pages))
print(f"총 {len(pages)}장 생성 완료 → {OUT}/")
