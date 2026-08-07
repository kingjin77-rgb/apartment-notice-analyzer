/**
 * 분양공고문 검토보고서 — 가로 16:9 제안서 슬라이드 엔진 (JL 제안서 스타일)
 *
 * report_engine.js(세로 docx)와 같은 content.js를 입력으로 받아 렌더한다.
 * 디자인 기준: 법무법인 제이엘 제안서 샘플(운암산 리버포레 조경 제안서)
 *  - 흰 배경 + 크고 굵은 검정 제목(좌상단) + 우상단 JL 워드마크
 *  - 둥근 모서리 카드 3색 체계: 파랑(핵심 검토), 진네이비(문제 조항), 딥그린(개선요청/표 헤더)
 *  - 표지·본문 모두 화이트, 별도 섹션 표지 없음(여백 최소화)
 */
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

/* ── 브랜드 자산 ──────────────────────────────────────────────── */
const LOGO_PATH = path.join(__dirname, "brand", "jl_logo_crop.png");
const LOGO_RATIO = 409 / 138; // 실제 로고 crop 비율(가로/세로)

/* ── 팔레트 (JL 제안서 샘플 기준) ─────────────────────────────── */
const C = {
  WHITE: "FFFFFF", INK: "111827", BODY: "374151", MUTED: "6B7280",
  BLUE: "3B82F6",            // 핵심 하이라이트 카드
  NAVY_DARK: "1E2A3B",       // 문제점 카드
  GREEN: "1E4D3B",           // 개선요청 카드 · 표 헤더
  CARD: "F3F4F6", LINE: "E5E7EB", SOFT: "FAFAFA",
  RED: "C0392B", ORANGE: "C77700", OK: "2E7D32",
};
// 2026-08-07: 실제 업로드된 브랜드 폰트로 교체(사용자 확인: 옴니고딕=제목, 나눔스퀘어=본문).
// 폰트 파일은 report_pipeline/template/brand/fonts/ (git 미포함 — README 참고, 로컬 설치 필요).
// 렌더링 PC에 미설치 시 Office가 기본폰트로 자동 대체할 뿐 파일이 손상되지는 않음.
const FONT_HEAD = "210 OmniGothic 050"; // 표지·섹션제목·타이틀용 (5단계 중 최고굵기)
const FONT_BODY = "NanumSquare";        // 본문·표·캡션용
const FONT = FONT_BODY; // 하위호환 별칭 — 개별 타이틀 라인만 FONT_HEAD로 명시 교체
const SEV_COLOR = { "상": C.RED, "중": C.ORANGE, "하": C.OK, "주의": C.RED, "확인필요": C.ORANGE, "양호": C.OK };
const RATING_COLOR = { "양호": C.OK, "보통": C.ORANGE, "주의": C.RED };
const RATING_BG = { "주의": "FBEAEA", "확인필요": "FBF1E3", "상": "FBEAEA", "중": "FBF1E3" };

/* ── 캔버스 기하 ──────────────────────────────────────────────── */
const W = 13.333, H = 7.5;
const M = 0.55;
const CW = W - M * 2;
const TOP = 1.18;
const LIMIT = H - 0.42;
const GAP = 0.13;
const R = 0.09;                       // 카드 라운딩

function estLines(text, fontPt, boxWidthIn) {
  const s = String(text == null ? "" : text);
  if (!s) return 1;
  const hangul = (s.match(/[ㄱ-힝]/g) || []).length;
  const ratio = s.length ? hangul / s.length : 1;
  const emPerChar = 0.55 + 0.45 * ratio;
  const charsPerLine = Math.max(8, (boxWidthIn * 72) / (fontPt * emPerChar));
  const hard = s.split("\n").length - 1;
  return Math.ceil(s.length / charsPerLine) + hard || 1;
}
function textH(text, fontPt, boxWidthIn, lineFactor = 1.38) {
  return estLines(text, fontPt, boxWidthIn) * (fontPt * lineFactor) / 72;
}

class Deck {
  constructor(content) {
    this.pres = new pptxgen();
    this.pres.layout = "LAYOUT_WIDE";
    this.pres.author = "법무법인 제이엘";
    this.pres.title = content.title || "검토보고서";
    this.content = content;
    this.slide = null;
    this.y = TOP;
    this.sectionTitle = "";
    this.sectionNum = "";
    this.pageNo = 0;
  }

