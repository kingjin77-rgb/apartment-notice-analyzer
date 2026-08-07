/**
 * Pexels 무료 API로 표지·섹션표지용 무드샷을 받아 template/brand/stock/ 에 저장한다.
 *
 * ⚠ 이 스크립트는 실제 인터넷 접속이 되는 환경(PC 로컬 등)에서만 동작한다.
 *   클라우드 세션 샌드박스는 외부 egress가 막혀있어 여기서 실행하면 실패한다(확인됨, 2026-08-07).
 *
 * 사용법:
 *   1) secrets/.env 에 PEXELS_API_KEY=... 채워넣기 (secrets/README.md 참고)
 *   2) report_pipeline/ 에서: node scripts/fetch_stock_images.js
 *
 * 외부 패키지 의존성 없음 — Node 18+ 내장 fetch만 사용.
 */
const fs = require("fs");
const path = require("path");

/* ── .env 로더 (dotenv 미사용, 의존성 0) ─────────────────────── */
function loadEnv(envPath) {
  if (!fs.existsSync(envPath)) return {};
  const out = {};
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
    if (m && !line.trim().startsWith("#")) out[m[1]] = m[2].trim();
  }
  return out;
}
const ENV_PATH = path.join(__dirname, "..", "..", "secrets", ".env");
const env = { ...loadEnv(ENV_PATH), ...process.env };
const PEXELS_KEY = env.PEXELS_API_KEY;

/* ── 표지/섹션표지용 무드샷 카테고리 (JL 제안서 샘플 톤 기준) ─── */
const QUERIES = [
  { key: "cover_handshake", q: "business handshake office", count: 2 },
  { key: "cover_building", q: "modern glass office building exterior", count: 3 },
  { key: "cover_interior", q: "modern apartment interior living room", count: 2 },
  { key: "section_meeting", q: "office meeting presentation", count: 2 },
  { key: "section_construction", q: "construction site blueprint architect", count: 2 },
  { key: "section_document", q: "legal document signing desk", count: 2 },
  { key: "section_law", q: "law books gavel", count: 2 },
];

const OUT_DIR = path.join(__dirname, "..", "template", "brand", "stock");

async function searchAndDownload({ key, q, count }) {
  const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(q)}&per_page=${count}&orientation=landscape`;
  const res = await fetch(url, { headers: { Authorization: PEXELS_KEY } });
  if (!res.ok) throw new Error(`Pexels 검색 실패 (${key}): HTTP ${res.status}`);
  const data = await res.json();
  const photos = data.photos || [];
  if (!photos.length) { console.warn(`⚠ 결과 없음: ${key} ("${q}")`); return; }

  fs.mkdirSync(OUT_DIR, { recursive: true });
  let i = 0;
  for (const photo of photos) {
    i += 1;
    const imgUrl = photo.src.large2x || photo.src.large;
    const imgRes = await fetch(imgUrl);
    if (!imgRes.ok) { console.warn(`⚠ 다운로드 실패: ${key}_${i}`); continue; }
    const buf = Buffer.from(await imgRes.arrayBuffer());
    const outPath = path.join(OUT_DIR, `${key}_${i}.jpg`);
    fs.writeFileSync(outPath, buf);
    console.log(`✓ ${outPath} (사진작가: ${photo.photographer}, Pexels 라이선스 - 저작자표시 불요)`);
  }
}

async function main() {
  if (!PEXELS_KEY) {
    console.error("PEXELS_API_KEY가 없음 — secrets/.env 확인 (secrets/README.md 참고)");
    process.exit(1);
  }
  for (const item of QUERIES) {
    try {
      await searchAndDownload(item);
    } catch (e) {
      console.error(`✗ ${item.key} 실패:`, e.message);
    }
  }
  console.log(`\n완료. 결과: ${OUT_DIR}`);
}

main();
