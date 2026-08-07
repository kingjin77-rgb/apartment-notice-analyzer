/* 수정가능(네이티브 요소) PPTX 데모 — 대장님 제안서 틀 실측 반영
 * 틀: 좌상단 아이콘+티일블루(#156082) 제목, 우상단 JL로고, 하단 회색라인+연회색밴드 푸터
 */
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";
p.author = "법무법인 제이엘";
p.title = "안양 에버포레 자연&e편한세상 검토보고서(통합본) — 편집가능 데모";

const W = 13.333, H = 7.5;
const TITLE_C = "156082";      // 실측 제목색
const NAVY = "1F3864";
const INK = "222B36", BODY = "3d4854", MUTED = "8a93a0";
const LINE = "D9DDE2";
const F_HEAD = "210 OmniGothic 050";
const F_BODY = "NanumSquare";
const LOGO = "/root/repos/apartment-notice-analyzer/report_pipeline/template/brand/jl_logo_crop.png";
const LOGO_R = 409 / 138;

let pageNo = 11; // 데모용 시작 페이지번호

function frame(s, title) {
  pageNo += 1;
  // 헤더 아이콘(집 모양 자리 — 네이비 라운드사각 + ⌂)
  s.addShape(p.ShapeType.roundRect, { x: 0.62, y: 0.42, w: 0.34, h: 0.34, fill: { color: TITLE_C }, rectRadius: 0.06, line: { type: "none" } });
  s.addText("⌂", { x: 0.62, y: 0.42, w: 0.34, h: 0.34, align: "center", valign: "middle", fontFace: "Segoe UI Symbol", fontSize: 14, bold: true, color: "FFFFFF", margin: 0 });
  // 제목
  s.addText(title, { x: 1.08, y: 0.36, w: 9.6, h: 0.5, fontFace: F_HEAD, fontSize: 19, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
  // 우상단 로고
  const lh = 0.36, lw = lh * LOGO_R;
  s.addImage({ path: LOGO, x: W - 0.62 - lw, y: 0.34, w: lw, h: lh });
  // 푸터: 얇은 라인 + 연회색 밴드 + 텍스트
  s.addShape(p.ShapeType.line, { x: 0, y: 6.98, w: W, h: 0, line: { color: "9E9E9E", width: 0.75 } });
  s.addShape(p.ShapeType.rect, { x: 0, y: 7.17, w: W, h: 0.33, fill: { color: "F2F2F2" }, line: { type: "none" } });
  s.addText("법무법인 제이엘 | JL LAWFIRM", { x: 0.62, y: 6.99, w: 4, h: 0.18, fontFace: F_BODY, fontSize: 8.5, color: "6b7480", margin: 0 });
  s.addText(String(pageNo), { x: W - 1.0, y: 6.99, w: 0.4, h: 0.18, align: "right", fontFace: F_BODY, fontSize: 8.5, color: "6b7480", margin: 0 });
}

/* ── 슬라이드 1: 동별 유의사항 — 실제 배치도 + 콜아웃 ── */
{
  const s = p.addSlide();
  s.background = { color: "FFFFFF" };
  frame(s, "동별·위치별 유의사항  |  A1BL (101~104동)");

  // 좌: 실제 배치도
  const img = { w: 7.5, h: 4.8 };
  s.addImage({ path: "/tmp/a1bl_site.png", x: 0.62, y: 1.15, w: img.w, h: img.h });
  s.addShape(p.ShapeType.rect, { x: 0.62, y: 1.15, w: img.w, h: img.h, fill: { type: "none" }, line: { color: LINE, width: 1 } });
  s.addText("단지배치도 — 사업주체 공식 홈페이지(elife.co.kr) 게시 자료 발췌, 세부사항은 인·허가 및 시공 과정에서 변경될 수 있음(공고문 고지)", {
    x: 0.62, y: 6.02, w: img.w, h: 0.35, fontFace: F_BODY, fontSize: 8.5, color: MUTED, margin: 0 });

  // 우: 동별 콜아웃 4개 (전부 편집가능한 텍스트박스)
  const items = [
    ["101동", "지하1층 부대복리시설(라운지카페·도담누리터) 직접 인접 — 진동·소음 영향 원문 명시 고지. 재활용 보관소 101·102동 사이 배치", "C0392B"],
    ["102동", "문주(102·103동 사이) 인접 — 차량 소음·빛 산란 및 시야 차단 원문 고지. 재활용 보관소 101·102동 사이 배치", "C77700"],
    ["103동", "지하1층 커뮤니티센터(생활지원센터·멀티룸), 지상1층 스터디라운지 인접 — 소음·사생활 침해 고지. 재활용 보관소 103·104동 사이", "C0392B"],
    ["104동", "재활용 보관소(103·104동 사이) 인접 — 수거차량 상시 접근에 따른 소음·분진·냄새 고지(원문 명시)", "C77700"],
  ];
  let y = 1.15;
  for (const [dong, txt, c] of items) {
    s.addShape(p.ShapeType.roundRect, { x: 8.35, y, w: 4.35, h: 1.13, fill: { color: "FFFFFF" }, rectRadius: 0.05, line: { color: LINE, width: 1 } });
    s.addShape(p.ShapeType.rect, { x: 8.35, y, w: 0.055, h: 1.13, fill: { color: c }, line: { type: "none" } });
    s.addText(dong, { x: 8.52, y: y + 0.08, w: 1.2, h: 0.25, fontFace: F_HEAD, fontSize: 12.5, bold: true, color: NAVY, margin: 0 });
    s.addText(txt, { x: 8.52, y: y + 0.34, w: 4.05, h: 0.75, fontFace: F_BODY, fontSize: 9.5, color: BODY, lineSpacingMultiple: 1.18, valign: "top", margin: 0 });
    y += 1.245;
  }
}

/* ── 슬라이드 2: 독소조항 3단 (틀의 3카드 배경 그대로) ── */
{
  const s = p.addSlide();
  s.background = { color: "FFFFFF" };
  frame(s, "계약 전 확인·개선요청  |  부대복리시설 인접 소음 (중요 상)");

  const cards = [
    { x: 0.73, bg: "F8FBFD", label: "문제 조항 (원문)", lc: "C0392B",
      txt: "“101동 지하1층 부대복리시설(라운지카페, 도담누리터 등)이, 103동 지하1층 생활지원센터, 멀티룸(주민회의실), 키즈스테이션과 지상1층 스터디라운지 … 미세한 진동 및 소음에 의한 사생활 및 환경권이 침해당할 수 있습니다.”",
      sub: "입주자모집공고 원문 직접 인용" },
    { x: 4.79, bg: "FFFFFF", label: "법무법인 JL 검토", lc: NAVY,
      txt: "침해 가능성만 고지하고 소음 저감 설계·방음 조치 내용은 일절 기재하지 않음 — 101·103동 계약자에게 위험이 전가되는 구조",
      sub: "면책 고지 편중 · 완화조치 미기재" },
    { x: 8.85, bg: "F3F3F3", label: "개선요청", lc: "2E7D32",
      txt: "101동·103동 인접 세대에는 계약 전 개별 안내문을 발송하고, 방음 보강 조치 여부를 확인해 줄 것을 요청합니다.",
      sub: "입주예정자협의회 명의 사전 요청 권고" },
  ];
  for (const c of cards) {
    s.addShape(p.ShapeType.rect, { x: c.x, y: 1.35, w: 3.72, h: 5.2, fill: { color: c.bg }, line: { color: LINE, width: 1 } });
    s.addText(c.label, { x: c.x + 0.25, y: 1.6, w: 3.2, h: 0.3, fontFace: F_HEAD, fontSize: 13, bold: true, color: c.lc, margin: 0 });
    s.addShape(p.ShapeType.line, { x: c.x + 0.25, y: 2.0, w: 3.2, h: 0, line: { color: LINE, width: 1 } });
    s.addText(c.txt, { x: c.x + 0.25, y: 2.15, w: 3.22, h: 3.6, fontFace: F_BODY, fontSize: 12, color: BODY, lineSpacingMultiple: 1.35, valign: "top", margin: 0 });
    s.addText(c.sub, { x: c.x + 0.25, y: 6.05, w: 3.22, h: 0.3, fontFace: F_BODY, fontSize: 9, color: MUTED, margin: 0 });
  }
  // 카드 사이 화살표
  for (const ax of [4.5, 8.56]) {
    s.addText("▶", { x: ax, y: 3.7, w: 0.3, h: 0.4, fontFace: "Arial", fontSize: 14, color: "C89B3C", align: "center", margin: 0 });
  }
}

/* ── 슬라이드 3: 요약 스코어카드 (네이티브 표) ── */
{
  const s = p.addSlide();
  s.background = { color: "FFFFFF" };
  frame(s, "최우선 개선요구사항 요약  |  통합본 (A1BL·A2BL 공통)");

  const rows = [
    ["항목", "블록", "평가", "핵심 근거"],
    ["A1·A2 부대복리시설 공유 여부 미확정", "공통", "주의", "통합운영 여부를 입주자대표회의 구성 후 결정 — 타 블록 시설 사용 불가 가능성 원문 명시"],
    ["내진설계 등급 고지 누락", "공통", "주의", "원문 전수검색 결과 '내진' 0건 — 유사 단지 내진 I등급 명시와 대조적"],
    ["분양보증 고지 미확인", "공통", "주의", "분양보증(HUG 등) 문구 양 블록 0건 — 단 시행자가 경기주택도시공사(공공)라 HUG 체계 밖일 수 있음, 보증구조 확인 요청 필요"],
    ["이의제기 금지 문구 광범위 반복", "공통", "주의", "'이의를 제기할 수 없습니다' A1BL 57회·A2BL 52회 실측 — 재산가치 직결 사항 포함"],
    ["재활용 보관소 전동 인접", "공통", "주의", "A1BL: 101·102동 사이, 103·104동 사이 명시 / A2BL: 각 동 인접(동별 위치 상이) — 수거차량 소음·분진·냄새 원문 고지"],
    ["필로티 층고 동별 상이", "A2BL", "주의", "동별 필로티 구조 차이 — 저층 세대 확인 필요"],
    ["계약금 부담 수준", "공통", "양호", "계약금 10% · 중도금 60%(분납) · 잔금 30% — 표준적 구조"],
  ];
  const SEV = { "주의": "C0392B", "양호": "2E7D32" };
  const body = rows.map((r, ri) => r.map((cell, ci) => ({
    text: String(cell),
    options: ri === 0
      ? { fontFace: F_HEAD, fontSize: 11, bold: true, color: "FFFFFF", fill: { color: NAVY }, align: "center", valign: "middle" }
      : { fontFace: F_BODY, fontSize: 10.5, bold: ci === 2, color: ci === 2 ? (SEV[cell] || INK) : (ci === 0 ? INK : BODY), fill: { color: ri % 2 ? "FFFFFF" : "F8F9FB" }, align: ci === 1 || ci === 2 ? "center" : "left", valign: "middle" },
  })));
  s.addTable(body, {
    x: 0.62, y: 1.3, w: W - 1.24,
    colW: [(W - 1.24) * 0.27, (W - 1.24) * 0.08, (W - 1.24) * 0.08, (W - 1.24) * 0.57],
    border: { type: "solid", color: LINE, pt: 0.75 }, margin: 0.06, autoPage: false,
    rowH: 0.62,
  });
}

p.writeFile({ fileName: "/tmp/JL_편집가능_데모_안양에버포레_통합.pptx" }).then(() => console.log("OK"));
