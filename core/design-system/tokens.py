"""
AUREON OS Design System — Design Tokens
========================================
Complete design token module defining the visual language of AUREON OS.
Includes color palettes (light + dark), typography, spacing, radii,
shadows, animations, z-index scale, and all AUREON brand constants.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any


# ---------------------------------------------------------------------------
# Brand Identity Constants
# ---------------------------------------------------------------------------

class Brand:
    """AUREON core brand colors and identity constants."""
    # Primary gradient endpoints
    BLUE        = "#1677F8"
    VIOLET      = "#A99BFF"
    VIOLET_DEEP = "#7B6FEF"
    BLUE_DEEP   = "#0D5BD6"

    # Neutral palette
    INK         = "#17233D"   # primary text / wordmark
    INK_SOFT    = "#2E3F5C"
    SLATE       = "#4A5B7A"
    MIST        = "#8C9BB5"
    CLOUD       = "#D0D8E8"
    SNOW        = "#F4F6FB"
    WHITE       = "#FFFFFF"

    # Semantic
    SUCCESS     = "#22C55E"
    WARNING     = "#F59E0B"
    ERROR       = "#EF4444"
    INFO        = "#38BDF8"

    # Gradient definitions (CSS-ready strings)
    GRADIENT_PRIMARY     = "linear-gradient(135deg, #1677F8 0%, #A99BFF 100%)"
    GRADIENT_DEEP        = "linear-gradient(135deg, #0D5BD6 0%, #7B6FEF 100%)"
    GRADIENT_DAWN        = "linear-gradient(180deg, #FFA94D 0%, #1677F8 60%, #0D1B40 100%)"
    GRADIENT_WALLPAPER   = "linear-gradient(160deg, #0D1B40 0%, #1677F8 50%, #A99BFF 100%)"


# ---------------------------------------------------------------------------
# Color Palette — Light Mode
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ColorScale:
    """A single color's tonal scale (50–950)."""
    c50:  str
    c100: str
    c200: str
    c300: str
    c400: str
    c500: str
    c600: str
    c700: str
    c800: str
    c900: str
    c950: str

    def __getitem__(self, shade: int) -> str:
        return getattr(self, f"c{shade}")


PALETTE_BLUE = ColorScale(
    c50="#EEF5FF", c100="#D9E8FF", c200="#B5CFFF", c300="#85AEFF",
    c400="#5088FF", c500="#1677F8", c600="#0D5BD6", c700="#0A44A8",
    c800="#082F7A", c900="#061E52", c950="#030F2B",
)

PALETTE_VIOLET = ColorScale(
    c50="#F2F0FF", c100="#E6E0FF", c200="#CFC4FF", c300="#B8A8FF",
    c400="#A99BFF", c500="#8A7BEF", c600="#6B5FCC", c700="#4F45A3",
    c800="#352E78", c900="#1E1A4D", c950="#0E0D28",
)

PALETTE_SLATE = ColorScale(
    c50="#F8FAFC", c100="#F1F5F9", c200="#E2E8F0", c300="#CBD5E1",
    c400="#94A3B8", c500="#64748B", c600="#475569", c700="#334155",
    c800="#1E293B", c900="#0F172A", c950="#020617",
)

PALETTE_GREEN = ColorScale(
    c50="#F0FDF4", c100="#DCFCE7", c200="#BBF7D0", c300="#86EFAC",
    c400="#4ADE80", c500="#22C55E", c600="#16A34A", c700="#15803D",
    c800="#166534", c900="#14532D", c950="#052E16",
)

PALETTE_AMBER = ColorScale(
    c50="#FFFBEB", c100="#FEF3C7", c200="#FDE68A", c300="#FCD34D",
    c400="#FBBF24", c500="#F59E0B", c600="#D97706", c700="#B45309",
    c800="#92400E", c900="#78350F", c950="#451A03",
)

PALETTE_RED = ColorScale(
    c50="#FEF2F2", c100="#FEE2E2", c200="#FECACA", c300="#FCA5A5",
    c400="#F87171", c500="#EF4444", c600="#DC2626", c700="#B91C1C",
    c800="#991B1B", c900="#7F1D1D", c950="#450A0A",
)


