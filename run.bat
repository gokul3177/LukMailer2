@echo off
title LukMailer - AI Job Outreach Bot
cd /d "%~dp0"

echo ============================================================
echo           LukMailer - Initializing Environment
echo ============================================================

set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;C:\Users\ADMIN\mingit\cmd;%PATH%"

python -c "import openai, pandas, openpyxl, pydantic" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [*] Launching LukMailer...
python main.py

pause
