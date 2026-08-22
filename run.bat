@echo off
setlocal
cd /d "%~dp0"

echo ===============================================================
echo [SENTINEL-X] ZERO-TRUST GAME INTEGRITY & RING 0 KERNEL PLATFORM
echo ===============================================================

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [+] Creating Python virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip websockets aiohttp
) else (
    call .venv\Scripts\activate.bat
)

echo [+] Compiling Native SIMD Vector Scanner (if MSVC/clang available)...
where clang++ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    clang++ -O3 -std=c++17 -o agent\native\vector_scanner.exe agent\native\vector_scanner.cpp >nul 2>&1
)

echo [+] Launching Sentinel-X Server on http://127.0.0.1:8080 ...
python server\server.py

pause
