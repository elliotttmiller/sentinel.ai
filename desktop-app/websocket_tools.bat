@echo off
REM WebSocket Diagnostic Tools Launcher for Sentinel
REM This batch file provides easy access to WebSocket diagnostic tools

echo ===== Sentinel WebSocket Diagnostic Tools =====
echo.
echo 1. Test WebSocket Connection
echo 2. Check WebSocket Health
echo 3. Monitor WebSockets in Real-time
echo 4. Exit
echo.

:menu
set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto test_websocket
if "%choice%"=="2" goto check_health
if "%choice%"=="3" goto monitor
if "%choice%"=="4" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:test_websocket
echo.
echo Running WebSocket test...
python scripts\test_websocket.py
echo.
pause
goto menu

:check_health
echo.
echo Running WebSocket health check...
echo.
echo Options:
echo 1. Basic Health Check
echo 2. Detailed Health Check
echo 3. Try to Fix Issues
echo.
set /p health_option=Enter option (1-3): 
echo.

if "%health_option%"=="1" python scripts\check_websocket_health.py
if "%health_option%"=="2" python scripts\check_websocket_health.py --full
if "%health_option%"=="3" python scripts\check_websocket_health.py --fix
echo.
pause
goto menu

:monitor
echo.
echo Starting WebSocket monitor...
echo.
python scripts\monitor_websockets.py
echo.
pause
goto menu

:end
echo.
echo Goodbye!
exit /b