# ---------------------------------------------------------------------------
# Semantic Color Tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ColorTokens:
    # Backgrounds
    bg_base:          str
    bg_raised:        str
    bg_overlay:       str
    bg_sunken:        str

    # Surfaces (cards, panels)
    surface_1:        str
    surface_2:        str
    surface_3:        str

    # Borders
    border_subtle:    str
    border_default:   str
    border_strong:    str

    # Text
    text_primary:     str
    text_secondary:   str
    text_tertiary:    str
    text_disabled:    str
    text_on_accent:   str

    # Accent (interactive)
    accent_default:   str
    accent_hover:     str
    accent_pressed:   str
    accent_subtle:    str

    # State colors
    success:          str
    success_subtle:   str
    warning:          str
    warning_subtle:   str
    error:            str
    error_subtle:     str
    info:             str
    info_subtle:      str

    # Overlay / scrim
    scrim_light:      str
    scrim_medium:     str
    scrim_heavy:      str

    # Window chrome
    titlebar_bg:      str
    titlebar_text:    str
    dock_bg:          str
    dock_border:      str


LIGHT_COLORS = ColorTokens(
    bg_base="#F4F6FB",         bg_raised="#FFFFFF",
    bg_overlay="#FFFFFF",      bg_sunken="#E8EDF6",
    surface_1="#FFFFFF",       surface_2="#F4F6FB",
    surface_3="#EBF0F9",
    border_subtle="#E8EDF6",   border_default="#CBD5E1",
    border_strong="#94A3B8",
    text_primary="#17233D",    text_secondary="#2E3F5C",
    text_tertiary="#64748B",   text_disabled="#94A3B8",
    text_on_accent="#FFFFFF",
    accent_default="#1677F8",  accent_hover="#0D5BD6",
    accent_pressed="#0A44A8",  accent_subtle="#D9E8FF",
    success="#22C55E",         success_subtle="#DCFCE7",
    warning="#F59E0B",         warning_subtle="#FEF3C7",
    error="#EF4444",           error_subtle="#FEE2E2",
    info="#38BDF8",            info_subtle="#E0F2FE",
    scrim_light="rgba(15,23,42,0.15)",
    scrim_medium="rgba(15,23,42,0.40)",
    scrim_heavy="rgba(15,23,42,0.70)",
    titlebar_bg="#FFFFFF",     titlebar_text="#17233D",
    dock_bg="rgba(255,255,255,0.75)",
    dock_border="rgba(203,213,225,0.60)",
)

DARK_COLORS = ColorTokens(
    bg_base="#0B111E",         bg_raised="#111A2D",
    bg_overlay="#18243A",      bg_sunken="#070D18",
    surface_1="#111A2D",       surface_2="#18243A",
    surface_3="#1E2D47",
    border_subtle="#1E2D47",   border_default="#2E3F5C",
    border_strong="#4A5B7A",
    text_primary="#E8EDF6",    text_secondary="#CBD5E1",
    text_tertiary="#8C9BB5",   text_disabled="#4A5B7A",
    text_on_accent="#FFFFFF",
    accent_default="#1677F8",  accent_hover="#5088FF",
    accent_pressed="#85AEFF",  accent_subtle="#061E52",
    success="#22C55E",         success_subtle="#052E16",
    warning="#F59E0B",         warning_subtle="#451A03",
    error="#EF4444",           error_subtle="#450A0A",
    info="#38BDF8",            info_subtle="#0C4A6E",
    scrim_light="rgba(0,0,0,0.25)",
    scrim_medium="rgba(0,0,0,0.55)",
    scrim_heavy="rgba(0,0,0,0.80)",
    titlebar_bg="#0B111E",     titlebar_text="#E8EDF6",
    dock_bg="rgba(11,17,30,0.80)",
    dock_border="rgba(46,63,92,0.60)",
)


