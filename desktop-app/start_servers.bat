@echo off
REM Start two separate uvicorn servers on different ports
REM This script opens two separate command prompt windows and runs the servers from desktop-app directory

echo Starting two uvicorn servers from desktop-app directory...
echo Server 1: http://localhost:8001
echo Server 2: http://localhost:8002
echo.

REM Start the first server in a new command prompt window
start "Uvicorn Server 1 (Port 8001)" cmd /k "python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a moment to ensure the first window opens
timeout /t 2 /nobreak > nul

REM Start the second server in another new command prompt window
start "Uvicorn Server 2 (Port 8002)" cmd /k "python -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload"

echo Both terminals should now be open with the servers running.
pause 