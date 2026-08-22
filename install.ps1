# Sentinel-X Universal Zero-Dependency Windows Launcher
$ErrorActionPreference = "SilentlyContinue"

Clear-Host
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   SENTINEL-X ZERO-TRUST GAME SECURITY PLATFORM        " -ForegroundColor Cyan
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

# 3. Interactive Target Game Selection Prompt
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   SELECT APPLICATION / GAME TO PROTECT:               " -ForegroundColor Yellow
Write-Host "   [1] 🎮 Sentinel-X Arena (Default Demo Target)       " -ForegroundColor White
Write-Host "   [2] 🎯 CyberStrike 2026 (Unreal Engine 5)           " -ForegroundColor White
Write-Host "   [3] 🛡️ Tactical Breach 2026 (Unity Engine)          " -ForegroundColor White
Write-Host "   [4] 📁 Custom Executable (.exe), Roblox, or Pokemon " -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan
$choice = Read-Host "Enter target game [1-4] (Default: 1)"
if (-not $choice) { $choice = "1" }

if ($choice -eq "4") {
    Write-Host ""
    Write-Host "-------------------------------------------------------" -ForegroundColor Yellow
    $customAppName = Read-Host "Enter Game / App Name (e.g. Roblox / Pokemon)"
    if (-not $customAppName) { $customAppName = "Custom Game" }
    $customExePath = Read-Host "Paste full path to game .exe or folder (or press Enter to auto-scan)"
    Write-Host "-------------------------------------------------------" -ForegroundColor Yellow
    Write-Host "[+] Target '$customAppName' registered with Sentinel-X!" -ForegroundColor Green
}

# 4. Clean up stale port 8080 processes
try {
    $conns = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            if ($c.OwningProcess) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }
        }
    }
} catch {}

Write-Host ""
Write-Host "[+] Starting Sentinel-X Security Agent & Web Console..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8080/"

# Launch zero-dependency server directly with Python
& $PYTHON server\server.py
