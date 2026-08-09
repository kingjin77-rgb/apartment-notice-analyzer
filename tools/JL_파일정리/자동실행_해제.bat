@echo off
chcp 949 >nul
title 법무법인 제이엘 - 자동 실행 해제
schtasks /delete /tn "JL_분양공고_파일정리" /f
echo.
echo   해제되었습니다.
pause >nul
