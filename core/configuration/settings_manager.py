"""
AUREON OS — Settings Manager
==============================
Handles loading/saving settings to ~/.aureon/settings.json,
versioned schema migrations, live change watchers, and reset-to-defaults.

Usage:
    manager = SettingsManager()
    settings = manager.load()
    settings.appearance.theme = Theme.DARK
    manager.save(settings)
    manager.watch("appearance.theme", callback)
"""

from __future__ import annotations

import copy
import dataclasses
import json
import logging
import os
import shutil
import threading
import time
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .settings_schema import (
    AureonSettings, AppearanceSettings, WallpaperSettings, DockSettings,
    WindowSettings, DisplaySettings, InputSettings, SoundSettings,
    NetworkSettings, PrivacySettings, SecuritySettings, PowerSettings,
    NotificationSettings, LocalizationSettings, AISettings,
    AccessibilitySettings, DeveloperSettings,
    Theme, AccentColor, DockPosition, DockStyle, WindowAnimation,
    PowerPlan, DisplayScaling, PrivacyLevel, NotificationBehavior,
    WallpaperMode, LanguageCode,
)

logger = logging.getLogger("aureon.settings")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SETTINGS_DIR  = Path.home() / ".aureon"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"
BACKUP_DIR    = SETTINGS_DIR / "backups"
CURRENT_SCHEMA_VERSION = 4

_SECTION_CLASSES = {
    "appearance":    AppearanceSettings,
    "wallpaper":     WallpaperSettings,
    "dock":          DockSettings,
    "windows":       WindowSettings,
    "display":       DisplaySettings,
    "input":         InputSettings,
    "sound":         SoundSettings,
    "network":       NetworkSettings,
    "privacy":       PrivacySettings,
    "security":      SecuritySettings,
    "power":         PowerSettings,
    "notifications": NotificationSettings,
    "localization":  LocalizationSettings,
    "ai":            AISettings,
    "accessibility": AccessibilitySettings,
    "developer":     DeveloperSettings,
}


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _coerce_value(field_type: Any, raw: Any) -> Any:
    """Attempt to coerce a raw JSON value to the declared dataclass field type."""
    origin = getattr(field_type, "__origin__", None)

    # Handle Optional[X]
    if origin is type(None):
        return None
    if hasattr(field_type, "__args__"):
        # Optional = Union[X, None]
        args = [a for a in field_type.__args__ if a is not type(None)]
        if args:
            return _coerce_value(args[0], raw)

    # Enums
    if isinstance(field_type, type) and issubclass(field_type, str) and issubclass(field_type, type(field_type)):
        try:
            return field_type(raw)
        except ValueError:
            return raw
    if hasattr(field_type, "__mro__") and any(
        c.__name__ == "Enum" for c in getattr(field_type, "__mro__", [])
    ):
        try:
            return field_type(raw)
        except (ValueError, KeyError):
            return raw

    # Lists
    if origin is list:
        item_type = field_type.__args__[0] if hasattr(field_type, "__args__") else str
        if isinstance(raw, list):
            return [_coerce_value(item_type, item) for item in raw]
        return raw

    # Primitives
    if field_type in (int, float, str, bool) and not isinstance(raw, field_type):
        try:
            return field_type(raw)
        except (TypeError, ValueError):
            return raw

    return raw


def _dict_to_section(cls, data: Dict[str, Any]) -> Any:
    """Instantiate a settings dataclass from a dict, skipping private fields."""
    init_kwargs: Dict[str, Any] = {}
    for f in fields(cls):
        if f.name.startswith("_"):
            continue
        raw = data.get(f.name)
        if raw is None and f.name not in data:
            # Use field default
            if f.default is not dataclasses.MISSING:
                init_kwargs[f.name] = f.default
            elif f.default_factory is not dataclasses.MISSING:
                init_kwargs[f.name] = f.default_factory()
        else:
            init_kwargs[f.name] = _coerce_value(f.type, raw)
    return cls(**init_kwargs)


def _section_to_dict(section: Any) -> Dict[str, Any]:
    """Serialize a settings section to a plain dict (excludes private fields)."""
    result: Dict[str, Any] = {}
    for f in fields(section):
        if f.name.startswith("_"):
            continue
        value = getattr(section, f.name)
        # Enums → their .value
        if hasattr(value, "value") and hasattr(value, "__class__") and issubclass(
            type(value), str
        ):
            result[f.name] = str(value)
        elif isinstance(value, list):
            result[f.name] = value
        else:
            result[f.name] = value
    return result


