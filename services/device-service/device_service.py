#!/usr/bin/env python3
"""
AUREON OS — Device & Hardware Discovery Service
Provides abstraction for display monitors, audio endpoints, and bluetooth devices.
"""

import platform

class DeviceService:
    @staticmethod
    def get_connected_displays():
        return [
            {"id": "disp-0", "name": "Built-in Liquid Retina XDR", "resolution": "2560x1600", "refresh": "120Hz", "primary": True},
            {"id": "disp-1", "name": "Aureon Studio Display 5K", "resolution": "5120x2880", "refresh": "60Hz", "primary": False}
        ]

    @staticmethod
    def get_audio_devices():
        return {
            "output": [
                {"id": "out-0", "name": "Internal High-Fidelity Speakers", "default": True},
                {"id": "out-1", "name": "AirPods Max (Spatial Audio)", "default": False}
            ],
            "input": [
                {"id": "in-0", "name": "Studio-Quality Three-Mic Array", "default": True}
            ]
        }

if __name__ == '__main__':
    print(f"[DeviceService] Running on {platform.system()} {platform.machine()}")
    print(f"Displays: {DeviceService.get_connected_displays()}")
