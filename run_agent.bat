@echo off
setlocal

cd /d "%~dp0"
cls

echo =======================================================
echo   🛡️  SENTINEL-X ZERO-TRUST GAME SECURITY PLATFORM     
echo =======================================================

echo [+] Stopping stale processes on port 8080...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [+] Syncing newest version from GitHub...
git fetch origin main >nul 2>&1
git reset --hard origin/main >nul 2>&1

echo [+] Starting Security Agent Daemon & Web Console...
echo [+] Select any game/process (Roblox, Pokemon, CS2, etc.) in the dashboard!

python server\server.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Server exited.
    pause
)
