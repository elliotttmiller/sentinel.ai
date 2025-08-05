@echo off
REM Test Real Agent Execution System - Windows Version

echo 🚀 Starting Sentinel Real Agent Execution Test
echo ==============================================

REM Navigate to the desktop-app directory
cd /d "%~dp0"

echo 📍 Current directory: %CD%

echo 🔧 Installing required dependencies...
pip install -q fastapi uvicorn loguru python-dotenv asyncio pathlib

echo 🌟 Starting FastAPI server with real agent execution...
echo 🌐 Server will be available at: http://localhost:8001
echo 📁 Mission workspaces will be created in: ./sentinel_workspace/
echo.
echo 🎯 Try these test missions:
echo    - "Create a simple website for my portfolio"
echo    - "Write a Python script to organize my files"
echo    - "Set up a new Python project called MyApp"
echo.
echo Press Ctrl+C to stop the server
echo ==============================================

REM Start the server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

pause
