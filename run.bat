@echo off
cd /d "%~dp0"
title JobMatch AI - ATS & Skill-Gap Analyzer
echo ========================================================
echo        Starting JobMatch AI Server (FastAPI)...
echo ========================================================
echo.
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server failed to start with return code %ERRORLEVEL%.
    pause
)
