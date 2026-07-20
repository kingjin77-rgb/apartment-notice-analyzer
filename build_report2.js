const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign, PageBreak
} = require("docx");
const fs = require("fs");

const RED = "C00000";
const ORANGE = "B45309";
const GREEN = "2E7D32";
const BLUE = "1F4E78";
const GRAY = "595959";
const LIGHTGRAY = "F2F2F2";

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 120 } }); }
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], bullet: { level: 0 }, spacing: { after: 80 } });
}
function quoteBox(text) {
  return new Paragraph({
    children: [new TextRun({ text: `"${text}"`, italics: true, color: GRAY, size: 20 })],
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: "999999", space: 8 } },
    indent: { left: 200 },
    spacing: { before: 80, after: 80 },
  });
}
function labelLine(label, text, color = BLUE) {
  return new Paragraph({
    spacing: { after: 60 },
    children: [
      new TextRun({ text: `${label}  `, bold: true, color }),
      new TextRun({ text }),
    ],
  });
}
function commentBox(text) {
  return new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: "EAF1F8" },
    border: {
      top: { style: BorderStyle.SINGLE, size: 4, color: BLUE },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: BLUE },
      left: { style: BorderStyle.SINGLE, size: 4, color: BLUE },
      right: { style: BorderStyle.SINGLE, size: 4, color: BLUE },
    },
    indent: { left: 60, right: 60 },
    spacing: { before: 100, after: 200 },
    children: [
      new TextRun({ text: "법무법인 의견  ", bold: true, color: BLUE }),
      new TextRun({ text }),
    ],
  });
}
function cell(text, opts = {}) {
  const { bold = false, shade = null, width = 2000, color = "000000", align = AlignmentType.LEFT } = opts;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text, bold, color })] })],
  });
}
function simpleTable(rows, widths) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, i) => new TableRow({
      children: r.map((val, ci) => cell(val, {
        bold: i === 0,
        shade: i === 0 ? BLUE : (i % 2 ? LIGHTGRAY : null),
        color: i === 0 ? "FFFFFF" : "000000",
        width: widths[ci],
        align: ci === 1 && i > 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
      })),
    })),
  });
}

// ================= PART builders =================

const children = [];

// ---- Cover ----
children.push(
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 },
    children: [new TextRun({ text: "상주자이르네 입주자모집공고문 상세 검토보고서", bold: true, size: 40 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: "건축·구조·소방·계약조항 종합분석 (AI 1차 스크리닝, 관계법령 원문 대조)", size: 22, color: GRAY })] }),
  simpleTable([
    ["대상 단지", "상주자이르네 (2026000038 입주자모집공고, 공고일 2026.03.09 / 사업계획승인일 2022.05.16)"],
    ["배포 대상", "상주자이르네 입주예정자협의회"],
    ["작성일", "2026.07.16"],
  ], [2400, 6950]),
  new Paragraph({ spacing: { before: 200, after: 200 }, children: [new TextRun({ text: "" })] }),
  new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: "FFF4E5" },
    border: {
      top: { style: BorderStyle.SINGLE, size: 6, color: ORANGE }, bottom: { style: BorderStyle.SINGLE, size: 6, color: ORANGE },
      left: { style: BorderStyle.SINGLE, size: 6, color: ORANGE }, right: { style: BorderStyle.SINGLE, size: 6, color: ORANGE },
    },
    spacing: { before: 100, after: 100 }, indent: { left: 100, right: 100 },
    children: [new TextRun({
      text: "본 보고서는 입주자모집공고문 원문, 관계법령 원문(약관의 규제에 관한 법률·공동주택관리법 등), 공개 행정정보를 대조하여 작성한 1차 검토자료입니다. 최종 법률의견을 대체하지 않으며, 구조·소방 등 전문분야는 별도 기술자문을 권고합니다.",
      size: 20,
    })],
  })
);

