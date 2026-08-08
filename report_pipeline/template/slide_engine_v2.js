/**
 * 슬라이드 엔진 v2 — 데이터 주도 범용 엔진 (2026-08-08)
 *
 * 에버포레 통합본에서 확정된 "전문가 스타일"(화이트 + #156082 제목 + 회색밴드 푸터,
 * 편집가능 네이티브 요소)을 범용화한 것. 단지별 하드코딩 금지 — 모든 내용은
 * content/<slug>/content_v2.js 에서 온다. 이 파일은 절대 단지별로 수정하지 않는다.
 *
 * content_v2 스키마:
 * {
 *   title, subtitle, coverTable: [[k,v]...], disclaimer,
 *   typeVerdict: { name, confidence, evidence }   // 1단계 유형판별 결과 (표지에 명시)
 *   pages: [
 *     { type: "summaryTable", title, headers, widths, rows: [[..]], sevCol: <중요도 컬럼 인덱스|null> }
 *     { type: "scoreCard", title, rows: [[항목,평가,근거]...] }          // 첫 행은 헤더
 *     { type: "siteCallout", title, image, caption, items: [[라벨, 본문, 색HEX]...] }
 *     { type: "toxicPair", title, items: [{index,cat,text,fix,severity?,evidenceImage?}] } // 2건/장 자동분할
 *     { type: "fullImage", image }                                       // HTML 렌더 캡처 전면
 *     { type: "recommendations", title, items: [[번호,제목,내용]...] }
 *   ]
 * }
 */
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const W = 13.333, H = 7.5;
const TITLE_C = "156082", NAVY = "1F3864", GOLD = "C89B3C";
const INK = "222B36", BODY = "3d4854", MUTED = "8a93a0", LINE = "D9DDE2";
// 2026-08-08 대장님 확인: 실제 JL 주 제안서 폰트는 에스코어드림(S-Core Dream, 무료·상업용 가능).
// 렌더 PC에 폰트 파일 설치 필요(에스코어 홈페이지 무료배포 → brand/fonts/에 보관+PC 설치).
// 미설치 시 Office가 기본체로 대체 — 최종 납품 전 반드시 설치 상태에서 확인할 것.
const F_HEAD = "S-Core Dream 6 Bold", F_BODY = "S-Core Dream 4 Regular";
const LOGO = path.join(__dirname, "brand", "jl_logo_crop.png");
const LOGO_R = 409 / 138;
const SEV = { "주의": "C0392B", "양호": "2E7D32", "확인필요": "C77700", "보통": "C77700", "상": "C0392B", "중": "C77700", "하": "2E7D32" };

class DeckV2 {
  constructor(content) {
    this.p = new pptxgen();
    this.p.layout = "LAYOUT_WIDE";
    this.p.author = "법무법인 제이엘";
    this.p.title = content.title || "검토보고서";
    this.c = content;
    this.pageNo = 0;
  }

