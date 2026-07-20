const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign
} = require("docx");
const fs = require("fs");

const RED = "C00000";
const ORANGE = "B45309";
const GRAY = "595959";
const LIGHTGRAY = "F2F2F2";
const LIGHTRED = "FDEAEA";
const LIGHTORANGE = "FDF3E7";

function h(text, level) {
  return new Paragraph({ text, heading: level, spacing: { before: 300, after: 150 } });
}
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 120 },
  });
}
function bullet(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    bullet: { level: 0 },
    spacing: { after: 80 },
  });
}
function quoteBox(text) {
  return new Paragraph({
    children: [new TextRun({ text: `"${text}"`, italics: true, color: GRAY })],
    border: {
      left: { style: BorderStyle.SINGLE, size: 12, color: "999999", space: 8 },
    },
    indent: { left: 200 },
    spacing: { before: 100, after: 100 },
  });
}

function cell(text, opts = {}) {
  const { bold = false, shade = null, width = 2000, color = "000000", align = AlignmentType.LEFT } = opts;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, bold, color })],
    })],
  });
}

// ---- 1. 대출규제 표 ----
const loanRows = [
  ["대책 항목", "적용 여부", "근거"],
  ["주담대 여신한도 차등화 (6억원 제한)", "제외", "상주시는 비수도권·비규제지역 — 수도권/규제지역 전용 규제"],
  ["스트레스 금리 상향 (1.5%→3.0%)", "제외", "비규제지역은 기존 하한 0.75%~상한 3.0% 유지"],
  ["전세대출 DSR 반영", "제외", "수도권·규제지역 1주택자 전세대출에 한정"],
  ["LTV(주택담보대출비율) 제한", "적용", "무주택(처분조건부 1주택 포함) 70%, 유주택 60%"],
];
const loanTable = new Table({
  width: { size: 9350, type: WidthType.DXA },
  columnWidths: [3400, 1400, 4550],
  rows: loanRows.map((r, i) => new TableRow({
    children: [
      cell(r[0], { bold: i === 0, shade: i === 0 ? "1F4E78" : (i % 2 ? LIGHTGRAY : null), color: i === 0 ? "FFFFFF" : "000000", width: 3400 }),
      cell(r[1], { bold: true, shade: i === 0 ? "1F4E78" : (r[1] === "적용" ? LIGHTORANGE : LIGHTGRAY), color: i === 0 ? "FFFFFF" : (r[1] === "적용" ? ORANGE : "000000"), width: 1400, align: AlignmentType.CENTER }),
      cell(r[2], { shade: i === 0 ? "1F4E78" : null, color: i === 0 ? "FFFFFF" : "000000", width: 4550 }),
    ],
  })),
});

