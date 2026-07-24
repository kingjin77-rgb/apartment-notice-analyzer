/**
 * Verify — 산출물이 RULES.md를 기계적으로 지켰는지 점검.
 * 여기서 실패하면 사람이 content.js를 고치는 것으로 끝나야 한다 — 이 스크립트가
 * 스스로 문서를 고치지 않는다.
 *
 * 사용법: node scripts/verify.js <apartment-slug> <docx-path>
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const slug = process.argv[2];
const docxPath = process.argv[3];
if (!slug || !docxPath) {
  console.error("사용법: node verify.js <apartment-slug> <docx-path>");
  process.exit(1);
}

const content = require(path.join(__dirname, "..", "content", slug, "content.js"));

const FORBIDDEN_PHRASES = [
  "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9",
  "정정 안내", "정정안내", "이전 버전", "확정판", "재검증판",
  "니가", "우리끼리",
];

let failures = [];

// 1) 파일 존재 및 최소 크기
if (!fs.existsSync(docxPath)) {
  failures.push(`산출물 파일 없음: ${docxPath}`);
} else {
  const size = fs.statSync(docxPath).size;
  if (size < 5000) failures.push(`산출물이 비정상적으로 작음 (${size} bytes)`);
}

// 2) 금지어 검사 — content.js의 텍스트 블록을 훑는다 (렌더 전 소스 기준)
function collectText(blocks) {
  let out = "";
  for (const b of blocks) {
    if (typeof b.text === "string") out += b.text + "\n";
    if (b.rows) out += JSON.stringify(b.rows) + "\n";
  }
  return out;
}
let allText = content.title + "\n" + content.subtitle + "\n" + content.disclaimer + "\n";
for (const section of content.sections) {
  allText += section.title + "\n" + collectText(section.blocks);
}
for (const phrase of FORBIDDEN_PHRASES) {
  if (allText.includes(phrase)) {
    failures.push(`금지어 발견: "${phrase}" — RULES.md #5 위반`);
  }
}

// 3) 대출 섹션 검사
if (!content.includeLoanSection) {
  const loanKeywords = ["대출규제", "LTV", "DSR", "스트레스DSR"];
  for (const kw of loanKeywords) {
    if (allText.includes(kw)) {
      failures.push(`includeLoanSection=false인데 대출 관련 키워드 "${kw}" 발견 — RULES.md #10 위반`);
    }
  }
}

// 4) 부록 섹션 금지
for (const section of content.sections) {
  if (/부록/.test(section.title)) {
    failures.push(`"부록" 섹션 발견 (${section.title}) — RULES.md #6 위반`);
  }
}

// 5) 필수 섹션 존재 확인 (개선요구/독소조항 계열 최소 1개)
const sectionTitles = content.sections.map(s => s.title).join(" ");
if (!/개선요구|개선요청|개선사항/.test(sectionTitles)) {
  failures.push("개선요구사항 관련 섹션이 없음 — RULES.md #9 위반 소지");
}

// 6) python-docx로 실제 파싱 가능한지 (파일 손상 여부)
try {
  execSync(`python -c "from docx import Document; d = Document(r'${docxPath}'); print(len(d.paragraphs), len(d.tables))"`, { stdio: "pipe" });
} catch (e) {
  failures.push(`python-docx 파싱 실패 (파일 손상 가능성): ${e.message}`);
}

if (failures.length) {
  console.error(`VERIFY 실패 (${failures.length}건):`);
  failures.forEach(f => console.error("  ✗ " + f));
  process.exit(1);
}

console.log("VERIFY 통과: 모든 규칙 충족");
