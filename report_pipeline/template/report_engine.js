/**
 * 분양공고문 검토보고서 — 고정 렌더링 엔진 (loop-engineering: template 부분)
 *
 * 이 파일은 절대 apartment별로 수정하지 않는다. 매번 바뀌는 내용은
 * content/{apartment-slug}/content.js 에서만 채운다.
 *
 * 규칙(RULES.md 요약, 자세한 내용은 RULES.md 참고):
 *  - 원문 직접 추출(source_get_content) 기반 사실만 기재. LLM 요약(notebook_query) 금지.
 *  - 버전 라벨·정정안내·내부 진행상황 등 "우리끼리 표현" 금지 — 최종 제출본처럼 작성.
 *  - 부록 페이지 없음. 지체상금·재무부담류는 헤드라인에 넣지 않음(옵션 content.dropLowInterest로 제어).
 *  - 대출/LTV 규제분석 섹션은 기본 비활성 (content.includeLoanSection = true일 때만 렌더).
 *  - 페이지 분리 자동제어(keepNext/keepLines/cantSplit)를 모든 블록에 기본 적용.
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign, ImageRun,
} = require("docx");
const fs = require("fs");

const COLORS = {
  NAVY: "1F3864", NAVY2: "2E5395", GOLD: "C89B3C",
  RED: "C00000", ORANGE: "B45309", GREEN: "2E7D32",
  GRAY: "595959", LIGHTGRAY: "F2F2F2", CREAM: "F7F3EA",
  LINE: "E2DED4", REDBG: "FBEAEA", ORANGEBG: "FBF1E3", GREENBG: "EAF3EA",
};
// 2026-08-07: 실제 업로드된 브랜드 폰트로 교체(사용자 확인: 옴니고딕=제목, 나눔스퀘어=본문).
// 폰트 파일은 report_pipeline/template/brand/fonts/ (git 미포함 — README 참고, 로컬 설치 필요).
const FONT_HEAD = "210 OmniGothic 050"; // 표지·섹션제목·소제목용
const FONT_BODY = "NanumSquare";        // 본문 기본값(Document default)
const FONT = FONT_BODY;
const RATING_COLOR = { "양호": COLORS.GREEN, "보통": COLORS.ORANGE, "주의": COLORS.RED };
const SEV_COLOR = { "상": COLORS.RED, "중": COLORS.ORANGE, "하": COLORS.GREEN,
  "주의": COLORS.RED, "확인필요": COLORS.ORANGE, "양호": COLORS.GREEN };
const SEV_BG = { "상": COLORS.REDBG, "중": COLORS.ORANGEBG, "하": COLORS.GREENBG,
  "주의": COLORS.REDBG, "확인필요": COLORS.ORANGEBG, "양호": COLORS.GREENBG };
const LINE_BORDER = { style: BorderStyle.SINGLE, size: 4, color: COLORS.LINE };
const TABLE_BORDERS = {
  top: LINE_BORDER, bottom: LINE_BORDER, left: LINE_BORDER, right: LINE_BORDER,
  insideHorizontal: LINE_BORDER, insideVertical: LINE_BORDER,
};

let figCount = 0;

function sectionBar(num, text) {
  return new Table({
    width: { size: 9350, type: WidthType.DXA },
    columnWidths: [9350],
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        width: { size: 9350, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: COLORS.NAVY },
        margins: { top: 260, bottom: 260, left: 200, right: 200 },
        borders: { bottom: { style: BorderStyle.SINGLE, size: 24, color: COLORS.GOLD } },
        children: [new Paragraph({
          spacing: { before: 0, after: 0 },
          children: [
            new TextRun({ text: num ? `${num}   ` : "", bold: true, color: COLORS.GOLD, size: 24, font: FONT_HEAD }),
            new TextRun({ text, bold: true, color: "FFFFFF", size: 24, font: FONT_HEAD }),
          ],
        })],
      })],
    })],
  });
}
function h1(num, text) {
  // 표(sectionBar) 앞뒤에 빈 Paragraph로 여백을 주면 Word에서 문단부호가 점처럼 보이는
  // 경우가 있어, 여백은 표 셀 margins(top/bottom 260)로만 준다 — 빈 문단을 만들지 않는다.
  return [sectionBar(num, text)];
}
function h2(text, color = COLORS.NAVY) {
  return new Paragraph({
    keepNext: true, keepLines: true,
    spacing: { before: 240, after: 100, line: 276, lineRule: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: COLORS.GOLD, space: 6 } },
    indent: { left: 80 },
    children: [new TextRun({ text, bold: true, color, size: 22, font: FONT_HEAD })],
  });
}
function p(text, opts = {}) {
  return new Paragraph({ keepLines: true, children: [new TextRun({ text, ...opts })], spacing: { after: 120, line: 276, lineRule: "auto" } });
}
function quoteBox(text) {
  // "원문 인용" 라벨 + 크림색 박스(4방향 얇은 테두리) — 항상 라벨을 먼저 붙여 원문임을 명시한다.
  return [
    new Paragraph({
      keepNext: true, keepLines: true,
      spacing: { before: 160, after: 60, line: 276, lineRule: "auto" },
      children: [new TextRun({ text: "원문 인용", bold: true, color: COLORS.GRAY, size: 16 })],
    }),
    new Paragraph({
      keepNext: true, keepLines: true,
      shading: { type: ShadingType.CLEAR, fill: COLORS.CREAM },
      border: {
        top: { style: BorderStyle.SINGLE, size: 4, color: COLORS.LINE },
        bottom: { style: BorderStyle.SINGLE, size: 4, color: COLORS.LINE },
        left: { style: BorderStyle.SINGLE, size: 4, color: COLORS.LINE },
        right: { style: BorderStyle.SINGLE, size: 4, color: COLORS.LINE },
      },
      indent: { left: 160, right: 160 },
      spacing: { before: 100, after: 160, line: 288, lineRule: "auto" },
      children: [new TextRun({ text: `“${text}”`, color: "2B2E33", size: 20 })],
    }),
  ];
}
function commentBox(text, label = "법무법인제이엘 검토") {
  return new Paragraph({
    keepLines: true,
    shading: { type: ShadingType.CLEAR, fill: "EDF1F8" },
    border: { left: { style: BorderStyle.SINGLE, size: 28, color: COLORS.NAVY2 } },
    indent: { left: 140 },
    spacing: { before: 40, after: 260, line: 280, lineRule: "auto" },
    children: [
      new TextRun({ text: "✓  ", bold: true, color: COLORS.NAVY }),
      new TextRun({ text: label + "   ", bold: true, color: COLORS.NAVY2 }),
      new TextRun({ text }),
    ],
  });
}
function figCaption(text, source) {
  figCount += 1;
  return new Paragraph({
    keepLines: true,
    spacing: { before: 60, after: 200, line: 276, lineRule: "auto" },
    children: [
      new TextRun({ text: `[그림 ${figCount}] ${text}`, bold: true, size: 18, color: COLORS.GRAY }),
      new TextRun({ text: source ? `   자료: ${source}` : "", italics: true, size: 18, color: "999999" }),
    ],
  });
}
function cell(text, opts = {}) {
  const { bold = false, shade = null, width = 2000, color = "000000", align = AlignmentType.LEFT, size = 20 } = opts;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 90, bottom: 90, left: 120, right: 120 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text, bold, color, size })] })],
  });
}
function simpleTable(rows, widths, opts = {}) {
  const { centerCols = [], cellSize = 20, headColor = COLORS.NAVY } = opts;
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    borders: TABLE_BORDERS,
    rows: rows.map((r, i) => new TableRow({
      cantSplit: true,
      children: r.map((val, ci) => cell(val, {
        bold: i === 0,
        shade: i === 0 ? headColor : (i % 2 ? COLORS.CREAM : null),
        color: i === 0 ? "FFFFFF" : "000000",
        width: widths[ci],
        align: (centerCols.includes(ci) && i > 0) ? AlignmentType.CENTER : AlignmentType.LEFT,
        size: cellSize,
      })),
    })),
  });
}
function scoreCard(rows, widths) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    borders: TABLE_BORDERS,
    rows: rows.map((r, i) => {
      if (i === 0) {
        return new TableRow({
          cantSplit: true,
          children: r.map((val, ci) => cell(val, { bold: true, shade: COLORS.NAVY, color: "FFFFFF", width: widths[ci], align: ci === 1 ? AlignmentType.CENTER : AlignmentType.LEFT, size: 20 })),
        });
      }
      const [category, rating, summary] = r;
      const sevBg = SEV_BG[rating];
      return new TableRow({
        cantSplit: true,
        children: [
          cell(category, { bold: true, width: widths[0], shade: sevBg || (i % 2 ? COLORS.CREAM : null), size: 20 }),
          cell(`● ${rating}`, { bold: true, color: RATING_COLOR[rating] || "000000", width: widths[1], align: AlignmentType.CENTER, shade: sevBg || (i % 2 ? COLORS.CREAM : null), size: 20 }),
          cell(summary, { width: widths[2], shade: sevBg || (i % 2 ? COLORS.CREAM : null), size: 19 }),
        ],
      });
    }),
  });
}
function image(path, width, height, type = "jpg") {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({ type, data: fs.readFileSync(path), transformation: { width, height } })],
  });
}

/**
 * content 객체를 받아 전체 docx children 배열을 조립한다.
 * content 스키마는 content/_schema.md 참고.
 */
