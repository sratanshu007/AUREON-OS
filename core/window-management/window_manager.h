#pragma once
#include <string>
#include <vector>
#include <memory>

namespace aureon::core {

enum class SnapZone {
    None,
    LeftHalf,
    RightHalf,
    TopLeftQuarter,
    TopRightQuarter,
    BottomLeftQuarter,
    BottomRightQuarter,
    Maximize
};

struct WindowGeometry {
    int x{100};
    int y{100};
    int width{800};
    int height{600};
};

struct WindowInfo {
    std::string id;
    std::string title;
    std::string appId;
    WindowGeometry geometry;
    bool isMinimized{false};
    bool isMaximized{false};
    bool isFocused{false};
    int workspaceId{0};
};

class WindowManager {
public:
    WindowManager();
    ~WindowManager() = default;

    std::string createWindow(const std::string& appId, const std::string& title, const WindowGeometry& geom);
    void closeWindow(const std::string& windowId);
    void minimizeWindow(const std::string& windowId);
    void maximizeWindow(const std::string& windowId);
    void focusWindow(const std::string& windowId);
    void snapWindow(const std::string& windowId, SnapZone zone);

    const std::vector<WindowInfo>& getWindows() const;
    const WindowInfo* getWindow(const std::string& windowId) const;

private:
    std::vector<WindowInfo> m_windows;
    int m_nextId{1};
};

} // namespace aureon::core
