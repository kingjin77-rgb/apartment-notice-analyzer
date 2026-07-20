const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign, Header, Footer,
  PageNumber, ImageRun, TabStopType, TabStopPosition,
} = require("docx");
const fs = require("fs");

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
        borders: {
          bottom: { style: BorderStyle.SINGLE, size: 24, color: GOLD },
        },
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
function h2(text) {
  return new Paragraph({
    spacing: { before: 240, after: 100 },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: GOLD, space: 6 } },
    indent: { left: 80 },
    children: [new TextRun({ text, bold: true, color: NAVY, size: 22 })],
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
    children: [new TextRun({ text: "법무법인 의견   ", bold: true, color: NAVY2 }), new TextRun({ text })],
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
  const { bold = false, shade = null, width = 2000, color = "000000", align = AlignmentType.LEFT } = opts;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 90, bottom: 90, left: 120, right: 120 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text, bold, color, size: 20 })] })],
  });
}
function simpleTable(rows, widths, opts = {}) {
  const { centerCols = [] } = opts;
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, i) => new TableRow({
      children: r.map((val, ci) => cell(val, {
        bold: i === 0,
        shade: i === 0 ? NAVY : (i % 2 ? CREAM : null),
        color: i === 0 ? "FFFFFF" : "000000",
        width: widths[ci],
        align: (centerCols.includes(ci) && i > 0) ? AlignmentType.CENTER : AlignmentType.LEFT,
      })),
    })),
  });
}

const children = [];

// ================= COVER =================
children.push(
  new Paragraph({ spacing: { before: 600, after: 0 }, children: [new TextRun({ text: "" })] }),
  new Paragraph({
    shading: { type: ShadingType.CLEAR, fill: NAVY },
    spacing: { before: 0, after: 0 },
    children: [new TextRun({ text: "  " })],
    border: { bottom: { style: BorderStyle.SINGLE, size: 32, color: GOLD } },
  }),
  new Paragraph({ spacing: { before: 300, after: 60 },
    children: [new TextRun({ text: "상주자이르네 입주자모집공고문", bold: true, size: 46, color: NAVY })] }),
  new Paragraph({ spacing: { after: 240 },
    children: [new TextRun({ text: "상세 검토보고서", bold: true, size: 46, color: NAVY })] }),
  new Paragraph({ spacing: { after: 300 },
    children: [new TextRun({ text: "건축·구조·소방·입지·계약조항 종합분석", size: 24, color: GRAY }),
               new TextRun({ text: "  |  AI 1차 스크리닝, 관계법령 원문·공공데이터 대조", size: 24, color: GRAY, italics: true })] }),
  simpleTable([
    ["대상 단지", "상주자이르네 (2026000038, 공고일 2026.03.09 / 사업계획승인일 2022.05.16)"],
    ["소재지", "경상북도 상주시 함창읍 윤직리 840번지 일원"],
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
      text: "본 보고서는 입주자모집공고문 원문, 관계법령 원문(약관의 규제에 관한 법률·공동주택관리법 등), 국토교통부·나이스·카카오 공공데이터를 대조하여 작성한 1차 검토자료입니다. 최종 법률의견을 대체하지 않으며, 구조·소방 등 전문분야는 별도 기술자문을 권고합니다.",
      size: 19,
    })],
  })
);

