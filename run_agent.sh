#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "======================================================="
echo "       STARTING SENTINEL-X SECURITY AGENT              "
echo "======================================================="

# 1. Start Rust Security Core in background if built
if [ -f "agent/rust-core/target/release/sentinel-core" ]; then
    echo "[+] Launching Rust Security Core Daemon..."
    ./agent/rust-core/target/release/sentinel-core &
    RUST_PID=$!
    trap "kill $RUST_PID 2>/dev/null || true" EXIT
fi

# 2. Start Local Authoritative Server & Console
echo "[+] Starting Local Authoritative Server & Console on 127.0.0.1:8080..."
python3 server/server.py
