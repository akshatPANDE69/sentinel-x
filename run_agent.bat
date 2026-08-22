@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
cls

echo =======================================================
echo        STARTING SENTINEL-X SECURITY AGENT              
echo =======================================================

echo [+] Checking for stale processes on port 8080...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8080 ^| findstr LISTENING') do (
    echo [+] Stopping stale server process PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo =======================================================
echo   SELECT TARGET APPLICATION / GAME TO PROTECT:
echo   [1] Sentinel-X Arena (Default Demo Target)
echo   [2] CyberStrike 2026 (Unreal Engine 5)
echo   [3] Tactical Breach 2026 (Unity Engine)
echo   [4] Custom Executable (.exe) or Emulator (Pokemon)
echo =======================================================
set /p GAME_CHOICE="Enter target game [1-4] (Default: 1): "
if "%GAME_CHOICE%"=="" set GAME_CHOICE=1

if "%GAME_CHOICE%"=="4" (
    echo.
    echo -------------------------------------------------------
    set /p CUSTOM_NAME="Enter Game / App Name (e.g. Pokemon Emerald): "
    set /p CUSTOM_PATH="Paste or type full path to .exe file: "
    echo -------------------------------------------------------
    echo [+] Registered !CUSTOM_NAME! at !CUSTOM_PATH!
)

echo.
echo [+] Target application confirmed!
echo [+] Starting Local Authoritative Server and Security Console...
echo [+] Opening http://127.0.0.1:8080/ in your default browser...

start http://127.0.0.1:8080/

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe server\server.py
) else (
    python server\server.py
)