// ---- Executive summary ----
children.push(h1("한눈에 보기"));
[
  "본 단지는 2022.05.16 사업계획승인을 받아, 이후 강화된 건축·소방 기준 다수가 원칙적으로 소급 적용되지 않습니다. 다만 소급 여부와 무관하게 협의회가 시행사에 확인·개선을 요구할 수 있는 사안이 다수 확인됩니다.",
  "가장 시급한 확인사항은 ① 구조형식(무량판 여부) 미기재, ② 근린생활시설(106동 등 인접) 업종·설비 제약 부재, ③ 커뮤니티시설 입주 초기 미운영 가능성입니다.",
  "계약조항 중 5건은 「약관의 규제에 관한 법률」 조문에 직접 저촉되는 것으로 판단되어 삭제·수정을 요구할 근거가 있습니다.",
  "대출규제는 공고일(2026.03.09) 기준 LTV만 적용(무주택 70%/유주택 60%)되며, 6억 한도·전세대출 DSR 등은 비규제지역이라 제외됩니다.",
  "에너지효율 1+등급, 전기차충전 58대(법정 의무비율 이상)는 양호한 요소로 확인되어 함께 안내드립니다.",
].forEach(t => children.push(bullet(t)));

// ---- 1. 대출규제 ----
children.push(h1("1. 대출규제 안내 (공고일 2026.03.09 기준)"));
children.push(p("대출규제는 오늘 날짜가 아니라 입주자모집공고일 시점에 시행 중이던 규제가 적용되는 것이 원칙입니다."));
children.push(simpleTable([
  ["대책 항목", "적용 여부", "근거"],
  ["주담대 여신한도 차등화 (6억원 제한)", "제외", "상주시는 비수도권·비규제지역 — 수도권/규제지역 전용 규제"],
  ["스트레스 금리 상향 (1.5%→3.0%)", "제외", "비규제지역은 기존 하한 0.75%~상한 3.0% 유지"],
  ["전세대출 DSR 반영", "제외", "수도권·규제지역 1주택자 전세대출에 한정"],
  ["LTV(주택담보대출비율) 제한", "적용", "무주택(처분조건부 1주택 포함) 70%, 유주택 60%"],
], [3400, 1400, 4550]));
children.push(commentBox("공고문 자체에는 대출규제 기준일·LTV 수치가 명시되어 있지 않고 “정부정책 변경 시 계약자 책임하에 조달”이라는 포괄조항만 있습니다. 계약 전 반드시 취급은행에 개별 대출한도를 재확인하시길 권고드리며, 2025.10.15 대책 이후 2026.03.09 공고일 사이 추가 개정이 있었는지는 저희 쪽에서도 별도 확인하겠습니다."));

// ---- 2. 건축·구조 ----
children.push(h1("2. 건축·구조 — 사업계획승인 이후 기준 변화"));
children.push(labelLine("사업계획승인일", "2022.05.16 (공고문 명시)"));
children.push(labelLine("강화된 내용(승인 이후)", "무량판 구조가 ‘특수구조 건축물’로 지정되어 구조 심의·감리중간보고서 의무 등 안전관리가 강화됨 (건축법 시행령 개정, 2023.09.12 시행)"));
children.push(labelLine("그러나", "법령 불소급 원칙상, 승인 당시 적법하게 설계되었다면 현행 기준으로 전면 재설계를 요구할 수 없습니다."));
children.push(p("본 공고문의 구조 관련 조항입니다:"));
children.push(quoteBox("주요 구조체는 정밀구조계산에 따라 최적화 될 수 있으며, 이에 따라 내력벽은 비내력벽으로 변경될 수 있습니다. 지하주차장 구조는 공사 여건에 따라 PC 또는 데크로 변경될 수 있으며, 피트(PIT)공간의 구획, 높이 및 면적, 비내력벽의 두께 등이 변경될 수 있습니다."));
children.push(commentBox("공고문에 구조형식(벽식/무량판 등)이 명시되어 있지 않고, 오히려 ‘내력벽→비내력벽 변경 가능’이라는 포괄적 변경 여지만 열려 있습니다. 법적으로 무량판 구조 자체가 금지된 것은 아니나, 최근 사회적으로 안전 우려가 큰 사안인 만큼 협의회 명의로 시행사에 구조형식 및 구조계산서(또는 구조 심의결과) 공개를 요청하실 것을 권고드립니다. 소급 규제 대상이 아니라는 이유로 시행사가 공개를 거부할 법적 근거는 없습니다."));

