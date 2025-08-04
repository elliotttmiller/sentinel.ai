# Start both servers with uvicorn --reload
Write-Host "Starting servers with uvicorn --reload..." -ForegroundColor Green

# Get current directory
$CurrentDir = Get-Location

# Start Desktop App (port 8001)
Write-Host "Starting Desktop App on port 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$CurrentDir'; uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload"

# Wait a moment
Start-Sleep -Seconds 2

# Start Cognitive Engine (port 8002)
Write-Host "Starting Cognitive Engine on port 8002..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$CurrentDir'; uvicorn src.cognitive_engine_service:app --host 0.0.0.0 --port 8002 --reload"

Write-Host "Both servers started with --reload!" -ForegroundColor Green
Write-Host "Desktop App: http://localhost:8001" -ForegroundColor Cyan
Write-Host "Cognitive Engine: http://localhost:8002" -ForegroundColor Cyan 

29935489e31e251ab182e648ff7c9905ba6a5d79 