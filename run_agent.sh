#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "======================================================="
echo "       STARTING SENTINEL-X SECURITY AGENT              "
echo "======================================================="

# Kill stale server on port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo ""
echo "======================================================="
echo "  SELECT APPLICATION / GAME TO PROTECT:                "
echo "  [1] Sentinel-X Arena (Default Demo Target)           "
echo "  [2] CyberStrike 2026 (Unreal Engine 5)               "
echo "  [3] Tactical Breach 2026 (Unity Engine)              "
echo "  [4] Custom Executable Path (.app / .exe)             "
echo "======================================================="
read -p "Enter target game [1-4] (Default: 1): " choice
choice=${choice:-1}

if [ "$choice" = "4" ]; then
    echo "-------------------------------------------------------"
    read -p "Enter Game / App Name: " custom_name
    read -p "Paste or type full path to application binary: " custom_path
    echo "-------------------------------------------------------"
    echo "[+] Target registered: $custom_name ($custom_path)"
fi

echo "[+] Starting Local Authoritative Server & Console on 127.0.0.1:8080..."
python3 server/server.py
