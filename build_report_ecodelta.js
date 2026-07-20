const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign, ImageRun, PageBreak,
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
    children: [new TextRun({ text: `"${text}"`, italics: true, color: GRAY, size: 20 })],
    shading: { type: ShadingType.CLEAR, fill: LIGHTGRAY },
    border: { left: { style: BorderStyle.SINGLE, size: 16, color: "999999", space: 8 } },
    indent: { left: 100 },
    spacing: { before: 100, after: 100 },
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
    children: [new TextRun({ text: "에코델타시티 푸르지오 트레파크", bold: true, size: 46, color: NAVY })] }),
  new Paragraph({ spacing: { after: 240 },
    children: [new TextRun({ text: "상세 검토보고서", bold: true, size: 46, color: NAVY })] }),
  new Paragraph({ spacing: { after: 300 },
    children: [new TextRun({ text: "독소조항 · 동별유의사항 · 단지주변조사", size: 24, color: GRAY }),
               new TextRun({ text: "  |  공공 API 데이터 대조", size: 24, color: GRAY, italics: true })] }),
  simpleTable([
    ["대상 단지", "에코델타시티 푸르지오 트레파크 (2025000038, 공고일 2025.08.22 / 사업계획승인일 미확인)"],
    ["소재지", "부산광역시 강서구 강동동 일원(에코델타시티 11BL)"],
    ["견본주택", "부산광역시 강서구 명지동 3237-9"],
    ["작성", "법무법인제이엘"],
    ["배포 대상", "에코델타시티 푸르지오 트레파크 입주예정자협의회"],
    ["작성일", "2026.07.20"],
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
      text: "본 보고서는 법무법인제이엘이 입주자모집공고문 원문, 관계법령 원문, 공공데이터를 직접 대조하여 작성한 검토자료입니다.",
      size: 19,
    })],
  })
);

// ================= 한눈에 보기 =================
children.push(...h1("", "한눈에 보기"));
[
  "독소조항 6건: 설계변경 동의간주, 지체상금 면제, 옵션 임의대체, 대출불가 계약해제금지, 조경수 고사 면책, 공용부 점용면책 — 모두 약관법 저촉 소지.",
  "동별유의사항 18건: 101~113동, T1~T4동 차별 적용 — 문주·부대시설·근생시설·공용부 소음·조망·사생활 침해 다수.",
  "커뮤니티시설 밀도 높음: 스카이 게스트하우스(101/102동 25~27층), 스카이 라운지(102/103동 34~36층), 스카이 파티룸(103/104동 14~16층), 야외수영장(103동 1층) 등.",
  "대출규제 2025.08.22 기준: 부산 비규제지역 → LTV만 적용(무주택 70%/유주택 60%), 스트레스DSR 3단계는 지방 0.75% 유예.",
  "분양보증 정상, 에너지효율 1+++등급 확인.",
].forEach(t => children.push(bullet(t)));

children.push(new Paragraph({
  shading: { type: ShadingType.CLEAR, fill: CREAM }, spacing: { before: 120, after: 100 },
  indent: { left: 100, right: 100 },
  children: [new TextRun({ text: "계약조항 검토 결과 (총 24건)", bold: true, color: NAVY, size: 21 })],
}));

children.push(new Paragraph({
  children: [new ImageRun({ type: "png", data: fs.readFileSync("chart_risk_ecodelta.png"), transformation: { width: 560, height: 202 } })],
}));
children.push(figCaption("계약조항 검토 결과 분포", "본 검토보고서 자체 분석"));

