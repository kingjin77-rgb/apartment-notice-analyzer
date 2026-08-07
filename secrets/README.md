# API 키 저장소

모든 외부 API 키는 여기(`secrets/.env`)에 저장한다. `.gitignore`에 `.env`가 등록돼 있어서
이 파일 자체는 **절대 GitHub에 올라가지 않는다** — 저장소는 kingjin77-rgb 계정 하에 공개적으로
접근 가능하므로, 키가 코드에 하드코딩되거나 커밋되지 않도록 항상 이 폴더의 `.env`만 사용할 것.

## 사용법
1. `secrets/.env.example`을 `secrets/.env`로 복사
2. 실제 키 값 채워넣기
3. Node 스크립트에서는 `require('dotenv').config({ path: 'secrets/.env' })`로 로드

## 중요: PC ↔ 클라우드 세션 간 동기화 안 됨
`.env`는 의도적으로 git에서 제외되기 때문에, **PC와 클라우드 세션 양쪽에 각각 따로 키를 넣어야 함.**
한쪽에만 넣으면 다른 쪽 Claude 세션은 그 키를 못 씀 — 이 저장소를 여는 모든 환경(PC 로컬, 클라우드,
다른 계정 세션 포함)에서 이 폴더에 `.env`를 각자 채워야 한다.

## 현재 등록된 키
- PEXELS_API_KEY: (미등록 — 사용자가 https://www.pexels.com/api/ 가입 후 발급)
