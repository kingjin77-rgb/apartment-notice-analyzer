const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign, Header, Footer,
  PageNumber, ImageRun, TabStopType, TabStopPosition, PageBreak,
} = require("docx");
const fs = require("fs");

const FONT = "210 OmniGothicOTF 030";
const NAVY = "1F3864";
const NAVY2 = "2E5395";
const GOLD = "C89B3C";
const RED = "C00000";
const ORANGE = "B45309";
const GREEN = "2E7D32";
const GRAY = "595959";
const LIGHTGRAY = "F2F2F2";
const CREAM = "F7F3EA";

let figCount = 0;

function sectionBar(num, text) {
  return new Table({
    width: { size: 9350, type: WidthType.DXA },
    columnWidths: [9350],
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: 9350, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: NAVY },
        margins: { top: 140, bottom: 140, left: 200, right: 200 },
        borders: { bottom: { style: BorderStyle.SINGLE, size: 24, color: GOLD } },
        children: [new Paragraph({
          children: [
            new TextRun({ text: num ? `${num}   ` : "", bold: true, color: GOLD, size: 24 }),
            new TextRun({ text, bold: true, color: "FFFFFF", size: 24 }),
          ],
        })],
      })],
    })],
  });
}
function h1(num, text) {
  return [
    new Paragraph({ spacing: { before: 420, after: 0 }, children: [new TextRun({ text: "" })] }),
    sectionBar(num, text),
    new Paragraph({ spacing: { before: 160, after: 0 }, children: [new TextRun({ text: "" })] }),
  ];
}
function h2(text, color = NAVY) {
  return new Paragraph({
    spacing: { before: 240, after: 100 },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: GOLD, space: 6 } },
    indent: { left: 80 },
    children: [new TextRun({ text, bold: true, color, size: 22 })],
  });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], bullet: { level: 0 }, spacing: { after: 80 } });
}
function quoteBox(text) {
  return new Paragraph({
    children: [new TextRun({ text: `“${text}”`, italics: true, color: GRAY, size: 20 })],
    shading: { type: ShadingType.CLEAR, fill: LIGHTGRAY },
    border: { left: { style: BorderStyle.SINGLE, size: 16, color: "999999", space: 8 } },
    indent: { left: 100 },
    spacing: { before: 100, after: 100 },
  });
}
function labelLine(label, text, color = NAVY) {
  return new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: `${label}  `, bold: true, color }), new TextRun({ text })],
  });
}
function commentBox(text) {
  return new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: "EDF1F8" },
    border: { left: { style: BorderStyle.SINGLE, size: 28, color: NAVY2 } },
    indent: { left: 140 },
    spacing: { before: 100, after: 240 },
    children: [new TextRun({ text: "법무법인제이엘 검토   ", bold: true, color: NAVY2 }), new TextRun({ text })],
  });
}
function figCaption(text, source) {
  figCount += 1;
  return new Paragraph({
    spacing: { before: 60, after: 200 },
    children: [
      new TextRun({ text: `[그림 ${figCount}] ${text}`, bold: true, size: 18, color: GRAY }),
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
  const { centerCols = [], cellSize = 20, headColor = NAVY } = opts;
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, i) => new TableRow({
      children: r.map((val, ci) => cell(val, {
        bold: i === 0,
        shade: i === 0 ? headColor : (i % 2 ? CREAM : null),
        color: i === 0 ? "FFFFFF" : "000000",
        width: widths[ci],
        align: (centerCols.includes(ci) && i > 0) ? AlignmentType.CENTER : AlignmentType.LEFT,
        size: cellSize,
      })),
    })),
  });
}

const children = [];

