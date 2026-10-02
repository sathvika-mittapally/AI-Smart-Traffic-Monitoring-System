# ==============================================================================
# AI-Based Smart Traffic Monitoring & Control System - PowerShell Launcher
# ==============================================================================

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "          AI-BASED SMART TRAFFIC MONITORING & CONTROL SYSTEM" -ForegroundColor Yellow
Write-Host "                   Major Project Academic Suite" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "D:\AI_Smart_Traffic_Monitoring_System"

Write-Host "[*] Checking Python environment..." -ForegroundColor Gray
python --version

Write-Host "[*] Launching browser and starting Flask server on http://localhost:5000 ..." -ForegroundColor Cyan
Start-Process "http://localhost:5000"

python app.py
