@echo off
chcp 65001 >nul
REM 법무법인제이엘 AI 감정평가 웹앱 — 로컬 실행기
REM Claude 없이도 동작한다. index.html·data.js는 순수 정적 파일이라
REM 지도·감정가 계산·보고서 생성이 전부 브라우저 안에서 돈다.
REM 이 파일은 그 정적 파일들을 로컬 웹서버로 띄우기만 한다(파이썬 내장 모듈).
REM Claude 계정 상태와 완전히 무관하게 동작한다.

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [오류] 이 PC에 파이썬이 설치돼 있지 않습니다.
    echo python.org 에서 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

if not exist "keys.js" (
    echo [오류] keys.js 가 없습니다. keys.example.js 를 keys.js 로 복사한 뒤
    echo        카카오·공공데이터포털 키를 채워 넣으세요.
    pause
    exit /b 1
)

echo 법무법인제이엘 AI 감정평가 — 로컬 서버를 시작합니다.
echo 브라우저가 자동으로 열립니다. 이 창을 닫으면 서버가 꺼집니다.
echo.

start "" http://localhost:8934
python -m http.server 8934