// ================= COVER =================
children.push(
  new Paragraph({ spacing: { before: 600, after: 0 }, children: [new TextRun({ text: "" })] }),
  new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: NAVY }, spacing: { before: 0, after: 0 },
    children: [new TextRun({ text: "  " })],
    border: { bottom: { style: BorderStyle.SINGLE, size: 32, color: GOLD } },
  }),
  new Paragraph({ spacing: { before: 300, after: 60 },
    children: [new TextRun({ text: "상주자이르네 입주자모집공고문", bold: true, size: 46, color: NAVY })] }),
  new Paragraph({ spacing: { after: 240 },
    children: [new TextRun({ text: "상세 검토보고서", bold: true, size: 46, color: NAVY })] }),
  new Paragraph({ spacing: { after: 300 },
    children: [new TextRun({ text: "독소조항 · 개선요구사항 · 단지주변조사", size: 24, color: GRAY }),
               new TextRun({ text: "  |  관계법령 원문·공공데이터 대조", size: 24, color: GRAY, italics: true })] }),
  simpleTable([
    ["대상 단지", "상주자이르네 (2026000038, 공고일 2026.03.09 / 사업계획승인일 2022.05.16)"],
    ["소재지", "경상북도 상주시 함창읍 윤직리 840번지 일원"],
    ["작성", "법무법인제이엘"],
    ["배포 대상", "상주자이르네 입주예정자협의회"],
    ["작성일", "2026.07.16"],
  ], [2200, 7150]),
  new Paragraph({ spacing: { before: 260, after: 0 }, children: [new TextRun({ text: "" })] }),
  new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
    border: {
      top: { style: BorderStyle.SINGLE, size: 6, color: GOLD }, bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD },
      left: { style: BorderStyle.SINGLE, size: 6, color: GOLD }, right: { style: BorderStyle.SINGLE, size: 6, color: GOLD },
    },
    spacing: { before: 100, after: 100 }, indent: { left: 100, right: 100 },
    children: [new TextRun({
      text: "본 보고서는 법무법인제이엘이 입주자모집공고문 원문, 관계법령 원문(약관의 규제에 관한 법률·공동주택관리법 등), 국토교통부·나이스·카카오 공공데이터를 직접 대조하여 작성한 1차 검토자료입니다. 최종 법률의견을 대체하지 않으며, 구조·소방 등 전문분야는 별도 기술자문과 병행합니다.",
      size: 19,
    })],
  })
);

// ================= 목차 요약 =================
children.push(...h1("", "한눈에 보기"));
[
  "본 보고서는 ① 대출규제, ② 독소조항(법령 저촉 소지), ③ 개선요구사항(확인·협의 대상), ④ 단지 주변조사 순으로 구성했습니다.",
  "독소조항은 시공·마감재·조경·계약해제 등 실거주에 직접 영향을 주는 항목을 우선 배치했습니다. 계약조항 중 9건이 「약관의 규제에 관한 법률」 조문 저촉 소지가 있어 개선협의 요청 대상입니다.",
  "개선요구사항의 핵심은 101·102·103·106동에 차별적으로 적용되는 동별 유의사항(배치도 첨부)입니다.",
  "대출규제는 공고일(2026.03.09) 기준 LTV만 적용(무주택 70%/유주택 60%)되며, 6억 한도·전세대출 DSR 등은 비규제지역이라 제외됩니다.",
  "분양보증(HUG)은 정상 확인되며, 에너지효율 1+등급·전기차충전 58대는 양호한 요소입니다.",
].forEach(t => children.push(bullet(t)));
children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: CREAM }, spacing: { before: 120, after: 100 },
  indent: { left: 100, right: 100 },
  children: [new TextRun({ text: "계약조항 검토 결과 (총 17건)", bold: true, color: NAVY, size: 21 })],
}));
children.push(new Paragraph({
  children: [new ImageRun({ type: "png", data: fs.readFileSync("chart_risk.png"), transformation: { width: 560, height: 202 } })],
}));
children.push(figCaption("계약조항 검토 결과 분포", "본 검토보고서 자체 분석"));

