@echo off
cd /d "%~dp0"
title JobMatch AI - ATS & Skill-Gap Analyzer
echo ========================================================
echo        Starting JobMatch AI Server on Port 8001...
echo ========================================================
echo.
set PORT=8001
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server failed to start with return code %ERRORLEVEL%.
    pause
)
