#!/usr/bin/env bash
set -e
echo "============================================"
echo "    Setting up AUREON OS Dev Environment    "
echo "============================================"

# Detect OS
OS="$(uname -s)"
echo "Detected Host OS: $OS"

if [ "$OS" = "Darwin" ]; then
    echo "Checking Homebrew & Dependencies for macOS..."
    command -v brew >/dev/null 2>&1 || echo "Homebrew not found. Please install from brew.sh"
    echo "Recommended: brew install cmake ninja qt6 python3"
elif [ "$OS" = "Linux" ]; then
    echo "Checking Linux packages..."
    echo "Recommended: sudo apt install build-essential cmake ninja-build qt6-base-dev libpipewire-0.3-dev"
fi

python3 -m pip install -q psutil websockets fastapi uvicorn 2>/dev/null || true
echo "Setup complete. Run 'python3 run.py' to launch AUREON OS!"
