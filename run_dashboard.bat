@echo off
title TeraPulse LiDAR - Interactive Prototype
echo ========================================================
echo   Starting TeraPulse LiDAR Dashboard Server...
echo ========================================================
cd /d "%~dp0"

echo Opening browser at http://localhost:5000 ...
start http://localhost:5000

echo Starting Flask server on port 5000...
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe web\app.py
) else (
    python web\app.py
)
pause
