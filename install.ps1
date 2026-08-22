# Sentinel-X Universal Zero-Dependency Windows Launcher
$ErrorActionPreference = "SilentlyContinue"

Clear-Host
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   🛡️  SENTINEL-X ZERO-TRUST GAME SECURITY PLATFORM    " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Update / Clone Repo
if (Test-Path "sentinel-x") {
    Set-Location sentinel-x
    git pull *>$null
} elseif (-not (Test-Path "server\server.py")) {
    Write-Host "[+] Fetching Sentinel-X repository..." -ForegroundColor Yellow
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git clone https://github.com/akshatPANDE69/sentinel-x.git sentinel-x *>$null
        if (Test-Path "sentinel-x") { Set-Location sentinel-x }
    } else {
        $zipUrl = "https://github.com/akshatPANDE69/sentinel-x/archive/refs/heads/main.zip"
        $zipFile = "$env:TEMP\sentinel-x.zip"
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
        Expand-Archive -Path $zipFile -DestinationPath "$env:TEMP\sx_extract" -Force
        Move-Item -Path "$env:TEMP\sx_extract\sentinel-x-main" -Destination ".\sentinel-x" -Force
        Set-Location sentinel-x
    }
}

# 2. Check Python
$PYTHON = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "" }

if (-not $PYTHON) {
    Write-Host "[-] Python 3 is required. Please install from https://python.org or Microsoft Store." -ForegroundColor Red
    exit 1
}

# 3. Clean up stale port 8080 processes
try {
    $conns = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            if ($c.OwningProcess) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }
        }
    }
} catch {}

Write-Host "[+] Starting Sentinel-X Security Agent & Web Console..." -ForegroundColor Green
Write-Host "[+] All target game selection is managed cleanly in the web dashboard!" -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8080/"

# Launch zero-dependency server directly with Python
& $PYTHON server\server.py
