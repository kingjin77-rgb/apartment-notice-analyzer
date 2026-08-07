/* 안양 에버포레 자연&e편한세상 통합 검토보고서 — 편집가능 PPTX 전체본
 * 대장님 제안서 틀 실측(#156082 제목, 회색밴드 푸터, 3카드) + 실제 배치도 + content.js 검증 데이터
 */
const pptxgen = require("pptxgenjs");
const path = require("path");
const A1 = require("/root/repos/apartment-notice-analyzer/report_pipeline/content/anyang-everforest-a1bl/content.js");
const A2 = require("/root/repos/apartment-notice-analyzer/report_pipeline/content/anyang-everforest-a2bl/content.js");

const p = new pptxgen();
p.layout = "LAYOUT_WIDE";
p.author = "법무법인 제이엘";
p.title = "안양 에버포레 자연&e편한세상 입주자모집공고 검토보고서 (A1BL·A2BL 통합본)";

const W = 13.333, H = 7.5;
const TITLE_C = "156082", NAVY = "1F3864", GOLD = "C89B3C";
const INK = "222B36", BODY = "3d4854", MUTED = "8a93a0", LINE = "D9DDE2";
const F_HEAD = "210 OmniGothic 050", F_BODY = "NanumSquare";
const LOGO = "/root/repos/apartment-notice-analyzer/report_pipeline/template/brand/jl_logo_crop.png";
const LOGO_R = 409 / 138;
const SEV = { "주의": "C0392B", "양호": "2E7D32", "확인필요": "C77700", "보통": "C77700" };

let pageNo = 0;

