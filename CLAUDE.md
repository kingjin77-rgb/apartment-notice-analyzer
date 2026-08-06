# apartment-notice-analyzer — 프로젝트 지식 (LLM Wiki)

> 목적: 새 Claude 세션이 이 파일 하나만 읽으면 맥락 재설명 없이 바로 일할 수 있게 한다 (토큰 절약).
> 갱신 규칙: 작업 세션이 끝날 때마다 "변경 이력"에 한 줄 추가. 오래된 내용은 지우지 말고 취소선.

## 프로젝트 정체
- 법무법인 제이엘 분양공고문 분석기. **목표: 입주민을 위한 독소조항·개선요청 발굴.**
- 중점: 유의사항, 동별·세대별 유의점, 마감재, 내진 등 실질 항목. 지체상금·일반 재무부담 같은 저관심 항목은 헤드라인 금지 (RULES.md 7번).
- 산출물 2종: ① 세로 docx 검토보고서 ② 가로 16:9 제안서 PPTX (동일 content.js에서 생성).

## 빌드 명령 (report_pipeline/ 에서)
```
npm install                                        # 최초 1회
node scripts/build.js <slug> <출력.docx>           # 세로 보고서
node scripts/build_slides.js <slug> <출력.pptx>    # 가로 제안서 슬라이드
node scripts/verify.js <slug>                      # 규칙 검사
```
- slug 목록: paragon3-dongtan-rental / anyang-ipark-sujain / bucheon-urban-square / cheonan-elif-seongseong / gwangmyeong-hillstate11 / platinum-sky-heron
- 새 단지 추가 = content/<slug>/content.js + assets/ 생성 (엔진 파일은 절대 단지별 수정 금지)

## 디자인 (JL 제안서 스타일 — 2026-08-06 확정)
- 슬라이드: 흰 배경, 굵은 검정 제목 좌상단, 우상단 "법무법인 JL" 워드마크
- 카드 3색: 파랑 #3B82F6(핵심 검토) / 진네이비 #1E2A3B(문제 조항) / 딥그린 #1E4D3B(개선요청·표 헤더)
- 금지: 네이비 전면 표지, 색 띠/스트라이프 장식, 과도한 여백. 폰트 "맑은 고딕" 고정.
- docx 팔레트: NAVY #1F3864, GOLD #C89B3C (report_engine.js)

## 인프라·계정
- GitHub: github.com/kingjin77-rgb/apartment-notice-analyzer ← **이 저장소가 유일한 소스 저장소**
  - PC 로컬 사본: D:\DDownloads\apartment_notice_analyzer
- Claude 계정: hyunjink057 로 통일. 구글드라이브(hyunjink057): 분양공고문_원본 / 검토보고서_완성본 / 법령_원본 3개 폴더
- 완성 보고서 docx는 저장소에 두지 않는다 → 드라이브 검토보고서_완성본으로. (재생성 가능하므로 보관 불필요)
- 법령 원문 PDF → 드라이브 법령_원본. law_mapping.json 의 requires_verification 항목은 PDF 원문 대조 후에만 false 로.

## 파이프라인 구조 요점
- section_splitter.py: 문장 분할 후 law_mapping.json 6개 카테고리 키워드 필터 — **미매칭 문장이 버려지는 구조적 결함 있음 (개선 예정 1순위)**
- toxic_clause.py: RED_FLAG_PATTERNS 정규식 12종 + defect_precedent 병합 (2026-08-06 수리 완료)
- 변경공고 대조 기능 없음 — **개선 예정 2순위** (파라곤3차·광명11·천안이 변경/정정공고 단일 소스 사용 중)
- NotebookLM 연동 폐기 → 구글드라이브로 전환 (RULES.md 1번의 notebook_query 언급은 역사적 잔재)

## 변경 이력
- 2026-08-06 (클라우드 세션): toxic_clause risk_level 배선 버그 수정, red_flags 정규식화, defect_precedent 병합, fire_safety "감지기" 오탐 제거, indoor_air "입회" 오탐·단위없는 숫자 오인식 수정, slide_engine.js JL 스타일 전면 재작성(40→30장), build_slides.js 신규.