// ================= 1부. 대출규제 =================
children.push(...h1("1부", "대출규제 안내 (공고일 2026.03.09 기준)"));
children.push(p("대출규제는 오늘 날짜가 아니라 입주자모집공고일 시점에 시행 중이던 규제가 적용되는 것이 원칙입니다. 공고일 기준으로 직접 확인했습니다."));
children.push(simpleTable([
  ["대책 항목", "적용 여부", "근거"],
  ["주담대 여신한도 차등화 (6억원 제한)", "제외", "상주시는 비수도권·비규제지역 — 수도권/규제지역 전용 규제"],
  ["스트레스 금리 상향 (1.5%→3.0%)", "제외", "비규제지역은 기존 하한 0.75%~상한 3.0% 유지"],
  ["전세대출 DSR 반영", "제외", "수도권·규제지역 1주택자 전세대출에 한정"],
  ["LTV(주택담보대출비율) 제한", "적용", "무주택(처분조건부 1주택 포함) 70%, 유주택 60%"],
], [3400, 1400, 4550], { centerCols: [1] }));
children.push(figCaption("공고일(2026.03.09) 기준 대출규제 적용 여부", "2025.10.15 주택시장 안정화 대책 원문 대조"));
children.push(commentBox("공고문 자체는 대출규제 기준일·LTV 수치를 명시하지 않고 '정부정책 변경 시 계약자 책임하에 조달'이라는 포괄조항만 두고 있어, 대출규제 기준 명시 개선협의 요청 대상입니다. 계약 전 개별 세대 기준 취급은행 사전상담 필요."));

// ================= 2부. 독소조항 =================
children.push(...h1("2부", "독소조항 — 「약관의 규제에 관한 법률」 등 저촉 소지"));
children.push(p("실거주에 직접 영향을 주는 시공·마감재·조경·계약해제 관련 조항을 우선 배치했습니다."));

children.push(h2("2-1. 시공·마감재·조경"));
const constructionRisk = [
  { text: "발코니 확장 세대의 상부세대가 비확장일 경우 상부세대의 배관 일부가 확장세대 상부에 노출되어 이로 인한 소음이 발생할 수 있으며 이로 인하여 사업주체 또는 시공사에 이의를 제기할 수 없습니다.",
    reason: "배관노출 소음 하자책임 면제", law: "약관의 규제에 관한 법률 제7조제3호, 공동주택관리법 제36조제1항",
    comment: "하자담보책임을 사전에 포괄 면제하는 조항은 무효 소지가 있습니다. 하자보수 대상 일률배제 문구 삭제 및 저감시공 대안 개선협의 요청." },
  { text: "세대 내 적용되는 마감 자재는 자재의 품절, 품귀, 생산 중단, 제조 회사의 도산 등 부득이한 경우에는 동질, 동급 이상의 제품으로 변경될 수 있습니다.",
    reason: "마감재 변경 — 사전 공지·동의 절차 미비", law: "약관의 규제에 관한 법률 제10조제1호",
    comment: "'동급 이상' 대체는 표준이나 사전 공지·동의 절차가 빠져 있어 임의 하향 시공 여지 있음. 변경 전 사전고지 절차 신설 개선협의 요청." },
  { text: "준공 후 조경 유지관리 의무는 관리주체 및 입주자에게 있으며, 유지관리 소홀로 인한 조경수 고사 및 조경 하자는 시공사에 책임이 없습니다.",
    reason: "조경 하자책임 일률 면제", law: "약관의 규제에 관한 법률 제7조제3호",
    comment: "고사 원인이 시공불량인지 관리소홀인지 불명확한 상태에서 시공사 책임을 일률 면제하는 것은 무효 소지가 있습니다. 초기 하자(준공 후 1년 등) 시공사 책임 명시 개선협의 요청." },
  { text: "발코니 확장 세대는 인접세대 또는 상부세대가 비확장일 경우와 세대내 비확장 발코니에 면하는 경우 추가 단열재 시공으로 인하여 침실 및 거실 발코니 벽체부위에 단차가 생길 수 있으며 이로 인하여 사업주체 또는 시공사에 이의를 제기할 수 없습니다.",
    reason: "발코니 확장 단차 이의제기 금지", law: "약관의 규제에 관한 법률 제14조제1호",
    comment: "시공상 단차·마감불량 관련 이의제기 자체를 금지하는 것은 무효 소지가 있습니다. 단차 저감시공 및 이의제기권 확보 개선협의 요청." },
];
constructionRisk.forEach((item, i) => {
  children.push(h2(`시공 ${i + 1}. ${item.reason}`, RED));
  children.push(quoteBox(item.text));
  children.push(labelLine("법적 근거", item.law, RED));
  children.push(commentBox(item.comment));
});

