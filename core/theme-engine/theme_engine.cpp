#include "theme_engine.h"

namespace aureon::core {

ThemeEngine::ThemeEngine() = default;

void ThemeEngine::setThemeMode(ThemeMode mode) {
    m_mode = mode;
}

ThemeMode ThemeEngine::themeMode() const {
    return m_mode;
}

void ThemeEngine::setAccentColor(const std::string& hexColor) {
    m_accent = hexColor;
}

std::string ThemeEngine::accentColor() const {
    return m_accent;
}

std::string ThemeEngine::primaryBg() const {
    return (m_mode == ThemeMode::Dark) ? "#0E1525" : "#EEF3FF";
}

std::string ThemeEngine::surfaceColor() const {
    return (m_mode == ThemeMode::Dark) ? "#18233C" : "#FFFFFF";
}

std::string ThemeEngine::textColor() const {
    return (m_mode == ThemeMode::Dark) ? "#F0F4FC" : "#17233D";
}

} // namespace aureon::core
