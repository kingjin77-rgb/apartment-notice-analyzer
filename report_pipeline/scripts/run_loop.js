/**
 * Orchestrator — discover -> build -> verify 순서로 실행, 실패 시 즉시 중단.
 * 사용법: node scripts/run_loop.js <apartment-slug>
 */
const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

const slug = process.argv[2];
if (!slug) {
  console.error("사용법: node run_loop.js <apartment-slug>");
  process.exit(1);
}

const root = path.join(__dirname, "..");
const outPath = path.join(root, "content", slug, `${slug}.docx`);
const statePath = path.join(root, "state", "STATE.json");

function run(step, cmd) {
  console.log(`\n=== ${step} ===`);
  try {
    execSync(cmd, { stdio: "inherit", cwd: root });
  } catch (e) {
    console.error(`\n${step} 단계에서 중단됨. run_loop 종료.`);
    updateState(slug, outPath, false);
    process.exit(1);
  }
}

function updateState(slug, outPath, passed) {
  let state = { runs: [] };
  if (fs.existsSync(statePath)) {
    try { state = JSON.parse(fs.readFileSync(statePath, "utf-8")); } catch (e) {}
  }
  state.runs = state.runs || [];
  state.runs.push({
    slug,
    outPath,
    verifyPassed: passed,
    timestamp_note: "타임스탬프는 실행 환경에서 채워 넣을 것 (스크립트는 Date.now() 사용 안 함)",
  });
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2), "utf-8");
}

run("1. DISCOVER", `node scripts/discover.js ${slug}`);
run("2. BUILD", `node scripts/build.js ${slug} "${outPath}"`);
run("3. VERIFY", `node scripts/verify.js ${slug} "${outPath}"`);

updateState(slug, outPath, true);
console.log(`\n✓ run_loop 완료: ${outPath}`);
