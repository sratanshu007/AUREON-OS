# AUREON OS — Installation Guide

## 1. Quick Web / Desktop Shell Preview
No compilation required. Simply execute:
```bash
python3 run.py
```
This runs the lightweight desktop server and automatically loads the boot experience, login screen, and interactive desktop environment.

## 2. macOS Native App Installation
1. Install prerequisites:
   ```bash
   brew install cmake ninja qt6 python3
   ```
2. Build the bundle:
   ```bash
   ./scripts/build_macos.sh
   ```
3. Drag `build_macos/bin/AureonDesktop.app` to `/Applications`.

## 3. Linux Distribution Installation
For standalone bootable media:
1. Boot using the AUREON OS Live USB.
2. Run the installer:
   ```bash
   python3 distribution/installer/install.py
   ```
3. Follow on-screen instructions to select target partition, create user, and install bootloader.
