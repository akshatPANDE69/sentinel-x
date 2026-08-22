# Sentinel-X Universal Zero-Dependency Windows Launcher
$ErrorActionPreference = "SilentlyContinue"

Clear-Host
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   🛡️  SENTINEL-X ZERO-TRUST GAME SECURITY PLATFORM    " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Force kill any stale python processes on port 8080 or port 8081
try {
    $conns = Get-NetTCPConnection -LocalPort 8080,8081,8082,8085 -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            if ($c.OwningProcess) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }
        }
    }
} catch {}

# Sync / Clone Repo
if (Test-Path "sentinel-x") {
    Set-Location sentinel-x
    git fetch origin main *>$null
    git reset --hard origin/main *>$null
} elseif (Test-Path ".git") {
    git fetch origin main *>$null
    git reset --hard origin/main *>$null
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

$PYTHON = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "" }

if (-not $PYTHON) {
    Write-Host "[-] Python 3 is required. Please install from https://python.org or Microsoft Store." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Starting Sentinel-X Security Agent & Web Console..." -ForegroundColor Green
Write-Host "[+] Target games (Roblox, Pokemon, CS2, etc.) are chosen directly in the dashboard!" -ForegroundColor Cyan

# Launch server
& $PYTHON server\server.py