children.push(h2("2-2. 계약해제·설계변경·공용시설"));
const contractRisk = [
  { text: "아파트 현장여건(지질상태, 주변 민원 등)에 따라 공사공법이 변경될 수 있으며... 관계법령에서 정하는 경미한 설계변경은 계약자의 동의가 있는 것으로 간주하여 계약자의 동의없이 사업주체가 인·허가를 통해 진행할 수 있습니다.",
    reason: "설계변경 동의 간주", law: "약관의 규제에 관한 법률 제10조제1호, 제12조제1호",
    comment: "경미한 설계변경의 구체적 기준 및 중대 변경 시 사전 통지·동의 절차 신설 개선협의 요청." },
  { text: "입주예정일은... 지연될 수 있으며, 이 경우 입주 지연에 따른 이의를 제기할 수 없으며, 지체상금은 발생하지 않습니다.",
    reason: "지체상금 면제 + 이의제기 금지", law: "약관의 규제에 관한 법률 제7조제2호",
    comment: "사업주체 귀책사유 시 지체상금 지급 조항 신설 개선협의 요청." },
  { text: "본 아파트의 판매시점에 따라 향후 분양조건의 차이가 있을 수 있으며, 이에 이의를 제기하실 수 없습니다.",
    reason: "분양조건 차이 이의제기 금지", law: "약관의 규제에 관한 법률 제11조제1호, 제14조제1호",
    comment: "동일 사유 대량 발생 대비, 협의회 차원 대표 문제제기 창구 사전 확보 필요." },
  { text: "견본주택에서 확인이 곤란한 공용부문의 시설물(공용계단, 지하주차장, 엘리베이터의 용량·속도·탑승위치 등)은... 최종 주택건설사업계획승인 도면에 준하며, 이로 인해 사업주체 또는 시공사에게 이의를 제기할 수 없습니다.",
    reason: "공용시설 임의변경 + 이의제기 금지", law: "약관의 규제에 관한 법률 제10조제1호, 제14조제1호",
    comment: "최종 사업계획승인 도면 사전공개 및 중대 하향변경 시 통지의무 신설 개선협의 요청." },
  { text: "공급계약이 계약자의 사정이나 귀책사유로 인해 해제가 될 경우 계약자는 위약금과 별도로 시행위탁자( 및 시공사)가 대납한 이자 전액을 시행위탁자( 및 시공사)에게 지급하여야 합니다.",
    reason: "위약금 + 대납이자 이중부담", law: "약관의 규제에 관한 법률 제8조",
    comment: "위약금 외 대납이자 전액 상환까지 강제하는 것은 과도한 손해배상액 예정 소지. 이자 부담 상한 설정 개선협의 요청." },
  { text: "상기 유상옵션은 계약 시점 이후 시공을 위해 자재를 발주해야 하므로 중도금 납부 이후에는 유상옵션 공급주체 및 시공사의 동의 없이 계약 해제 및 변경이 불가합니다.",
    reason: "유상옵션 해제권 박탈", law: "약관의 규제에 관한 법률 제9조",
    comment: "특정 시점 이후 해제권을 전면 박탈하는 것은 소비자 보호 측면에서 점검 필요. 해제 가능 기간 확대 개선협의 요청." },
  { text: "추가 선택품목은... 판매가 및 사양에 대해 교체 및 해약을 요구할 수 없으므로 타사 및 기타, 시중품목과 비교 검토한 후에 계약 체결하시기 바랍니다.",
    reason: "추가 선택품목 교체·해약 원천금지", law: "약관의 규제에 관한 법률 제9조",
    comment: "품질 불량 등 합리적 사유가 있는 경우까지 교체·해약을 금지하는 것은 과도함. 하자 발생 시 예외 인정 개선협의 요청." },
  { text: "중도금 대출 기간 이내라도 계약자의 금융 신용불량 등 결격사유 등이 발생할 경우 중도금 대출취급기관의 중도금 대출 중단 등 요구에 따라 공급대금이 납부되지 않을 경우 공급계약서에 따라 계약 해제를 할 수 있으며",
    reason: "대출중단 시 유예없는 계약해제", law: "약관의 규제에 관한 법률 제9조",
    comment: "최고·유예기간 없는 즉시 해제는 불리한 특약 소지. 최소 유예기간 부여 개선협의 요청." },
];
contractRisk.forEach((item, i) => {
  children.push(h2(`계약 ${i + 1}. ${item.reason}`, RED));
  children.push(quoteBox(item.text));
  children.push(labelLine("법적 근거", item.law, RED));
  children.push(commentBox(item.comment));
});

