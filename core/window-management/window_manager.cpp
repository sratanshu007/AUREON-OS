#include "window_manager.h"
#include <algorithm>

namespace aureon::core {

WindowManager::WindowManager() = default;

std::string WindowManager::createWindow(const std::string& appId, const std::string& title, const WindowGeometry& geom) {
    std::string id = "win_" + std::to_string(m_nextId++);
    WindowInfo win;
    win.id = id;
    win.appId = appId;
    win.title = title;
    win.geometry = geom;
    win.isFocused = true;

    for (auto& w : m_windows) {
        w.isFocused = false;
    }

    m_windows.push_back(win);
    return id;
}

void WindowManager::closeWindow(const std::string& windowId) {
    m_windows.erase(std::remove_if(m_windows.begin(), m_windows.end(),
        [&windowId](const WindowInfo& w) { return w.id == windowId; }), m_windows.end());
}

void WindowManager::minimizeWindow(const std::string& windowId) {
    for (auto& w : m_windows) {
        if (w.id == windowId) {
            w.isMinimized = true;
            w.isFocused = false;
            break;
        }
    }
}

void WindowManager::maximizeWindow(const std::string& windowId) {
    for (auto& w : m_windows) {
        if (w.id == windowId) {
            w.isMaximized = !w.isMaximized;
            w.isFocused = true;
            break;
        }
    }
}

void WindowManager::focusWindow(const std::string& windowId) {
    for (auto& w : m_windows) {
        w.isFocused = (w.id == windowId);
        if (w.isFocused) {
            w.isMinimized = false;
        }
    }
}

void WindowManager::snapWindow(const std::string& windowId, SnapZone zone) {
    for (auto& w : m_windows) {
        if (w.id == windowId) {
            if (zone == SnapZone::LeftHalf) {
                w.geometry.x = 0;
                w.geometry.y = 36;
                w.geometry.width = 1280;
                w.geometry.height = 1500;
            } else if (zone == SnapZone::RightHalf) {
                w.geometry.x = 1280;
                w.geometry.y = 36;
                w.geometry.width = 1280;
                w.geometry.height = 1500;
            }
            break;
        }
    }
}

const std::vector<WindowInfo>& WindowManager::getWindows() const {
    return m_windows;
}

const WindowInfo* WindowManager::getWindow(const std::string& windowId) const {
    for (const auto& w : m_windows) {
        if (w.id == windowId) return &w;
    }
    return nullptr;
}

} // namespace aureon::core
