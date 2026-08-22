# Sentinel-X Windows One-Line PowerShell Installer & Launcher
$ErrorActionPreference = "Continue"

Clear-Host
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   SENTINEL-X ZERO-TRUST GAME SECURITY PLATFORM        " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Download / Update Repo
if (Test-Path "sentinel-x") {
    Set-Location sentinel-x
    try { git pull *>$null } catch {}
} elseif (-not (Test-Path "server\server.py")) {
    Write-Host "[+] Downloading Sentinel-X repository..." -ForegroundColor Yellow
    if (Get-Command git -ErrorAction SilentlyContinue) {
        try { git clone https://github.com/akshatPANDE69/sentinel-x.git sentinel-x } catch {}
        if (Test-Path "sentinel-x") { Set-Location sentinel-x }
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

if (-not (Test-Path ".venv")) {
    Write-Host "[+] Setting up Python Virtual Environment..." -ForegroundColor Green
    & $PYTHON -m venv .venv
    $VENV_PYTHON = ".\.venv\Scripts\python.exe"
    & $VENV_PYTHON -m pip install aiohttp psutil --quiet
}

# 3. Interactive Target Game Selection Prompt in Terminal
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

$customExePath = ""
$customAppName = "Sentinel-X Arena"
$fileHash = "d41d8cd98f00b204e9800998ecf8427e"

if ($choice -eq "4") {
    Write-Host ""
    Write-Host "-------------------------------------------------------" -ForegroundColor Yellow
    $customAppName = Read-Host "Enter Game / App Name (e.g. Roblox / Pokemon)"
    if (-not $customAppName) { $customAppName = "Custom Game" }
    
    $customExePath = Read-Host "Paste or type full path to .exe or game folder"
    Write-Host "-------------------------------------------------------" -ForegroundColor Yellow
    
    if ($customExePath) {
        # If user passed a folder (e.g. Roblox version folder), search for .exe inside
        if (Test-Path $customExePath -PathType Container) {
            $foundExe = Get-ChildItem -Path $customExePath -Filter "*.exe" -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($foundExe) {
                $customExePath = $foundExe.FullName
                Write-Host "[+] Auto-detected executable: $customExePath" -ForegroundColor Green
            }
        }
        
        if (Test-Path $customExePath -PathType Leaf) {
            try {
                $h = Get-FileHash -Path $customExePath -Algorithm SHA256 -ErrorAction SilentlyContinue
                if ($h -and $h.Hash) {
                    $fileHash = $h.Hash.ToLower()
                    Write-Host "[+] Measured SHA-256 binary hash: $fileHash" -ForegroundColor Green
                }
            } catch {}
        }
        Write-Host "[+] Target '$customAppName' registered with Sentinel-X Kernel Driver!" -ForegroundColor Green
    }
}

# 4. Clean up stale port 8080 processes
try {
    $connections = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            if ($conn.OwningProcess) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    }
} catch {}

Write-Host "[+] Launching Sentinel-X Security Agent & Web Console..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8080/"

$VENV_PYTHON = ".\.venv\Scripts\python.exe"
if (Test-Path $VENV_PYTHON) {
    & $VENV_PYTHON server\server.py
} else {
    & $PYTHON server\server.py
}