// ================= Executive Summary =================
children.push(...h1("", "한눈에 보기"));
[
  "본 단지는 2022.05.16 사업계획승인을 받아, 이후 강화된 건축·소방 기준 다수가 원칙적으로 소급 적용되지 않습니다. 다만 소급 여부와 무관하게 협의회가 시행사에 확인·개선을 요구할 수 있는 사안이 다수 확인됩니다.",
  "가장 시급한 확인사항은 ① 구조형식(무량판 여부) 미기재, ② 근린생활시설(106동 등 인접) 업종·설비 제약 부재, ③ 커뮤니티시설 입주 초기 미운영 가능성입니다.",
  "계약조항 중 5건은 「약관의 규제에 관한 법률」 조문에 직접 저촉되는 것으로 판단되어 삭제·수정을 요구할 근거가 있습니다.",
  "대출규제는 공고일(2026.03.09) 기준 LTV만 적용(무주택 70%/유주택 60%)되며, 6억 한도·전세대출 DSR 등은 비규제지역이라 제외됩니다.",
  "에너지효율 1+등급, 전기차충전 58대(법정 의무비율 이상)는 양호한 요소로 확인되어 함께 안내드립니다.",
  "입지 조사 결과 반경 1km 내 초·중·고 6개교, 대형마트·편의점·병원 등 생활 인프라는 양호하나, 장례식장 2개소가 인근에 위치해 참고가 필요합니다.",
].forEach(t => children.push(bullet(t)));
children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: CREAM },
  spacing: { before: 120, after: 100 },
  indent: { left: 100, right: 100 },
  children: [new TextRun({ text: "계약조항 검토 결과 (총 17건)", bold: true, color: NAVY, size: 21 })],
}));
children.push(new Paragraph({
  children: [new ImageRun({ type: "png", data: fs.readFileSync("chart_risk.png"), transformation: { width: 560, height: 202 } })],
}));
children.push(figCaption("계약조항 검토 결과 분포", "본 검토보고서 자체 분석"));

// ================= 1. 대출규제 =================
children.push(...h1("01", "대출규제 안내 (공고일 2026.03.09 기준)"));
children.push(p("대출규제는 오늘 날짜가 아니라 입주자모집공고일 시점에 시행 중이던 규제가 적용되는 것이 원칙입니다."));
children.push(simpleTable([
  ["대책 항목", "적용 여부", "근거"],
  ["주담대 여신한도 차등화 (6억원 제한)", "제외", "상주시는 비수도권·비규제지역 — 수도권/규제지역 전용 규제"],
  ["스트레스 금리 상향 (1.5%→3.0%)", "제외", "비규제지역은 기존 하한 0.75%~상한 3.0% 유지"],
  ["전세대출 DSR 반영", "제외", "수도권·규제지역 1주택자 전세대출에 한정"],
  ["LTV(주택담보대출비율) 제한", "적용", "무주택(처분조건부 1주택 포함) 70%, 유주택 60%"],
], [3400, 1400, 4550], { centerCols: [1] }));
children.push(figCaption("공고일(2026.03.09) 기준 대출규제 적용 여부", "2025.10.15 주택시장 안정화 대책 원문 대조"));
children.push(commentBox("공고문 자체에는 대출규제 기준일·LTV 수치가 명시되어 있지 않고 “정부정책 변경 시 계약자 책임하에 조달”이라는 포괄조항만 있습니다. 계약 전 반드시 취급은행에 개별 대출한도를 재확인하시길 권고드립니다."));

// ================= 2. 건축 구조 =================
children.push(...h1("02", "건축·구조 — 사업계획승인 이후 기준 변화"));
children.push(labelLine("사업계획승인일", "2022.05.16 (공고문 명시)"));
children.push(labelLine("강화된 내용(승인 이후)", "무량판 구조가 '특수구조 건축물'로 지정되어 구조 심의·감리중간보고서 의무 등 안전관리가 강화됨 (건축법 시행령 개정, 2023.09.12 시행)"));
children.push(labelLine("그러나", "법령 불소급 원칙상, 승인 당시 적법하게 설계되었다면 현행 기준으로 전면 재설계를 요구할 수 없습니다."));
children.push(quoteBox("주요 구조체는 정밀구조계산에 따라 최적화 될 수 있으며, 이에 따라 내력벽은 비내력벽으로 변경될 수 있습니다. 지하주차장 구조는 공사 여건에 따라 PC 또는 데크로 변경될 수 있으며, 피트(PIT)공간의 구획, 높이 및 면적, 비내력벽의 두께 등이 변경될 수 있습니다."));
children.push(commentBox("공고문에 구조형식(벽식/무량판 등)이 명시되어 있지 않고, 오히려 '내력벽→비내력벽 변경 가능'이라는 포괄적 변경 여지만 열려 있습니다. 최근 사회적으로 안전 우려가 큰 사안인 만큼 협의회 명의로 시행사에 구조형식 및 구조계산서(또는 구조 심의결과) 공개를 요청하실 것을 권고드립니다."));

