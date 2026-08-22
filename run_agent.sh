#!/usr/bin/env bash
set -e
source .venv/bin/activate 2>/dev/null || true
echo "======================================================="
echo "      STARTING SENTINEL-X ENDPOINT SECURITY AGENT      "
echo "======================================================="
python3 server/server.py
