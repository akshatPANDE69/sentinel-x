#!/usr/bin/env bash
set -e

echo "======================================================="
echo "   INSTALLING SENTINEL-X ZERO-TRUST SECURITY AGENT     "
echo "======================================================="

# If executed via curl | bash, clone repository into sentinel-x directory if not present
if [ ! -f "server/server.py" ]; then
    echo "Cloning Sentinel-X repository from GitHub..."
    if command -v git &> /dev/null; then
        git clone https://github.com/akshatPANDE69/sentinel-x.git sentinel-x
        cd sentinel-x
    else
        echo "Error: git is required to clone Sentinel-X."
        exit 1
    fi
fi

# Ensure Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required. Please install Python 3.10+."
    exit 1
fi

echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install aiohttp psutil --quiet

# Compile native lockless SPSC queue and SIMD scanner
if command -v clang++ &> /dev/null; then
    echo "Compiling native SPSC Queue & SIMD Vector Scanner..."
    clang++ -O3 -std=c++17 -pthread -o agent/native/spsc_benchmark agent/native/spsc_benchmark.cpp 2>/dev/null || true
    clang++ -O3 -std=c++17 -o agent/native/vector_scanner agent/native/vector_scanner.cpp 2>/dev/null || true
fi

# Generate self-signed local SSL cert for optional HTTPS
if command -v openssl &> /dev/null && [ ! -f "server/cert.pem" ]; then
    echo "Generating local SSL certificate for HTTPS..."
    openssl req -x509 -newkey rsa:2048 -keyout server/key.pem -out server/cert.pem -days 365 -nodes -subj "/CN=localhost" 2>/dev/null || true
fi

echo ""
echo "======================================================="
echo "       ✅ SENTINEL-X INSTALLED SUCCESSFULLY!          "
echo "======================================================="
echo "To start the security agent, run:"
echo "  ./run_agent.sh"
echo ""
echo "Then open your browser to:"
echo "  http://127.0.0.1:8080/   or   https://127.0.0.1:8443/"
echo "======================================================="