// ================= 3부. 개선요구사항 =================
children.push(...h1("3부", "개선요구사항 — 확인·협의 대상"));
children.push(p("법령 위반 소지는 아니나, 시행사·시공사에 확인·공개·협의를 요청할 수 있는 사안입니다."));

children.push(h2("3-1. 동별 유의사항 — 배치도 대조"));
children.push(p("공고문 전체를 전수 검토해 특정 동·라인·층에만 차별적으로 적용되는 유의사항을 찾아 배치도에 표시했습니다."));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({ type: "png", data: fs.readFileSync("images/site_plan_annotated_crop.png"), transformation: { width: 440, height: 320 } })],
}));
children.push(figCaption("단지배치도 — 동별 유의사항 확인 동 표시", "상주자이르네 공식 홈페이지 배치도 + 본 법인 주석"));
children.push(simpleTable([
  ["동", "유의사항", "유형", "개선요구"],
  ["101동", "필로티 인접 저층: 발전기·전기실·주차장 급기DA 소음·진동·연기", "소음", "가동시간 제한 및 저층 방음보강 시공 요청"],
  ["101·102동", "1층 인접 저층부: 골프연습장·피트니스 소음·사생활침해", "사생활", "운영시간 제한 및 방음설계 근거자료 공개 요청"],
  ["101·106동", "문주 인접 저층: 조망간섭, 경관조명 눈부심", "조망", "조명 각도·밝기 조정 및 해당세대 보상협의 요청"],
  ["102동", "지하1층 인접 저층: 사우나 배기 소음·진동·냄새", "소음", "배기구 방향 재설계 또는 소음저감 보강 요청"],
  ["102동", "최상층 CLUB CLOUD 인접동·하부세대: 빛산란, 소음·사생활침해", "소음", "운영시간 제한·방음창호 기본사양·조명차폐 요청"],
  ["103동", "북측외벽 외부EV 인접세대: 운행 소음·진동", "소음", "저진동 사양 확인 및 인접세대 방음보강 요청"],
  ["106동", "지상1층 인접 2층 등: 근생시설 유지보수 사생활침해", "사생활", "유지보수 작업시간 야간·주말 제한 요청"],
  ["106동", "인접: 근생 부속설비(실외기·배기팬) 조망·소음·사생활침해", "조망", "설비 반대편 재배치 또는 방음펜스 설치 요청"],
  ["106동", "인접: 쓰레기분리수거장 냄새·소음·분진, 수거차량 상시접근", "소음", "밀폐형 구조 적용 및 수거차량 시간대 제한 요청"],
  ["106동", "인접: 근생 급배기D.A 소음·진동·연기", "소음", "덕트 방향 재검토 및 저층 방음보강 요청"],
], [1100, 4200, 900, 3150], { cellSize: 18, headColor: RED }));
children.push(figCaption("동별 유의사항 매트릭스 (특정 동)", "상주자이르네 입주자모집공고문 원문 전수 검토"));

children.push(h2("공통 유의사항 (동 무관, 위치 조건부 적용)"));
children.push(simpleTable([
  ["대상 위치", "유의사항", "개선요구"],
  ["각 동 저층세대", "차량·보행 소음, 쓰레기보관소 악취·분진", "저층 대상 조경 차폐(식재보강) 요청"],
  ["각 동 지붕층 인접 최상층", "태양광·안테나·중계기 소음진동", "설비 배치도 공개 요청, 실제 인접세대 확정 필요"],
  ["필로티 설치동", "차량·보행 피해, 캐노피 형태 변경가능", "캐노피 확정 사양 사전공개 요청"],
  ["필로티 상부 2층", "완강기 설치로 인한 실내 공간제약", "설치 위치 사전고지 및 조기 도면제공 요청"],
  ["레벨차 구간 인접세대", "옹벽·비탈면으로 인한 조망침해", "옹벽 확정도면 공개 요청"],
  ["외부 EV·기계실·휀룸 인접세대", "장비 운행 소음·진동", "저소음 사양 확인 및 방음보강 요청"],
  ["사다리차 접근불가 호수", "승강기 이용 필수", "해당 호수 리스트 사전공지 요청"],
  ["경관조명·로고(BI) 인접세대", "눈부심, 빛반사 소음", "밝기·각도 시운전 결과 공유 및 차광옵션 제공 요청"],
  ["지하주차장 출입구 인접 저층세대", "환기·채광 시설물 소음·조망 침해", "시설물 최종 위치도 공개 요청"],
], [2400, 3900, 3050], { cellSize: 18 }));
children.push(figCaption("동별 유의사항 매트릭스 (공통사항)", "상주자이르네 입주자모집공고문 원문 전수 검토"));