// ================= 동별 유의사항 매트릭스 =================
children.push(h2("동별 유의사항 요약 (상세는 3부)"));
children.push(simpleTable([
  ["대상", "주요 유의사항", "유형"],
  ["101~105동, T1~T4동 1~3층", "문주로 인한 조망/일조/소음/사생활 침해", "조망|일조|소음|사생활"],
  ["101/102동 25~27층", "스카이 게스트하우스 소음/사생활", "소음|사생활"],
  ["102/103동 34~36층", "스카이 라운지 소음/사생활", "소음|사생활"],
  ["103/104동 14~16층", "스카이 파티룸 소음/사생활", "소음|사생활"],
  ["103동 1층", "야외수영장 소음/사생활", "소음|사생활"],
  ["105~110동 지하1~2층", "피트니스·사우나·게스트하우스·도서관·노래방 소음/사생활", "소음|사생활"],
  ["108동 1층/지하1층", "어린이집·맘스스테이션 소음/사생활", "소음|사생활"],
  ["근생시설 인접(T1/T2/111/112동)", "근린생활시설 소음/악취", "소음|기타"],
], [2000, 5200, 2150], { cellSize: 18 }));

// ================= 1부. 대출규제 =================
children.push(...h1("1부", "대출규제 안내 (공고일 2025.08.22 기준)"));
children.push(simpleTable([
  ["항목", "부산(비규제지역)", "근거"],
  ["LTV", "무주택 70%, 유주택 60%", "2025.10.15 대책"],
  ["스트레스DSR 3단계", "0.75% 유예(2025년 말까지)", "2025.07.01 시행, 지방유예"],
  ["6억 한도", "비적용", "수도권·규제지역 전용"],
  ["전세DSR", "비적용", "비규제지역 제외"],
], [2400, 4600, 2350]));
children.push(commentBox("공고문에 대출규제 기준 명시 부재. 계약 전 취급은행 사전상담 필수."));

// ================= 2부. 독소조항 =================
children.push(...h1("2부", "독소조항 — 약관의 규제에 관한 법률 저촉 소지"));

const toxic = [
  { cat: "설계변경", text: "경미한 설계변경은 동의 간주하고 사업주체가 인허가를 진행함", fix: "통보·동의 절차 신설 요청" },
  { cat: "시공", text: "천재지변·파업 등 불가항력 사유 시 지체상금 미발생, 이의제기 불허", fix: "건설사 통제범위 파업은 제외, 사업주체 귀책사유 명시 요청" },
  { cat: "마감재", text: "옵션 자재 임의 대체 시공 가능, 해약/교체 불가", fix: "품질 하향 시 예외 인정 요청" },
  { cat: "계약해제", text: "대출 불가 시 계약해제 불허, 판촉조건 포기 강제", fix: "정부 규제에 따른 대출불가는 해제사유 인정 요청" },
  { cat: "조경", text: "수목 결속재(철사/고무바) 미제거 상태 유지 가능, 이의제기 불허", fix: "준공 후 1년 내 결속재 제거 조건 신설 요청" },
  { cat: "공용시설", text: "부대복리시설을 사업주체 사무실·창고로 점용 가능, 이의제기 불허", fix: "입주자 사용 개시 일정 명시 요청" },
];

toxic.forEach((t, i) => {
  children.push(h2(`${i+1}. ${t.cat}`, RED));
  children.push(quoteBox(t.text));
  children.push(commentBox(`개선요청: ${t.fix}`));
});

// ================= 3부. 동별 유의사항 (상세) =================
children.push(...h1("3부", "동별 유의사항 — 18개 항목 상세"));
children.push(p("공고문 전체 전수 스캔 결과. 배치도 확인 권장."));

