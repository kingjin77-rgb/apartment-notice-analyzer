@echo off
chcp 949 >nul
title 법무법인 제이엘 - 파일 정리
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0JL_파일정리.ps1"
echo.
echo   창을 닫으려면 아무 키나 누르세요.
pause >nul