  newContentSlide(continued = false) {
    this.pageNo += 1;
    const s = this.pres.addSlide();
    s.background = { color: C.WHITE };

    const title = (this.sectionNum !== "" ? `${this.sectionNum}. ` : "") + (this.sectionTitle || "");
    s.addText([
      { text: title, options: { fontFace: FONT_HEAD, fontSize: 21, bold: true, color: C.INK } },
    ], { x: M, y: 0.34, w: CW - 1.7, h: 0.62, valign: "middle", margin: 0 });

    // 우상단 JL 워드마크(실제 로고 이미지)
    if (fs.existsSync(LOGO_PATH)) {
      const logoH = 0.34, logoW = logoH * LOGO_RATIO;
      s.addImage({ path: LOGO_PATH, x: W - M - logoW, y: 0.32, w: logoW, h: logoH });
    } else {
      s.addText([
        { text: "법무법인 ", options: { fontFace: FONT, fontSize: 11, bold: true, color: C.INK } },
        { text: "JL", options: { fontFace: FONT, fontSize: 13, bold: true, color: C.GREEN } },
      ], { x: W - M - 1.5, y: 0.36, w: 1.5, h: 0.3, align: "right", valign: "middle", margin: 0 });
    }

    s.addText(String(this.pageNo), {
      x: W - M - 0.6, y: H - 0.36, w: 0.6, h: 0.24, align: "right",
      fontFace: FONT, fontSize: 9, color: C.MUTED, margin: 0,
    });

    this.slide = s;
    this.y = TOP;
    return s;
  }

  ensure(need) {
    if (!this.slide) { this.newContentSlide(false); return; }
    if (this.y + need > LIMIT) this.newContentSlide(true);
  }

  /* ── 블록 렌더러 ─────────────────────────────────────────── */

  h2(text) {
    const h = 0.40;
    this.ensure(h + 0.28);
    if (this.y > TOP + 0.01) this.y += 0.12;
    this.slide.addText(String(text), {
      x: M, y: this.y, w: CW, h,
      fontFace: FONT_HEAD, fontSize: 16, bold: true, color: C.INK,
      valign: "middle", margin: 0,
    });
    this.y += h + 0.05;
  }

  p(text, opts = {}) {
    const size = opts.small ? 12 : 13;
    const h = Math.max(0.28, textH(text, size, CW) + 0.05);
    this.ensure(h);
    this.slide.addText(String(text), {
      x: M, y: this.y, w: CW, h,
      fontFace: FONT, fontSize: size, color: C.BODY,
      lineSpacingMultiple: 1.3, valign: "top", margin: 0,
    });
    this.y += h + GAP * 0.5;
  }

  /* 원문 인용 — 연회색 라운드 카드 */
  quote(text) {
    const size = 12;
    const inner = CW - 0.56;
    const th = textH(text, size, inner, 1.34);
    const h = th + 0.46;
    this.ensure(h);
    this.slide.addShape(this.pres.ShapeType.roundRect, {
      x: M, y: this.y, w: CW, h, fill: { color: C.CARD },
      rectRadius: R, line: { color: C.CARD, width: 0 },
    });
    this.slide.addText("원문 인용", {
      x: M + 0.26, y: this.y + 0.09, w: 1.6, h: 0.22,
      fontFace: FONT, fontSize: 9.5, bold: true, color: C.BLUE, margin: 0,
    });
    this.slide.addText(`“${String(text)}”`, {
      x: M + 0.26, y: this.y + 0.30, w: inner, h: th,
      fontFace: FONT, fontSize: size, color: C.BODY,
      lineSpacingMultiple: 1.28, valign: "top", margin: 0,
    });
    this.y += h + GAP;
  }

  /* 법인 검토 — 파랑 하이라이트 카드 (샘플의 핵심 스탯 카드) */
  comment(text, label) {
    const size = 12.5;
    const inner = CW - 0.56;
    const th = textH(text, size, inner, 1.34);
    const h = th + 0.48;
    this.ensure(h);
    this.slide.addShape(this.pres.ShapeType.roundRect, {
      x: M, y: this.y, w: CW, h, fill: { color: C.BLUE },
      rectRadius: R, line: { color: C.BLUE, width: 0 },
    });
    this.slide.addText(`✓  ${label || "법무법인제이엘 검토"}`, {
      x: M + 0.26, y: this.y + 0.09, w: 5.0, h: 0.24,
      fontFace: FONT, fontSize: 10, bold: true, color: "DCEAFE", margin: 0,
    });
    this.slide.addText(String(text), {
      x: M + 0.26, y: this.y + 0.32, w: inner, h: th,
      fontFace: FONT, fontSize: size, bold: true, color: C.WHITE,
      lineSpacingMultiple: 1.28, valign: "top", margin: 0,
    });
    this.y += h + GAP;
  }