// ---- 2. 핵심 유의조항 (높음) ----
const highRisk = [
  {
    text: "아파트 현장여건(지질상태, 주변 민원 등)에 따라 공사공법이 변경될 수 있으며, 또한 기능/구조/성능/품질 등 개선 등을 위하여 설계변경이 추진될 수 있으며, 관계법령에서 정하는 경미한 설계변경은 계약자의 동의가 있는 것으로 간주하여 계약자의 동의없이 사업주체가 인·허가를 통해 진행할 수 있습니다.",
    reason: "사업주체가 일방적으로 설계변경을 추진하면서 수분양자 동의를 사전 간주하고, 통보·동의 절차 없이 임의로 인허가를 진행할 수 있도록 규정.",
    law: "약관의 규제에 관한 법률 제10조제1호, 제12조제1호",
    lawDetail: "상당한 이유 없이 급부의 내용을 사업자가 일방적으로 결정·변경할 수 있도록 하거나, 고객의 의사표시가 있는 것으로 간주하는 조항은 무효.",
    apply: "직접적용",
    ask: "'경미한 설계변경'의 구체적 범위를 명시하도록 요구, 중대한 변경 시 사전 통지·동의 절차 신설 요구",
  },
  {
    text: "입주예정일은 공정에 따라 변경될 수 있으며, 공사 중 천재지변, 정부 정책이나 관계 법령의 변경 등 예기치 못한 사유가 발생할 경우 예정된 공사일정 및 입주 시기 등이 지연될 수 있으며, 이 경우 입주 지연에 따른 이의를 제기할 수 없으며, 지체상금은 발생하지 않습니다.",
    reason: "사업주체 귀책범위를 '정부 정책 변경' 등으로 자의적으로 넓게 면책하고, 지체상금 지급의무를 원천 면제하며 이의제기 자체를 금지.",
    law: "약관의 규제에 관한 법률 제7조제2호",
    lawDetail: "상당한 이유 없이 사업자의 손해배상 범위를 제한하거나, 사업자가 부담할 위험을 고객에게 떠넘기는 조항은 무효.",
    apply: "직접적용",
    ask: "사업주체 귀책사유로 인한 지연에 대해서는 지체상금 지급 조항 신설 요구, '이의를 제기할 수 없다' 문구 삭제 요구",
  },
  {
    text: "본 아파트의 판매시점에 따라 향후 분양조건의 차이가 있을 수 있으며, 이에 이의를 제기하실 수 없습니다.",
    reason: "향후 할인분양 등 분양조건 변경 시 기존 수분양자의 형평성 문제제기 권리를 사전 차단.",
    law: "약관의 규제에 관한 법률 제11조제1호, 제14조제1호",
    lawDetail: "법률상 고객의 항변권 등을 상당한 이유 없이 배제·제한하는 조항, 고객에게 부당하게 불리한 소송 제기 금지 조항은 무효.",
    apply: "유추적용",
    ask: "동일 사유 대량 발생 시 협의회 차원의 대표 문제제기 절차 확보 필요",
  },
  {
    text: "견본주택에서 확인이 곤란한 공용부문의 시설물(공용계단, 지하주차장, 엘리베이터의 용량·속도·탑승위치 등)은 현장여건에 맞게 설계 변경된 최종 주택건설사업계획승인 도면에 준하며, 이로 인해 사업주체 또는 시공사에게 이의를 제기할 수 없습니다.",
    reason: "수분양자가 사전 확인이 어려운 공용시설에 대해 임의적 설계 하향 변경 가능성을 열어두고 일체의 이의제기를 금지.",
    law: "약관의 규제에 관한 법률 제10조제1호, 제14조제1호",
    lawDetail: "급부 내용을 사업자가 일방적으로 결정·변경할 수 있도록 하는 조항 및 부당한 소송 제기 금지 조항은 무효.",
    apply: "직접적용",
    ask: "최종 사업계획승인 도면 사전 공개 요구, 최초 고지 사양 대비 중대한 하향 변경 시 통지 의무화 요구",
  },
  {
    text: "발코니 확장 세대의 상부세대가 비확장일 경우 상부세대의 배관 일부가 확장세대 상부에 노출되어 이로 인한 소음이 발생할 수 있으며 이로 인하여 사업주체 또는 시공사에 이의를 제기할 수 없습니다.",
    reason: "구조적 설계 결함으로 인한 소음 피해 발생 가능성을 명시하면서도 하자보수·배상 책임을 완전히 면제.",
    law: "약관의 규제에 관한 법률 제7조제3호, 공동주택관리법 제36조제1항",
    lawDetail: "상당한 이유 없이 사업자의 담보책임을 배제·제한하는 조항은 무효이며, 사업주체는 공동주택 하자에 대해 분양에 따른 담보책임을 짐.",
    apply: "직접적용",
    ask: "배관 노출 소음을 하자보수 대상에서 일률 배제하는 조항 삭제 요구, 저감시공(방음자재 등) 대안 요구",
  },
];

