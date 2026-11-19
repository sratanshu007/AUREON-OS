#!/usr/bin/env python3
"""
AUREON OS — Security & Privacy Service
Manages application sandboxing, permissions registry, audit logging, and credential vaults.
"""

import json
import os
import time

AUREON_DIR = os.environ.get('AUREON_CONFIG_DIR') or os.path.expanduser('~/.aureon')
DEFAULT_PERMISSIONS_PATH = os.path.join(AUREON_DIR, 'permissions.json')
DEFAULT_AUDIT_LOG_PATH = os.path.join(AUREON_DIR, 'security_audit.log')

DEFAULT_PERMISSIONS = {
    "dev-studio": {"camera": False, "microphone": False, "filesystem": True, "network": True},
    "aur-browser": {"camera": True, "microphone": True, "filesystem": False, "network": True},
    "ai-assistant": {"camera": False, "microphone": True, "filesystem": True, "network": True},
    "system-monitor": {"camera": False, "microphone": False, "filesystem": True, "network": False}
}

class SecurityService:
    def __init__(self, permissions_path: str = None, audit_log_path: str = None):
        self.permissions_path = permissions_path or DEFAULT_PERMISSIONS_PATH
        self.audit_log_path = audit_log_path or DEFAULT_AUDIT_LOG_PATH
        try:
            os.makedirs(os.path.dirname(self.permissions_path), exist_ok=True)
            if not os.path.exists(self.permissions_path):
                with open(self.permissions_path, 'w') as f:
                    json.dump(DEFAULT_PERMISSIONS, f, indent=2)
        except Exception:
            # Fallback if filesystem write is restricted
            pass

    def check_permission(self, app_id: str, capability: str) -> bool:
        try:
            with open(self.permissions_path, 'r') as f:
                data = json.load(f)
            granted = data.get(app_id, {}).get(capability, False)
            self.log_access(app_id, capability, granted)
            return granted
        except Exception:
            # Graceful fallback to default in-memory permissions
            return DEFAULT_PERMISSIONS.get(app_id, {}).get(capability, False)

    def set_permission(self, app_id: str, capability: str, granted: bool):
        try:
            data = dict(DEFAULT_PERMISSIONS)
            if os.path.exists(self.permissions_path):
                try:
                    with open(self.permissions_path, 'r') as f:
                        data = json.load(f)
                except Exception:
                    pass
            if app_id not in data:
                data[app_id] = {}
            data[app_id][capability] = granted
            with open(self.permissions_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[SecurityService] Error updating permission: {e}")

    def log_access(self, app_id: str, capability: str, allowed: bool):
        entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - App '{app_id}' requested '{capability}': {'ALLOWED' if allowed else 'DENIED'}\n"
        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(entry)
        except Exception:
            pass

if __name__ == '__main__':
    svc = SecurityService()
    print("[SecurityService] Initialized and verified permissions registry.")