  table(rows, widths) {
    if (!rows || !rows.length) return;
    const total = (widths && widths.length) ? widths.reduce((a, b) => a + b, 0) : 0;
    const colW = (widths && total)
      ? widths.map((w) => (w / total) * CW)
      : new Array(rows[0].length).fill(CW / rows[0].length);

    const rowH = rows.map((r, ri) => {
      const per = r.map((cell, ci) => textH(cell, 11.5, Math.max(0.6, colW[ci] - 0.2), 1.28));
      return Math.max(0.32, Math.max(...per) + 0.16);
    });
    const totalH = rowH.reduce((a, b) => a + b, 0);
    this.ensure(Math.min(totalH, LIMIT - TOP));

    const body = rows.map((r, ri) => r.map((cell) => ({
      text: String(cell == null ? "" : cell),
      options: {
        fontFace: FONT, fontSize: 11.5, valign: "middle",
        color: ri === 0 ? C.WHITE : C.BODY,
        bold: ri === 0,
        fill: { color: ri === 0 ? C.GREEN : (ri % 2 ? C.WHITE : C.SOFT) },
        align: ri === 0 ? "center" : "left",
      },
    })));

    this.slide.addTable(body, {
      x: M, y: this.y, w: CW, colW, rowH,
      border: { type: "solid", color: C.LINE, pt: 0.75 },
      autoPage: false, margin: 0.06,
    });
    this.y += totalH + GAP;
  }

  scoreCard(rows, widths) {
    if (!rows || !rows.length) return;
    const total = (widths && widths.length) ? widths.reduce((a, b) => a + b, 0) : 0;
    const colW = (widths && total) ? widths.map((w) => (w / total) * CW)
      : [CW * 0.26, CW * 0.14, CW * 0.60];

    const header = rows[0];
    const dataRows = rows.slice(1);
    const hH = 0.36;
    this.ensure(hH + 0.5);
    this.slide.addTable(
      [header.map((cell) => ({
        text: String(cell), options: {
          fontFace: FONT, fontSize: 11.5, bold: true, color: C.WHITE,
          fill: { color: C.GREEN }, align: "center", valign: "middle",
        },
      }))],
      { x: M, y: this.y, w: CW, colW, rowH: [hH], border: { type: "solid", color: C.LINE, pt: 0.75 }, margin: 0.06 }
    );
    this.y += hH;

    dataRows.forEach((r, i) => {
      const [cat, rating, summary] = r;
      const rh = Math.max(0.36, textH(summary, 11.5, colW[2] - 0.22, 1.28) + 0.16);
      if (this.y + rh > LIMIT) this.newContentSlide(true);
      const bg = RATING_BG[rating] || (i % 2 ? C.SOFT : C.WHITE);
      this.slide.addTable(
        [[
          { text: String(cat), options: { fontFace: FONT, fontSize: 11.5, bold: true, color: C.INK, fill: { color: bg }, valign: "middle" } },
          { text: `● ${rating}`, options: { fontFace: FONT, fontSize: 11.5, bold: true, color: RATING_COLOR[rating] || SEV_COLOR[rating] || C.INK, fill: { color: bg }, align: "center", valign: "middle" } },
          { text: String(summary), options: { fontFace: FONT, fontSize: 11.5, color: C.BODY, fill: { color: bg }, valign: "middle" } },
        ]],
        { x: M, y: this.y, w: CW, colW, rowH: [rh], border: { type: "solid", color: C.LINE, pt: 0.75 }, margin: 0.06 }
      );
      this.y += rh;
    });
    this.y += GAP;
  }

  image(absPath, caption, source) {
    if (!absPath || !fs.existsSync(absPath)) return;
    const capH = caption ? 0.30 : 0;
    let avail = LIMIT - this.y - capH;
    if (avail < 1.6) { this.newContentSlide(true); avail = LIMIT - this.y - capH; }

    const maxH = Math.min(avail, 4.7);
    const maxW = CW;
    let dim = null;
    try { dim = pngJpgSize(absPath); } catch (e) { dim = null; }
    let w = maxW, h = maxH;
    if (dim && dim.w && dim.h) {
      const r = dim.w / dim.h;
      h = Math.min(maxH, maxW / r);
      w = h * r;
      if (w > maxW) { w = maxW; h = w / r; }
    }
    const x = M + (CW - w) / 2;
    this.slide.addImage({ path: absPath, x, y: this.y, w, h, rounding: true });
    this.y += h + 0.05;
    if (caption) {
      this.slide.addText(source ? `${caption}   ·   ${source}` : String(caption), {
        x: M, y: this.y, w: CW, h: 0.24, align: "center",
        fontFace: FONT, fontSize: 10, color: C.MUTED, margin: 0,
      });
      this.y += 0.28;
    }
    this.y += GAP * 0.6;
  }

