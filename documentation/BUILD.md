# AUREON OS — Build Guide

## Prerequisites

| Platform | Requirements |
|---|---|
| **macOS** | macOS 13.0+, Xcode Command Line Tools, CMake 3.25+, Qt 6.5+ |
| **Linux** | Ubuntu 22.04+ or Fedora 38+, GCC 11+ / Clang 14+, Qt6, PipeWire dev |

---

## Build Commands

### Clean Build
```bash
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)
```

### Running Tests
```bash
python3 -m unittest discover -s tests/unit
python3 -m unittest discover -s tests/integration
```
