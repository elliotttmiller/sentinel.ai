# Start two separate uvicorn servers on different ports
# This script opens two separate terminals and runs the servers from desktop-app directory

# Command for the first server (port 8001)
$server1Cmd = "python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload"

# Command for the second server (port 8002)
$server2Cmd = "python -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload"

# Start the first server in a new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", $server1Cmd -WindowStyle Normal

# Wait a moment to ensure the first terminal opens
Start-Sleep -Seconds 2

# Start the second server in another new terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", $server2Cmd -WindowStyle Normal

Write-Host "Starting two uvicorn servers from desktop-app directory..."
Write-Host "Server 1: http://localhost:8001"
Write-Host "Server 2: http://localhost:8002"
Write-Host "Both terminals should now be open with the servers running." 