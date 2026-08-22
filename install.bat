@echo off
echo =======================================================
echo    INSTALLING SENTINEL-X ZERO-TRUST SECURITY AGENT     
echo =======================================================
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install aiohttp psutil
echo.
echo Sentinel-X Installed Successfully!
echo Run 'run_agent.bat' to start the endpoint security agent.