// ================= 3. 내진 =================
children.push(...h1("03", "내진설계"));
children.push(quoteBox("본 아파트는 「건축법」 제48조 제3항 및 제48조의3 제2항에 따른 내진성능 확보 여부와 내진 능력 공개에 의거 메르칼리 진도 등급을 기준으로 내진능력을 공개합니다. 내진중요도 I등급, Ⅶ등급"));
children.push(labelLine("강화된 내용(승인 이후)", "국토교통부가 내진설계 일반기준(KDS 17 10 00)을 2024.03.21 개정 — 주로 기계설비 내진 보완이 중심이며, 구조체 자체 기준의 전면 강화 여부는 추가 확인이 필요합니다."));
children.push(commentBox("내진설계는 구조 전문분야로 정확한 적정성 판단에는 구조기술사 자문이 필요합니다. 협의회 차원에서 '내진성능 확인서' 및 설계 당시 적용 기준(KDS 버전)을 시행사에 요청하실 것을 권고드립니다."));

// ================= 4. 층간소음 =================
children.push(...h1("04", "층간소음·바닥충격음 차단성능"));
children.push(quoteBox("1. 경량충격음 차단성능 ★★★★   2. 중량충격음 차단성능 ★★★"));
children.push(labelLine("정책 변화", "2023.12.12 국토부 '기준 미달 시 준공 불허'로 층간소음 정책 패러다임 전환. 다만 기존 승인단지는 준공 불허 대상에서 제외되고 바닥방음 보강지원 사업으로 대응합니다."));
children.push(labelLine("우리 단지 해당여부", "사업계획승인일(2022.05.16)이 정책 발표(2023.12.12)보다 앞서므로, 강화된 기준의 법적 강제 대상은 아닙니다."));
children.push(commentBox("법적 강제 대상이 아니라는 점은 명확하나, 중량충격음 ★★★(4단계 중 낮은 편)은 입주 후 층간소음 민원의 실질적 원인이 될 수 있습니다. ① 정확한 성적서(dB 수치) 공개, ② 차음재 성능 상향시공 요청, ③ 바닥방음 보강지원 사업 활용 가능성 확인을 권고드립니다."));

// ================= 5. 소방 =================
children.push(...h1("05", "소방시설"));
children.push(quoteBox("최초 사업계획승인일이 2022년 5월 16일로 소방내진설계가 적용됩니다. 스프링클러 배관 관경 및 기준 개수 등 소화 시설물의 기준은 수리계산에 의해 설계도면과 다르게 시공될 수 있습니다."));
children.push(labelLine("강화된 내용(승인 이후)", "연립·다세대주택 간이스프링클러 설치 의무 확대 (2024.12.01 시행) — 연립·다세대 대상이며, 아파트인 상주자이르네의 직접 해당 여부는 추가 확인 필요."));
children.push(commentBox("ESS 화재안전기준 강화 등 최신 소방 이슈는 확정적 근거자료를 확보하지 못했습니다. 협의회 명의로 소방시설 완비증명서 및 화재안전기준 적용판을 시행사에 정식 요청하실 것을 권고드리며, 저희도 추가로 확인하겠습니다."));

