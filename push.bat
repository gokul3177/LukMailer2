@echo off
title Push LukMailer to GitHub
cd /d "%~dp0"

set "PATH=C:\Users\ADMIN\mingit\cmd;C:\Users\ADMIN\mingit\mingw64\bin;%PATH%"

echo ============================================================
echo             Pushing LukMailer to GitHub
echo ============================================================
echo Remote repository: https://github.com/gokul3177/LukMailer2.git
echo.

git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Push failed or requires authentication.
) else (
    echo.
    echo [✓] Successfully pushed to GitHub!
)

pause