children.push(h2("3-2. 소방·구조·에너지"));
children.push(quoteBox("최초 사업계획승인일이 2022년 5월 16일로 소방내진설계가 적용됩니다. 스프링클러 배관 관경 및 기준 개수 등 소화 시설물의 기준은 수리계산에 의해 설계도면과 다르게 시공될 수 있습니다."));
children.push(labelLine("강화된 내용(승인 이후)", "연립·다세대주택 간이스프링클러 설치 의무 확대(2024.12.01 시행, 아파트 직접 해당여부 확인필요)"));
children.push(commentBox("소방시설 완비증명서 및 화재안전기준 적용판 공개 요청. ESS 화재안전기준 등 최신 개정사항과의 관련성은 추가 확인 후 다음 보고서 반영."));
children.push(quoteBox("주요 구조체는 정밀구조계산에 따라 최적화 될 수 있으며, 이에 따라 내력벽은 비내력벽으로 변경될 수 있습니다."));
children.push(commentBox("구조형식(벽식/무량판 등) 미기재 상태입니다. 구조형식 및 구조계산서(또는 구조심의 결과) 공개 요청 — 소급규제 대상이 아니라는 이유로 거부할 법적 근거는 없습니다."));
children.push(quoteBox("본 아파트는 「건축법」 제48조 제3항 및 제48조의3 제2항에 따른 내진성능 확보 여부와 내진 능력 공개에 의거... 내진중요도 I등급, Ⅶ등급"));
children.push(commentBox("내진성능 확인서 및 설계 당시 적용 기준(KDS 버전) 공개 요청. 필요 시 제3자 구조기술사 검토 주선 가능."));
children.push(quoteBox("1. 경량충격음 차단성능 ★★★★   2. 중량충격음 차단성능 ★★★"));
children.push(commentBox("중량충격음 ★★★(4단계 중 낮은 편)은 입주 후 민원 소지가 있습니다. 정확한 성적서(dB 수치) 공개 및 차음재 성능 상향시공 개선협의 요청."));
children.push(quoteBox("전기차 충전시스템은 총 58개(급속 2대, 완속 56대)설치되며, 주차장의 위치 및 구조에 따라 배치 위치는 달라질 수 있습니다."));
children.push(commentBox("법정 의무비율(5%, 약 41대)을 상회하는 58대로 양호합니다. 준공 시 최종 배치도 확인 필요 — 특정 동 편중 여부 점검."));
children.push(quoteBox("건축물 에너지효율등급 예비인증서 인증등급 1+등급"));
children.push(commentBox("상위권 등급으로 확인됩니다. 준공 시 본인증 등급의 예비인증 동일 유지 여부 확인 필요."));

children.push(h2("3-3. 커뮤니티시설·근린생활시설"));
children.push(quoteBox("CLUB XIAN은 입주지정기간 경과 후 관리주체에서 운영하게 되며... 운동기구는 준공 후 입주지정기간이 종료된 이후 설치 될 수도 있음을 알려드립니다."));
children.push(commentBox("피트니스·골프연습장·사우나 등은 입주와 동시 운영이 아니라 순차 운영됩니다. 정확한 개장 일정 서면 사전공지 요청."));
children.push(quoteBox("106동 인근에 근린생활시설 부속시설물(에어컨실외기, 배기팬, 설비시설 등)이... 쓰레기 분리수거장은... 106동에 인접하여 냄새 및 소음, 분진이 발생할 수 있습니다."));
children.push(commentBox("106동 집중 리스크입니다(위 3-1 매트릭스 참조). 업종 제한(특히 음식점) 협의 및 설비 위치 사전공유 요청."));