const midRisk = [
  ["마감재/사양 변경", "품절·단종 시 '동급 이상' 대체는 표준이나, 사전 공지·동의 절차가 빠져 있어 임의 하향 시공의 여지가 있음."],
  ["계약 해제/위약금", "해제 시 위약금 외에 대납이자 전액까지 추가 부담시켜 이중 페널티 소지."],
  ["유상옵션(발코니확장 등)", "중도금 납부 이후 옵션 해제·변경을 시공사 동의 없이 전면 금지."],
  ["추가 선택품목", "품질·사양 불만이 있어도 교체·해약 요구 자체를 원천 금지."],
  ["조경 하자책임", "조경수 고사 등 원인(시공불량 vs 관리소홀) 불명확한 상태에서 시공사 책임을 일률 면제."],
  ["중도금 대출 중단", "계약자 귀책 대출중단 시 최고·유예기간 없이 즉시 계약해제 가능 조항."],
  ["환경권 침해 수인조항 (지붕층 시설물)", "일조·조망·소음·사생활 침해 가능성을 언급하며 이의제기 배제."],
  ["환경권 침해 수인조항 (단지 내 도로·시설 인접)", "인접세대의 소음·진동·조망 저해 등을 일률적으로 수인하도록 고지."],
  ["발코니 확장 단차", "인접·상부세대 비확장 시 발생하는 시공상 단차·마감 불량 관련 이의제기 배제."],
];

const highRiskBlocks = [];
highRisk.forEach((item, i) => {
  highRiskBlocks.push(
    new Paragraph({
      spacing: { before: 260, after: 80 },
      children: [
        new TextRun({ text: `⚠ 위험 ${i + 1}  `, bold: true, color: RED }),
        new TextRun({ text: item.reason, bold: true }),
      ],
    })
  );
  highRiskBlocks.push(quoteBox(item.text));
  highRiskBlocks.push(new Paragraph({
    spacing: { after: 40 },
    children: [
      new TextRun({ text: "법적 근거  ", bold: true, color: "1F4E78" }),
      new TextRun({ text: item.law, bold: true }),
      new TextRun({ text: `  (${item.apply})`, italics: true, color: GRAY }),
    ],
  }));
  highRiskBlocks.push(new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: item.lawDetail, size: 20, color: GRAY, italics: true })],
  }));
  highRiskBlocks.push(new Paragraph({
    spacing: { after: 160 },
    children: [
      new TextRun({ text: "권고 개선요구안  ", bold: true, color: "2E7D32" }),
      new TextRun({ text: item.ask }),
    ],
  }));
});

const midRiskBlocks = [];
midRiskBlocks.push(p("아래 9건은 즉시 무효를 다투기보다, 협의회 차원의 서면 질의·개선요구 대상으로 정리했습니다.", { italics: true, color: GRAY, size: 20 }));
midRisk.forEach(([cat, desc]) => {
  midRiskBlocks.push(new Paragraph({
    spacing: { after: 100 },
    children: [
      new TextRun({ text: `${cat}  —  `, bold: true }),
      new TextRun({ text: desc }),
    ],
    bullet: { level: 0 },
  }));
});

