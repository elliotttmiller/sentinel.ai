# Sentinel Automated Startup Script (PowerShell)
# Run this script to start Sentinel with full automation

param(
    [switch]$Verbose,
    [switch]$SkipChecks
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = "Green"
$Host.UI.RawUI.BackgroundColor = "Black"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 SENTINEL AUTOMATED STARTUP SYSTEM" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📁 Current directory: $ScriptDir" -ForegroundColor Green
Write-Host ""

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting Sentinel with automated setup..." -ForegroundColor Yellow
Write-Host ""

# Run the Python startup script
try {
    python start_sentinel.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Sentinel startup completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Sentinel startup failed!" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error running Sentinel startup: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit" 