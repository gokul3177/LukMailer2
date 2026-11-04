@echo off
title LukMailer - AI Job Outreach Bot
cd /d "%~dp0"

echo ============================================================
echo           LukMailer - Initializing Environment
echo ============================================================

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo (Make sure to check the box "Add Python to PATH" during installation)
    pause
    exit /b
)

echo [*] Checking dependencies...
pip install -r requirements.txt

echo.
echo [*] Launching LukMailer...
python main.py

pause

