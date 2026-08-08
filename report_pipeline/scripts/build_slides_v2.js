#!/usr/bin/env node
/** v2 보고서 빌드 — content_v2.js(데이터) + slide_engine_v2.js(엔진)
 * 사용: node scripts/build_slides_v2.js <slug> <출력.pptx>
 * content/<slug>/content_v2.js 스키마는 slide_engine_v2.js 상단 주석 참고.
 */
const path = require("path");
const { renderToFile } = require(path.join(__dirname, "..", "template", "slide_engine_v2.js"));

const [, , slug, out] = process.argv;
if (!slug || !out) { console.error("사용: node build_slides_v2.js <slug> <출력.pptx>"); process.exit(1); }

const content = require(path.join(__dirname, "..", "content", slug, "content_v2.js"));
renderToFile(content, out).then(({ pages }) => console.log(`BUILD v2 완료: ${out} (${pages}장)`))
  .catch((e) => { console.error("빌드 실패:", e.message); process.exit(1); });