# ---------------------------------------------------------------------------
# Typography Scale
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TypeScale:
    name:        str
    size_px:     int
    size_rem:    float
    line_height: float    # unitless multiplier
    weight:      int
    tracking:    str      # letter-spacing


FONT_FAMILIES = {
    "sans":  "'Inter', 'SF Pro Display', 'Segoe UI Variable', system-ui, sans-serif",
    "mono":  "'JetBrains Mono', 'Cascadia Code', 'Fira Code', 'SF Mono', monospace",
    "serif": "'Playfair Display', 'Georgia', serif",
}

TYPE_SCALE: Dict[str, TypeScale] = {
    "display_2xl": TypeScale("display_2xl", 72,  4.500, 1.10, 700, "-0.03em"),
    "display_xl":  TypeScale("display_xl",  60,  3.750, 1.12, 700, "-0.025em"),
    "display_lg":  TypeScale("display_lg",  48,  3.000, 1.14, 600, "-0.02em"),
    "display_md":  TypeScale("display_md",  36,  2.250, 1.20, 600, "-0.015em"),
    "display_sm":  TypeScale("display_sm",  30,  1.875, 1.25, 600, "-0.01em"),
    "heading_xl":  TypeScale("heading_xl",  24,  1.500, 1.33, 600, "-0.01em"),
    "heading_lg":  TypeScale("heading_lg",  20,  1.250, 1.40, 600, "-0.005em"),
    "heading_md":  TypeScale("heading_md",  18,  1.125, 1.44, 600,  "0"),
    "heading_sm":  TypeScale("heading_sm",  16,  1.000, 1.50, 600,  "0"),
    "heading_xs":  TypeScale("heading_xs",  14,  0.875, 1.57, 600, "0.005em"),
    "body_xl":     TypeScale("body_xl",     20,  1.250, 1.60, 400,  "0"),
    "body_lg":     TypeScale("body_lg",     18,  1.125, 1.65, 400,  "0"),
    "body_md":     TypeScale("body_md",     16,  1.000, 1.60, 400,  "0"),
    "body_sm":     TypeScale("body_sm",     14,  0.875, 1.57, 400,  "0"),
    "body_xs":     TypeScale("body_xs",     12,  0.750, 1.60, 400, "0.01em"),
    "label_lg":    TypeScale("label_lg",    16,  1.000, 1.25, 500, "0.01em"),
    "label_md":    TypeScale("label_md",    14,  0.875, 1.25, 500, "0.01em"),
    "label_sm":    TypeScale("label_sm",    12,  0.750, 1.25, 500, "0.025em"),
    "label_xs":    TypeScale("label_xs",    10,  0.625, 1.25, 600, "0.05em"),
    "code_md":     TypeScale("code_md",     14,  0.875, 1.60, 400,  "0"),
    "code_sm":     TypeScale("code_sm",     12,  0.750, 1.60, 400,  "0"),
}


# ---------------------------------------------------------------------------
# Spacing Scale  (base 4px)
# ---------------------------------------------------------------------------

SPACING: Dict[str, int] = {
    "0":    0,   "px":  1,   "0.5": 2,   "1":   4,
    "1.5":  6,   "2":   8,   "2.5": 10,  "3":   12,
    "3.5":  14,  "4":   16,  "5":   20,  "6":   24,
    "7":    28,  "8":   32,  "9":   36,  "10":  40,
    "11":   44,  "12":  48,  "14":  56,  "16":  64,
    "20":   80,  "24":  96,  "28": 112,  "32": 128,
    "36": 144,  "40": 160,  "48": 192,  "56": 224,
    "64": 256,  "72": 288,  "80": 320,  "96": 384,
}


# ---------------------------------------------------------------------------
# Border Radius Scale
# ---------------------------------------------------------------------------

RADIUS: Dict[str, str] = {
    "none":  "0px",
    "xs":    "2px",
    "sm":    "4px",
    "md":    "8px",
    "lg":    "12px",
    "xl":    "16px",
    "2xl":   "20px",
    "3xl":   "24px",
    "4xl":   "32px",
    "full":  "9999px",
    # App-specific aliases
    "window":   "12px",
    "card":     "16px",
    "dialog":   "20px",
    "button":   "8px",
    "input":    "8px",
    "badge":    "9999px",
    "tooltip":  "6px",
    "menu":     "12px",
    "dock":     "20px",
}