const doc = new Document({
  sections: [{
    properties: {},
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 40 },
        children: [new TextRun({ text: "상주자이르네 입주자모집공고문 검토보고서", bold: true, size: 40 })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "(AI 1차 스크리닝 — 공고문 조항 및 관계법령 원문 대조)", size: 24, color: GRAY })],
      }),
      new Table({
        width: { size: 9350, type: WidthType.DXA },
        columnWidths: [2400, 6950],
        rows: [
          ["대상 단지", "상주자이르네 (2026000038 입주자모집공고, 공고일 2026.03.09)"],
          ["배포 대상", "상주자이르네 입주예정자협의회"],
          ["작성", "법무법인 ○○○ (검토·서명 전 초안)"],
          ["작성일", "2026.07.16"],
        ].map(([k, v]) => new TableRow({
          children: [
            cell(k, { bold: true, shade: LIGHTGRAY, width: 2400 }),
            cell(v, { width: 6950 }),
          ],
        })),
      }),
      new Paragraph({ spacing: { before: 200, after: 200 }, children: [new TextRun({ text: "" })] }),
      new Paragraph({
        shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
        border: {
          top: { style: BorderStyle.SINGLE, size: 6, color: ORANGE },
          bottom: { style: BorderStyle.SINGLE, size: 6, color: ORANGE },
          left: { style: BorderStyle.SINGLE, size: 6, color: ORANGE },
          right: { style: BorderStyle.SINGLE, size: 6, color: ORANGE },
        },
        spacing: { before: 100, after: 100 },
        indent: { left: 100, right: 100 },
        children: [new TextRun({
          text: "본 보고서는 AI(NotebookLM)가 입주자모집공고문 원문과 관계법령 원문(약관의 규제에 관한 법률, 공동주택관리법 등)을 대조하여 작성한 1차 스크리닝 자료입니다. 최종 법률의견이 아니며, 변호사의 최종 검토·서명 전에는 대외 배포용으로 사용할 수 없습니다.",
          size: 20,
        })],
      }),

      h("1. 대출규제 안내 (공고일 2026.03.09 기준)", HeadingLevel.HEADING_1),
      p("대출규제는 오늘 날짜가 아니라 입주자모집공고일(2026.03.09) 시점에 시행 중이던 규제가 적용되는 것이 원칙입니다. 2025.10.15 주택시장 안정화 대책 기준으로 정리하면:"),
      loanTable,
      new Paragraph({ spacing: { before: 150, after: 100 }, children: [
        new TextRun({ text: "한계: ", bold: true, color: RED }),
        new TextRun({ text: "2025.10.15~2026.03.09 사이 추가·수정 대책이 있었는지는 이 노트북 소스만으로는 확인되지 않습니다. 실제 적용 여부는 계약 전 대출 취급은행 확인이 필요합니다.", size: 20, color: GRAY }),
      ]}),

      h("2. 핵심 유의조항 — 개선요구 우선순위 (위험도 높음 5건)", HeadingLevel.HEADING_1),
      p("아래 5건은 공고문 조항을 「약관의 규제에 관한 법률」·「공동주택관리법」 원문과 직접 대조한 결과, 무효 소지가 있거나 수분양자에게 일방적으로 불리한 조항입니다."),
      ...highRiskBlocks,

      h("3. 추가 검토필요 조항 (9건)", HeadingLevel.HEADING_1),
      ...midRiskBlocks,

      h("4. 결론 및 변호사 검토 요청사항", HeadingLevel.HEADING_1),
      bullet("위 5건(핵심)은 약관규제법 위반 소지가 뚜렷하여 시행사에 서면으로 조항 삭제·수정을 요구할 근거가 있습니다."),
      bullet("9건(추가 검토)은 즉시 무효 주장보다 협의회 명의 질의서로 구체적 적용 범위·절차를 먼저 확인하는 것을 권고합니다."),
      bullet("대출규제는 개별 세대의 주택 보유 현황에 따라 LTV가 달라지므로, 계약자별 대출 가능 여부는 은행 사전상담을 안내하는 것이 필요합니다."),
      bullet("본 1차 스크리닝에서 다루지 않은 조항(청약자격, 계약금/중도금 납부방식 등 통상적 조건)은 별도 이상 소견이 없어 생략하였습니다."),

      h("5. 변호사 검토·서명란", HeadingLevel.HEADING_1),
      new Table({
        width: { size: 9350, type: WidthType.DXA },
        columnWidths: [2400, 6950],
        rows: [
          ["검토 변호사", ""],
          ["검토일", ""],
          ["최종 의견", ""],
          ["서명", ""],
        ].map(([k, v]) => new TableRow({
          children: [
            cell(k, { bold: true, shade: LIGHTGRAY, width: 2400 }),
            new TableCell({
              width: { size: 6950, type: WidthType.DXA },
              margins: { top: 200, bottom: 200, left: 100, right: 100 },
              children: [new Paragraph({ children: [new TextRun({ text: v })] })],
            }),
          ],
        })),
      }),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("상주자이르네_검토보고서_초안.docx", buf);
  console.log("done");
});
