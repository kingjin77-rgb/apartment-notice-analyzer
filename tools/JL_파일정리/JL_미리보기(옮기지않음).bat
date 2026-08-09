@echo off
chcp 949 >nul
title 법무법인 제이엘 - 미리보기
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0JL_파일정리.ps1" -WhatIf
echo.
echo   실제로 옮기지 않고 결과만 보여드렸습니다.
pause >nul
