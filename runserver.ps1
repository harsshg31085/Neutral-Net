function Cleanup {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    if ($frontendProcess) { Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue }
    if ($backendProcess)  { Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue }
    exit
}

$null = Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

Write-Host "Starting frontend on http://localhost:3000..." -ForegroundColor Cyan
Push-Location frontend
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npx http-server -p 3000" -PassThru
Pop-Location

Write-Host "Waiting for frontend to be ready..." -ForegroundColor DarkGray
while ($true) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { break }
    } catch {

    }
    Start-Sleep -Seconds 1
}

Start-Process "http://localhost:3000"

Push-Location backend

$venvPython = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Could not find virtual environment at $venvPython. Please check folder name."
    exit
}

Write-Host "Starting Django backend on http://localhost:8000 using venv..." -ForegroundColor Green

$backendProcess = Start-Process -FilePath $venvPython -ArgumentList "manage.py runserver 8000" -PassThru -NoNewWindow

Pop-Location

Write-Host "Servers are running. Press Ctrl+C to stop." -ForegroundColor White
Wait-Process -Id $frontendProcess.Id, $backendProcess.Id