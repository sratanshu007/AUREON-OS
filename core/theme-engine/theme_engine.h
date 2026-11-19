#pragma once
#include <string>

namespace aureon::core {

enum class ThemeMode {
    Light,
    Dark,
    Auto
};

class ThemeEngine {
public:
    ThemeEngine();
    void setThemeMode(ThemeMode mode);
    ThemeMode themeMode() const;

    void setAccentColor(const std::string& hexColor);
    std::string accentColor() const;

    std::string primaryBg() const;
    std::string surfaceColor() const;
    std::string textColor() const;

private:
    ThemeMode m_mode{ThemeMode::Light};
    std::string m_accent{"#1677F8"};
};

} // namespace aureon::core