// ---- 3. 내진 ----
children.push(h1("3. 내진설계"));
children.push(quoteBox("본 아파트는 「건축법」 제48조 제3항 및 제48조의3 제2항에 따른 내진성능 확보 여부와 내진 능력 공개에 의거 메르칼리 진도 등급을 기준으로 내진능력을 공개합니다. 내진중요도 I등급, Ⅶ등급"));
children.push(labelLine("강화된 내용(승인 이후)", "국토교통부가 내진설계 일반기준(KDS 17 10 00)을 2024.03.21 개정 — 주로 기계설비 내진에 대한 보완이 중심이며, 구조체 자체의 내진설계기준이 전면 강화되었는지는 확인이 더 필요합니다."));
children.push(commentBox("내진설계는 구조 전문분야로, 정확한 적정성 판단에는 구조기술사 자문이 필요합니다. 협의회 차원에서 ‘내진성능 확인서’ 및 설계 당시 적용 기준(KDS 버전)을 시행사에 요청하실 것을 권고드리며, 필요 시 저희가 제3자 구조기술사 검토를 주선해 드릴 수 있습니다."));

// ---- 4. 층간소음 ----
children.push(h1("4. 층간소음·바닥충격음 차단성능"));
children.push(quoteBox("1. 경량충격음 차단성능 ★★★★  2. 중량충격음 차단성능 ★★★"));
children.push(labelLine("정책 변화", "2023.12.12 국토부 ‘기준 미달 시 준공 불허’로 층간소음 정책 패러다임 전환. 다만 이 노트북 확인 결과, 해당 정책은 향후 신축 단지부터 적용되며 기존 승인단지는 준공 불허 대상에서 제외되고 바닥방음 보강지원 사업으로 대응합니다."));
children.push(labelLine("우리 단지 해당여부", "사업계획승인일(2022.05.16)이 정책 발표(2023.12.12)보다 앞서므로, 이 강화된 기준의 법적 강제 대상은 아닙니다."));
children.push(commentBox("법적 강제 대상이 아니라는 점은 명확하나, 중량충격음 ★★★(4단계 중 낮은 편)은 입주 후 층간소음 민원의 실질적 원인이 될 수 있습니다. ① 정확한 성적서(dB 수치) 공개 요청, ② 시공사에 완충재·차음재 성능 상향시공(비용 협의) 요청, ③ 국토부·지자체의 바닥방음 보강지원 사업 활용 가능성 확인을 권고드립니다. 강제할 권리는 아니지만 실제 협상에서 시행사가 수용한 사례가 다수 있는 항목입니다."));

// ---- 5. 소방 ----
children.push(h1("5. 소방시설"));
children.push(quoteBox("최초 사업계획승인일이 2022년 5월 16일로 소방내진설계가 적용됩니다. 스프링클러 배관 관경 및 기준 개수 등 소화 시설물의 기준은 수리계산에 의해 설계도면과 다르게 시공될 수 있습니다."));
children.push(labelLine("강화된 내용(승인 이후)", "연립·다세대주택에 간이스프링클러 설치 의무 확대 (2024.12.01 시행) — 다만 이는 연립·다세대 대상이며, 상주자이르네는 아파트로 분류되어 직접 해당 여부는 추가 확인이 필요합니다."));
children.push(commentBox("ESS(전기저장시설) 화재안전기준 강화 등 최신 소방 이슈는 이 검토에서 확정적 근거자료를 확보하지 못했습니다. ‘부실 조사’가 되지 않도록, 협의회 명의로 소방시설 완비증명서 및 화재안전기준 적용판을 시행사에 정식 요청하실 것을 권고드리며, 저희 쪽에서도 관련 법령을 추가로 확인해 다음 보고서에 반영하겠습니다."));

