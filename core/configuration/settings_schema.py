"""
AUREON OS — Settings Schema
============================
Defines all configuration variables as Python dataclasses.
Every field has a type annotation, default value, and optional validator.
Used by SettingsManager to validate, load, migrate and persist settings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Theme(str, Enum):
    LIGHT  = "light"
    DARK   = "dark"
    AUTO   = "auto"          # follows system preference


class AccentColor(str, Enum):
    BLUE   = "blue"          # #1677F8
    VIOLET = "violet"        # #A99BFF
    TEAL   = "teal"
    GREEN  = "green"
    ROSE   = "rose"
    AMBER  = "amber"
    CUSTOM = "custom"


class DockPosition(str, Enum):
    BOTTOM = "bottom"
    LEFT   = "left"
    RIGHT  = "right"


class DockStyle(str, Enum):
    GLASS  = "glass"
    OPAQUE = "opaque"
    MINIMAL= "minimal"


class WindowAnimation(str, Enum):
    SCALE  = "scale"
    FADE   = "fade"
    SLIDE  = "slide"
    NONE   = "none"


class LanguageCode(str, Enum):
    EN_US = "en_US"
    EN_GB = "en_GB"
    DE_DE = "de_DE"
    FR_FR = "fr_FR"
    ES_ES = "es_ES"
    JA_JP = "ja_JP"
    ZH_CN = "zh_CN"
    AR_SA = "ar_SA"
    PT_BR = "pt_BR"
    RU_RU = "ru_RU"


class PowerPlan(str, Enum):
    PERFORMANCE  = "performance"
    BALANCED     = "balanced"
    POWER_SAVER  = "power_saver"
    ULTRA_SAVER  = "ultra_saver"


class DisplayScaling(str, Enum):
    X1_0 = "1.0"
    X1_25 = "1.25"
    X1_5  = "1.5"
    X1_75 = "1.75"
    X2_0  = "2.0"
    X2_5  = "2.5"
    X3_0  = "3.0"
    CUSTOM = "custom"


class PrivacyLevel(str, Enum):
    STRICT   = "strict"
    BALANCED = "balanced"
    OPEN     = "open"


class NotificationBehavior(str, Enum):
    ALL      = "all"
    PRIORITY = "priority"
    SILENT   = "silent"
    OFF      = "off"


class WallpaperMode(str, Enum):
    FILL   = "fill"
    FIT    = "fit"
    STRETCH= "stretch"
    TILE   = "tile"
    CENTER = "center"


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _in_range(lo: float, hi: float) -> Callable[[Any], None]:
    def validator(value: Any) -> None:
        if not (lo <= float(value) <= hi):
            raise ValueError(f"Value {value!r} must be in range [{lo}, {hi}]")
    return validator


def _non_empty_str(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Value must be a non-empty string")


def _hex_color(value: Any) -> None:
    if not re.match(r'^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$', str(value)):
        raise ValueError(f"Value {value!r} is not a valid hex color (#RRGGBB or #RRGGBBAA)")


def _positive_int(value: Any) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Value {value!r} must be a positive integer")


def _non_negative_int(value: Any) -> None:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"Value {value!r} must be a non-negative integer")


# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------

@dataclass
class AppearanceSettings:
    """Visual appearance and theming configuration."""
    theme:                   Theme          = Theme.LIGHT
    accent_color:            AccentColor    = AccentColor.BLUE
    accent_custom_hex:       str            = "#1677F8"
    font_size_base:          int            = 16          # px
    font_family_sans:        str            = "Inter"
    font_family_mono:        str            = "JetBrains Mono"
    icon_theme:              str            = "aureon"
    cursor_theme:            str            = "aureon-default"
    animations_enabled:      bool           = True
    animation_speed:         float          = 1.0         # multiplier (0.5–3.0)
    reduce_motion:           bool           = False
    transparency_enabled:    bool           = True
    transparency_level:      float          = 0.75        # 0.0–1.0
    blur_enabled:            bool           = True
    blur_intensity:          int            = 20          # px
    rounded_corners:         bool           = True
    corner_radius:           int            = 12          # px

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "accent_custom_hex":    _hex_color,
        "font_size_base":       _in_range(8, 32),
        "animation_speed":      _in_range(0.25, 5.0),
        "transparency_level":   _in_range(0.0, 1.0),
        "blur_intensity":       _in_range(0, 80),
        "corner_radius":        _in_range(0, 48),
    }, repr=False)


@dataclass
class WallpaperSettings:
    """Desktop wallpaper and background configuration."""
    wallpaper_path:   str          = "builtin://mountain_lake_sunrise"
    wallpaper_mode:   WallpaperMode= WallpaperMode.FILL
    slideshow_enabled:bool         = False
    slideshow_interval_minutes: int= 30
    slideshow_folder: str          = ""
    color_fallback:   str          = "#0B111E"
    parallax_enabled: bool         = False

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "color_fallback":               _hex_color,
        "slideshow_interval_minutes":   _positive_int,
    }, repr=False)


@dataclass
class DockSettings:
    """Dock / taskbar configuration."""
    position:            DockPosition = DockPosition.BOTTOM
    style:               DockStyle    = DockStyle.GLASS
    icon_size:           int          = 52             # px (24–128)
    magnification:       bool         = True
    magnification_max:   int          = 80             # px
    auto_hide:           bool         = False
    auto_hide_delay_ms:  int          = 400
    show_badges:         bool         = True
    show_running_dots:   bool         = True
    pinned_apps:         List[str]    = field(default_factory=lambda: [
        "aureon.desktop-shell",
        "aureon.files",
        "aureon.browser",
        "aureon.terminal",
        "aureon.settings",
        "aureon.store",
    ])

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "icon_size":         _in_range(24, 128),
        "magnification_max": _in_range(32, 200),
        "auto_hide_delay_ms":_non_negative_int,
    }, repr=False)


@dataclass
class WindowSettings:
    """Window management and behaviour configuration."""
    animation:            WindowAnimation = WindowAnimation.SCALE
    focus_follows_mouse:  bool            = False
    raise_on_focus:       bool            = True
    snap_enabled:         bool            = True
    snap_threshold_px:    int             = 20
    tiling_enabled:       bool            = False
    tiling_gap_px:        int             = 8
    titlebar_buttons_left:bool            = False        # True → macOS style
    double_click_action:  str             = "maximize"   # maximize | shade | none
    scroll_inactive:      bool            = True

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "snap_threshold_px": _in_range(1, 100),
        "tiling_gap_px":     _non_negative_int,
    }, repr=False)


@dataclass
class DisplaySettings:
    """Multi-display and scaling configuration."""
    primary_display_id:  str            = "auto"
    scaling:             DisplayScaling = DisplayScaling.X1_0
    custom_scale_factor: float          = 1.0
    refresh_rate:        int            = 60            # Hz
    night_mode_enabled:  bool           = False
    night_mode_start:    str            = "20:00"
    night_mode_end:      str            = "07:00"
    night_mode_temp_k:   int            = 3400          # Kelvin (1000–6500)
    hdr_enabled:         bool           = False
    color_profile:       str            = "sRGB"

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "custom_scale_factor": _in_range(0.5, 5.0),
        "refresh_rate":        _in_range(30, 360),
        "night_mode_temp_k":   _in_range(1000, 6500),
    }, repr=False)


@dataclass
class InputSettings:
    """Keyboard, mouse, touchpad configuration."""
    # Keyboard
    keyboard_layout:        str   = "us"
    keyboard_repeat_delay:  int   = 500      # ms
    keyboard_repeat_rate:   int   =30        # chars/s
    caps_lock_remap:        str   = "none"   # none | ctrl | esc
    compose_key:            str   = "none"
    # Mouse
    mouse_speed:            float = 1.0
    mouse_natural_scroll:   bool  = False
    mouse_acceleration:     bool  = True
    # Touchpad
    touchpad_speed:         float = 1.0
    touchpad_natural_scroll:bool  = True
    touchpad_tap_to_click:  bool  = True
    touchpad_two_finger_scroll:bool = True
    touchpad_pinch_to_zoom: bool  = True
    touchpad_three_finger_swipe:bool = True
    # Accessibility
    sticky_keys:            bool  = False
    slow_keys:              bool  = False
    bounce_keys:            bool  = False

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "mouse_speed":        _in_range(0.1, 5.0),
        "touchpad_speed":     _in_range(0.1, 5.0),
        "keyboard_repeat_delay": _in_range(100, 2000),
        "keyboard_repeat_rate":  _in_range(1, 100),
    }, repr=False)


@dataclass
class SoundSettings:
    """Audio output/input and notification sounds."""
    output_device:       str   = "default"
    input_device:        str   = "default"
    output_volume:       int   = 70     # 0–100
    input_volume:        int   = 80     # 0–100
    muted:               bool  = False
    input_muted:         bool  = False
    startup_sound:       bool  = True
    ui_sounds:           bool  = True
    notification_sounds: bool  = True
    volume_overdrive:    bool  = False  # allow >100%

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "output_volume": _in_range(0, 150),
        "input_volume":  _in_range(0, 100),
    }, repr=False)


@dataclass
class NetworkSettings:
    """Network, VPN and proxy configuration."""
    wifi_enabled:         bool  = True
    ethernet_enabled:     bool  = True
    bluetooth_enabled:    bool  = True
    airplane_mode:        bool  = False
    vpn_enabled:          bool  = False
    vpn_profile:          str   = ""
    proxy_mode:           str   = "none"   # none | manual | auto
    proxy_host:           str   = ""
    proxy_port:           int   = 0
    proxy_pac_url:        str   = ""
    dns_servers:          List[str] = field(default_factory=lambda: ["1.1.1.1", "8.8.8.8"])
    metered_connection:   bool  = False
    auto_connect_known:   bool  = True

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "proxy_port": _in_range(0, 65535),
    }, repr=False)


@dataclass
class PrivacySettings:
    """Privacy and telemetry configuration."""
    privacy_level:          PrivacyLevel = PrivacyLevel.BALANCED
    send_diagnostics:       bool         = True
    send_crash_reports:     bool         = True
    location_services:      bool         = True
    camera_access:          bool         = True
    microphone_access:      bool         = True
    clipboard_monitoring:   bool         = True
    screen_recording_guard: bool         = True
    ad_tracking:            bool         = False
    analytics_id:           str          = ""


@dataclass
class SecuritySettings:
    """Authentication and security configuration."""
    lock_on_sleep:          bool  = True
    lock_timeout_minutes:   int   = 5
    screen_lock_enabled:    bool  = True
    biometric_enabled:      bool  = True
    require_password_after: int   = 0     # seconds (0 = immediately)
    firewall_enabled:       bool  = True
    auto_updates:           bool  = True
    secure_boot:            bool  = True
    encrypt_home:           bool  = False
    filevault_enabled:      bool  = False

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "lock_timeout_minutes":   _in_range(1, 240),
        "require_password_after": _non_negative_int,
    }, repr=False)


@dataclass
class PowerSettings:
    """Power management and battery configuration."""
    plan:                       PowerPlan = PowerPlan.BALANCED
    sleep_on_battery_minutes:   int       = 10
    sleep_on_power_minutes:     int       = 30
    display_off_on_battery_min: int       = 5
    display_off_on_power_min:   int       = 15
    low_battery_threshold:      int       = 20   # percent
    critical_battery_threshold: int       = 5    # percent
    wake_on_lan:                bool      = False
    turbo_boost:                bool      = True
    battery_percent_in_menu:    bool      = True
    prevent_sleep_on_power:     bool      = False

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "sleep_on_battery_minutes":   _in_range(1, 1440),
        "sleep_on_power_minutes":     _in_range(1, 1440),
        "display_off_on_battery_min": _in_range(1, 240),
        "display_off_on_power_min":   _in_range(1, 240),
        "low_battery_threshold":      _in_range(5, 50),
        "critical_battery_threshold": _in_range(1, 20),
    }, repr=False)


@dataclass
class NotificationSettings:
    """Global notification preferences."""
    behavior:               NotificationBehavior = NotificationBehavior.ALL
    do_not_disturb:         bool                 = False
    dnd_schedule_enabled:   bool                 = False
    dnd_start:              str                  = "22:00"
    dnd_end:                str                  = "08:00"
    banner_duration_seconds:int                  = 5
    show_on_lock_screen:    bool                 = True
    group_by_app:           bool                 = True
    sound_enabled:          bool                 = True
    badges_enabled:         bool                 = True
    max_in_center:          int                  = 50

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "banner_duration_seconds": _in_range(1, 30),
        "max_in_center":           _in_range(5, 200),
    }, repr=False)


@dataclass
class LocalizationSettings:
    """Language, region and format configuration."""
    language:          LanguageCode = LanguageCode.EN_US
    region:            str          = "US"
    timezone:          str          = "UTC"
    calendar_type:     str          = "gregorian"
    first_day_of_week: int          = 0        # 0=Sunday, 1=Monday
    use_24h_clock:     bool         = False
    date_format:       str          = "MM/DD/YYYY"
    temperature_unit:  str          = "fahrenheit"   # fahrenheit | celsius | kelvin
    measurement_unit:  str          = "imperial"     # imperial | metric
    currency_symbol:   str          = "$"
    number_format:     str          = "1,234.56"

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "first_day_of_week": _in_range(0, 6),
    }, repr=False)


@dataclass
class AISettings:
    """AI Assistant and intelligence features configuration."""
    ai_enabled:            bool  = True
    model_preference:      str   = "aureon-local"
    online_model_fallback: bool  = True
    context_aware:         bool  = True
    learn_from_usage:      bool  = True
    privacy_mode:          bool  = False    # disables cloud model calls
    voice_enabled:         bool  = True
    wake_word:             str   = "Hey Aureon"
    smart_suggestions:     bool  = True
    summarization:         bool  = True
    max_context_tokens:    int   = 4096

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "max_context_tokens": _in_range(512, 128000),
    }, repr=False)


@dataclass
class AccessibilitySettings:
    """Accessibility and assistive technology settings."""
    screen_reader:          bool  = False
    high_contrast:          bool  = False
    large_text:             bool  = False
    large_text_scale:       float = 1.5
    bold_text:              bool  = False
    increase_contrast:      bool  = False
    reduce_motion:          bool  = False
    color_blind_mode:       str   = "none"    # none | deuteranopia | protanopia | tritanopia
    pointer_size:           int   = 1         # 1–5 scale
    pointer_color:          str   = "#FFFFFF"
    keyboard_navigation:    bool  = True
    focus_highlight:        bool  = True
    speak_selected_text:    bool  = False
    spoken_content_rate:    float = 1.0

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "large_text_scale":    _in_range(1.0, 4.0),
        "pointer_size":        _in_range(1, 5),
        "pointer_color":       _hex_color,
        "spoken_content_rate": _in_range(0.5, 4.0),
    }, repr=False)


@dataclass
class DeveloperSettings:
    """Developer mode and debugging options (hidden in release)."""
    developer_mode:         bool  = False
    show_fps_counter:       bool  = False
    show_resource_monitor:  bool  = False
    gpu_layer_borders:      bool  = False
    log_level:              str   = "warn"      # debug | info | warn | error
    remote_debug_port:      int   = 9229
    allow_insecure_origins: bool  = False
    mock_hardware:          bool  = False

    _validators: Dict[str, Callable] = field(default_factory=lambda: {
        "remote_debug_port": _in_range(1024, 65535),
    }, repr=False)


# ---------------------------------------------------------------------------
# Root Settings Schema
# ---------------------------------------------------------------------------

@dataclass
class AureonSettings:
    """
    Root settings object for AUREON OS.
    Version is bumped on every schema-breaking change to trigger migration.
    """
    schema_version:  int                   = 4
    appearance:      AppearanceSettings    = field(default_factory=AppearanceSettings)
    wallpaper:       WallpaperSettings     = field(default_factory=WallpaperSettings)
    dock:            DockSettings          = field(default_factory=DockSettings)
    windows:         WindowSettings        = field(default_factory=WindowSettings)
    display:         DisplaySettings       = field(default_factory=DisplaySettings)
    input:           InputSettings         = field(default_factory=InputSettings)
    sound:           SoundSettings         = field(default_factory=SoundSettings)
    network:         NetworkSettings       = field(default_factory=NetworkSettings)
    privacy:         PrivacySettings       = field(default_factory=PrivacySettings)
    security:        SecuritySettings      = field(default_factory=SecuritySettings)
    power:           PowerSettings         = field(default_factory=PowerSettings)
    notifications:   NotificationSettings  = field(default_factory=NotificationSettings)
    localization:    LocalizationSettings  = field(default_factory=LocalizationSettings)
    ai:              AISettings            = field(default_factory=AISettings)
    accessibility:   AccessibilitySettings = field(default_factory=AccessibilitySettings)
    developer:       DeveloperSettings     = field(default_factory=DeveloperSettings)

    def validate(self) -> List[str]:
        """Run all validators. Returns list of error messages (empty = OK)."""
        errors: List[str] = []
        for section_name in (
            "appearance", "wallpaper", "dock", "windows", "display",
            "input", "sound", "network", "privacy", "security", "power",
            "notifications", "localization", "ai", "accessibility", "developer",
        ):
            section = getattr(self, section_name)
            validators: Dict = getattr(section, "_validators", {})
            for field_name, validator in validators.items():
                try:
                    validator(getattr(section, field_name))
                except ValueError as exc:
                    errors.append(f"{section_name}.{field_name}: {exc}")
        return errors
