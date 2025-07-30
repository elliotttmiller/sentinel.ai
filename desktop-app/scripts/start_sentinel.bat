@echo off
title Sentinel Automated Startup
color 0A

echo.
echo ============================================================
echo 🚀 SENTINEL AUTOMATED STARTUP SYSTEM
echo ============================================================
echo.

cd /d "%~dp0"

echo 📁 Current directory: %CD%
echo.

echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Sentinel with automated setup...
echo.

python start_sentinel.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Sentinel startup failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sentinel startup completed!
echo.
pause 