children.push(h2("3-4. 기타 확인사항 (참고, 낮은 비중)"));
children.push(p("아래는 계약 실효성에 큰 영향은 없으나, 단지별로 조건이 다를 수 있어 전수조사 차원에서 확인한 항목입니다.", { italics: true, color: GRAY, size: 19 }));
children.push(simpleTable([
  ["항목", "내용", "확인사항"],
  ["시행 신탁구조", "시행수탁자 교보자산신탁은 하자보수 책임 없음. 신탁재산 한도 초과분은 시행위탁자 ㈜고은건설이 부담", "시행사 재무상태는 별도 확인 권장(참고용)"],
  ["셔틀버스 지원", "점촌 시내 셔틀버스 1년 한시 지원 후 입주자대표회의 자체비용 연장", "1년 후 비용 부담 주체임을 사전 인지 필요"],
  ["영구배수공법", "부력방지 배수공법 적용 시 공용 전기세·하수도요금 발생, 관리비 포함 부과", "관리비 예상 항목에 반영 필요"],
  ["관리비예치금", "선수관리비 징수·사용은 사업주체·시공사와 무관 명시", "입주자대표회의 구성 후 별도 확인 필요"],
], [1800, 4900, 2650], { cellSize: 18 }));
children.push(figCaption("기타 확인사항", "상주자이르네 입주자모집공고문 원문"));

// ================= 4부. 단지 주변조사 =================
children.push(...h1("4부", "단지 주변조사"));
children.push(h2("4-1. 주변 편의시설 (카카오맵 기준, 반경 1km)"));
children.push(simpleTable([
  ["구분", "개소", "대표 시설 (최단거리)"],
  ["대형마트", "1", "함창농협 하나로마트 (818m)"],
  ["편의점", "4", "GS25 상주함창LH점 (272m)"],
  ["어린이집/유치원", "3", "함창가온어린이집 (223m)"],
  ["병원", "7", "함창치과의원 (599m)"],
  ["약국", "4", "중앙약국 (690m)"],
], [2000, 1000, 6350], { centerCols: [1] }));
children.push(figCaption("반경 1km 내 생활 편의시설", "카카오맵 로컬 API (2026.07.16 조회)"));
children.push(commentBox("장례식장 2개소(삼성장례컨설팅 729m, 중앙장례식장 955m)가 반경 1km 내 확인되어 참고 안내. 법적 하자 사안은 아니므로 별도 대응 불필요."));

children.push(h2("4-2. 학군"));
children.push(p("NEIS(교육정보 개방포털) 공식 확인 결과 및 카카오맵 인접 학교입니다. 학업성취도·서열 데이터는 정책상 공식 비공개이며, 아래는 위치·학교급 등 객관적 사실만 포함합니다."));
children.push(simpleTable([
  ["학교급", "학교명", "비고"],
  ["초등학교", "함창초등학교 / 함창중앙초등학교", "NEIS 공식 확인"],
  ["중학교", "함창중학교 / 상지여자중학교", "NEIS 공식 확인 / 카카오맵 394m"],
  ["고등학교", "함창고등학교 / 상지미래경영고등학교", "NEIS 공식 확인 / 카카오맵 399m"],
], [1600, 4600, 3150]));
children.push(figCaption("함창읍 소재 초·중·고 현황", "NEIS 교육정보 개방포털 + 카카오맵"));

children.push(h2("4-3. 인근 시세 (국토부 실거래가, 2026.01~06 함창읍)"));
children.push(simpleTable([
  ["단지명", "준공연도", "전용면적", "거래가"],
  ["상주함창엘에이치천년나무2단지", "2016", "67.86㎡", "2.8억~2.9억"],
  ["상주함창엘에이치천년나무2단지", "2016", "74.94㎡", "2.6억"],
  ["녹원", "1993", "84.29㎡", "0.73억"],
], [3600, 1400, 1900, 2450], { centerCols: [1, 2, 3] }));
children.push(figCaption("함창읍 아파트 실거래 현황", "국토교통부 실거래가 공개시스템"));
children.push(commentBox("함창읍 내 가장 최근 준공 단지(2016년 천년나무2단지) 대비 신축·평면·커뮤니티 시설 수준을 감안한 분양가 참고자료로 안내."));

