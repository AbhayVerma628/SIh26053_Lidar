@echo off
title TeraPulse LiDAR - Server & Public Link
echo ========================================================
echo   Starting TeraPulse LiDAR Server + Public Online Link
echo ========================================================
cd /d "%~dp0"

echo 1. Starting Local Server in background...
if exist "venv\Scripts\python.exe" (
    start "Flask Server" /B venv\Scripts\python.exe web\app.py
) else (
    start "Flask Server" /B python web\app.py
)

timeout /t 3 /nobreak >nul

echo.
echo 2. Generating Public HTTPS Link via Cloudflare Tunnel...
echo Copy the *.trycloudflare.com link below and share it anywhere!
echo ========================================================
.\cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