function buildDocument(content) {
  figCount = 0;
  const children = [];

  // ---- 표지 ----
  children.push(
    new Paragraph({
      shading: { type: ShadingType.CLEAR, fill: COLORS.NAVY }, spacing: { before: 0, after: 0 },
      children: [new TextRun({ text: "  " })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 32, color: COLORS.GOLD } },
    }),
    new Paragraph({ spacing: { before: 300, after: 60 },
      children: [new TextRun({ text: content.title, bold: true, size: 46, color: COLORS.NAVY, font: FONT_HEAD })] }),
    new Paragraph({ spacing: { after: 240 },
      children: [new TextRun({ text: content.subtitle, bold: true, size: 32, color: COLORS.NAVY, font: FONT_HEAD })] }),
    simpleTable(content.coverTable, [2200, 7150]),
    new Paragraph({ spacing: { before: 260, after: 0 }, children: [new TextRun({ text: "" })] }),
    new Paragraph({
      shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
      border: {
        top: { style: BorderStyle.SINGLE, size: 6, color: COLORS.GOLD }, bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.GOLD },
        left: { style: BorderStyle.SINGLE, size: 6, color: COLORS.GOLD }, right: { style: BorderStyle.SINGLE, size: 6, color: COLORS.GOLD },
      },
      spacing: { before: 100, after: 100 }, indent: { left: 100, right: 100 },
      children: [new TextRun({ text: content.disclaimer, size: 19 })],
    })
  );

  // ---- 섹션 렌더 (content.sections 순서대로) ----
  for (const section of content.sections) {
    children.push(...h1(section.num, section.title));
    for (const block of section.blocks) {
      children.push(...renderBlock(block));
    }
  }

  return children;
}

