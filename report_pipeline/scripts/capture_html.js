#!/usr/bin/env node
/** HTML 슬라이드 → 2664x1500 PNG 캡처 자동화 (2026-08-08)
 * 사용: node scripts/capture_html.js <입력.html> <출력.png>
 * 크로미움 헤드리스는 창 높이에 브라우저 UI 여백이 포함되므로 크게 찍고 상단 크롭한다.
 * 크로미움 경로: PLAYWRIGHT 프리설치(/opt/pw-browsers/chromium) → 없으면 chromium/chrome PATH 탐색.
 */
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const [, , input, output] = process.argv;
if (!input || !output) { console.error("사용: node capture_html.js <입력.html> <출력.png>"); process.exit(1); }

const candidates = ["/opt/pw-browsers/chromium", "chromium", "chromium-browser", "google-chrome"];
let chrome = null;
for (const c of candidates) {
  try { execSync(`command -v ${c}`, { stdio: "ignore" }); chrome = c; break; } catch (e) { /* 다음 후보 */ }
}
if (!chrome) { console.error("크로미움을 찾을 수 없음"); process.exit(1); }

const raw = output + ".raw.png";
const url = "file://" + path.resolve(input);
execSync(`"${chrome}" --headless --no-sandbox --disable-gpu --force-device-scale-factor=2 --window-size=1332,920 --virtual-time-budget=8000 --screenshot="${raw}" "${url}"`, { stdio: "ignore" });

// PIL 없이 node로 크롭하기엔 과하므로 python3 원라이너 사용 (환경에 PIL 상주)
execSync(`python3 -c "from PIL import Image; Image.open('${raw}').crop((0,0,2664,1500)).save('${output}')"`);
fs.unlinkSync(raw);
console.log("캡처 완료:", output);
