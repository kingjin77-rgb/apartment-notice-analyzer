#!/bin/bash
# 검수 일괄 러너 (2026-08-08) — PLAYBOOK 6단계 검수게이트
# 사용: bash scripts/run_qa.sh <원문텍스트.txt> <slug> [docx경로]
set -u
TXT="$1"; SLUG="$2"; DOCX="${3:-}"
cd "$(dirname "$0")/.."
FAIL=0

echo "══ [1/3] 사업유형 판별 + 유형-보고서 정합성 ══"
python3 scripts/verify_type_consistency.py "$TXT" "$SLUG"
RC=$?
if [ $RC -eq 2 ]; then echo "→ 치명: 빌드 중단 권고"; FAIL=2;
elif [ $RC -eq 1 ]; then echo "→ 경고: 사람 확인 필요"; [ $FAIL -lt 1 ] && FAIL=1; fi

if [ -n "$DOCX" ] && [ -f "$DOCX" ]; then
  echo "══ [2/3] RULES.md 기계 검사 (verify.js) ══"
  node scripts/verify.js "$SLUG" "$DOCX" || { echo "→ 규칙 위반"; FAIL=2; }
else
  echo "══ [2/3] verify.js 건너뜀 (docx 미지정) ══"
fi

echo "══ [3/3] '미기재/누락' 주장 재검증 목록 ══"
echo "content_v2/content.js 에서 '미기재|누락|확인되지 않' 표현을 추출 — 각각 원문 재검색 2회 수행할 것(사람/에이전트):"
node -e "
try {
  let c;
  try { c = require('./content/$SLUG/content_v2.js'); } catch(e) { c = require('./content/$SLUG/content.js'); }
  const s = JSON.stringify(c);
  const hits = s.match(/[^\"]{0,40}(미기재|누락|확인되지 않)[^\"]{0,30}/g) || [];
  hits.slice(0, 12).forEach((h, i) => console.log('  ' + (i+1) + '. …' + h + '…'));
  if (!hits.length) console.log('  (해당 표현 없음)');
} catch(e) { console.log('  content 로드 실패:', e.message); }
"
echo ""
if [ $FAIL -eq 2 ]; then echo "◆ QA 결과: 실패(치명) — 납품 금지"; exit 2;
elif [ $FAIL -eq 1 ]; then echo "◆ QA 결과: 경고 — 사람 확인 후 진행"; exit 1;
else echo "◆ QA 결과: 통과"; exit 0; fi