function renderBlock(block) {
  switch (block.type) {
    case "p": return [p(block.text, block.opts || {})];
    case "h2": return [h2(block.text, block.color ? COLORS[block.color] : undefined)];
    case "quote": return quoteBox(block.text);
    case "comment": return [commentBox(block.text, block.label)];
    case "table": return [simpleTable(block.rows, block.widths, block.opts || {})];
    case "scoreCard": return [scoreCard(block.rows, block.widths)];
    case "image": {
      const out = [image(block.path, block.width, block.height, block.imgType || "jpg")];
      if (block.caption) out.push(figCaption(block.caption, block.source));
      return out;
    }
    case "toxicItem": return [itemCard(block)];
    default:
      throw new Error(`Unknown block type: ${block.type}`);
  }
}

/**
 * toxicItem 카드 — 왼쪽에 중요도색 굵은 라인, 안에 [번호+카테고리+중요도 배지] →
 * "원문 인용" 박스 → 개선요청 줄. 단일 셀 표로 감싸 카드처럼 보이게 한다(docx는
 * div/box-shadow가 없어 1x1 표가 가장 안정적인 "카드" 구현 방식).
 */
function itemCard(block) {
  const severity = block.severity || "상";
  const sevColor = SEV_COLOR[severity] || COLORS.RED;
  return new Table({
    width: { size: 9350, type: WidthType.DXA },
    columnWidths: [9350],
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        width: { size: 9350, type: WidthType.DXA },
        margins: { top: 180, bottom: 200, left: 240, right: 220 },
        borders: {
          top: LINE_BORDER, bottom: LINE_BORDER, right: LINE_BORDER,
          left: { style: BorderStyle.SINGLE, size: 32, color: sevColor },
        },
        children: [
          new Paragraph({
            keepNext: true, keepLines: true,
            spacing: { after: 40, line: 276, lineRule: "auto" },
            children: [
              new TextRun({ text: `${String(block.index).padStart(2, "0")}   `, bold: true, color: "8A8F99", size: 18 }),
              new TextRun({ text: block.cat, bold: true, color: COLORS.NAVY, size: 23 }),
              new TextRun({ text: `   ［${severity}］`, bold: true, color: sevColor, size: 18 }),
            ],
          }),
          ...quoteBox(block.text),
          new Paragraph({
            keepLines: true,
            spacing: { before: 20, after: 40, line: 280, lineRule: "auto" },
            children: [
              new TextRun({ text: "✓  개선요청   ", bold: true, color: COLORS.NAVY2, size: 20 }),
              new TextRun({ text: block.fix, size: 20 }),
            ],
          }),
        ],
      })],
    })],
  });
}

async function renderToFile(content, outPath) {
  const children = buildDocument(content);
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: FONT, size: 21 },
          paragraph: { spacing: { line: 276, lineRule: "auto", after: 0 } },
        },
      },
    },
    sections: [{ children }],
  });
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buf);
  return outPath;
}

module.exports = { buildDocument, renderToFile, COLORS, FONT };
