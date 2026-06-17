# run-smoke-tests.ps1
# Starts the backend, runs pytest, then cleans up.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$backendDir = (Resolve-Path $backendDir).Path
$port = 18080
$backendProcess = $null

function Stop-Backend {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Write-Host "[smoke] Stopping backend (PID $($backendProcess.Id))..."
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

try {
    # 1. Start backend
    Write-Host "[smoke] Starting backend on port $port..."
    $backendProcess = Start-Process -FilePath "python" `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--port", $port `
        -WorkingDirectory $backendDir `
        -PassThru -NoNewWindow

    # 2. Wait for backend to be ready (up to 30 seconds)
    Write-Host "[smoke] Waiting for backend to be ready..."
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        if ($backendProcess.HasExited) {
            Write-Host "[smoke] ERROR: Backend process exited early with code $($backendProcess.ExitCode)."
            exit 1
        }
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/docs" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                $ready = $true
                break
            }
        } catch {
            # Not ready yet
        }
    }

    if (-not $ready) {
        Write-Host "[smoke] ERROR: Backend did not become ready within 30 seconds."
        exit 1
    }
    Write-Host "[smoke] Backend is ready."

    # 3. Run pytest
    Write-Host "[smoke] Running pytest..."
    Push-Location $backendDir
    try {
        python -m pytest tests/ -v
        $testExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    # 4. Report
    if ($testExit -eq 0) {
        Write-Host "[smoke] All tests passed."
    } else {
        Write-Host "[smoke] Some tests failed (exit code $testExit)."
    }

    exit $testExit

} finally {
    # 5. Cleanup
    Stop-Backend
}
