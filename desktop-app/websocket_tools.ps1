# WebSocket Diagnostic Tools Launcher for Sentinel
# This PowerShell script provides easy access to WebSocket diagnostic tools

function Show-Menu {
    Clear-Host
    Write-Host "===== Sentinel WebSocket Diagnostic Tools =====" -ForegroundColor Cyan
    Write-Host
    Write-Host "1. Test WebSocket Connection" -ForegroundColor White
    Write-Host "2. Check WebSocket Health" -ForegroundColor White
    Write-Host "3. Monitor WebSockets in Real-time" -ForegroundColor White
    Write-Host "4. Exit" -ForegroundColor White
    Write-Host
}

function Test-WebSocket {
    Write-Host
    Write-Host "Running WebSocket test..." -ForegroundColor Yellow
    python scripts\test_websocket.py
    Write-Host
    Read-Host "Press Enter to continue"
}

function Get-WebSocketHealth {
    Write-Host
    Write-Host "Running WebSocket health check..." -ForegroundColor Yellow
    Write-Host
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "1. Basic Health Check" -ForegroundColor White
    Write-Host "2. Detailed Health Check" -ForegroundColor White
    Write-Host "3. Try to Fix Issues" -ForegroundColor White
    Write-Host
    $healthOption = Read-Host "Enter option (1-3)"
    Write-Host
    
    switch ($healthOption) {
        "1" { python scripts\check_websocket_health.py }
        "2" { python scripts\check_websocket_health.py --full }
        "3" { python scripts\check_websocket_health.py --fix }
        default { Write-Host "Invalid option" -ForegroundColor Red }
    }
    
    Write-Host
    Read-Host "Press Enter to continue"
}

function Start-WebSocketMonitor {
    Write-Host
    Write-Host "Starting WebSocket monitor..." -ForegroundColor Yellow
    Write-Host
    python scripts\monitor_websockets.py
    Write-Host
    Read-Host "Press Enter to continue"
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-4)"
    
    switch ($choice) {
        "1" { Test-WebSocket }
        "2" { Get-WebSocketHealth }
        "3" { Start-WebSocketMonitor }
        "4" { 
            Write-Host
            Write-Host "Goodbye!" -ForegroundColor Green
            exit
        }
        default { 
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Read-Host "Press Enter to continue"
        }
    }
} while ($true)
