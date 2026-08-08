/** 안양 에버포레 자연&e편한세상 통합본 — content_v2 (v2 엔진 스모크 겸 참조 예시)
 * 데이터는 A1/A2 기존 content.js를 재사용하고, 루프1·2회차 분석 산출물(증거카드·차트·가산비)을 연결한다.
 * 신규 단지는 이 파일을 참조 예시로 삼아 작성 (ANALYSIS_PLAYBOOK.md 5단계).
 */
const path = require("path");
const A1 = require("../anyang-everforest-a1bl/content.js");
const A2 = require("../anyang-everforest-a2bl/content.js");
const ASSETS = path.join(__dirname, "..", "anyang-everforest-a1bl", "assets");
const A2ASSETS = path.join(__dirname, "..", "anyang-everforest-a2bl", "assets");

const a1tox = A1.sections[1].blocks.filter(b => b.type === "toxicItem");
const a2tox = A2.sections[1].blocks.filter(b => b.type === "toxicItem");
// 루프1회차 증거카드를 해당 항목에 연결 (03 중계장치, 04 부대복리시설)
for (const b of a1tox) {
  if (b.index === 3) b.evidenceImage = path.join(ASSETS, "evidence_relay.png");
  if (b.index === 4) b.evidenceImage = path.join(ASSETS, "evidence_facility.png");
}

