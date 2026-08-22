#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "==============================================================="
echo "🛡️  STARTING SENTINEL-X ZERO-TRUST GAME INTEGRITY PLATFORM..."
echo "==============================================================="

if [ ! -d ".venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip websockets aiohttp
fi

echo "[+] Launching Sentinel-X Server..."
.venv/bin/python3 server/server.py