  /* 독소조항 — [문제 조항: 진네이비 카드] → [개선요청: 딥그린 카드] */
  toxicItem(b) {
    const sev = b.severity || "상";
    const sevC = SEV_COLOR[sev] || C.RED;
    const inner = CW - 0.56;

    const headH = 0.34;
    const qh = textH(b.text, 11.5, inner, 1.30) + 0.42;
    const fh = textH("개선요청  " + (b.fix || ""), 12, inner, 1.30) + 0.42;
    const total = headH + 0.06 + qh + 0.10 + fh;
    this.ensure(total);

    // 헤더: 번호 + 카테고리 + 중요도 배지
    this.slide.addText([
      { text: String(b.index).padStart(2, "0") + "  ", options: { fontFace: FONT, fontSize: 12, bold: true, color: C.MUTED } },
      { text: String(b.cat || ""), options: { fontFace: FONT_HEAD, fontSize: 14.5, bold: true, color: C.INK } },
    ], { x: M, y: this.y, w: CW - 1.1, h: headH, valign: "middle", margin: 0 });
    this.slide.addShape(this.pres.ShapeType.roundRect, {
      x: W - M - 0.72, y: this.y + 0.03, w: 0.72, h: 0.28,
      fill: { color: sevC }, rectRadius: 0.07, line: { color: sevC, width: 0 },
    });
    this.slide.addText(`중요 ${sev}`, {
      x: W - M - 0.72, y: this.y + 0.03, w: 0.72, h: 0.28, align: "center", valign: "middle",
      fontFace: FONT, fontSize: 9, bold: true, color: C.WHITE, margin: 0,
    });
    this.y += headH + 0.06;

    // 문제 조항 (진네이비)
    this.slide.addShape(this.pres.ShapeType.roundRect, {
      x: M, y: this.y, w: CW, h: qh, fill: { color: C.NAVY_DARK },
      rectRadius: R, line: { color: C.NAVY_DARK, width: 0 },
    });
    this.slide.addText("문제 조항 (원문)", {
      x: M + 0.26, y: this.y + 0.07, w: 2.4, h: 0.2,
      fontFace: FONT, fontSize: 9, bold: true, color: "9DB2CC", margin: 0,
    });
    this.slide.addText(`“${String(b.text || "")}”`, {
      x: M + 0.26, y: this.y + 0.27, w: inner, h: qh - 0.32,
      fontFace: FONT, fontSize: 11.5, color: C.WHITE,
      lineSpacingMultiple: 1.26, valign: "top", margin: 0,
    });
    this.y += qh + 0.10;

    // 개선요청 (딥그린)
    this.slide.addShape(this.pres.ShapeType.roundRect, {
      x: M, y: this.y, w: CW, h: fh, fill: { color: C.GREEN },
      rectRadius: R, line: { color: C.GREEN, width: 0 },
    });
    this.slide.addText("✓ 개선요청", {
      x: M + 0.26, y: this.y + 0.07, w: 2.4, h: 0.2,
      fontFace: FONT, fontSize: 9, bold: true, color: "A9CDBB", margin: 0,
    });
    this.slide.addText(String(b.fix || ""), {
      x: M + 0.26, y: this.y + 0.27, w: inner, h: fh - 0.32,
      fontFace: FONT, fontSize: 12, bold: true, color: C.WHITE,
      lineSpacingMultiple: 1.26, valign: "top", margin: 0,
    });
    this.y += fh + GAP + 0.06;
  }
}

function pngJpgSize(file) {
  const buf = fs.readFileSync(file);
  if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) {
    return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  }
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    let i = 2;
    while (i < buf.length - 9) {
      if (buf[i] !== 0xff) { i++; continue; }
      const marker = buf[i + 1];
      if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
        return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
      }
      i += 2 + buf.readUInt16BE(i + 2);
    }
  }
  return null;
}

