# Sentinel-X Windows One-Line PowerShell Installer
$ErrorActionPreference = "Stop"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   INSTALLING SENTINEL-X SECURITY AGENT (WINDOWS)      " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Download repo if running standalone one-liner
if (-not (Test-Path "server\server.py")) {
    Write-Host "[+] Downloading Sentinel-X repository..." -ForegroundColor Yellow
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git clone https://github.com/akshatPANDE69/sentinel-x.git sentinel-x
        Set-Location sentinel-x
    } else {
        $zipUrl = "https://github.com/akshatPANDE69/sentinel-x/archive/refs/heads/main.zip"
        $zipFile = "$env:TEMP\sentinel-x.zip"
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile
        Expand-Archive -Path $zipFile -DestinationPath "$env:TEMP\sx_extract" -Force
        Move-Item -Path "$env:TEMP\sx_extract\sentinel-x-main" -Destination ".\sentinel-x" -Force
        Set-Location sentinel-x
    }
}

# 2. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Python 3 is required. Please install from https://python.org or Microsoft Store." -ForegroundColor Red
    exit 1
}

$PYTHON = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }

Write-Host "[+] Setting up Python Virtual Environment..." -ForegroundColor Green
& $PYTHON -m venv .venv
$VENV_PYTHON = ".\.venv\Scripts\python.exe"

& $VENV_PYTHON -m pip install aiohttp psutil --quiet

# 3. Compile Rust Core if Cargo is available
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Write-Host "[+] Building Rust Security Core (Release)..." -ForegroundColor Green
    Push-Location "agent\rust-core"
    cargo build --release --quiet
    Pop-Location
} else {
    Write-Host "[!] Cargo not detected. Running with native Python security orchestrator." -ForegroundColor Yellow
}

# 4. Ensure data directory
New-Item -ItemType Directory -Force -Path "data\games" | Out-Null

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "       ✅ SENTINEL-X INSTALLED SUCCESSFULLY!          " -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "To start the security agent, run:" -ForegroundColor White
Write-Host "  .\run_agent.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then open your browser to:" -ForegroundColor White
Write-Host "  http://127.0.0.1:8080/" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Ask user if they want to start immediately
$startNow = Read-Host "Would you like to start Sentinel-X right now? (Y/n)"
if ($startNow -ne "n" -and $startNow -ne "N") {
    & .\run_agent.bat
}
