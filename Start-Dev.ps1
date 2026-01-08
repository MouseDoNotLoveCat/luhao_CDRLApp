# Railway Engineering Quality and Safety Supervision Issue Database Management Platform - PowerShell Startup Script

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Railway Engineering Quality and Safety Supervision Platform" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
} catch {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
} catch {
    Write-Host "[ERROR] Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js 18.0.0 or higher" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Python version:" -ForegroundColor Green
python --version
Write-Host "[OK] Node.js version:" -ForegroundColor Green
node --version
Write-Host "[OK] npm version:" -ForegroundColor Green
npm --version
Write-Host ""

# Save current directory
$ROOT_DIR = Get-Location

# Start backend service
Write-Host "[START] Starting backend service..." -ForegroundColor Yellow
Write-Host "        Backend will run on http://localhost:8000" -ForegroundColor Gray
Write-Host ""

# Check backend directory
if (-not (Test-Path "backend")) {
    Write-Host "[ERROR] Backend directory not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Skip dependency installation - already installed
Write-Host "[SKIP] Backend dependencies already installed" -ForegroundColor Green

# Start backend service in new window
$backendCommand = "cd '$ROOT_DIR'; python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal
Write-Host "[OK] Backend service starting..." -ForegroundColor Green
Write-Host ""

# Wait for backend service to start
Write-Host "Waiting 3 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start frontend development server
Write-Host "[START] Starting frontend development server..." -ForegroundColor Yellow
Write-Host "        Frontend will run on http://localhost:3000" -ForegroundColor Gray
Write-Host ""

# Check frontend directory
if (-not (Test-Path "frontend")) {
    Write-Host "[ERROR] Frontend directory not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location "frontend"

# Check dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "[INSTALL] Installing frontend dependencies..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
}

# Return to root directory
Set-Location $ROOT_DIR

# Start frontend development server in new window
$frontendCommand = "cd '$ROOT_DIR\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal
Write-Host "[OK] Frontend service starting..." -ForegroundColor Green
Write-Host ""

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  [OK] Application started!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Backend API:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Backend Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Frontend App:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Close the new windows to stop services" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit this window"