// ================= 6. 전기차 =================
children.push(...h1("06", "전기차 충전시설"));
children.push(quoteBox("전기차 충전시스템은 총 58개(급속 2대, 완속 56대)설치되며, 주차장의 위치 및 구조에 따라 배치 위치는 달라질 수 있습니다."));
children.push(labelLine("법정 기준", "2022.01.28 시행 개정법상 신축 아파트(100세대 이상)는 총 주차대수의 5% 이상 설치 의무. 총 820세대 기준 최소 41대 이상 필요."));
children.push(commentBox("58대는 법정 의무비율(약 7.1%)을 상회하는 양호한 수준입니다. 다만 배치 위치가 유동적이므로 준공 시 실제 위치를 확인하시길 권고드립니다."));

// ================= 7. 에너지 =================
children.push(...h1("07", "에너지절약설계"));
children.push(quoteBox("건축물 에너지효율등급 예비인증서 인증등급 1+등급 / 단열조치 준수(가목) 적용 「건축물의 에너지절약설계기준」 제6조제1호에 의한 단열조치"));
children.push(commentBox("에너지효율 1+등급은 상위권에 해당하며 관리비 절감에 실질적으로 도움이 되는 긍정적 요소입니다. 준공 시 본인증 등급이 예비인증과 동일한지만 확인하시면 됩니다."));

// ================= 8. 입지·생활 인프라 =================
children.push(...h1("08", "입지·생활 인프라"));
children.push(h2("8-1. 주변 편의시설 (카카오맵 기준, 반경 1km)"));
children.push(simpleTable([
  ["구분", "개소", "대표 시설 (최단거리)"],
  ["대형마트", "1", "함창농협 하나로마트 (818m)"],
  ["편의점", "4", "GS25 상주함창LH점 (272m)"],
  ["어린이집/유치원", "3", "함창가온어린이집 (223m)"],
  ["병원", "7", "함창치과의원 (599m)"],
  ["약국", "4", "중앙약국 (690m)"],
], [2000, 1000, 6350], { centerCols: [1] }));
children.push(figCaption("반경 1km 내 생활 편의시설", "카카오맵 로컬 API (2026.07.16 조회)"));
children.push(commentBox("장례식장 2개소(삼성장례컨설팅 729m, 중앙장례식장 955m)가 반경 1km 내 확인됩니다. 법적 하자는 아니나 실거주 관점에서 참고하실 사항으로 안내드립니다."));

children.push(h2("8-2. 학군"));
children.push(p("NEIS(교육정보 개방포털) 공식 확인 결과 및 카카오맵 인접 학교입니다. 학업성취도·서열 데이터는 정책상 공식 비공개이며, 아래는 위치·학교급 등 객관적 사실만 포함합니다."));
children.push(simpleTable([
  ["학교급", "학교명", "비고"],
  ["초등학교", "함창초등학교 / 함창중앙초등학교", "NEIS 공식 확인"],
  ["중학교", "함창중학교 / 상지여자중학교", "NEIS 공식 확인 / 카카오맵 394m"],
  ["고등학교", "함창고등학교 / 상지미래경영고등학교", "NEIS 공식 확인 / 카카오맵 399m"],
], [1600, 4600, 3150], { centerCols: [] }));
children.push(figCaption("함창읍 소재 초·중·고 현황", "NEIS 교육정보 개방포털 + 카카오맵"));

children.push(h2("8-3. 인근 시세 (국토부 실거래가, 2026.01~06 함창읍)"));
children.push(simpleTable([
  ["단지명", "준공연도", "전용면적", "거래가"],
  ["상주함창엘에이치천년나무2단지", "2016", "67.86㎡", "2.8억~2.9억"],
  ["상주함창엘에이치천년나무2단지", "2016", "74.94㎡", "2.6억"],
  ["녹원", "1993", "84.29㎡", "0.73억"],
], [3600, 1400, 1900, 2450], { centerCols: [1, 2, 3] }));
children.push(figCaption("함창읍 아파트 실거래 현황", "국토교통부 실거래가 공개시스템"));
children.push(commentBox("함창읍 내 가장 최근 준공 단지(2016년 천년나무2단지)와 비교 시, 신축·평면·커뮤니티 시설 수준을 감안한 분양가 적정성 판단에 참고하실 수 있습니다. 정확한 감정은 공인중개사·감정평가사 자문을 권고드립니다."));