# ---------------------------------------------------------------------------
# Shadow / Elevation Scale
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Shadow:
    css:         str   # CSS box-shadow value
    elevation:   int   # logical elevation level


SHADOWS_LIGHT: Dict[str, Shadow] = {
    "none":    Shadow("none", 0),
    "xs":      Shadow("0 1px 2px rgba(15,23,42,0.06)", 1),
    "sm":      Shadow("0 1px 3px rgba(15,23,42,0.08), 0 1px 2px rgba(15,23,42,0.05)", 2),
    "md":      Shadow("0 4px 6px -1px rgba(15,23,42,0.08), 0 2px 4px -2px rgba(15,23,42,0.05)", 3),
    "lg":      Shadow("0 10px 15px -3px rgba(15,23,42,0.08), 0 4px 6px -4px rgba(15,23,42,0.05)", 4),
    "xl":      Shadow("0 20px 25px -5px rgba(15,23,42,0.10), 0 8px 10px -6px rgba(15,23,42,0.05)", 5),
    "2xl":     Shadow("0 25px 50px -12px rgba(15,23,42,0.18)", 6),
    "inner":   Shadow("inset 0 2px 4px 0 rgba(15,23,42,0.06)", 0),
    "accent":  Shadow("0 0 0 3px rgba(22,119,248,0.25)", 0),
    "window":  Shadow("0 32px 64px -12px rgba(15,23,42,0.22), 0 0 0 1px rgba(203,213,225,0.5)", 7),
    "dock":    Shadow("0 8px 32px rgba(15,23,42,0.20), 0 2px 8px rgba(15,23,42,0.08)", 6),
}

SHADOWS_DARK: Dict[str, Shadow] = {
    "none":    Shadow("none", 0),
    "xs":      Shadow("0 1px 2px rgba(0,0,0,0.25)", 1),
    "sm":      Shadow("0 1px 3px rgba(0,0,0,0.30), 0 1px 2px rgba(0,0,0,0.20)", 2),
    "md":      Shadow("0 4px 6px -1px rgba(0,0,0,0.30), 0 2px 4px -2px rgba(0,0,0,0.20)", 3),
    "lg":      Shadow("0 10px 15px -3px rgba(0,0,0,0.35), 0 4px 6px -4px rgba(0,0,0,0.20)", 4),
    "xl":      Shadow("0 20px 25px -5px rgba(0,0,0,0.40), 0 8px 10px -6px rgba(0,0,0,0.20)", 5),
    "2xl":     Shadow("0 25px 50px -12px rgba(0,0,0,0.60)", 6),
    "inner":   Shadow("inset 0 2px 4px 0 rgba(0,0,0,0.30)", 0),
    "accent":  Shadow("0 0 0 3px rgba(22,119,248,0.35)", 0),
    "window":  Shadow("0 32px 64px -12px rgba(0,0,0,0.70), 0 0 0 1px rgba(46,63,92,0.5)", 7),
    "dock":    Shadow("0 8px 32px rgba(0,0,0,0.60), 0 2px 8px rgba(0,0,0,0.40)", 6),
}


# ---------------------------------------------------------------------------
# Animation / Transition Tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AnimationTokens:
    # Durations (ms)
    instant:   int   # 0 — immediate
    fast:      int   # micro-interactions
    normal:    int   # standard UI
    slow:      int   # complex transitions
    xslow:     int   # onboarding / splash

    # Easings (CSS cubic-bezier)
    ease_default:    str
    ease_in:         str
    ease_out:        str
    ease_in_out:     str
    ease_spring:     str
    ease_bounce:     str
    ease_decelerate: str
    ease_accelerate: str


