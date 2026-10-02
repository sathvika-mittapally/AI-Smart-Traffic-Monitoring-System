@echo off
TITLE AI-Based Smart Traffic Monitoring & Control Center
COLOR 0B

echo ==============================================================================
echo            AI-BASED SMART TRAFFIC MONITORING & CONTROL SYSTEM
echo                     Major Project Academic Suite
echo ==============================================================================
echo.

cd /d "D:\AI_Smart_Traffic_Monitoring_System"

echo [*] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] ERROR: Python is not found in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo [*] Checking and generating sample simulation videos...
python -c "from core.video_generator import generate_all_sample_videos; generate_all_sample_videos()"

echo [*] Starting Traffic Control Operations Server on http://localhost:5000 ...
start "" http://localhost:5000

python app.py
pause
