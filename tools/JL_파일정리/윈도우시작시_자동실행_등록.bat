@echo off
chcp 949 >nul
title 법무법인 제이엘 - 자동 실행 등록
cd /d "%~dp0"
echo.
echo   윈도우에 로그인할 때마다 자동 감시가 켜지도록 등록합니다.
echo   (해제하려면 같은 폴더의 "자동실행_해제.bat" 을 실행하세요)
echo.
schtasks /create /tn "JL_분양공고_파일정리" /tr "powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"%~dp0JL_파일정리.ps1\" -Watch" /sc onlogon /rl highest /f
echo.
if %errorlevel%==0 (echo   등록되었습니다.) else (echo   등록 실패 - 이 파일을 마우스 오른쪽 클릭 후 "관리자 권한으로 실행" 해 주세요.)
pause >nul
