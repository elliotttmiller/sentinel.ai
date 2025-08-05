@echo off
echo ===== Sentinel WebSocket Fix =====
echo.

:: Check if Python is available
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.6 or higher.
    echo.
    pause
    exit /b 1
)

echo Applying WebSocket serialization fixes...
echo.

:: Run the fix script
python scripts\apply_websocket_fix.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Fix application failed. See errors above.
    pause
    exit /b 1
)

echo.
echo Fix applied successfully! Please restart your Sentinel servers.
echo.
pause
