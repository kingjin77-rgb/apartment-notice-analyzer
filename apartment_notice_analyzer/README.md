# 아파트 모집공고문 분석 프로그램

4개 모듈 병렬 개발 구조. **실제 문서(의왕역 SK VIEW 입주자모집공고문, 64페이지)로 1차 검증 완료.**

## 실행 방법

```bash
pip install -r requirements.txt
cp .env.example .env   # 키 값 채워 넣기
streamlit run app.py
```

## 모듈별 상태 (실제 문서 검증 결과 반영)

| 모듈 | 파일 | 상태 |
|---|---|---|
| PDF 텍스트 추출 | `modules/ocr_parser.py` | **검증 완료** — PyMuPDF로 64페이지 정상 추출 (텍스트 기반 PDF) |
| 법령 조항 대조 | `modules/section_splitter.py` | 키워드 fallback은 실제 문서에서 **270건 오탐** (표준 문구 반복 때문). Claude API 연결 필수 |
| 독소조항 1차 스크리닝 | `modules/toxic_clause.py` | 키워드 fallback은 실제 문서에서 **0건 검출** — red-flag 키워드가 실제 표현과 불일치, 이 역시 Claude API 필요 |
| 동별/세대별 체크 | `modules/unit_analysis.py` (`parse_supply_price_table`) | **검증 완료** — 타입별 세대수 합계가 원본 표와 정확히 일치(3/34/66/415/50/142/110세대, 합계 820세대). 향(방위)은 이 표에 없어 평면도 이미지 분석 별도 필요. SK 계열 템플릿 기준, 타사 양식은 재검증 필요 |
| 주변환경 조사 | `modules/surrounding_environment.py` | 카카오 로컬 API 클라이언트 완료, 실키 미검증 |
| 학군조사 | `modules/school_district.py` | NEIS API 클라이언트 완료. 학업성취도/순위는 정책상 공식 미공개 |
| **사전고지 유의사항 (입예협용)** | `modules/hoa_disclosure_report.py` | **개선 완료** — 노이즈 필터(대출·청약자격 등 무관 키워드 제외), 상/중/하 심각도 분류, 법무법인 검토의견 템플릿 추가. 실제 문서 112건, 상 3건/중 59건/하 50건 |
| **대출규제 기준일 안내** | `hoa_disclosure_report.extract_loan_regulation_notice` | **신규** — 공고문 내 "OO대책 발표일 + LTV/DSR" 문구를 찾아 리포트 최상단에 강조 표시. 실제 문서에서 2025.10.15 정상 추출 |
| **주소 자동추출** | `modules/notice_metadata.py` | **신규** — 견본주택/공급위치 주소를 공고문에서 자동 추출해 주변환경·학군조사에 수동입력 없이 바로 사용 가능 |
| **종합 분석 그래프** | `modules/chart_generator.py` | **신규, 검증 완료** — matplotlib 기반. 특별공급 유형별 세대수, 특별/일반 비중, 타입별 세대수·평균분양가, 층별 분양가 추이, 유의사항 심각도 분포 등 6종. 전부 공고문 자체 데이터 기반이라 100% 정확 (외부 API 불필요) |
| **인근 실거래가 비교 (부동산지인 스타일)** | `modules/market_analysis.py` | 코드 작성 완료, **이 샌드박스에서 라이브 테스트 불가** — 국토교통부 실거래가 API가 data.go.kr 도메인이라 네트워크 정책상 차단됨. 로컬 환경에서 첫 실행 검증 필요 |
| **건축물대장 대조** | `modules/building_registry.py` | 코드 작성 완료 (건축HUB 건축물대장정보 API), **마찬가지로 이 샌드박스에서 라이브 테스트 불가**. 공고문에 적힌 층수·세대수·용도를 실제 건축물대장과 대조하는 용도 |

## 핵심 결론: 키워드 fallback은 실전에서 못 씀

더미 샘플에서는 키워드 매칭이 그럴듯하게 동작했지만, 실제 64페이지 공고문은 "변경될 수 있습니다", "위약금", "계약해제" 같은 표준 법정 문구가 수백 번 반복돼서 노이즈만 잔뜩 잡힙니다. **법령 대조·독소조항 스크리닝은 Claude API 연결이 사실상 필수**입니다. 동/호수 체크(공급금액표 파싱)는 API 없이도 정규식 상태기계로 정확히 동작 검증됨.

## 폴더 구조

```
apartment_notice_analyzer/
├── app.py
├── modules/
│   ├── ocr_parser.py              # PDF/OCR 추출
│   ├── section_splitter.py         # 조항 분류
│   ├── law_api.py                  # 국가법령정보 API
│   ├── toxic_clause.py             # 독소조항 스크리닝
│   ├── unit_analysis.py            # 공급금액표 파싱 + 평면도 Vision 분석
│   ├── surrounding_environment.py  # 카카오 로컬 API
│   ├── school_district.py          # NEIS API
│   └── report_generator.py         # docx 리포트 (5개 섹션)
├── data/
│   ├── law_mapping.json
│   ├── standard_contract_reference.json
│   └── sample_notice.txt           # 더미 (개발용)
└── .env.example
```

## 아직 안 된 것 — 입지분석·학군분석

`surrounding_environment.py`(카카오 로컬 API), `school_district.py`(NEIS API) 모듈 자체는 이미 만들어져 있고,
주소도 이제 공고문에서 자동 추출됩니다(이 문서: 경기도 의왕시 삼동 277-6번지).
**다만 실제 카카오/NEIS API 키가 없어 이 샌드박스에서 라이브 테스트는 못 했습니다.**
`.env`에 `KAKAO_REST_API_KEY`, `NEIS_API_KEY`를 채우고 `run_env`/`run_school` 체크박스를 켜면 바로 동작할 것으로 예상되나,
실제 응답 형식(카카오 검색 결과 필드명 등)은 실키로 한 번 검증이 필요합니다.

## 다음 단계

1. **`.env`에 실제 키(ANTHROPIC_API_KEY, LAW_GO_KR_OC, KAKAO_REST_API_KEY, NEIS_API_KEY) 채우고 재실행**
2. **`data/law_mapping.json`, `standard_contract_reference.json`, `JL_OPINION_TEMPLATES` 법률 검증** — 이지훈/하혜용 변호사 검토
3. **카카오/NEIS API 실키로 입지분석·학군분석 라이브 테스트**
4. **평면도 이미지 있으면** `unit_analysis.analyze_floor_plan_image()`로 향/구조 분석 테스트
5. **`parse_supply_price_table`을 다른 시공사 양식 공고문으로도 검증** — 지금은 SK 계열 템플릿 1건만 확인됨
6. **상/중/하 분류 기준, 법무법인 검토의견 문구 검수** — 지금은 초안 휴리스틱/템플릿

## 기존 JL 자산과의 연결점

- 하자담보책임기간 확장프로그램의 22개 카테고리 → `law_mapping.json` 확장에 재사용 검토
- 도면분석기(Claude Vision) → `unit_analysis.analyze_floor_plan_image()`와 동일 패턴
- Clova OCR → `ocr_parser.py`에서 등기자동화와 동일하게 재사용
