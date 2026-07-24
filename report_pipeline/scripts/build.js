/**
 * Build — template + content -> 최종 docx.
 * 사용법: node scripts/build.js <apartment-slug> <output-path>
 */
const path = require("path");
const { renderToFile } = require("../template/report_engine.js");

const slug = process.argv[2];
const outPath = process.argv[3];
if (!slug || !outPath) {
  console.error("사용법: node build.js <apartment-slug> <output-path>");
  process.exit(1);
}

const content = require(path.join(__dirname, "..", "content", slug, "content.js"));

renderToFile(content, outPath)
  .then((p) => console.log(`BUILD 완료: ${p}`))
  .catch((e) => { console.error("BUILD 실패:", e); process.exit(1); });
