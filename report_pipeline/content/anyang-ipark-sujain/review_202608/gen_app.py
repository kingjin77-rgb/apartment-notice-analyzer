# -*- coding: utf-8 -*-
"""안양역 센트럴 아이파크 수자인 — 반응형 웹앱 (다운로드 버튼 포함)"""
import base64

pdf_b64 = base64.b64encode(open('/tmp/ay/안양역_센트럴_아이파크_수자인_검토보고서_JL.pdf','rb').read()).decode()
pptx_b64 = base64.b64encode(open('/tmp/ay/안양역_센트럴_아이파크_수자인_검토보고서_JL.pptx','rb').read()).decode()

FINDINGS = [
 ("01","치명","혼합단지","조합원 선점 구조 — 중형은 조합원, 일반분양은 초소형",
  "전용 84형은 34세대를 짓고 일반분양은 단 1세대. 59형은 200세대 중 37세대만 일반분양. 일반분양 407세대의 90.7%(369세대)가 전용 43㎡ 이하.",
  "총 세대수 출처: 공식 홈페이지 평면정보(2026.08.12. 확인) — 일반분양 세대수는 공고문 7면과 8개 타입 전부 일치. 853세대 중 비일반분양 446세대의 구성(조합원분·보류지·임대)은 공고문에 없음.",
  "조합원분·보류지·임대 세대수와 동·층 분포 공개 요청"),
 ("02","치명","혼합단지","1·2단지 대지지분 39.5% 격차 — 무작위 추첨으로 배정",
  "같은 주택형인데 43A1(1단지) 대지지분 19.0858㎡ vs 43A2(2단지) 13.6802㎡ = 1.395배. 59B1 26.8023 vs 59B2 19.2136도 정확히 1.395배 — 단지 간 체계적 배분 차이.",
  "대지비 원단위 [분석]: 43A1(21층+) 1,402만원/㎡ vs 43A2 1,846만원/㎡(+31.7%). 청약은 주택형 단위(선택 불가)였고 격차 크기·원인은 공고문에 없음. — 7·8면",
  "타입별 대지지분·원단위 비교표와 배분 기준(관리처분계획 근거) 공개 요청"),
 ("03","치명","재개발 종속","대지권 등기 '상당 기간' + 잔금 10% 유예조항 명시적 배제",
  "\"대지에 대한 소유권은 상당 기간이 소요될 수 있음. 이 경우 건물등기와 대지권 등기를 별도로 이행\"(53면). 주택공급규칙 §60의 잔금 10% 유예는 \"대지권에 대한 등기는 … 본 조항은 적용되지 아니합니다\"(11면)로 배제.",
  "[분석] 재개발 대지권 등기는 이전고시(조합 최종 단계)에 종속 — 지연 원인은 조합 사정인데 위험(완납+무담보+처분 제약)은 일반분양자 부담. 면적 정산도 등기 시까지 이연.",
  "이전고시 예정 시기 서면 고지, 등기 지연 시 보호장치(잔금 일부 유보 등) 협의 요청"),
 ("04","치명","재개발 종속","도시계획시설 준공·기부채납 이후에야 입주 — 지연·취소 전면 면책",
  "\"도시계획시설이 준공 및 기부채납 된 이후에 입주가 가능할 수 있으며 … 입주가 지연될 수 있습니다\"(53면) + \"변경, 취소 또는 지연 … 일체의 책임을 지지 않습니다\"(52~53면).",
  "[분석] 아파트가 다 지어져도 조합이 이행할 공원·주차장·치안센터(55면)가 늦어지면 입주가 밀리는 구조. '취소'까지 면책 — 약관규제법 §6·§7 시비 소지.",
  "기부채납 지연 시에도 지체상금 적용됨을 계약서에 명기, 대상 시설 목록·준공 예정 고지 요청"),
 ("05","치명","자금관리","분양대금 전액이 조합 모계좌로 — '(외2)'·대리사무사 정보 공백",
  "모계좌 예금주 \"안양역세권 지구 재개발정비사업 조합(외2)\"(40면) — 공동예금주 2인의 정체가 72면 어디에도 없음. 72면 표제는 '자금관리 대리사무사 현황'을 예고했지만 표에는 대리사무사 정보가 없음.",
  "[분석] 관리계좌 외 납부 시 HUG 분양보증 대상 제외(40·70면)라고 못 박으면서 관리 주체는 공란. 발코니 확장비 계좌는 예금주조차 '추후 안내'(45면).",
  "(외2) 예금주 전원·대리사무사·확장비 계좌 예금주 명시, 조합 사업비와 분리 관리 여부 확인 요청"),
 ("06","치명","계약","중도금 이자 부담 주체 상호 모순 — 정정공고 요구 1순위",
  "41면 \"중도금 이자후불제 조건으로 융자 알선\"(=계약자 후납) ↔ 42면 \"최초 입주개시일 전일까지는 사업주체가 부담\"(=이자지원). 양립 불가능한 두 조건이 같은 공고문에 병기.",
  "[분석] 59B1 9억원 기준 중도금 60%=5.4억, 금리 4.5%·1.5년 가정 시 약 3,600만원이 좌우. 48면 '오기는 계약자가 재확인' 조항이 사업주체 방어논리로 작동할 위험.",
  "이자 부담 주체·기간 단일 조항 확정 정정공고 + 공급계약서 특약으로 '사업주체 부담' 확정 요청"),
 ("07","높음","옵션","발코니 확장 사실상 강제 — 전 유상옵션이 확장계약에 종속",
  "\"평면은 발코니 확장을 전제로 설계\"(44면) + \"유상옵션은 … 발코니 확장옵션 선택 계약시에만 추가선택이 가능하며, 이에 대해 이의를 제기할 수 없습니다\"(51면) — 비데·식기세척기·냉장고까지 확장에 종속.",
  "[분석] 확장비 ㎡당 환산 시 59A2 287,288원으로 84A1(233,929원)보다 22.8% 높음 — 그러나 타입별 실제 확장면적이 공고문에 없어 단가 검증 자체가 불가.",
  "타입별 확장면적·정산내역 공개, 확장과 무관한 품목의 개별 선택 허용 요청"),
 ("08","높음","옵션","시스템에어컨 '기본' 패키지의 배관 함정",
  "옵션 미선택 시 거실+안방 매립배관 2개소 기본 제공(47면). '기본(일부 실)' 패키지 선택 시 ①기본 배관 제거 ②시스템 실외기에 추가 에어컨 연결 금지(48면) ③실외기실 점유 — 미포함 침실의 냉방 설치 경로 봉쇄.",
  "[분석] 안 산 사람보다 확장성이 나빠지는 역설. 견본주택 전시품은 냉난방기인데 실공급품은 '냉방 전용'(48면 명문). 개별 구매 에어컨은 홈네트워크 연동 원천 배제(48면).",
  "통합 경고문 명기, 예비 배관 제공, 동일 규격 제품 연동 개방 요청"),
 ("09","높음","옵션","옵션 가격 역전·모델 미특정·해지 위약금 요율 공백",
  "동일 세부내용의 주방특화가 39A1(476만원) > 59B1·B2(356만원), 아트월은 59B(963만원) > 84A1(780만원) — 면적과 가격이 역방향인데 산정근거 없음(49면).",
  "[분석] 에어컨 옵션(최고 1,397만원)은 모델명 없이 '추후 변경(금액 포함) 가능'(47면). 해지 시 '위약금+원상회복비' 부담인데 요율 미기재, 해지 기한도 '별도로 공지하는 일정 시점'(51면).",
  "산정내역 공개, 위약금 요율·해지 기한의 객관적 기준 사전 명시 요청"),
 ("10","높음","공고 품질","실재하는 오기 7건 + '전화·문자로 정정, 이의불가' 조항",
  "없는 주택형 '34A1'(49면), '43B' 혼용(49면), 정의 없는 '갑·을·병' 계약서 문구 혼입(59~60면), 무직자 각서 기산일 '2024.01.01'(35면, 전년도 서식 잔재 추정), 서류 상이 시 '취소'↔'소명' 상충(28면), 오탈자 3건.",
  "\"오류가 있을 경우 … 문자발송, 분양 홈페이지, 현장 상담안내, 전화안내 등 방법을 선택해 정정고지를 할 수 있으며 … 이의를 제기할 수 없으므로\"(52면) — 법정 공시 문서의 정정을 전화로 갈음.",
  "오기 일괄 정정공고(공고 형식) 요구, 정정 방식 조항 수정 요청"),
 ("11","치명","포괄 위임","설계변경 '제반 권리 위탁 동의 간주' — 통보는 재량·최장 6개월",
  "\"각종 설계의 경미한 변경에 대하여 … 제반 권리를 사업주체에게 위탁하는데 동의하는 것으로 간주하며, 이의를 제기할 수 없습니다\"(59면) + 변경 통보는 \"6개월 이하의 기간마다 … 통보할 수 있다\"(재량).",
  "[분석] 의사표시 의제(약관규제법 §10) 시비 소지. 교통영향평가 재심의가 예정된 단지라 '변경'은 가정이 아니라 예정된 절차 — 계약자는 자기 집 설계 변경을 최장 6개월간 모를 수 있음.",
  "위탁 간주 문구 삭제, 변경 즉시(최소 분기별) 서면 통지 의무화 요청"),
 ("12","치명","미확정 사양","주차계획 이중 미확정 — 재심의 예정 + 무동의 축소 조항",
  "\"착공신고 후 교통영향평가 재심의가 예정되어 있어 … 주차계획과 일부 차이가 발생할 수 있으며 … 계약자의 동의 없이 … 어떠한 민원이나 이의도 제기할 수 없습니다\"(60면).",
  "[분석] \"주차대수 및 조경면적 … 축소 또는 증가될 수 있으며\"(60면)와 결합 — 주차대수가 절차·계약 이중 경로로 계약 후 변동 가능. 가정형 상투가 아니라 재심의가 '예정'된 확정 사실.",
  "승인 기준 주차대수를 하한으로 명시, 재심의 결과 개별 통지, 축소 시 협의 절차 신설 요청"),
 ("13","높음","미확정 사양","1호선·안양역 소음은 확정 고지, 방음시설은 미확정",
  "\"동측에는 안양역 및 지하철 1호선이 인접해 있어, 소음 발생 및 일부 세대에서 사생활 침해\"(55면) + 방음벽은 \"준공 시 소음 측정에 따라 … 설치될 수 있으며\"(56면) — 설치되면 저층 조망 침해가 다시 세대 부담.",
  "[분석] 예측 소음도·방음벽 위치·차음 사양·철도 직면 동/라인 특정이 전혀 없음. 소음 피해와 방음벽 부작용 양쪽 모두 이의 불가.",
  "소음예측 결과·방음계획 확정본·철도 직면 라인·창호 차음등급 공개 요청"),
 ("14","높음","동별 중첩","204·201·104동에 부담시설 5중 집중",
  "204동: 근생 실외기(측벽)+근생EV+근생 인접+재활용보관창고+문주. 201동: 근생EV+공공보행통로+문주+옥상 안테나+주차램프. 104동: 공공보행통로+보호자대기쉼터+문주+안테나+램프. (62~63·53·55·59면 동 지정 조항 집계)",
  "[분석] 조항이 흩어져 있어 문장 단위로는 개별 리스크로 보이지만 동별 집계 시 집중이 드러남. 조합원 배정 선행 구조상 중첩 동 저층이 일반분양분에 몰렸는지 점검 필요.",
  "동·호수별 부담시설 종합표 제공, 측벽 실외기 저소음 사양·방음 처리 요청"),
 ("15","중간","생활 제약","전 세대 이삿짐 사다리차 불가 — EV 규격은 미공개",
  "\"단지 배치 및 창호 형태 상 이삿짐 사다리차의 진입 및 이용이 불가능하므로, 이삿짐 운반 시 엘리베이터를 이용하여야\"(57면) — 예외 없는 전 세대 고지.",
  "[분석] 대형 가전·가구는 EV 규격 안에서만 반입 가능한데 공고문에 EV 유효 규격이 없음. '희망 가전 설치 불가할 수 있으니 유의'(57면)와 결합하면 검증 불가능한 위험 전가.",
  "동별 EV 유효 규격 서면 교부, 입주기 EV 예약·보양 운영계획 고지 요청"),
 ("16","높음","교육환경","배정 유력 만안초는 16학급 소규모 — 수용 계획 미확인",
  "만안초(추정 배정, 통학구역 고시 미확보): 2026학년도 16학급·353명 — 853세대 유입 추정 171~213명(계수 0.2~0.25, 타 시도 사례)은 현 학생의 48~60%. 도보권 중학교는 안양여중(사립·여)·근명중(사립·공학) 2곳뿐.",
  "공고문: \"학교 및 학군의 경우 교육청의 여건에 따라 분양 당시와 일치하지 않을 수 있으며 … 이의를 제기할 수 없습니다\"(53면). 학교 신설·증축 계획은 공개 자료에서 미발견(계획 없음 확정 아님).",
  "학교용지부담금·취학수요 협의 결과 공개, 교육지원청에 취학구역·수용 계획 조회 요청"),
]

