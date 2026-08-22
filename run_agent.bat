@echo off
call .venv\Scripts\activate 2>nul
echo =======================================================
echo       STARTING SENTINEL-X ENDPOINT SECURITY AGENT      
echo =======================================================
python server\server.py
