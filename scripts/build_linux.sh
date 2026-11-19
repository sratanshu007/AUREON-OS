#!/usr/bin/env bash
set -e
echo "============================================"
echo "    Building AUREON Desktop for Linux       "
echo "============================================"

BUILD_DIR="build_linux"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DAUREON_PLATFORM=linux \
  -DAUREON_ENABLE_WAYLAND=ON

cmake --build . -j$(nproc)

echo "Build complete. Output generated in $BUILD_DIR/bin/"
