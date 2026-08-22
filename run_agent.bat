@echo off
setlocal

cd /d "%~dp0"

echo =======================================================
echo        STARTING SENTINEL-X SECURITY AGENT              
echo =======================================================

if exist agent\rust-core\target\release\sentinel-core.exe (
    echo [+] Launching Rust Security Core Daemon...
    start /B agent\rust-core\target\release\sentinel-core.exe
)

echo [+] Starting Local Authoritative Server and Security Console...
echo [+] Opening http://127.0.0.1:8080/ in your browser...

if exist .venv\Scripts\python.exe (
    start http://127.0.0.1:8080/
    .venv\Scripts\python.exe server\server.py
) else (
    start http://127.0.0.1:8080/
    python server\server.py
)