children.push(h2("8-4. 커뮤니티시설 운영시기"));
children.push(quoteBox("CLUB XIAN은 입주지정기간 경과 후 관리주체에서 운영하게 되며... 커뮤니티센터에는 운동기구가 설치되나, 운동기구는 준공 후 입주지정기간이 종료된 이후 설치 될 수도 있음을 알려드립니다."));
children.push(commentBox("피트니스·골프연습장·사우나 등 CLUB XIAN 시설은 입주와 동시 운영이 아니라 '입주지정기간 경과 후' 순차 운영되며, 운동기구 자체도 추후 설치될 수 있습니다. 입주 전 정확한 개장 일정을 서면으로 사전 공지하도록 요청하실 것을 권고드립니다."));

children.push(h2("8-5. 근린생활시설(상가) 인접동 이슈"));
children.push(quoteBox("101동, 102동, 106동 지상1층에 인접하여 설치되는 작은도서관, 피트니스/골프연습장, 근린생활시설의 시설 유지보수 등으로 인한 2층 및 저층부 일부세대는 사생활 침해 등 생활의 불편이 발생할 수 있습니다."));
children.push(quoteBox("106동 인근에 근린생활시설 부속시설물(에어컨실외기, 배기팬, 설비시설 등)이 추후 상가 입점자 공사로 인하여 설치될 수 있으며... 근린생활시설용 쓰레기 분리수거장은... 106동에 인접하여 이로 인한 냄새 및 소음, 분진이 발생할 수 있습니다."));
children.push(commentBox("106동은 근린생활시설의 실외기·배기팬·탈취설비·쓰레기분리수거장이 모두 인접해 향후 냄새·소음·분진 민원이 집중될 가능성이 높습니다. 업종 제한(특히 음식점) 협의, 106동 대상 설비 위치 사전 공유를 시행사·상가 분양주체에 요청하실 것을 권고드립니다."));

// ================= 9. 계약조항 =================
children.push(...h1("09", "계약조항 핵심 유의사항"));
children.push(p("공고문 조항을 「약관의 규제에 관한 법률」·「공동주택관리법」 원문과 대조한 결과입니다."));

