# AUREON OS — Architecture & Technical Specifications

> **Tagline:** Dream. Create. Explore.  
> **Product Type:** Cross-Platform Desktop Environment & Native Linux Distribution

---

## 1. Executive Overview

AUREON OS is designed as a unified operating-system experience combining:
- **macOS Elegance:** Refined translucent glass interfaces, fluid micro-interactions, floating dock, and universal search.
- **Windows Productivity:** Superior multitasking, advanced window snapping, powerful file management, and hardware controls.
- **Linux Freedom:** Native Wayland compositor, modular systemd/PipeWire integration, and total customizability.
- **AUREON Intelligence:** On-device local AI assistant (Ollama compatible), semantic search, and opt-in cross-device sync.

---

## 2. Layered Architecture

```
┌────────────────────────────────────────────────────────┐
│                   AUREON SHELL UI                      │
│   (Desktop, Floating Dock, MenuBar, Control Center)    │
│            Qt6 Quick / QML + HTML5 Canvas              │
├────────────────────────────────────────────────────────┤
│                   CORE SYSTEM APPS                     │
│  Files • Browser • Terminal • Settings • Store • Notes │
│  Calendar • Photos • Music • Videos • AI Assistant    │
├────────────────────────────────────────────────────────┤
│                   CORE ENGINES (C++)                   │
│  WindowManager • SearchEngine • NotificationEngine     │
│  WorkspaceManager • ThemeEngine (Tokens & Glass)       │
├────────────────────────────────────────────────────────┤
│                  SYSTEM SERVICES (Python)              │
│  system_service (8765) • ai_service • security_service │
│  sync_service • device_service • update_service        │
├────────────────────────────────────────────────────────┤
│                   PLATFORM INTEGRATION                 │
│      macOS (IOKit, CoreWLAN)  │  Linux (Wayland, D-Bus)│
└────────────────────────────────────────────────────────┘
```

---

## 3. Design Tokens & Visual Hierarchy

The default theme is strictly **Light Mode**, centered around ambient lighting, translucent frosted glass panels, and subtle shadows.

- **Primary Background:** `#EEF3FF`
- **Secondary Background:** `#F8FAFF`
- **Surface (Glass):** `rgba(255, 255, 255, 0.85)`
- **Primary Blue:** `#1677F8`
- **Electric Blue:** `#238BFF`
- **Lavender:** `#A99BFF`
- **Soft Violet:** `#8175EE`
- **Text Primary:** `#17233D`
- **Text Secondary:** `#65738D`
- **Border:** `#DCE5F5`

---

## 4. Window Management & Multitasking

AUREON includes a high-performance Window Manager:
- **Floating Glass Chrome:** Custom title bar with macOS-style traffic light controls.
- **Snap Zones:** Drag-to-snap left, right, quadrants, and full maximize.
- **Z-Order Management:** Click-to-focus and multi-window stacking.
- **Taskbar Synchronization:** Running indicators glow on the bottom dock for active windows.

---

## 5. Security Model

- **Application Sandboxing:** Declarative permissions stored in `~/.aureon/permissions.json`.
- **Zero-Cloud Leaks:** Local AI inference through Ollama is strictly on-device by default.
- **Audit Logging:** All capability requests (camera, mic, filesystem) are written to local logs.