def _settings_to_dict(settings: AureonSettings) -> Dict[str, Any]:
    d: Dict[str, Any] = {"schema_version": settings.schema_version}
    for key in _SECTION_CLASSES:
        d[key] = _section_to_dict(getattr(settings, key))
    return d


# ---------------------------------------------------------------------------
# Migration engine
# ---------------------------------------------------------------------------

class MigrationError(RuntimeError):
    """Raised when a settings migration fails unrecoverably."""


def _migrate_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    v1→v2: Split old 'display.scale' (int) into new DisplayScaling enum.
    Old field 'appearance.window_animations' (bool) → 'windows.animation' (str).
    """
    old_scale = data.get("display", {}).pop("scale", None)
    if old_scale is not None:
        mapping = {1: "1.0", 2: "2.0", 3: "3.0"}
        data.setdefault("display", {})["scaling"] = mapping.get(old_scale, "1.0")

    old_anim = data.get("appearance", {}).pop("window_animations", None)
    if old_anim is not None:
        data.setdefault("windows", {})["animation"] = "scale" if old_anim else "none"

    data["schema_version"] = 2
    logger.info("Migrated settings v1 → v2")
    return data


def _migrate_v2_to_v3(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    v2→v3: 'sound.master_volume' renamed to 'sound.output_volume'.
           New 'ai' section added with defaults.
    """
    sound = data.get("sound", {})
    if "master_volume" in sound:
        sound["output_volume"] = sound.pop("master_volume")

    data.setdefault("ai", {})

    data["schema_version"] = 3
    logger.info("Migrated settings v2 → v3")
    return data


