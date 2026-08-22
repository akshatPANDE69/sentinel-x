@echo off
setlocal

cd /d "%~dp0"
cls

echo =======================================================
echo   🛡️  SENTINEL-X ZERO-TRUST GAME SECURITY PLATFORM     
echo =======================================================
echo [+] Starting Security Agent Daemon & Web Console...
echo [+] Select any game/process (Roblox, Pokemon, CS2, etc.) in the dashboard!

start http://127.0.0.1:8080/

python server\server.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Server exited.
    pause
)