const dongDetail = [
  ["101~105동, T1~T4동 1~3층", "문주로 인한 조망/일조/소음/사생활 침해", "즉시 배치도 확인"],
  ["101/102동 25~27층", "스카이 게스트하우스 설치", "운영시간 제한 협의 요청"],
  ["102/103동 34~36층", "스카이 라운지 설치", "운영시간 제한 협의 요청"],
  ["103/104동 14~16층", "스카이 파티룸 설치", "운영시간 제한 협의 요청"],
  ["103동 1층", "야외수영장 설치", "운영시간 제한 협의 요청"],
  ["105동 지하1층", "관리사무소/경로당/컨시어지", "소음 저감 요청"],
  ["106동 지하1층", "피트니스/골프연습장", "운영시간 제한 협의 요청"],
  ["107동 지하1층", "커뮤니티 운동센터/사우나", "운영시간 제한 협의 요청"],
  ["110동 지하1층", "게스트하우스", "운영시간 제한 협의 요청"],
  ["108동 1층/지하1층", "어린이집/맘스스테이션", "운영시간 제한 협의 요청"],
  ["109동 지하1~2층", "도서관/노래방/시네마룸", "운영시간 제한 협의 요청"],
  ["T1/T2/111/112동 인접", "근린생활시설(2층) 소음/악취", "업종 제한 협의 요청"],
  ["102/103/104동 14~16층", "옥외 필로티(공중정원)", "소음/사생활 침해 협의 요청"],
  ["101/104/107/108/110/113동", "어린이놀이터", "물놀이테마(103/104/110/113동 추가)"],
  ["101~106/111/112동 1층", "음식물쓰레기 옥외투입구", "악취/소음 저감 요청"],
  ["110동 인접", "근생 옥상공간이 110동과 연결", "프라이버시 침해 협의 요청"],
  ["101~105동, T1~T4동, 106동 5호라인", "집광채광루버 설치", "거실 커튼박스 폭 변경 가능성"],
  ["옥상층 전체동", "이동통신설비 안테나/중계기", "추후 이의제기 불가 명시"],
];

children.push(simpleTable(dongDetail, [2000, 4500, 3350], { cellSize: 17 }));

// ================= 4부. 확인사항 =================
children.push(...h1("4부", "기타 확인사항"));
children.push(simpleTable([
  ["항목", "내용"],
  ["분양보증", "HUG 정상 확인 — 보증서 번호, 금액, 기간 확인 완료"],
  ["에너지효율", "1+++등급 (최상위) — 준공 시 본인증 유지 여부 확인"],
  ["구조형식", "미기재 — 무량판 여부 사전 확인 권장"],
  ["내진설계", "Ⅰ등급 0.22g — 설계기준서 공개 요청"],
  ["층간소음등급", "경량★ / 중량★ (최하위) — 차음재 상향시공 협의 요청"],
  ["전기차충전", "명시 부재 — 배치계획 사전 확인 요청"],
], [2200, 7150]));

// ================= 부록 체크리스트 =================
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(...h1("부록", "검토 체크리스트"));

const checklist = [
  ["구분", "항목", "상태", "조치"],
  ["독소조항", "설계변경 동의간주", "위험", "통보·동의 절차 신설 요청"],
  ["독소조항", "지체상금 면제", "위험", "귀책사유 명시 요청"],
  ["독소조항", "옵션 임의대체", "위험", "품질 하향 예외 인정 요청"],
  ["독소조항", "대출불가 계약해제금지", "위험", "정부규제 해제사유 인정 요청"],
  ["독소조항", "조경수 고사 면책", "위험", "준공 후 1년 내 결속재 제거 요청"],
  ["독소조항", "공용부 점용면책", "위험", "개시일정 명시 요청"],
  ["동별유의", "문주(101~105/T동)", "검토", "배치도 확인 및 개선 협의"],
  ["동별유의", "스카이시설(게스트/라운지/파티룸)", "검토", "운영시간 제한 협의"],
  ["동별유의", "근생시설 소음", "검토", "업종 제한 협의"],
  ["기타", "분양보증", "확인", "정상(HUG)"],
  ["기타", "에너지효율", "확인", "1+++등급"],
  ["기타", "구조형식", "미확인", "사전 문의 필요"],
  ["기타", "층간소음", "우려", "차음재 상향 협의"],
];

children.push(simpleTable(checklist, [1200, 2500, 1400, 4250], { cellSize: 16 }));

// ================= Document =================
const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  sections: [{
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("에코델타시티_푸르지오_트레파크_검토보고서.docx", buf);
  console.log("done");
});