const highRisk = [
  { text: "아파트 현장여건(지질상태, 주변 민원 등)에 따라 공사공법이 변경될 수 있으며... 관계법령에서 정하는 경미한 설계변경은 계약자의 동의가 있는 것으로 간주하여 계약자의 동의없이 사업주체가 인·허가를 통해 진행할 수 있습니다.",
    reason: "설계변경 동의 간주 — 통보·동의 절차 없이 임의 인허가 진행 가능",
    law: "약관의 규제에 관한 법률 제10조제1호, 제12조제1호",
    comment: "'경미한 설계변경'의 범위가 불명확한 채로 동의를 간주하는 것은 무효 소지가 큽니다. 구체적 기준과 중대 변경 시 사전 통지·동의 절차 신설을 요구하실 것을 권고드립니다." },
  { text: "입주예정일은... 지연될 수 있으며, 이 경우 입주 지연에 따른 이의를 제기할 수 없으며, 지체상금은 발생하지 않습니다.",
    reason: "지체상금 면제 + 이의제기 금지",
    law: "약관의 규제에 관한 법률 제7조제2호",
    comment: "사업주체 귀책사유로 인한 지연에 대해서까지 지체상금을 면제하는 것은 무효 소지가 있습니다. 귀책사유가 사업주체에 있는 경우 지체상금 지급 조항 신설을 요구하실 것을 권고드립니다." },
  { text: "본 아파트의 판매시점에 따라 향후 분양조건의 차이가 있을 수 있으며, 이에 이의를 제기하실 수 없습니다.",
    reason: "분양조건 차이 이의제기 금지",
    law: "약관의 규제에 관한 법률 제11조제1호, 제14조제1호",
    comment: "동일 사유가 대량 발생할 경우를 대비해 협의회 차원의 대표 문제제기 창구를 미리 확보해 두실 것을 권고드립니다." },
  { text: "견본주택에서 확인이 곤란한 공용부문의 시설물(공용계단, 지하주차장, 엘리베이터의 용량·속도·탑승위치 등)은... 최종 주택건설사업계획승인 도면에 준하며, 이로 인해 사업주체 또는 시공사에게 이의를 제기할 수 없습니다.",
    reason: "공용시설 임의변경 + 이의제기 금지",
    law: "약관의 규제에 관한 법률 제10조제1호, 제14조제1호",
    comment: "최종 사업계획승인 도면의 사전 공개를 요청하시고, 최초 고지 사양 대비 중대한 하향 변경 시 통지 의무 신설을 요구하실 것을 권고드립니다." },
  { text: "발코니 확장 세대의 상부세대가 비확장일 경우 상부세대의 배관 일부가 확장세대 상부에 노출되어 이로 인한 소음이 발생할 수 있으며 이로 인하여 사업주체 또는 시공사에 이의를 제기할 수 없습니다.",
    reason: "배관노출 소음 하자책임 면제",
    law: "약관의 규제에 관한 법률 제7조제3호, 공동주택관리법 제36조제1항",
    comment: "하자담보책임을 사전에 포괄 면제하는 조항은 무효 소지가 있습니다. 하자보수 대상 일률 배제 문구 삭제 및 저감시공 대안을 요구하실 것을 권고드립니다." },
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
  ["마감재/사양 변경", "품절·단종 시 '동급 이상' 대체는 표준이나, 사전 공지·동의 절차가 빠져 있어 임의 하향 시공의 여지가 있음."],
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

// ================= 10. 결론 =================
children.push(...h1("10", "결론 및 협의회 대응 로드맵"));
children.push(h2("1순위 — 즉시 서면 질의"));
["구조형식(무량판 여부) 및 구조계산서·구조 심의결과 공개 요청",
 "106동(및 101·102동 저층부) 근린생활시설 업종 제한 및 실외기·배기설비 위치 협의",
 "커뮤니티시설(CLUB XIAN 등) 정확한 개장 일정 서면 공지 요청",
 "핵심 유의조항 5건에 대한 삭제·수정 요구 공문 발송"].forEach(t => children.push(bullet(t)));
children.push(h2("2순위 — 계약 전 확인"));
["대출규제(LTV/DSR) 개별 세대 기준 취급은행 사전상담",
 "바닥충격음 성능시험 성적서(dB 수치) 공개 요청",
 "전기차충전시설 최종 배치도 확인"].forEach(t => children.push(bullet(t)));
children.push(h2("3순위 — 준공 전후 모니터링"));
["소방시설 완비증명서 및 화재안전기준 적용판 확인",
 "내진성능 확인서(구조기술사 검토) 확보",
 "에너지효율 본인증 등급이 예비인증(1+등급)과 동일한지 확인"].forEach(t => children.push(bullet(t)));

children.push(new Paragraph({ spacing: { before: 300 }, children: [
  new TextRun({ text: "본 보고서는 AI 1차 스크리닝 및 공개 행정정보 기반 검토자료로, 협의회의 대응 우선순위 결정을 돕기 위해 작성되었습니다. 구조·소방 등 전문영역은 별도 기술자문을, 법적 대응은 정식 법률자문을 권고드립니다.", italics: true, color: GRAY, size: 20 }),
] }));

// ================= Header / Footer =================
const header = new Header({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 4 } },
    children: [
      new TextRun({ text: "상주자이르네 검토보고서", size: 16, color: "999999" }),
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
  sections: [{
    properties: {},
    headers: { default: header },
    footers: { default: footer },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("상주자이르네_검토보고서_v4.docx", buf);
  console.log("done");
});