cards = ""
for no,g,cat,title,body,calc,ask in FINDINGS:
    gc = {"치명":"g-r","높음":"g-o","중간":"g-b"}[g]
    cards += f'''<article class="card {gc}">
  <div class="chead"><span class="no">{no}</span><span class="pill {gc}">{g}</span><span class="cat">{cat}</span></div>
  <h3>{title}</h3>
  <p class="body">{body}</p>
  <p class="calc">{calc}</p>
  <p class="ask"><b>개선요청</b> — {ask}</p>
</article>'''

html = f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>안양역 센트럴 아이파크 수자인 — JL 검토보고서</title>
<style>
:root{{--navy:#0F2548;--blue:#3E6CB5;--red:#C0392B;--ink:#16202E;--sub:#5B6673;--line:#E1E7EE}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",sans-serif;color:var(--ink);background:#F4F6F9;
 word-break:keep-all;overflow-wrap:break-word;line-height:1.65}}
header{{background:var(--navy);color:#fff;padding:44px 20px 36px}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 4px}}
header .brand{{font-size:13px;font-weight:800;color:#7FA9E8;letter-spacing:2px}}
header h1{{font-size:clamp(22px,4.5vw,34px);font-weight:800;letter-spacing:-1px;margin-top:14px;line-height:1.3}}
header h1 em{{color:#FFD98A;font-style:normal}}
header .sub{{color:#B9C9E2;font-size:14.5px;font-weight:600;margin-top:10px}}
.badge{{display:inline-block;background:var(--red);color:#fff;font-size:12.5px;font-weight:800;padding:6px 12px;border-radius:8px;margin-top:14px;line-height:1.5;max-width:100%;white-space:normal;overflow-wrap:anywhere}}
html,body{{overflow-x:hidden}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:20px}}
.stats .s{{background:rgba(255,255,255,.07);border:1px solid rgba(127,169,232,.3);border-radius:12px;padding:12px 14px}}
.stats .v{{font-size:22px;font-weight:800}}.stats .v span{{font-size:13px;color:#7FA9E8}}
.stats .k{{font-size:11.5px;color:#8FA3C0;font-weight:600;margin-top:3px}}
.dl{{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}}
.dl a{{background:#fff;color:var(--navy);font-weight:800;font-size:13.5px;text-decoration:none;
 padding:11px 18px;border-radius:10px;display:inline-flex;align-items:center;gap:7px}}
.dl a.ghost{{background:transparent;color:#B9C9E2;border:1.5px solid rgba(127,169,232,.5)}}
main{{padding:30px 20px 60px}}
h2.sec{{font-size:20px;font-weight:800;color:var(--navy);letter-spacing:-.5px;margin:34px 0 6px}}
p.secsub{{font-size:13.5px;color:var(--sub);font-weight:600;margin-bottom:16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}}
.card{{background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:18px;border-top:4px solid var(--blue)}}
.card.g-r{{border-top-color:var(--red)}}.card.g-o{{border-top-color:#B7791F}}
.chead{{display:flex;align-items:center;gap:8px;margin-bottom:9px}}
.chead .no{{font-size:13px;font-weight:800;color:#B9C4D2}}
.pill{{font-size:11px;font-weight:800;padding:2px 9px;border-radius:20px}}
.pill.g-r{{background:#FBEAEA;color:var(--red)}}.pill.g-o{{background:#FCF3E2;color:#B7791F}}.pill.g-b{{background:#EDF2FA;color:var(--blue)}}
.chead .cat{{font-size:11.5px;font-weight:800;color:var(--sub)}}
.card h3{{font-size:16px;font-weight:800;color:var(--navy);letter-spacing:-.4px;line-height:1.4;margin-bottom:9px}}
.card .body{{font-size:13.5px;font-weight:600;color:#31404F;margin-bottom:9px}}
.card .calc{{font-size:12.5px;font-weight:600;color:var(--sub);background:#F7F9FC;border-left:3px solid #C9D4E2;
 padding:9px 12px;border-radius:0 8px 8px 0;margin-bottom:9px}}
.card .ask{{font-size:12.5px;font-weight:700;color:#fff;background:var(--navy);border-radius:9px;padding:9px 12px}}
.card .ask b{{color:#FFD98A}}
.note{{background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:18px;font-size:13.5px;font-weight:600;color:#31404F}}
.note b{{color:var(--navy)}}
footer{{background:var(--navy);color:#8FA3C0;font-size:12px;font-weight:600;padding:22px 20px;text-align:center;line-height:1.7}}
footer b{{color:#fff}}
</style></head><body>
<header><div class="wrap">
<div class="brand">JL LAWFIRM · 분양공고문 분석팀</div>
<h1>계약서에 없는 위험은, 공고문 <em>72면 안에</em> 있었습니다</h1>
<div class="sub">안양역 센트럴 아이파크 수자인 입주자모집공고(2026.01.) 전수 통독 검토보고서 · 검토기준일 2026.08.12</div>
<div class="badge">사업유형 판별 — 재개발정비사업 조합 물건 · 조합원분과 일반분양분이 병존하는 혼합단지</div>
<div class="stats">
<div class="s"><div class="v">853<span>세대</span></div><div class="k">지하4~지상35층 · 8개동 · 일반분양 407세대</div></div>
<div class="s"><div class="v">16<span>건</span></div><div class="k">상투 배제 후 선별된 발견 (치명 8 · 높음 6 · 중간 2)</div></div>
<div class="s"><div class="v">75<span>회</span></div><div class="k">"이의를 제기할 수 없다" 실측 (60~61면 29회)</div></div>
<div class="s"><div class="v">2029.04</div><div class="k">입주예정 — 도시계획시설 준공·기부채납 종속</div></div>
</div>
<div class="dl">
<a href="data:application/pdf;base64,{pdf_b64}" download="안양역_센트럴_아이파크_수자인_검토보고서_JL.pdf">📄 PDF 다운로드 (19면)</a>
<a href="data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{pptx_b64}" download="안양역_센트럴_아이파크_수자인_검토보고서_JL.pptx">📊 PPTX 다운로드</a>
</div>
</div></header>
<main><div class="wrap">
<h2 class="sec">발견 16건 — 이 단지에서만 확인된 것</h2>
<p class="secsub">여러 단지 공통 상투 조항 18유형(주차 층고·내진 등급·HUG 표준약관·실외기 고지 등)은 시작부터 배제했습니다. 원문 사실과 [분석]을 구분 표기하며, 전 건 원문 면수·인용을 확보했습니다.</p>
<div class="grid">{cards}</div>
<h2 class="sec">절차 경과 기록 (청약 단계)</h2>
<p class="secsub">청약은 종료되었으나 기록 가치가 있는 사항입니다.</p>
<div class="note">① <b>다자녀 특공 10%→3.2% 축소</b>(14면 명시) — 축소분 대부분(25세대)을 "1인가구 위주" 생애최초 추첨형으로 이전. 근거는 2020.02.28.자 국토부 공문 하나.<br>
② <b>생애최초 표제 "9% 범위: 61세대"</b> — 실제 15.0%로 표제와 자기모순(20면).<br>
③ <b>서류 미제출 = "계약 포기 간주·일반 당첨자"</b> 분류(28면) — 부적격 처리(통장 부활)보다 불리한 역전 구조, 소명 심사기한 미기재.<br>
④ 특공 222세대(54.6%) — 일반공급 185세대, 가점제 물량은 최대 약 74세대(18%) [분석].</div>
<h2 class="sec">종합 개선요청 — 입주예정자협의회 명의 요구 목록</h2>
<div class="note"><b>권리로 주장 가능(즉시)</b> — ① 오기 7건 일괄 정정공고 ② 분양가·옵션 산정근거 정보 요구 ③ 자금관리 주체((외2)·대리사무사) 공개 ④ DC조명 하자책임: 법정 하자담보책임은 공고 문구로 배제 불가 확인<br><br>
<b>요청·협의 사항(공문)</b> — ⑤ 세대구성(조합원분·보류지·임대) 공개 ⑥ 이전고시·기부채납 일정과 지체상금 적용 명문화 ⑦ 설계변경 즉시 통지 의무화 ⑧ 주차대수 하한·소음 방음계획·EV 규격 확정 ⑨ 학교 취학수요 협의 결과·만안초 수용 계획 조회 ⑩ 옵션 위약금 요율·해지 기한 특정<br><br>
법무법인 제이엘은 위 요구 목록의 공문 초안 작성과 사업주체·교육지원청 대응을 지원합니다.</div>
</div></main>
<footer><b>법무법인 제이엘 · 분양공고문 분석팀</b><br>본 보고서는 입주자모집공고 원문 72면 전수 통독과 공개자료 교차검증으로 작성되었으며, 원문 사실과 [분석]을 구분 표기합니다.<br>공급계약서·관리처분계획 확보 시 등기·설계변경 조항 대조를 보강합니다.</footer>
</body></html>'''

open('/tmp/ay/안양역_수자인_검토보고서_웹앱.html','w',encoding='utf-8').write(html)
print('webapp ok', len(html)//1024, 'KB')