  frame(title) {
    this.pageNo += 1;
    const s = this.p.addSlide();
    s.background = { color: "FFFFFF" };
    s.addShape(this.p.ShapeType.roundRect, { x: 0.62, y: 0.42, w: 0.34, h: 0.34, fill: { color: TITLE_C }, rectRadius: 0.06, line: { type: "none" } });
    s.addText("⌂", { x: 0.62, y: 0.42, w: 0.34, h: 0.34, align: "center", valign: "middle", fontFace: "Segoe UI Symbol", fontSize: 14, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(title || "", { x: 1.08, y: 0.36, w: 9.6, h: 0.5, fontFace: F_HEAD, fontSize: 18, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
    const lh = 0.36, lw = lh * LOGO_R;
    if (fs.existsSync(LOGO)) s.addImage({ path: LOGO, x: W - 0.62 - lw, y: 0.34, w: lw, h: lh });
    s.addShape(this.p.ShapeType.line, { x: 0, y: 6.98, w: W, h: 0, line: { color: "9E9E9E", width: 0.75 } });
    s.addShape(this.p.ShapeType.rect, { x: 0, y: 7.17, w: W, h: 0.33, fill: { color: "F2F2F2" }, line: { type: "none" } });
    s.addText("법무법인 제이엘 | JL LAWFIRM", { x: 0.62, y: 6.99, w: 4, h: 0.18, fontFace: F_BODY, fontSize: 8.5, color: "6b7480", margin: 0 });
    s.addText(String(this.pageNo), { x: W - 1.0, y: 6.99, w: 0.4, h: 0.18, align: "right", fontFace: F_BODY, fontSize: 8.5, color: "6b7480", margin: 0 });
    return s;
  }

  cover() {
    this.pageNo += 1;
    const s = this.p.addSlide();
    s.background = { color: "FFFFFF" };
    const lh = 0.5, lw = lh * LOGO_R;
    if (fs.existsSync(LOGO)) s.addImage({ path: LOGO, x: 0.7, y: 0.55, w: lw, h: lh });
    s.addText(this.c.subtitle || "입주자모집공고 검토보고서", { x: 0.72, y: 1.9, w: 11, h: 0.4, fontFace: F_HEAD, fontSize: 15, bold: true, color: GOLD, margin: 0 });
    s.addText(this.c.title || "", { x: 0.7, y: 2.3, w: 12, h: 0.95, fontFace: F_HEAD, fontSize: 40, bold: true, color: NAVY, margin: 0 });
    s.addShape(this.p.ShapeType.line, { x: 0.72, y: 3.35, w: 4.2, h: 0, line: { color: GOLD, width: 2.5 } });
    let y = 3.7;
    // 유형판별 명시 (PLAYBOOK 1단계 — 표지 필수 기재)
    if (this.c.typeVerdict) {
      const tv = this.c.typeVerdict;
      s.addShape(this.p.ShapeType.rect, { x: 0.72, y, w: 11.9, h: 0.42, fill: { color: "F0F5FA" }, line: { color: "C6D2E4", width: 0.75 } });
      s.addText([
        { text: "  사업유형 판별   ", options: { fontFace: F_HEAD, fontSize: 10, bold: true, color: TITLE_C } },
        { text: `${tv.name}  (확신도 ${tv.confidence})  —  근거: ${tv.evidence}`, options: { fontFace: F_BODY, fontSize: 10, color: BODY } },
      ], { x: 0.72, y, w: 11.9, h: 0.42, valign: "middle", margin: 0 });
      y += 0.56;
    }
    for (const [k, v] of this.c.coverTable || []) {
      s.addText(k, { x: 0.72, y, w: 1.5, h: 0.34, fontFace: F_HEAD, fontSize: 11, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
      s.addText(String(v), { x: 2.3, y, w: 10.3, h: 0.34, fontFace: F_BODY, fontSize: 11, color: BODY, valign: "middle", margin: 0 });
      y += 0.4;
    }
    if (this.c.disclaimer) {
      s.addText(String(this.c.disclaimer), { x: 0.72, y: Math.max(y + 0.2, 6.2), w: 11.9, h: 0.85, fontFace: F_BODY, fontSize: 8.5, color: MUTED, lineSpacingMultiple: 1.25, valign: "top", margin: 0 });
    }
  }

  summaryTable(pg) {
    const s = this.frame(pg.title);
    const rows = [pg.headers, ...pg.rows];
    const total = (pg.widths || rows[0].map(() => 1)).reduce((a, b) => a + b, 0);
    const colW = (pg.widths || rows[0].map(() => 1)).map((w) => (w / total) * (W - 1.24));
    const body = rows.map((r, ri) => r.map((cell, ci) => ({
      text: String(cell),
      options: ri === 0
        ? { fontFace: F_HEAD, fontSize: 10.5, bold: true, color: "FFFFFF", fill: { color: NAVY }, align: "center", valign: "middle" }
        : { fontFace: F_BODY, fontSize: 9.5, bold: ci === pg.sevCol, color: ci === pg.sevCol ? (SEV[cell] || INK) : (ci === 0 ? INK : BODY), fill: { color: ri % 2 ? "FFFFFF" : "F8F9FB" }, align: ci === pg.sevCol ? "center" : "left", valign: "middle" },
    })));
    s.addTable(body, { x: 0.62, y: 1.25, w: W - 1.24, colW, border: { type: "solid", color: LINE, pt: 0.75 }, margin: 0.05, autoPage: false });
  }

  scoreCard(pg) {
    this.summaryTable({ title: pg.title, headers: pg.rows[0], rows: pg.rows.slice(1).map(r => [r[0], `● ${r[1]}`, r[2]]), widths: [26, 10, 64], sevCol: 1 });
  }

  siteCallout(pg) {
    const s = this.frame(pg.title);
    const iw = 7.5, ih = 4.8;
    if (pg.image && fs.existsSync(pg.image)) {
      s.addImage({ path: pg.image, x: 0.62, y: 1.15, w: iw, h: ih });
      s.addShape(this.p.ShapeType.rect, { x: 0.62, y: 1.15, w: iw, h: ih, fill: { type: "none" }, line: { color: LINE, width: 1 } });
    }
    if (pg.caption) s.addText(pg.caption, { x: 0.62, y: 6.02, w: iw, h: 0.4, fontFace: F_BODY, fontSize: 8, color: MUTED, lineSpacingMultiple: 1.15, margin: 0 });
    const n = pg.items.length, gap = 0.12, boxH = (4.87 - gap * (n - 1)) / n;
    let y = 1.15;
    for (const [label, txt, color] of pg.items) {
      s.addShape(this.p.ShapeType.roundRect, { x: 8.35, y, w: 4.35, h: boxH, fill: { color: "FFFFFF" }, rectRadius: 0.05, line: { color: LINE, width: 1 } });
      s.addShape(this.p.ShapeType.rect, { x: 8.35, y, w: 0.055, h: boxH, fill: { color: color || NAVY }, line: { type: "none" } });
      s.addText(label, { x: 8.52, y: y + 0.05, w: 2.5, h: 0.24, fontFace: F_HEAD, fontSize: 11.5, bold: true, color: NAVY, margin: 0 });
      s.addText(txt, { x: 8.52, y: y + 0.3, w: 4.06, h: boxH - 0.36, fontFace: F_BODY, fontSize: n >= 5 ? 8.5 : 9.5, color: BODY, lineSpacingMultiple: 1.14, valign: "top", margin: 0 });
      y += boxH + gap;
    }
  }

  toxicPair(pg) {
    const items = pg.items;
    for (let i = 0; i < items.length; i += 2) {
      const pair = items.slice(i, i + 2);
      const s = this.frame(pg.title);
      let y = 1.18;
      for (const b of pair) {
        const sev = b.severity || "상";
        s.addText([
          { text: String(b.index).padStart(2, "0") + "  ", options: { fontFace: F_HEAD, fontSize: 12, bold: true, color: GOLD } },
          { text: String(b.cat || ""), options: { fontFace: F_HEAD, fontSize: 13.5, bold: true, color: INK } },
        ], { x: 0.62, y, w: 10.5, h: 0.32, valign: "middle", margin: 0 });
        s.addShape(this.p.ShapeType.roundRect, { x: W - 1.5, y: y + 0.02, w: 0.86, h: 0.28, fill: { color: SEV[sev] || "C0392B" }, rectRadius: 0.05, line: { type: "none" } });
        s.addText(`중요 ${sev}`, { x: W - 1.5, y: y + 0.02, w: 0.86, h: 0.28, align: "center", valign: "middle", fontFace: F_BODY, fontSize: 8.5, bold: true, color: "FFFFFF", margin: 0 });
        y += 0.4;
        // 원문 — 증거카드 이미지가 있으면 이미지(실페이지 발췌), 없으면 인용 박스
        if (b.evidenceImage && fs.existsSync(b.evidenceImage)) {
          let ih = 0.95;
          try {
            const dim = pngSize(b.evidenceImage);
            if (dim) ih = Math.min(1.35, (W - 1.24) * dim.h / dim.w);
          } catch (e) { /* 기본값 유지 */ }
          s.addImage({ path: b.evidenceImage, x: 0.62, y, w: W - 1.24, h: ih });
          s.addText("▲ 공고문 실페이지 발췌 (적색 표시는 당 법인 부가)", { x: 0.62, y: y + ih + 0.02, w: 6, h: 0.18, fontFace: F_BODY, fontSize: 7.5, color: MUTED, margin: 0 });
          y += ih + 0.24;
        } else {
          const qLong = String(b.text || "").length > 165;
          const qh = qLong ? 1.28 : 0.95;
          s.addShape(this.p.ShapeType.rect, { x: 0.62, y, w: W - 1.24, h: qh, fill: { color: "F8FBFD" }, line: { color: LINE, width: 0.75 } });
          s.addText("문제 조항 (원문)", { x: 0.82, y: y + 0.06, w: 2, h: 0.2, fontFace: F_BODY, fontSize: 8, bold: true, color: "C0392B", margin: 0 });
          s.addText(`“${b.text}”`, { x: 0.82, y: y + 0.27, w: W - 1.64, h: qh - 0.33, fontFace: F_BODY, fontSize: qLong ? 9.5 : 10.5, color: BODY, lineSpacingMultiple: 1.2, valign: "top", margin: 0 });
          y += qh + 0.08;
        }
        const fh = 0.62;
        s.addShape(this.p.ShapeType.rect, { x: 0.62, y, w: W - 1.24, h: fh, fill: { color: "EAF3EA" }, line: { color: "C2DCC4", width: 0.75 } });
        s.addText([
          { text: "✓ 개선요청   ", options: { fontFace: F_BODY, fontSize: 9, bold: true, color: "2E7D32" } },
          { text: String(b.fix || ""), options: { fontFace: F_BODY, fontSize: 10.5, bold: true, color: "1c3a1e" } },
        ], { x: 0.82, y: y + 0.05, w: W - 1.64, h: fh - 0.1, lineSpacingMultiple: 1.18, valign: "middle", margin: 0 });
        y += fh + 0.28;
      }
    }
  }

  fullImage(pg) {
    this.pageNo += 1;
    const s = this.p.addSlide();
    s.addImage({ path: pg.image, x: 0, y: 0, w: W, h: H });
  }

  recommendations(pg) {
    const s = this.frame(pg.title);
    let y = 1.4;
    for (const [n, t, d] of pg.items) {
      s.addShape(this.p.ShapeType.rect, { x: 0.62, y, w: W - 1.24, h: 0.92, fill: { color: "FFFFFF" }, line: { color: LINE, width: 1 } });
      s.addText(String(n), { x: 0.85, y: y + 0.13, w: 0.6, h: 0.65, fontFace: F_HEAD, fontSize: 26, bold: true, color: NAVY, margin: 0 });
      s.addText(t, { x: 1.6, y: y + 0.12, w: 2.8, h: 0.68, fontFace: F_HEAD, fontSize: 12.5, bold: true, color: TITLE_C, valign: "middle", margin: 0 });
      s.addText(d, { x: 4.5, y: y + 0.12, w: 8.0, h: 0.68, fontFace: F_BODY, fontSize: 10.5, color: BODY, lineSpacingMultiple: 1.2, valign: "middle", margin: 0 });
      y += 1.04;
    }
  }
}

function pngSize(file) {
  const buf = fs.readFileSync(file);
  if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) {
    return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  }
  return null;
}

async function renderToFile(content, outPath) {
  const d = new DeckV2(content);
  d.cover();
  for (const pg of content.pages || []) {
    if (typeof d[pg.type] !== "function") throw new Error(`알 수 없는 페이지 타입: ${pg.type}`);
    d[pg.type](pg);
  }
  await d.p.writeFile({ fileName: outPath });
  return { outPath, pages: d.pageNo };
}

module.exports = { renderToFile };