ANIMATION = AnimationTokens(
    instant=0, fast=100, normal=200, slow=350, xslow=600,
    ease_default="cubic-bezier(0.4, 0, 0.2, 1)",
    ease_in="cubic-bezier(0.4, 0, 1, 1)",
    ease_out="cubic-bezier(0, 0, 0.2, 1)",
    ease_in_out="cubic-bezier(0.4, 0, 0.2, 1)",
    ease_spring="cubic-bezier(0.34, 1.56, 0.64, 1)",
    ease_bounce="cubic-bezier(0.36, 0.07, 0.19, 0.97)",
    ease_decelerate="cubic-bezier(0, 0, 0.2, 1)",
    ease_accelerate="cubic-bezier(0.4, 0, 1, 1)",
)


# ---------------------------------------------------------------------------
# Z-Index Scale
# ---------------------------------------------------------------------------

Z_INDEX: Dict[str, int] = {
    "below":          -1,
    "base":            0,
    "raised":         10,
    "dropdown":      100,
    "sticky":        200,
    "fixed":         300,
    "overlay":       400,
    "modal_backdrop":500,
    "modal":         600,
    "popover":       700,
    "tooltip":       800,
    "notification":  900,
    "spotlight":    1000,
    "maximum":      9999,
}


# ---------------------------------------------------------------------------
# Blur / Backdrop Tokens
# ---------------------------------------------------------------------------

BLUR: Dict[str, str] = {
    "none":   "0",
    "sm":     "4px",
    "md":     "8px",
    "lg":     "16px",
    "xl":     "24px",
    "2xl":    "40px",
    "glass":  "20px",
    "dock":   "32px",
}


# ---------------------------------------------------------------------------
# Breakpoints
# ---------------------------------------------------------------------------

BREAKPOINTS: Dict[str, int] = {
    "xs":   480,
    "sm":   640,
    "md":   768,
    "lg":  1024,
    "xl":  1280,
    "2xl": 1536,
    "4k":  3840,
}


# ---------------------------------------------------------------------------
# Token Registry — unified access
# ---------------------------------------------------------------------------

class Tokens:
    """Unified token registry. Use Tokens.light or Tokens.dark for themed access."""
    brand        = Brand
    palette      = {
        "blue":   PALETTE_BLUE,
        "violet": PALETTE_VIOLET,
        "slate":  PALETTE_SLATE,
        "green":  PALETTE_GREEN,
        "amber":  PALETTE_AMBER,
        "red":    PALETTE_RED,
    }
    light        = LIGHT_COLORS
    dark         = DARK_COLORS
    type         = TYPE_SCALE
    fonts        = FONT_FAMILIES
    spacing      = SPACING
    radius       = RADIUS
    shadows      = {"light": SHADOWS_LIGHT, "dark": SHADOWS_DARK}
    animation    = ANIMATION
    z_index      = Z_INDEX
    blur         = BLUR
    breakpoints  = BREAKPOINTS

    @classmethod
    def for_theme(cls, theme: str = "light") -> ColorTokens:
        return cls.light if theme == "light" else cls.dark

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export all tokens as a plain dict (for JSON serialization)."""
        return {
            "brand": {k: v for k, v in vars(Brand).items() if not k.startswith("_")},
            "spacing": cls.spacing,
            "radius": cls.radius,
            "z_index": cls.z_index,
            "blur": cls.blur,
            "breakpoints": cls.breakpoints,
            "animation": {
                "durations": {
                    "instant": cls.animation.instant,
                    "fast":    cls.animation.fast,
                    "normal":  cls.animation.normal,
                    "slow":    cls.animation.slow,
                    "xslow":   cls.animation.xslow,
                },
                "easings": {
                    "default":    cls.animation.ease_default,
                    "in":         cls.animation.ease_in,
                    "out":        cls.animation.ease_out,
                    "in_out":     cls.animation.ease_in_out,
                    "spring":     cls.animation.ease_spring,
                    "bounce":     cls.animation.ease_bounce,
                    "decelerate": cls.animation.ease_decelerate,
                    "accelerate": cls.animation.ease_accelerate,
                },
            },
        }
