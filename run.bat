@echo off
title LukMailer - AI Job Outreach Bot
cd /d "%~dp0"

echo ============================================================
echo           LukMailer - Initializing Environment
echo ============================================================

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;%PATH%"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts;%PATH%"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    )
)

python -c "import openai, pandas, openpyxl, pydantic" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [*] Launching LukMailer...
python main.py

pause