def _migrate_v3_to_v4(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    v3→v4: 'notifications.type' renamed to 'notifications.behavior'.
           Added 'accessibility' section.
    """
    notif = data.get("notifications", {})
    if "type" in notif:
        notif["behavior"] = notif.pop("type")

    data.setdefault("accessibility", {})
    data.setdefault("developer", {})

    data["schema_version"] = 4
    logger.info("Migrated settings v3 → v4")
    return data


_MIGRATIONS: List[Callable[[Dict], Dict]] = [
    _migrate_v1_to_v2,
    _migrate_v2_to_v3,
    _migrate_v3_to_v4,
]


def run_migrations(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all pending migrations in order.
    Each migration function is responsible for bumping schema_version.
    """
    version = data.get("schema_version", 1)
    while version < CURRENT_SCHEMA_VERSION:
        idx = version - 1
        if idx >= len(_MIGRATIONS):
            raise MigrationError(
                f"No migration path from schema version {version} to {CURRENT_SCHEMA_VERSION}"
            )
        data = _MIGRATIONS[idx](data)
        version = data.get("schema_version", version + 1)
    return data


# ---------------------------------------------------------------------------
# Watcher
# ---------------------------------------------------------------------------

WatcherCallback = Callable[[str, Any, Any], None]   # (key_path, old_value, new_value)


class _WatcherRegistry:
    """Thread-safe registry of key-path → list[callback] mappings."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._watchers: Dict[str, List[WatcherCallback]] = {}

    def add(self, key_path: str, callback: WatcherCallback) -> None:
        with self._lock:
            self._watchers.setdefault(key_path, []).append(callback)

    def remove(self, key_path: str, callback: WatcherCallback) -> None:
        with self._lock:
            listeners = self._watchers.get(key_path, [])
            try:
                listeners.remove(callback)
            except ValueError:
                pass

    def notify(self, key_path: str, old_value: Any, new_value: Any) -> None:
        with self._lock:
            listeners = list(self._watchers.get(key_path, []))
        for cb in listeners:
            try:
                cb(key_path, old_value, new_value)
            except Exception as exc:
                logger.warning("Watcher callback raised: %s", exc)

    def notify_all_changed(
        self,
        old_dict: Dict[str, Any],
        new_dict: Dict[str, Any],
        prefix: str = "",
    ) -> None:
        """Recursively compare two settings dicts and notify changed paths."""
        for key in set(list(old_dict.keys()) + list(new_dict.keys())):
            full_key = f"{prefix}.{key}" if prefix else key
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                self.notify_all_changed(old_val, new_val, full_key)
            elif old_val != new_val:
                self.notify(full_key, old_val, new_val)


# ---------------------------------------------------------------------------
# SettingsManager
# ---------------------------------------------------------------------------

class SettingsManager:
    """
    Central settings manager for AUREON OS.

    Features:
      - load / save (atomic write with .tmp → rename)
      - automatic backup rotation (keeps last 10)
      - versioned schema migrations
      - change watchers by dot-separated key path
      - reset_to_defaults (whole or per-section)
      - get / set by dot-path string
    """

    def __init__(
        self,
        settings_file: Optional[Path] = None,
        auto_backup: bool = True,
        backup_count: int = 10,
    ) -> None:
        self._file = Path(settings_file) if settings_file else SETTINGS_FILE
        self._auto_backup = auto_backup
        self._backup_count = backup_count
        self._watchers = _WatcherRegistry()
        self._current: Optional[AureonSettings] = None
        self._lock = threading.RLock()
        self._ensure_dirs()

    # ------------------------------------------------------------------
    # Directory setup
    # ------------------------------------------------------------------

    def _ensure_dirs(self) -> None:
        try:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> AureonSettings:
        """
        Load settings from disk. If the file does not exist, returns defaults.
        Runs migrations as needed. Validates on load and logs any warnings.
        """
        with self._lock:
            if not self._file.exists():
                logger.info("No settings file found — using defaults.")
                self._current = AureonSettings()
                return copy.deepcopy(self._current)

            try:
                raw = self._file.read_text(encoding="utf-8")
                data: Dict[str, Any] = json.loads(raw)
            except (OSError, json.JSONDecodeError) as exc:
                logger.error("Failed to read settings file: %s — using defaults.", exc)
                self._current = AureonSettings()
                return copy.deepcopy(self._current)

            # Migrate if needed
            file_version = data.get("schema_version", 1)
            if file_version < CURRENT_SCHEMA_VERSION:
                if self._auto_backup:
                    self._create_backup(tag=f"pre-migrate-v{file_version}")
                try:
                    data = run_migrations(data)
                except MigrationError as exc:
                    logger.error("Migration failed: %s — using defaults.", exc)
                    self._current = AureonSettings()
                    return copy.deepcopy(self._current)

            # Deserialise
            settings = AureonSettings(schema_version=CURRENT_SCHEMA_VERSION)
            for section_key, section_cls in _SECTION_CLASSES.items():
                raw_section = data.get(section_key, {})
                try:
                    setattr(settings, section_key, _dict_to_section(section_cls, raw_section))
                except Exception as exc:
                    logger.warning("Error loading section %s: %s — using defaults.", section_key, exc)

            # Validate
            errors = settings.validate()
            for err in errors:
                logger.warning("Settings validation warning: %s", err)

            self._current = settings
            logger.info("Settings loaded from %s (schema v%d)", self._file, CURRENT_SCHEMA_VERSION)
            return copy.deepcopy(settings)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, settings: AureonSettings) -> None:
        """
        Atomically save settings to disk.
        Writes to a .tmp file first, then renames — prevents corruption.
        Notifies registered watchers of changed values.
        """
        with self._lock:
            if self._auto_backup and self._file.exists():
                self._create_backup()

            old_dict = _settings_to_dict(self._current) if self._current else {}
            settings.schema_version = CURRENT_SCHEMA_VERSION
            new_dict = _settings_to_dict(settings)

            tmp_path = self._file.with_suffix(".tmp")
            try:
                tmp_path.write_text(
                    json.dumps(new_dict, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                tmp_path.replace(self._file)
            except OSError as exc:
                logger.error("Failed to save settings: %s", exc)
                raise

            self._current = copy.deepcopy(settings)
            logger.info("Settings saved to %s", self._file)

            # Notify watchers
            self._watchers.notify_all_changed(old_dict, new_dict)

    # ------------------------------------------------------------------
    # Dot-path get / set
    # ------------------------------------------------------------------

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieve a setting value by dot-path, e.g. "appearance.theme".
        Returns `default` if the path does not exist.
        """
        with self._lock:
            if self._current is None:
                self.load()
            parts = key_path.split(".")
            obj: Any = self._current
            for part in parts:
                try:
                    obj = getattr(obj, part)
                except AttributeError:
                    return default
            return obj

    def set(self, key_path: str, value: Any) -> None:
        """
        Set a setting value by dot-path, e.g. "appearance.theme", "dark".
        Saves immediately after setting.
        """
        with self._lock:
            if self._current is None:
                self.load()
            settings = copy.deepcopy(self._current)
            parts = key_path.split(".")
            if len(parts) < 2:
                raise ValueError(f"key_path must have at least two parts: {key_path!r}")
            section_name, field_name = parts[0], parts[-1]
            section = getattr(settings, section_name, None)
            if section is None:
                raise AttributeError(f"No settings section: {section_name!r}")
            if not hasattr(section, field_name):
                raise AttributeError(f"No field {field_name!r} in section {section_name!r}")
            setattr(section, field_name, value)
            self.save(settings)

    # ------------------------------------------------------------------
    # Watchers
    # ------------------------------------------------------------------

    def watch(self, key_path: str, callback: WatcherCallback) -> None:
        """
        Register a callback fired when `key_path` changes.
        Signature: callback(key_path: str, old_value: Any, new_value: Any)
        """
        self._watchers.add(key_path, callback)

    def unwatch(self, key_path: str, callback: WatcherCallback) -> None:
        """Remove a previously registered watcher."""
        self._watchers.remove(key_path, callback)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset_to_defaults(self, section: Optional[str] = None) -> AureonSettings:
        """
        Reset settings to defaults.
        If `section` is provided (e.g. "appearance"), only that section is reset.
        Saves and returns the updated settings object.
        """
        with self._lock:
            if self._current is None:
                self.load()
            settings = copy.deepcopy(self._current)

            if section:
                cls = _SECTION_CLASSES.get(section)
                if cls is None:
                    raise ValueError(f"Unknown settings section: {section!r}")
                setattr(settings, section, cls())
                logger.info("Reset section '%s' to defaults", section)
            else:
                settings = AureonSettings()
                logger.info("Reset ALL settings to defaults")

            self.save(settings)
            return copy.deepcopy(settings)

    # ------------------------------------------------------------------
    # Backup management
    # ------------------------------------------------------------------

    def _create_backup(self, tag: str = "") -> Optional[Path]:
        if not self._file.exists():
            return None
        ts = time.strftime("%Y%m%d_%H%M%S")
        suffix = f"_{tag}" if tag else ""
        backup_path = BACKUP_DIR / f"settings_{ts}{suffix}.json"
        try:
            shutil.copy2(self._file, backup_path)
            logger.debug("Created backup: %s", backup_path)
            self._prune_backups()
            return backup_path
        except OSError as exc:
            logger.warning("Could not create settings backup: %s", exc)
            return None

    def _prune_backups(self) -> None:
        """Keep only the N most-recent backups."""
        backups = sorted(BACKUP_DIR.glob("settings_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in backups[self._backup_count:]:
            try:
                old.unlink()
            except OSError:
                pass

    def list_backups(self) -> List[Path]:
        """Return a sorted list of backup file paths (newest first)."""
        return sorted(BACKUP_DIR.glob("settings_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    def restore_backup(self, backup_path: Path) -> AureonSettings:
        """Restore settings from a named backup file. Returns the loaded settings."""
        with self._lock:
            if self._auto_backup:
                self._create_backup(tag="pre-restore")
            shutil.copy2(backup_path, self._file)
            self._current = None
            logger.info("Restored settings from backup: %s", backup_path)
            return self.load()

    # ------------------------------------------------------------------
    # Export / import (for settings sharing / sync)
    # ------------------------------------------------------------------

    def export_json(self, include_sensitive: bool = False) -> str:
        """Return the current settings as a JSON string for export/sync."""
        with self._lock:
            if self._current is None:
                self.load()
            d = _settings_to_dict(self._current)
            if not include_sensitive:
                # Redact security-sensitive fields
                d.get("security", {}).pop("encrypt_home", None)
                d.get("network", {}).pop("proxy_host", None)
                d.get("network", {}).pop("proxy_port", None)
            return json.dumps(d, indent=2, ensure_ascii=False)

    def import_json(self, json_str: str) -> AureonSettings:
        """Import and merge settings from a JSON string. Saves after import."""
        data = json.loads(json_str)
        # Run migrations in case the imported file is from an older version
        data = run_migrations(data)
        settings = AureonSettings(schema_version=CURRENT_SCHEMA_VERSION)
        for section_key, section_cls in _SECTION_CLASSES.items():
            raw_section = data.get(section_key, {})
            setattr(settings, section_key, _dict_to_section(section_cls, raw_section))
        self.save(settings)
        return copy.deepcopy(settings)