// ---- 6. 전기차 충전시설 ----
children.push(h1("6. 전기차 충전시설"));
children.push(quoteBox("전기차 충전시스템은 총 58개(급속 2대, 완속 56대)설치되며, 주차장의 위치 및 구조에 따라 배치 위치는 달라질 수 있습니다."));
children.push(labelLine("법정 기준", "2022.01.28 시행 개정법상 신축 아파트(100세대 이상)는 총 주차대수의 5% 이상 설치 의무. 총 820세대 기준 최소 41대 이상 필요."));
children.push(commentBox("58대는 법정 의무비율(약 7.1%)을 상회하는 양호한 수준입니다. 다만 ‘배치 위치는 달라질 수 있다’는 문구가 있어, 준공 시 실제 위치(특정 동에 편중되지 않는지)를 확인하시길 권고드립니다."));

// ---- 7. 에너지 ----
children.push(h1("7. 에너지절약설계"));
children.push(quoteBox("건축물 에너지효율등급 예비인증서 인증등급 1+등급 / 단열조치 준수(가목) 적용 「건축물의 에너지절약설계기준」 제6조제1호에 의한 단열조치"));
children.push(commentBox("에너지효율 1+등급은 상위권에 해당하며, 관리비(냉난방비) 절감에 실질적으로 도움이 되는 긍정적 요소입니다. 예비인증인 만큼, 준공 시 본인증 등급이 예비인증과 동일하게 유지되는지만 확인하시면 됩니다."));

// ---- 8. 입주민 생활이슈 ----
children.push(h1("8. 입주민 생활이슈 — 커뮤니티시설·근린생활시설"));
children.push(h2("8-1. 커뮤니티시설 운영시기"));
children.push(quoteBox("CLUB XIAN은 입주지정기간 경과 후 관리주체에서 운영하게 되며... 커뮤니티센터에는 운동기구가 설치되나, 운동기구는 준공 후 입주지정기간이 종료된 이후 설치 될 수도 있음을 알려드립니다."));
children.push(commentBox("피트니스·골프연습장·사우나 등 CLUB XIAN 시설은 입주와 동시 운영이 아니라 ‘입주지정기간 경과 후’ 순차 운영되며, 운동기구 자체도 추후 설치될 수 있다고 명시되어 있습니다. 타 단지(해링턴 마레 등) 사례에서도 커뮤니티시설 개방 지연이 입주 초기 최대 민원 중 하나였습니다. 입주 전 정확한 개장 일정을 서면으로 사전 공지하도록 요청하실 것을 권고드립니다."));
children.push(h2("8-2. 근린생활시설(상가) 인접동 이슈"));
children.push(quoteBox("101동, 102동, 106동 지상1층에 인접하여 설치되는 작은도서관, 피트니스/골프연습장, 근린생활시설의 시설 유지보수 등으로 인한 2층 및 저층부 일부세대는 사생활 침해 등 생활의 불편이 발생할 수 있습니다."));
children.push(quoteBox("106동 인근에 근린생활시설 부속시설물(에어컨실외기, 배기팬, 설비시설 등)이 추후 상가 입점자 공사로 인하여 설치될 수 있으며... 근린생활시설용 쓰레기 분리수거장은... 106동에 인접하여 이로 인한 냄새 및 소음, 분진이 발생할 수 있고 쓰레기 수거차량의 상시 접근으로 피해가 발생할 수 있습니다."));
children.push(commentBox("106동은 근린생활시설의 실외기·배기팬·탈취설비·쓰레기분리수거장이 모두 인접한 것으로 확인되어, 향후 입주 후 냄새·소음·분진 민원이 집중될 가능성이 높은 동입니다. 공고문에는 상가 업종제한(특히 음식점 입점) 관련 명시가 없습니다. 협의회 차원에서 ① 업종 제한(악취·소음 유발 업종 배제) 협의, ② 106동 대상 실외기·배기설비 위치 사전 공유, ③ 쓰레기 수거차량 동선·시간대 조정을 시행사·상가 분양주체에 요청하실 것을 권고드립니다."));

// ---- 9. 계약조항 핵심 유의사항 ----
children.push(h1("9. 계약조항 핵심 유의사항"));
children.push(p("공고문 조항을 「약관의 규제에 관한 법률」·「공동주택관리법」 원문과 대조한 결과입니다."));

