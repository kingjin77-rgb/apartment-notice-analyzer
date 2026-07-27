# 모집공고문 분석 — 확장 모듈 4종

## 파일

| 순위 | 파일 | 역할 | 라이브 검증 |
|---|---|---|---|
| 1 | `environment_analysis.py` | 소음·악취·대기 (EIASS + 에어코리아) | ❌ 로컬 필요 |
| 2 | `school_analysis.py` | 학군 (NEIS + 학교알리미) | ❌ 로컬 필요 |
| 3 | `landuse_analysis.py` | 용도지역·개발계획 (V-World) | ❌ 로컬 필요 |
| 4 | `defect_precedent.py` | 하자판정기준 대조 (오프라인 DB) | ✅ 완료 |

> 이 샌드박스에서 `data.go.kr` / `schoolinfo.go.kr` / `vworld.kr` 가 차단되어
> 1~3번은 코드만 작성. 4번은 외부 호출이 없어 정규식 매칭까지 실검증 완료
> (샘플 6문장 → 7건 탐지, 상4/중3).

## 환경변수

```bash
# 보유
export MOLIT_API_KEY="..."         # data.go.kr 일반인증키 (공용)
export KAKAO_REST_API_KEY="..."
export NEIS_API_KEY="..."

# 신규 발급 필요
export SCHOOLINFO_API_KEY="..."    # schoolinfo.go.kr 소셜로그인 → 인증키 신청
export VWORLD_API_KEY="..."        # vworld.kr 오픈API (무료)
export VWORLD_DOMAIN="http://localhost"

# EIASS 활용신청 후 발급된 서비스URL 붙여넣기
export EIASS_NOISE_URL="http://apis.data.go.kr/{기관코드}/..."
export EIASS_ODOR_URL="http://apis.data.go.kr/{기관코드}/..."
```

## 첫 실행 시 반드시 확인할 것

**1번 모듈**
- EIASS 소음·악취는 기관별로 오퍼레이션명·파라미터명이 다름.
  data.go.kr 상세페이지의 **요청변수 표**를 보고
  `fetch_noise()` / `fetch_odor()` 의 `params` 딕셔너리 키를 맞출 것.
  (현재 `lat/lon/radius` 로 가정해 둠)

**2번 모듈**
- 학교알리미 `apiType` 값이 서비스마다 다름.
  schoolinfo.go.kr > OpenAPI > API 제공목록 에서 '학생수' 계열 코드 확인 후
  `SCHOOLINFO_API_TYPE` 환경변수로 지정.
- NEIS `schoolInfo` 는 시도 전체를 페이징으로 받아 반경 필터링하므로
  최초 1회 캐싱 권장 (경기도 기준 약 4,700건).

**3번 모듈**
- V-World 는 신청 시 등록한 **도메인과 요청 도메인이 일치**해야 함.
  로컬 테스트는 `http://localhost` 로 등록.
- `LT_C_UQ111`(용도지역) 속성명이 레이어 버전에 따라
  `dgm_nm` / `uname` / `prposArea1Nm` 중 하나 → `_normalize_zone()` 에서 3종 모두 시도 중.

**4번 모듈**
- `SEED_CRITERIA` 의 수치(균열 0.3mm, 층간소음 58/50dB 등)는
  국토부 고시 개정 이력이 있으므로 **현행 고시 대조 후 확정**할 것.
- adc.go.kr 판정사례를 수집해 `data/defect_precedents.json` 에 누적하면
  시드와 자동 병합됨. 스키마는 `SEED_CRITERIA` 항목과 동일.

## 리포트 통합

각 모듈이 동일한 인터페이스를 제공하므로 `report_generator.py` 에서 그대로 호출.

```python
from environment_analysis import analyze_environment, to_docx_rows as env_rows
from school_analysis      import analyze_schools,     to_docx_rows as sch_rows
from landuse_analysis     import analyze_landuse,     to_docx_rows as land_rows
from defect_precedent     import scan_clauses, to_docx_rows as def_rows, to_opinion_blocks

addr = parsed_notice.address          # 공고문 파서에서 추출한 단지 주소
text = parsed_notice.full_text

env  = analyze_environment(addr, radius_m=1000)
sch  = analyze_schools(addr, radius_m=2000)
land = analyze_landuse(addr, radius_m=500)
dfc  = scan_clauses(text, source=parsed_notice.name)

doc.add_heading("환경권 분석", 1);      add_table(doc, env_rows(env))
doc.add_heading("학군 분석", 1);        add_table(doc, sch_rows(sch))
doc.add_heading("주변 개발여건", 1);    add_table(doc, land_rows(land))
doc.add_heading("면책조항 검토", 1);    add_table(doc, def_rows(dfc))

for b in to_opinion_blocks(dfc):
    doc.add_heading(f"[{b['severity']}] {b['heading']}", 2)
    doc.add_paragraph(b['opinion'])
```

## 교차검토 로직 (모듈 간 시너지)

- **3번 × 4번**: 주변에 준주거/상업지역이 있는데(3번) 공고문에 조망 포괄면책이
  있으면(4번 `VIEW-01`) → **심각도 '상' 승격**. 고지의무 위반 주장 근거.
- **1번 × 4번**: EIASS 소음 예측치가 기준 초과인데(1번) 공고문에 소음 면책이
  있으면 → 사전 인지 상태의 면책으로 **독소조항 강도 상향**.
- **2번**: 과밀 초등학교는 하자가 아니라 **교육지원청 협의 안건**으로 별도 분리.

## 다음 단계

1. 로컬에서 1~3번 파라미터명 맞추기 (실공고문 1건으로)
2. adc.go.kr 판정사례 30~50건 수기 수집 → DB 시드 강화
3. 교차검토 로직을 `cross_check.py` 로 분리
