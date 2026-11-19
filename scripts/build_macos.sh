#!/usr/bin/env bash
set -e
echo "============================================"
echo "    Building AUREON Desktop for macOS       "
echo "============================================"

BUILD_DIR="build_macos"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DAUREON_PLATFORM=macos

cmake --build . --config Release -j$(sysctl -n hw.ncpu)

echo "Build complete. App bundle created in $BUILD_DIR/bin/AureonDesktop.app"
