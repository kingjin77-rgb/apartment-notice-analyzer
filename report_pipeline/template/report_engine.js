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
};
const FONT = "맑은 고딕";
const RATING_COLOR = { "양호": COLORS.GREEN, "보통": COLORS.ORANGE, "주의": COLORS.RED };

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
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
        borders: { bottom: { style: BorderStyle.SINGLE, size: 24, color: COLORS.GOLD } },
        children: [new Paragraph({
          children: [
            new TextRun({ text: num ? `${num}   ` : "", bold: true, color: COLORS.GOLD, size: 24 }),
            new TextRun({ text, bold: true, color: "FFFFFF", size: 24 }),
          ],
        })],
      })],
    })],
  });
}
function h1(num, text) {
  return [
    new Paragraph({ keepNext: true, spacing: { before: 420, after: 0 }, children: [new TextRun({ text: "" })] }),
    sectionBar(num, text),
    new Paragraph({ keepNext: true, spacing: { before: 160, after: 0 }, children: [new TextRun({ text: "" })] }),
  ];
}
function h2(text, color = COLORS.NAVY) {
  return new Paragraph({
    keepNext: true, keepLines: true,
    spacing: { before: 240, after: 100, line: 276, lineRule: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: COLORS.GOLD, space: 6 } },
    indent: { left: 80 },
    children: [new TextRun({ text, bold: true, color, size: 22 })],
  });
}
function p(text, opts = {}) {
  return new Paragraph({ keepLines: true, children: [new TextRun({ text, ...opts })], spacing: { after: 120, line: 276, lineRule: "auto" } });
}
function quoteBox(text) {
  return new Paragraph({
    keepNext: true, keepLines: true,
    children: [new TextRun({ text: `"${text}"`, italics: true, color: COLORS.GRAY, size: 20 })],
    shading: { type: ShadingType.CLEAR, fill: COLORS.LIGHTGRAY },
    border: { left: { style: BorderStyle.SINGLE, size: 16, color: "999999", space: 8 } },
    indent: { left: 100 },
    spacing: { before: 100, after: 100, line: 276, lineRule: "auto" },
  });
}
function commentBox(text, label = "법무법인제이엘 검토") {
  return new Paragraph({
    keepLines: true,
    shading: { type: ShadingType.CLEAR, fill: "EDF1F8" },
    border: { left: { style: BorderStyle.SINGLE, size: 28, color: COLORS.NAVY2 } },
    indent: { left: 140 },
    spacing: { before: 100, after: 240, line: 276, lineRule: "auto" },
    children: [new TextRun({ text: label + "   ", bold: true, color: COLORS.NAVY2 }), new TextRun({ text })],
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
    rows: rows.map((r, i) => {
      if (i === 0) {
        return new TableRow({
          cantSplit: true,
          children: r.map((val, ci) => cell(val, { bold: true, shade: COLORS.NAVY, color: "FFFFFF", width: widths[ci], align: ci === 1 ? AlignmentType.CENTER : AlignmentType.LEFT, size: 20 })),
        });
      }
      const [category, rating, summary] = r;
      return new TableRow({
        cantSplit: true,
        children: [
          cell(category, { bold: true, width: widths[0], shade: i % 2 ? COLORS.CREAM : null, size: 20 }),
          cell(`● ${rating}`, { bold: true, color: RATING_COLOR[rating] || "000000", width: widths[1], align: AlignmentType.CENTER, shade: i % 2 ? COLORS.CREAM : null, size: 20 }),
          cell(summary, { width: widths[2], shade: i % 2 ? COLORS.CREAM : null, size: 19 }),
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
    new Paragraph({ spacing: { before: 600, after: 0 }, children: [new TextRun({ text: "" })] }),
    new Paragraph({
      shading: { type: ShadingType.CLEAR, fill: COLORS.NAVY }, spacing: { before: 0, after: 0 },
      children: [new TextRun({ text: "  " })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 32, color: COLORS.GOLD } },
    }),
    new Paragraph({ spacing: { before: 300, after: 60 },
      children: [new TextRun({ text: content.title, bold: true, size: 46, color: COLORS.NAVY })] }),
    new Paragraph({ spacing: { after: 240 },
      children: [new TextRun({ text: content.subtitle, bold: true, size: 32, color: COLORS.NAVY })] }),
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
    case "quote": return [quoteBox(block.text)];
    case "comment": return [commentBox(block.text, block.label)];
    case "table": return [simpleTable(block.rows, block.widths, block.opts || {})];
    case "scoreCard": return [scoreCard(block.rows, block.widths)];
    case "image": {
      const out = [image(block.path, block.width, block.height, block.imgType || "jpg")];
      if (block.caption) out.push(figCaption(block.caption, block.source));
      return out;
    }
    case "toxicItem": {
      const out = [h2(`${block.index}. [${block.cat}]`, COLORS.RED)];
      out.push(quoteBox(block.text));
      out.push(commentBox(`개선요청: ${block.fix}`));
      return out;
    }
    default:
      throw new Error(`Unknown block type: ${block.type}`);
  }
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