function frame(s, title) {
  pageNo += 1;
  s.background = { color: "FFFFFF" };
  s.addShape(p.ShapeType.roundRect, { x: 0.62, y: 0.42, w: 0.34, h: 0.34, fill: { color: TITLE_C }, rectRadius: 0.06, line: { type: "none" } });
  s.addText("⌂", { x: 0.62, y: 0.42, w: 0.34, h: 0.34, align: "center", valign: "middle", fontFace: "Segoe UI Symbol", fontSize: 14, bold: true, color: "FFFFFF", margin: 0 });
  s.addText(title, { x: 1.08, y: 0.36, w: 9.6, h: 0.5, fontFace: F_HEAD, fontSize: 18, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
  const lh = 0.36, lw = lh * LOGO_R;
  s.addImage({ path: LOGO, x: W - 0.62 - lw, y: 0.34, w: lw, h: lh });
  s.addShape(p.ShapeType.line, { x: 0, y: 6.98, w: W, h: 0, line: { color: "9E9E9E", width: 0.75 } });
  s.addShape(p.ShapeType.rect, { x: 0, y: 7.17, w: W, h: 0.33, fill: { color: "F2F2F2" }, line: { type: "none" } });
  s.addText("법무법인 제이엘 | JL LAWFIRM", { x: 0.62, y: 6.99, w: 4, h: 0.18, fontFace: F_BODY, fontSize: 8.5, color: "6b7480", margin: 0 });
  s.addText(String(pageNo), { x: W - 1.0, y: 6.99, w: 0.4, h: 0.18, align: "right", fontFace: F_BODY, fontSize: 8.5, color: "6b7480", margin: 0 });
  return s;
}

/* ══ 1. 표지 ══ */
{
  pageNo += 1;
  const s = p.addSlide();
  s.background = { color: "FFFFFF" };
  const lh = 0.5, lw = lh * LOGO_R;
  s.addImage({ path: LOGO, x: 0.7, y: 0.55, w: lw, h: lh });
  s.addText("입주자모집공고 검토보고서  |  A1BL·A2BL 통합본", { x: 0.72, y: 1.9, w: 11, h: 0.4, fontFace: F_HEAD, fontSize: 15, bold: true, color: GOLD, margin: 0 });
  s.addText("안양 에버포레 자연&e편한세상", { x: 0.7, y: 2.3, w: 12, h: 0.95, fontFace: F_HEAD, fontSize: 40, bold: true, color: NAVY, margin: 0 });
  s.addShape(p.ShapeType.line, { x: 0.72, y: 3.35, w: 4.2, h: 0, line: { color: GOLD, width: 2.5 } });
  const cover = [
    ["공급위치", "경기도 안양시 동안구 관양동 521번지 일원 (안양 관양고 주변 도시개발사업 내)"],
    ["사업방식", "「공공주택 특별법」 및 민간참여 공공주택사업 시행지침에 따른 민간참여 공공주택사업"],
    ["사업주체", "공공시행자 경기주택도시공사 / 민간참여사업자 디엘이앤씨㈜·㈜태영건설·금호건설㈜·신동아종합건설㈜"],
    ["공급규모", "A1BL 민영주택(연립) 4개동 60세대  ·  A2BL 국민주택 5개동 344세대  —  총 404세대"],
    ["주요일정", "입주자모집공고 2026.04.30. · 계약체결 2026.06.25.~06.27."],
    ["작성", "법무법인 제이엘 분양공고문 분석팀 · 검토기준일 2026.08.07."],
  ];
  let y = 3.75;
  for (const [k, v] of cover) {
    s.addText(k, { x: 0.72, y, w: 1.5, h: 0.34, fontFace: F_HEAD, fontSize: 11, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
    s.addText(v, { x: 2.3, y, w: 10.3, h: 0.34, fontFace: F_BODY, fontSize: 11, color: BODY, valign: "middle", margin: 0 });
    y += 0.4;
  }
  s.addText(String(A1.disclaimer || "본 보고서는 입주자모집공고 원문을 직접 전수 대조하여 작성되었습니다. 세부사항은 계약 전 반드시 사업주체 및 견본주택에서 재확인하시기 바랍니다."), {
    x: 0.72, y: 6.35, w: 11.9, h: 0.75, fontFace: F_BODY, fontSize: 8.5, color: MUTED, lineSpacingMultiple: 1.25, valign: "top", margin: 0 });
}

/* ══ 2. 통합 요약 ══ */
{
  const s = frame(p.addSlide(), "최우선 개선요구사항 요약  |  통합 (A1BL·A2BL)");
  const rows = [
    ["항목", "블록", "평가", "핵심 근거"],
    ["A1·A2 부대복리시설 공유 여부 미확정", "공통", "주의", "통합운영 여부를 입주자대표회의 구성 후 결정 — 타 블록 시설 사용 불가 가능성 원문 명시"],
    ["내진설계 등급 고지 누락", "공통", "주의", "양 블록 원문 전수검색 '내진' 0건 — 유사 단지 내진 I등급 명시와 대조적"],
    ["분양보증 고지 미확인", "공통", "주의", "분양보증(HUG 등) 문구 양 블록 0건 — 시행자가 경기주택도시공사(공공)라 HUG 체계 밖일 수 있음, 보증구조 확인 요청 필요"],
    ["이의제기 금지 문구 광범위 반복", "공통", "주의", "'이의를 제기할 수 없습니다' A1BL 57회·A2BL 52회 실측 — 재산가치 직결 사항 포함"],
    ["재활용 보관소 전동 인접", "공통", "주의", "A1BL: 101·102동 사이, 103·104동 사이 명시 / A2BL: 각 동 인접(동별 위치 상이) — 수거차량 소음·분진·냄새 원문 고지"],
    ["이동통신 중계장치 위치 사후 변경", "A1BL", "주의", "위치 미확정 상태에서 이의제기 금지 — 확정 위치 계약 전 공개 요청 필요"],
    ["필로티 층고 동별 상이", "A2BL", "주의", "필로티 층고 각 동마다 상이 — 필로티 위층·최상층 바닥난방 효율 저하 고지"],
    ["계약금 부담 수준", "공통", "양호", "분양대금 기준 계약금 10% · 중도금 60%(6회 분납) · 잔금 30% — 표준적 구조 (유상옵션은 20/80 별도)"],
    ["분양가상한제 산정 투명성", "공통", "양호", "주택법 제57조 근거 택지비·건축비 가산비 산출내역 원문 공개"],
  ];
  const body = rows.map((r, ri) => r.map((cell, ci) => ({
    text: String(cell),
    options: ri === 0
      ? { fontFace: F_HEAD, fontSize: 10.5, bold: true, color: "FFFFFF", fill: { color: NAVY }, align: "center", valign: "middle" }
      : { fontFace: F_BODY, fontSize: 9.5, bold: ci === 2, color: ci === 2 ? (SEV[cell] || INK) : (ci === 0 ? INK : BODY), fill: { color: ri % 2 ? "FFFFFF" : "F8F9FB" }, align: ci === 1 || ci === 2 ? "center" : "left", valign: "middle" },
  })));
  s.addTable(body, { x: 0.62, y: 1.25, w: W - 1.24,
    colW: [(W - 1.24) * 0.26, (W - 1.24) * 0.07, (W - 1.24) * 0.07, (W - 1.24) * 0.60],
    border: { type: "solid", color: LINE, pt: 0.75 }, margin: 0.05, autoPage: false, rowH: 0.56 });
}

/* ══ 3. 블록별 스코어카드 (A1 / A2) ══ */
function scoreSlide(content, label) {
  const sc = content.sections[0].blocks.find(b => b.type === "scoreCard");
  const s = frame(p.addSlide(), `블록별 종합평가  |  ${label}`);
  const rows = sc.rows;
  const body = rows.map((r, ri) => [
    { text: String(r[0]), options: ri === 0 ? hd() : { fontFace: F_BODY, fontSize: 9.5, bold: true, color: INK, fill: bg(ri), valign: "middle" } },
    { text: ri === 0 ? String(r[1]) : `● ${r[1]}`, options: ri === 0 ? hd() : { fontFace: F_BODY, fontSize: 9.5, bold: true, color: SEV[r[1]] || INK, fill: bg(ri), align: "center", valign: "middle" } },
    { text: String(r[2]), options: ri === 0 ? hd() : { fontFace: F_BODY, fontSize: 9.5, color: BODY, fill: bg(ri), valign: "middle" } },
  ]);
  function hd() { return { fontFace: F_HEAD, fontSize: 10.5, bold: true, color: "FFFFFF", fill: { color: NAVY }, align: "center", valign: "middle" }; }
  function bg(ri) { return { color: ri % 2 ? "FFFFFF" : "F8F9FB" }; }
  s.addTable(body, { x: 0.62, y: 1.25, w: W - 1.24,
    colW: [(W - 1.24) * 0.26, (W - 1.24) * 0.10, (W - 1.24) * 0.64],
    border: { type: "solid", color: LINE, pt: 0.75 }, margin: 0.05, autoPage: false, rowH: 0.62 });
}
scoreSlide(A1, "A1BL 민영주택 (101~104동, 60세대)");
scoreSlide(A2, "A2BL 국민주택 (201~205동, 344세대)");

/* ══ 4. 동별 유의사항 — 실제 배치도 + 콜아웃 ══ */
function siteSlide(label, imgPath, items, caption) {
  const s = frame(p.addSlide(), `동별·위치별 유의사항  |  ${label}`);
  const img = { w: 7.5, h: 4.8 };
  s.addImage({ path: imgPath, x: 0.62, y: 1.15, w: img.w, h: img.h });
  s.addShape(p.ShapeType.rect, { x: 0.62, y: 1.15, w: img.w, h: img.h, fill: { type: "none" }, line: { color: LINE, width: 1 } });
  s.addText(caption, { x: 0.62, y: 6.02, w: img.w, h: 0.4, fontFace: F_BODY, fontSize: 8, color: MUTED, lineSpacingMultiple: 1.15, margin: 0 });
  const n = items.length;
  const gap = 0.12, boxH = (4.87 - gap * (n - 1)) / n;
  let y = 1.15;
  for (const [dong, txt, c] of items) {
    s.addShape(p.ShapeType.roundRect, { x: 8.35, y, w: 4.35, h: boxH, fill: { color: "FFFFFF" }, rectRadius: 0.05, line: { color: LINE, width: 1 } });
    s.addShape(p.ShapeType.rect, { x: 8.35, y, w: 0.055, h: boxH, fill: { color: c }, line: { type: "none" } });
    s.addText(dong, { x: 8.52, y: y + 0.05, w: 1.5, h: 0.24, fontFace: F_HEAD, fontSize: 11.5, bold: true, color: NAVY, margin: 0 });
    s.addText(txt, { x: 8.52, y: y + 0.3, w: 4.06, h: boxH - 0.36, fontFace: F_BODY, fontSize: n >= 5 ? 8.5 : 9.5, color: BODY, lineSpacingMultiple: 1.14, valign: "top", margin: 0 });
    y += boxH + gap;
  }
}
const CAP = "단지배치도 — 사업주체 공식 홈페이지(elife.co.kr) 게시 자료 발췌. 세부사항은 인·허가 및 시공 과정에서 변경될 수 있음(공고문 고지). 시설 인접관계는 입주자모집공고 원문 기재 기준.";
siteSlide("A1BL (101~104동)", "/tmp/a1bl_site.png", [
  ["101동", "지하1층 부대복리시설(라운지카페·도담누리터) 직접 인접 — 진동·소음 영향 원문 명시 고지. 재활용 보관소 101·102동 사이 배치", "C0392B"],
  ["102동", "문주(102·103동 사이) 인접 — 차량 소음·빛 산란 및 시야 차단 원문 고지. 재활용 보관소 101·102동 사이 배치", "C77700"],
  ["103동", "지하1층 커뮤니티센터(생활지원센터·멀티룸), 지상1층 스터디라운지 인접 — 소음·사생활 침해 고지. 재활용 보관소 103·104동 사이", "C0392B"],
  ["104동", "재활용 보관소(103·104동 사이) 인접 — 수거차량 상시 접근에 따른 소음·분진·냄새 고지(원문 명시)", "C77700"],
], CAP);
{
  const t2 = A2.sections[2].blocks.find(b => b.type === "table");
  const colors = ["C0392B", "C77700", "C0392B", "C77700", "C0392B"];
  const items = t2.rows.slice(1).map((r, i) => [r[0], String(r[1]), colors[i % colors.length]]);
  siteSlide("A2BL (201~205동)", "/tmp/a2bl_site.png", items, CAP);
}

/* ══ 5. 독소조항 — 페이지당 2건 (원문인용 + 개선요청) ══ */
function toxicPages(content, label) {
  const items = content.sections[1].blocks.filter(b => b.type === "toxicItem");
  for (let i = 0; i < items.length; i += 2) {
    const pair = items.slice(i, i + 2);
    const s = frame(p.addSlide(), `계약 전 확인·개선요청 사항  |  ${label}`);
    let y = 1.18;
    for (const b of pair) {
      // 항목 헤더
      s.addText([
        { text: String(b.index).padStart(2, "0") + "  ", options: { fontFace: F_HEAD, fontSize: 12, bold: true, color: GOLD } },
        { text: String(b.cat || ""), options: { fontFace: F_HEAD, fontSize: 13.5, bold: true, color: INK } },
      ], { x: 0.62, y, w: 10.5, h: 0.32, valign: "middle", margin: 0 });
      s.addShape(p.ShapeType.roundRect, { x: W - 1.5, y: y + 0.02, w: 0.86, h: 0.28, fill: { color: "C0392B" }, rectRadius: 0.05, line: { type: "none" } });
      s.addText("중요 상", { x: W - 1.5, y: y + 0.02, w: 0.86, h: 0.28, align: "center", valign: "middle", fontFace: F_BODY, fontSize: 8.5, bold: true, color: "FFFFFF", margin: 0 });
      y += 0.4;
      // 원문 인용
      const qLong = String(b.text || "").length > 165;
      const qh = qLong ? 1.28 : 0.95;
      s.addShape(p.ShapeType.rect, { x: 0.62, y, w: W - 1.24, h: qh, fill: { color: "F8FBFD" }, line: { color: LINE, width: 0.75 } });
      s.addText("문제 조항 (원문)", { x: 0.82, y: y + 0.06, w: 2, h: 0.2, fontFace: F_BODY, fontSize: 8, bold: true, color: "C0392B", margin: 0 });
      s.addText(`“${b.text}”`, { x: 0.82, y: y + 0.27, w: W - 1.64, h: qh - 0.33, fontFace: F_BODY, fontSize: qLong ? 9.5 : 10.5, color: BODY, lineSpacingMultiple: 1.2, valign: "top", margin: 0 });
      y += qh + 0.08;
      // 개선요청
      const fh = 0.62;
      s.addShape(p.ShapeType.rect, { x: 0.62, y, w: W - 1.24, h: fh, fill: { color: "EAF3EA" }, line: { color: "C2DCC4", width: 0.75 } });
      s.addText([
        { text: "✓ 개선요청   ", options: { fontFace: F_BODY, fontSize: 9, bold: true, color: "2E7D32" } },
        { text: String(b.fix || ""), options: { fontFace: F_BODY, fontSize: 10.5, bold: true, color: "1c3a1e" } },
      ], { x: 0.82, y: y + 0.05, w: W - 1.64, h: fh - 0.1, lineSpacingMultiple: 1.18, valign: "middle", margin: 0 });
      y += fh + 0.28;
    }
  }
}
toxicPages(A1, "A1BL");
toxicPages(A2, "A2BL");

/* ══ 6. 마무리 — 종합 개선요청 ══ */
{
  const s = frame(p.addSlide(), "종합 — 입주예정자협의회 개선요청 권고");
  const recs = [
    ["1", "블록 간 시설 공유", "A1·A2 부대복리시설 통합운영에 대한 사업주체의 현재 계획(안)을 계약 전 서면 공개 요청"],
    ["2", "구조·안전 정보", "내진설계 적용 등급, 지하주차장 층고, 영구배수공법 등 미기재 구조 정보의 서면 고지 요청"],
    ["3", "보증 구조", "공공시행자(GH) 체계에서의 분양대금 보전 구조(분양보증 대체 장치) 확인·고지 요청"],
    ["4", "위치 미확정 설비", "이동통신 중계장치·옥외안테나 등 확정 위치의 계약 전 공개 및 전자파 적합성 자료 제공 요청"],
    ["5", "인접 세대 보호", "부대복리시설·재활용보관소·문주 인접 동(양 블록) 계약자 대상 개별 안내 및 방음·차폐 보강 확인 요청"],
  ];
  let y = 1.4;
  for (const [n, t, d] of recs) {
    s.addShape(p.ShapeType.rect, { x: 0.62, y, w: W - 1.24, h: 0.92, fill: { color: y % 2 ? "FFFFFF" : "FFFFFF" }, line: { color: LINE, width: 1 } });
    s.addText(n, { x: 0.85, y: y + 0.13, w: 0.6, h: 0.65, fontFace: F_HEAD, fontSize: 26, bold: true, color: NAVY, margin: 0 });
    s.addText(t, { x: 1.6, y: y + 0.12, w: 2.8, h: 0.68, fontFace: F_HEAD, fontSize: 12.5, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
    s.addText(d, { x: 4.5, y: y + 0.12, w: 8.0, h: 0.68, fontFace: F_BODY, fontSize: 10.5, color: BODY, lineSpacingMultiple: 1.2, valign: "middle", margin: 0 });
    y += 1.04;
  }
}

p.writeFile({ fileName: "/tmp/안양에버포레_통합검토보고서_JL.pptx" }).then(() => console.log("SLIDES:", pageNo));
