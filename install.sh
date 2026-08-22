#!/usr/bin/env bash
set -e
echo "======================================================="
echo "   INSTALLING SENTINEL-X ZERO-TRUST SECURITY AGENT     "
echo "======================================================="

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install aiohttp psutil

# Compile native lockless SPSC queue and SIMD scanner
if command -v clang++ &> /dev/null; then
    echo "Compiling native SPSC Queue & SIMD Vector Scanner..."
    clang++ -O3 -std=c++17 -pthread -o agent/native/spsc_benchmark agent/native/spsc_benchmark.cpp
    clang++ -O3 -std=c++17 -o agent/native/vector_scanner agent/native/vector_scanner.cpp
fi

echo ""
echo "✅ Sentinel-X Installed Successfully!"
echo "Run './run_agent.sh' to start the endpoint security agent."