const highRisk = [
  {
    text: "아파트 현장여건(지질상태, 주변 민원 등)에 따라 공사공법이 변경될 수 있으며... 관계법령에서 정하는 경미한 설계변경은 계약자의 동의가 있는 것으로 간주하여 계약자의 동의없이 사업주체가 인·허가를 통해 진행할 수 있습니다.",
    reason: "사업주체가 일방적으로 설계변경을 추진하면서 수분양자 동의를 사전 간주하고, 통보·동의 절차 없이 임의로 인허가를 진행할 수 있도록 규정.",
    law: "약관의 규제에 관한 법률 제10조제1호, 제12조제1호",
    comment: "‘경미한 설계변경’의 범위가 불명확한 채로 동의를 간주하는 것은 무효 소지가 큽니다. 시행사에 경미한 변경의 구체적 기준과 중대한 변경 시 사전 통지·동의 절차 신설을 서면으로 요구하실 것을 권고드립니다.",
  },
  {
    text: "입주예정일은... 지연될 수 있으며, 이 경우 입주 지연에 따른 이의를 제기할 수 없으며, 지체상금은 발생하지 않습니다.",
    reason: "사업주체 귀책범위를 ‘정부 정책 변경’ 등으로 자의적으로 넓게 면책하고, 지체상금 지급의무를 원천 면제.",
    law: "약관의 규제에 관한 법률 제7조제2호",
    comment: "사업주체 귀책사유로 인한 지연에 대해서까지 지체상금을 면제하는 것은 무효 소지가 있습니다. 최소한 귀책사유가 사업주체에 있는 경우 지체상금 지급 조항을 신설하도록 요구하실 것을 권고드립니다.",
  },
  {
    text: "본 아파트의 판매시점에 따라 향후 분양조건의 차이가 있을 수 있으며, 이에 이의를 제기하실 수 없습니다.",
    reason: "향후 할인분양 등 분양조건 변경 시 기존 수분양자의 형평성 문제제기 권리를 사전 차단.",
    law: "약관의 규제에 관한 법률 제11조제1호, 제14조제1호",
    comment: "즉시 무효를 다투기보다, 동일 사유가 대량 발생할 경우를 대비해 협의회 차원의 대표 문제제기 창구를 미리 확보해 두실 것을 권고드립니다.",
  },
  {
    text: "견본주택에서 확인이 곤란한 공용부문의 시설물(공용계단, 지하주차장, 엘리베이터의 용량·속도·탑승위치 등)은... 최종 주택건설사업계획승인 도면에 준하며, 이로 인해 사업주체 또는 시공사에게 이의를 제기할 수 없습니다.",
    reason: "수분양자가 사전 확인이 어려운 공용시설에 대해 임의적 설계 하향 변경 가능성을 열어두고 일체의 이의제기를 금지.",
    law: "약관의 규제에 관한 법률 제10조제1호, 제14조제1호",
    comment: "최종 사업계획승인 도면의 사전 공개를 요청하시고, 최초 고지 사양 대비 중대한 하향 변경이 있는 경우 통지 의무를 신설하도록 요구하실 것을 권고드립니다.",
  },
  {
    text: "발코니 확장 세대의 상부세대가 비확장일 경우 상부세대의 배관 일부가 확장세대 상부에 노출되어 이로 인한 소음이 발생할 수 있으며 이로 인하여 사업주체 또는 시공사에 이의를 제기할 수 없습니다.",
    reason: "구조적 설계 결함으로 인한 소음 피해 발생 가능성을 명시하면서도 하자보수·배상 책임을 완전히 면제.",
    law: "약관의 규제에 관한 법률 제7조제3호, 공동주택관리법 제36조제1항",
    comment: "하자담보책임을 사전에 포괄 면제하는 조항은 무효 소지가 있습니다. 배관 노출 소음을 하자보수 대상에서 일률 배제하는 문구 삭제 및 저감시공(방음자재 등) 대안을 요구하실 것을 권고드립니다.",
  },
];