module.exports = {
  title: "안양 에버포레 자연&e편한세상",
  subtitle: "입주자모집공고 검토보고서  |  A1BL·A2BL 통합본",
  typeVerdict: {
    name: "공공분양(민간참여형) — 민간참여 공공주택사업 내 민영·국민주택",
    confidence: "high",
    evidence: "「공공주택 특별법」·\"민간참여 공공주택\"·공공시행자(GH) 문구 (project_classifier 실측)",
  },
  coverTable: [
    ["공급위치", "경기도 안양시 동안구 관양동 521번지 일원 (안양 관양고 주변 도시개발사업 내)"],
    ["사업방식", "「공공주택 특별법」 및 민간참여 공공주택사업 시행지침에 따른 민간참여 공공주택사업"],
    ["사업주체", "공공시행자 경기주택도시공사 / 민간참여사업자 디엘이앤씨㈜·㈜태영건설·금호건설㈜·신동아종합건설㈜"],
    ["공급규모", "A1BL 민영주택(연립) 4개동 60세대  ·  A2BL 국민주택 5개동 344세대  —  총 404세대"],
    ["작성", "법무법인 제이엘 분양공고문 분석팀"],
  ],
  disclaimer: "본 보고서는 입주자모집공고 원문을 직접 전수 대조하여 작성되었습니다. 세부사항은 계약 전 반드시 사업주체 및 견본주택에서 재확인하시기 바랍니다.",
  pages: [
    { type: "summaryTable", title: "최우선 개선요구사항 요약  |  통합 (A1BL·A2BL)",
      headers: ["항목", "블록", "평가", "핵심 근거"], widths: [26, 7, 7, 60], sevCol: 2,
      rows: [
        ["A1·A2 부대복리시설 공유 여부 미확정", "공통", "주의", "통합운영 여부를 입주자대표회의 구성 후 결정 — 타 블록 시설 사용 불가 가능성 원문 명시"],
        ["사업주체 GH 단독 변경 동의간주", "공통", "주의", "사용검사 신청 전 민간 4사 이탈에 자동 동의 — 하자담보 책임구조 서면 확인 필요 (38면)"],
        ["가산비 163.2억 실사양 검증 필요", "A1BL", "주의", "입면마감특화 25.9억·층고증가 5.1억·문주특화 1.2억 등 계상↔실사양 대조 요구 7건"],
        ["이의제기 금지 문구 광범위 반복", "공통", "주의", "실측 A1BL 62회·A2BL 56회, 유의사항 파트 집중도 84% — 생활불편·재산가치 파트에 집중"],
        ["성능등급 인증서 저해상 게재", "공통", "주의", "구조·소음 등급이 판독 곤란한 이미지로만 게재, 내진능력 수치 부재 — 텍스트 공개 요구"],
        ["계약금 부담 수준", "공통", "양호", "계약금 10% · 중도금 60%(6회) · 잔금 30% — 표준적 구조"],
        ["분양가상한제 산정 투명성", "공통", "양호", "주택법 제57조 근거 가산비 산출내역 원문 공개 (그래서 검증이 가능함)"],
      ] },
    { type: "scoreCard", title: "블록별 종합평가  |  A1BL 민영주택 (101~104동, 60세대)", rows: A1.sections[0].blocks.find(b => b.type === "scoreCard").rows },
    { type: "scoreCard", title: "블록별 종합평가  |  A2BL 국민주택 (201~205동, 344세대)", rows: A2.sections[0].blocks.find(b => b.type === "scoreCard").rows },
    { type: "fullImage", image: path.join(ASSETS, "freq_chart.png") },
    { type: "siteCallout", title: "동별·위치별 유의사항  |  A1BL (101~104동)",
      image: path.join(ASSETS, "site_plan.png"),
      caption: "단지배치도 — 사업주체 공식 홈페이지(elife.co.kr) 게시 자료 발췌. 시설 인접관계는 입주자모집공고 원문 기재 기준.",
      items: [
        ["101동", "지하1층 부대복리시설(라운지카페·도담누리터) 직접 인접 — 진동·소음 명시 고지. 재활용 보관소 101·102동 사이", "C0392B"],
        ["102동", "문주(102·103동 사이) 인접 — 차량 소음·빛 산란·시야 차단 고지. 재활용 보관소 101·102동 사이", "C77700"],
        ["103동", "지하1층 커뮤니티센터·멀티룸, 지상1층 스터디라운지 인접 — 소음·사생활 침해 고지. 재활용 보관소 103·104동 사이", "C0392B"],
        ["104동", "재활용 보관소(103·104동 사이) 인접 — 수거차량 소음·분진·냄새 고지(원문 명시)", "C77700"],
      ] },
    { type: "siteCallout", title: "동별·위치별 유의사항  |  A2BL (201~205동)",
      image: path.join(A2ASSETS, "site_plan.png"),
      caption: "단지배치도 — 사업주체 공식 홈페이지(elife.co.kr) 게시 자료 발췌. 시설 인접관계는 입주자모집공고 원문 기재 기준.",
      items: A2.sections[2].blocks.find(b => b.type === "table").rows.slice(1).map((r, i) =>
        [r[0], String(r[1]), ["C0392B", "C77700", "C0392B", "C77700", "C0392B"][i % 5]]) },
    { type: "toxicPair", title: "계약 전 확인·개선요청 사항  |  A1BL", items: a1tox },
    { type: "toxicPair", title: "계약 전 확인·개선요청 사항  |  A2BL", items: a2tox },
    { type: "fullImage", image: path.join(ASSETS, "premium_audit.png") },
    { type: "fullImage", image: path.join(ASSETS, "contractor_risk.png") },
    { type: "recommendations", title: "종합 — 입주예정자협의회 개선요청 권고",
      items: [
        ["1", "블록 간 시설 공유", "A1·A2 부대복리시설 통합운영에 대한 사업주체의 현재 계획(안)을 계약 전 서면 공개 요청"],
        ["2", "하자담보 책임구조", "사업주체 GH 단독 변경 후에도 시공 4사의 하자담보책임 존속을 계약서에 명기, 연대책임 범위·공동도급 지분 공개"],
        ["3", "가산비 실사양 검증", "입면마감특화·층고증가·문주특화 등 가산비 계상 항목의 실제 반영 명세 및 변경 시 정산 기준 공개"],
        ["4", "보증 구조", "공공시행 체계에서의 분양대금 보전 구조(HUG 여부 또는 GH 보전)와 공사이행·하자보수 보증서 사본 제공"],
        ["5", "인접 세대 보호", "부대복리시설·재활용보관소·문주 인접 동(양 블록) 계약자 대상 개별 안내 및 방음·차폐 보강 확인"],
      ] },
  ],
};
