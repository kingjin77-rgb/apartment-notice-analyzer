/**
 * Build (슬라이드) — template + content -> 가로 16:9 제안서 PPTX.
 * 사용법: node scripts/build_slides.js <apartment-slug> <output-path>
 *
 * build.js(세로 docx)와 동일한 content/{slug}/content.js를 입력으로 쓴다.
 */
const path = require("path");
const { renderToFile } = require("../template/slide_engine.js");

const slug = process.argv[2];
const outPath = process.argv[3];
if (!slug || !outPath) {
  console.error("사용법: node build_slides.js <apartment-slug> <output-path>");
  process.exit(1);
}

const slugDir = path.join(__dirname, "..", "content", slug);
const content = require(path.join(slugDir, "content.js"));

renderToFile(content, outPath, slugDir)
  .then((p) => console.log(`SLIDES 완료: ${p}`))
  .catch((e) => { console.error("SLIDES 실패:", e); process.exit(1); });