children.push(h2("4-4. 분양보증·등기"));
children.push(quoteBox("주택도시보증공사 보증서 번호 제 01282026-101-0001300호, 보증금액 246,667,915,000원, 보증기간 입주자모집공고승인일로부터 소유권보존등기일까지"));
children.push(commentBox("분양보증(HUG)이 정상 확인되어 양호합니다. 다만 소유권보존등기(특히 대지 이전등기)는 지적공부정리 절차 등으로 지연될 수 있다고 명시되어 있어, 등기 일정은 입주 이후 별도 확인 필요."));

// ================= 부록: 한장 총정리 =================
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(...h1("부록", "총정리 (별도 배포용)"));
children.push(p("본 페이지만 별도로 출력·배포해 협의회 회의자료로 활용할 수 있습니다."));

const checklist = [
  ["구분", "항목", "내용", "우선순위"],
  ["독소조항", "배관노출 소음 면책", "하자담보책임 배제 — 약관법 제7조·공동주택관리법 제36조", "1순위"],
  ["독소조항", "설계변경 동의간주", "통보·동의 없이 임의 인허가 — 약관법 제10·12조", "1순위"],
  ["독소조항", "지체상금 면제", "귀책사유 불문 이의제기·지체상금 배제 — 약관법 제7조", "1순위"],
  ["독소조항", "공용시설 임의변경", "이의제기 금지 — 약관법 제10·14조", "1순위"],
  ["독소조항", "조경 하자책임 면제", "고사원인 불문 시공사 면책 — 약관법 제7조", "2순위"],
  ["독소조항", "위약금+대납이자 이중부담", "과도한 손해배상액 예정 소지 — 약관법 제8조", "2순위"],
  ["독소조항", "유상옵션 해제권 박탈", "중도금납부 후 해제 전면금지 — 약관법 제9조", "2순위"],
  ["독소조항", "분양조건 차이", "이의제기 금지 — 약관법 제11·14조", "3순위"],
  ["동별유의", "101동", "발전기·전기실·급기DA 소음 (저층)", "1순위"],
  ["동별유의", "102동", "사우나 배기·CLUB CLOUD 소음 (지하1층·최상층)", "1순위"],
  ["동별유의", "106동", "근생 인접 사생활·실외기·쓰레기장·급배기DA", "1순위"],
  ["동별유의", "103동", "외부EV 소음·진동 (북측외벽)", "2순위"],
  ["개선요구", "구조형식", "무량판 여부 미기재 → 구조계산서 공개 요청", "1순위"],
  ["개선요구", "층간소음", "중량충격음 ★★★ → 차음재 상향시공 요청", "1순위"],
  ["개선요구", "커뮤니티시설", "CLUB XIAN 개장일정 사전공지 요청", "1순위"],
  ["개선요구", "소방시설", "완비증명서·화재안전기준 적용판 공개 요청", "2순위"],
  ["개선요구", "대출규제", "LTV만 적용, 공고문에 기준 미명시 → 명시 요청", "2순위"],
  ["개선요구", "내진성능", "확인서·적용기준(KDS) 공개 요청", "3순위"],
  ["참고사항", "신탁구조", "시행수탁자 하자보수 면책, 초과분은 고은건설 부담", "참고"],
  ["참고사항", "셔틀버스", "1년 한시지원 후 입주자대표회의 비용전환", "참고"],
  ["양호확인", "분양보증", "HUG 보증서 정상 확인", "-"],
  ["양호확인", "전기차충전", "58대, 법정비율(5%) 상회", "-"],
  ["양호확인", "에너지효율", "1+등급", "-"],
];
children.push(simpleTable(checklist, [1350, 1750, 4650, 1600], { cellSize: 17, centerCols: [3] }));

// ================= Header / Footer =================
const header = new Header({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 4 } },
    children: [
      new TextRun({ text: "상주자이르네 검토보고서 · 법무법인제이엘", size: 16, color: "999999" }),
      new TextRun({ text: "\t2026 · 입주예정자협의회 배포용", size: 16, color: "999999" }),
    ],
  })],
});
const footer = new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "999999" })],
  })],
});

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  sections: [{
    properties: {},
    headers: { default: header },
    footers: { default: footer },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("상주자이르네_검토보고서_v6.docx", buf);
  console.log("done");
});
