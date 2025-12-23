# PowerShell script to start frontend and Django backend

# Function to stop background processes
function Cleanup {
    Write-Host "Stopping servers..."
    if ($frontendProcess) { Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue }
    if ($backendProcess)  { Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue }
    exit
}

# Trap Ctrl+C (SIGINT)
$null = Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

# Start frontend
Write-Host "Starting frontend on http://localhost:3000..."
Push-Location frontend
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npx http-server -p 3000" -PassThru
Pop-Location

# Wait until frontend is ready
Write-Host "Waiting for frontend to be ready..."
while ($true) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { break }
    } catch {
        # Ignore errors while waiting
    }
    Start-Sleep -Seconds 1
}

# Open default web browser at localhost:3000
Start-Process "http://localhost:3000"

# Activate backend virtual environment and start Django
Push-Location backend
Write-Host "Activating virtual environment..."
$venvActivate = Join-Path .venv\Scripts\Activate.ps1
& $venvActivate

Write-Host "Starting Django backend on http://localhost:8000..."
$backendProcess = Start-Process -FilePath "python" -ArgumentList "manage.py runserver 8000" -PassThru
Pop-Location

# Wait for both processes to exit
Wait-Process -Id $frontendProcess.Id, $backendProcess.Id
