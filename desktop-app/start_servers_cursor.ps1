# Start uvicorn servers in the current terminal (for Cursor)
# This script runs the servers sequentially in the current terminal

Write-Host "🚀 Starting uvicorn servers in Cursor terminal..." -ForegroundColor Green
Write-Host "Server 1: http://localhost:8001" -ForegroundColor Cyan
Write-Host "Server 2: http://localhost:8002" -ForegroundColor Cyan
Write-Host ""

# Start the first server in the background
Write-Host "Starting Server 1 on port 8001..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
} -Name "Server1"

# Wait a moment
Start-Sleep -Seconds 3

# Start the second server in the background
Write-Host "Starting Server 2 on port 8002..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
} -Name "Server2"

Write-Host ""
Write-Host "✅ Both servers are now running in background jobs!" -ForegroundColor Green
Write-Host "To view server logs, use:" -ForegroundColor Cyan
Write-Host "  Receive-Job -Name 'Server1' -Keep" -ForegroundColor White
Write-Host "  Receive-Job -Name 'Server2' -Keep" -ForegroundColor White
Write-Host ""
Write-Host "To stop servers, use:" -ForegroundColor Cyan
Write-Host "  Stop-Job -Name 'Server1'" -ForegroundColor White
Write-Host "  Stop-Job -Name 'Server2'" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Red

# Keep the script running and show job status
try {
    while ($true) {
        $jobs = Get-Job -Name "Server1", "Server2"
        $running = ($jobs | Where-Object { $_.State -eq "Running" }).Count
        Write-Host "`rServers running: $running/2" -NoNewline -ForegroundColor Green
        Start-Sleep -Seconds 5
    }
} catch {
    Write-Host ""
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Name "Server1", "Server2" -ErrorAction SilentlyContinue
    Remove-Job -Name "Server1", "Server2" -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
} 