/* ── 표지 (화이트, 샘플 표지 문법) ─────────────────────────────── */
function coverSlide(deck) {
  const c = deck.content;
  const s = deck.pres.addSlide();
  s.background = { color: C.WHITE };

  // 상단 eyebrow (파랑)
  s.addText(String(c.subtitle || ""), {
    x: M, y: 1.15, w: CW - 0.5, h: 0.4,
    fontFace: FONT, fontSize: 15, bold: true, color: C.BLUE, margin: 0,
  });
  // 대형 제목
  s.addText(`${String(c.title || "")} 검토보고서`, {
    x: M, y: 1.55, w: CW - 0.5, h: 1.5,
    fontFace: FONT_HEAD, fontSize: 40, bold: true, color: C.INK, valign: "middle", margin: 0,
  });

  // 표지 정보 카드 (연회색 라운드)
  const rows = (c.coverTable || []).filter(Boolean);
  if (rows.length) {
    const fs_ = 11;
    const colW = [CW * 0.14, CW * 0.60];
    const rowH = rows.map((r) => Math.max(0.28, textH(r[1], fs_, colW[1] - 0.2, 1.24) + 0.11));
    const tblH = rowH.reduce((a, b) => a + b, 0);
    const yTbl = 3.25;
    s.addShape(deck.pres.ShapeType.roundRect, {
      x: M - 0.12, y: yTbl - 0.14, w: colW[0] + colW[1] + 0.36, h: tblH + 0.28,
      fill: { color: C.CARD }, rectRadius: R, line: { color: C.CARD, width: 0 },
    });
    const body = rows.map((r) => [
      { text: String(r[0] ?? ""), options: { fontFace: FONT, fontSize: fs_, bold: true, color: C.BLUE, fill: { color: C.CARD }, valign: "middle" } },
      { text: String(r[1] ?? ""), options: { fontFace: FONT, fontSize: fs_, color: C.BODY, fill: { color: C.CARD }, valign: "middle" } },
    ]);
    s.addTable(body, {
      x: M, y: yTbl, w: colW[0] + colW[1], colW, rowH,
      border: { type: "none" }, margin: 0.04,
    });
    // 면책 문구 (하단, 작은 회색)
    if (c.disclaimer) {
      const dy = yTbl + tblH + 0.42;
      s.addText(String(c.disclaimer), {
        x: M, y: Math.min(dy, H - 1.35), w: CW, h: 0.95,
        fontFace: FONT, fontSize: 9.5, color: C.MUTED,
        lineSpacingMultiple: 1.25, valign: "top", margin: 0,
      });
    }
  }

  // 푸터 워드마크
  s.addText([
    { text: "법무법인 제이엘", options: { fontFace: FONT_HEAD, fontSize: 12, bold: true, color: C.INK } },
    { text: "  |  분양공고문 분석팀", options: { fontFace: FONT, fontSize: 11, color: C.MUTED } },
  ], { x: M, y: H - 0.62, w: 7, h: 0.35, valign: "middle", margin: 0 });
}

// 2026-08-07: 사용자 지시로 목차 슬라이드 영구 삭제(더 이상 호출 안 함, 함수도 제거).

function buildDeck(content, slugDir) {
  const deck = new Deck(content);
  coverSlide(deck);

  for (const sec of content.sections || []) {
    deck.sectionNum = sec.num ?? "";
    deck.sectionTitle = sec.title || "";
    deck.newContentSlide(false);

    for (const b of sec.blocks || []) {
      switch (b.type) {
        case "p": deck.p(b.text, b.opts || {}); break;
        case "h2": deck.h2(b.text); break;
        case "quote": deck.quote(b.text); break;
        case "comment": deck.comment(b.text, b.label); break;
        case "table": deck.table(b.rows, b.widths); break;
        case "scoreCard": deck.scoreCard(b.rows, b.widths); break;
        case "image": {
          const abs = path.isAbsolute(b.path) ? b.path : path.join(slugDir, b.path);
          deck.image(abs, b.caption, b.source);
          break;
        }
        case "toxicItem": deck.toxicItem(b); break;
        default: throw new Error(`Unknown block type: ${b.type}`);
      }
    }
  }
  return deck;
}

async function renderToFile(content, outPath, slugDir) {
  const deck = buildDeck(content, slugDir || process.cwd());
  await deck.pres.writeFile({ fileName: outPath });
  return outPath;
}

module.exports = { renderToFile, buildDeck, C, FONT };
