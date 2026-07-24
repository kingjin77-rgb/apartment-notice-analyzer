/**
 * Discover — 이번 실행에 필요한 입력이 다 있는지 확인.
 * 사용법: node scripts/discover.js <apartment-slug>
 */
const fs = require("fs");
const path = require("path");

const slug = process.argv[2];
if (!slug) {
  console.error("사용법: node discover.js <apartment-slug>");
  process.exit(1);
}

const contentDir = path.join(__dirname, "..", "content", slug);
const contentFile = path.join(contentDir, "content.js");

const errors = [];

if (!fs.existsSync(contentDir)) {
  errors.push(`content 디렉토리 없음: ${contentDir}`);
} else if (!fs.existsSync(contentFile)) {
  errors.push(`content.js 없음: ${contentFile}`);
}

if (errors.length) {
  console.error("DISCOVER 실패:");
  errors.forEach(e => console.error("  - " + e));
  process.exit(1);
}

// content.js 로드해서 이미지 참조 파일들이 실제로 존재하는지 확인
const content = require(contentFile);
const missingAssets = [];

// content.js는 자신의 __dirname 기준으로 항상 절대경로를 만들어 넘긴다 (README 참고).
function walkBlocks(blocks) {
  for (const b of blocks) {
    if (b.type === "image" && !fs.existsSync(b.path)) {
      missingAssets.push(b.path);
    }
  }
}
for (const section of content.sections) {
  walkBlocks(section.blocks);
}

if (missingAssets.length) {
  console.error("DISCOVER 실패 — 참조된 이미지 파일이 없음:");
  missingAssets.forEach(p => console.error("  - " + p));
  process.exit(1);
}

console.log(`DISCOVER 통과: ${slug} (섹션 ${content.sections.length}개, 이미지 참조 검증 완료)`);
