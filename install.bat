@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo    INSTALLING SENTINEL-X SECURITY AGENT (WINDOWS)      
echo =======================================================

if not exist server\server.py (
    echo [+] Cloning Sentinel-X repository...
    git clone https://github.com/akshatPANDE69/sentinel-x.git sentinel-x
    cd sentinel-x
)

echo [+] Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [-] Python 3 is required. Please install from https://python.org
    pause
    exit /b 1
)

echo [+] Setting up Python virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install aiohttp psutil --quiet

echo [+] Checking Rust compiler...
cargo --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [+] Compiling Rust Security Core...
    cd agent\rust-core
    cargo build --release --quiet
    cd ..\..
) else (
    echo [!] Cargo not found. Using native Python orchestrator.
)

if not exist data\games mkdir data\games

echo.
echo =======================================================
echo        SENTINEL-X INSTALLED SUCCESSFULLY!          
echo =======================================================
echo To start the security agent, run:
echo   run_agent.bat
echo.
echo Then open your browser to:
echo   http://127.0.0.1:8080/
echo =======================================================
echo.
pause
