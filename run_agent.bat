@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo =======================================================
echo        STARTING SENTINEL-X SECURITY AGENT              
echo =======================================================

echo [+] Checking for stale processes on port 8080...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8080 ^| findstr LISTENING') do (
    echo [+] Stopping stale server process PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

if exist agent\rust-core\target\release\sentinel-core.exe (
    echo [+] Launching Rust Security Core Daemon...
    start /B agent\rust-core\target\release\sentinel-core.exe
)

echo.
echo =======================================================
echo   SELECT TARGET APPLICATION / GAME TO PROTECT:
echo   [1] Sentinel-X Arena (Default Demo Target)
echo   [2] CyberStrike 2026 (Unreal Engine 5)
echo   [3] Tactical Breach 2026 (Unity Engine)
echo =======================================================
set /p GAME_CHOICE="Enter target game [1-3] (Default: 1): "
if "%GAME_CHOICE%"=="" set GAME_CHOICE=1

echo [+] Target application confirmed!
echo [+] Starting Local Authoritative Server and Security Console...
echo [+] Opening http://127.0.0.1:8080/ in your default browser...

if exist .venv\Scripts\python.exe (
    start http://127.0.0.1:8080/
    .venv\Scripts\python.exe server\server.py
) else (
    start http://127.0.0.1:8080/
    python server\server.py
)