highRisk.forEach((item, i) => {
  children.push(h2(`위험 ${i + 1}. ${item.reason}`));
  children.push(quoteBox(item.text));
  children.push(labelLine("법적 근거", item.law, RED));
  children.push(commentBox(item.comment));
});

children.push(h2("추가 검토필요 조항 (9건)"));
children.push(p("즉시 무효를 다투기보다, 협의회 차원의 서면 질의·개선요구 대상으로 정리했습니다.", { italics: true, color: GRAY, size: 20 }));
[
  ["마감재/사양 변경", "품절·단종 시 ‘동급 이상’ 대체는 표준이나, 사전 공지·동의 절차가 빠져 있어 임의 하향 시공의 여지가 있음."],
  ["계약 해제/위약금", "해제 시 위약금 외에 대납이자 전액까지 추가 부담시켜 이중 페널티 소지."],
  ["유상옵션(발코니확장 등)", "중도금 납부 이후 옵션 해제·변경을 시공사 동의 없이 전면 금지."],
  ["추가 선택품목", "품질·사양 불만이 있어도 교체·해약 요구 자체를 원천 금지."],
  ["조경 하자책임", "조경수 고사 등 원인(시공불량 vs 관리소홀) 불명확한 상태에서 시공사 책임을 일률 면제."],
  ["중도금 대출 중단", "계약자 귀책 대출중단 시 최고·유예기간 없이 즉시 계약해제 가능 조항."],
  ["환경권 침해 수인조항 (지붕층 시설물)", "일조·조망·소음진동·사생활 침해 가능성을 언급하며 이의제기 배제."],
  ["환경권 침해 수인조항 (단지 내 도로·시설 인접)", "인접세대의 소음·진동·조망 저해 등을 일률적으로 수인하도록 고지."],
  ["발코니 확장 단차", "인접·상부세대 비확장 시 발생하는 시공상 단차·마감 불량 관련 이의제기 배제."],
].forEach(([cat, desc]) => {
  children.push(new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text: `${cat}  —  `, bold: true }), new TextRun({ text: desc })],
    bullet: { level: 0 },
  }));
});

// ---- 10. 결론 및 대응 로드맵 ----
children.push(h1("10. 결론 및 협의회 대응 로드맵"));
children.push(h2("1순위 — 즉시 서면 질의"));
[
  "구조형식(무량판 여부) 및 구조계산서·구조 심의결과 공개 요청",
  "106동(및 101·102동 저층부) 근린생활시설 업종 제한 및 실외기·배기설비 위치 협의",
  "커뮤니티시설(CLUB XIAN 등) 정확한 개장 일정 서면 공지 요청",
  "핵심 유의조항 5건에 대한 삭제·수정 요구 공문 발송",
].forEach(t => children.push(bullet(t)));
children.push(h2("2순위 — 계약 전 확인"));
[
  "대출규제(LTV/DSR) 개별 세대 기준 취급은행 사전상담",
  "바닥충격음 성능시험 성적서(dB 수치) 공개 요청",
  "전기차충전시설 최종 배치도 확인",
].forEach(t => children.push(bullet(t)));
children.push(h2("3순위 — 준공 전후 모니터링"));
[
  "소방시설 완비증명서 및 화재안전기준 적용판 확인",
  "내진성능 확인서(구조기술사 검토) 확보",
  "에너지효율 본인증 등급이 예비인증(1+등급)과 동일한지 확인",
].forEach(t => children.push(bullet(t)));

children.push(new Paragraph({ spacing: { before: 300 }, children: [
  new TextRun({ text: "본 보고서는 AI 1차 스크리닝 및 공개 행정정보 기반 검토자료로, 협의회의 대응 우선순위 결정을 돕기 위해 작성되었습니다. 구조·소방 등 전문영역은 별도 기술자문을, 법적 대응은 정식 법률자문을 권고드립니다.", italics: true, color: GRAY, size: 20 }),
] }));

const doc = new Document({ sections: [{ properties: {}, children }] });

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("상주자이르네_검토보고서.docx", buf);
  console.log("done");
});
