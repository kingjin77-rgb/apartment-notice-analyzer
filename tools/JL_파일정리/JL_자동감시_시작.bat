@echo off
chcp 949 >nul
title 법무법인 제이엘 - 자동 감시 (창을 닫으면 멈춥니다)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0JL_파일정리.ps1" -Watch
pause >nul
