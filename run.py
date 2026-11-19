#!/usr/bin/env python3
"""
=============================================================================
                    AUREON OS — Master System Launcher
                        Dream • Create • Explore
=============================================================================
Starts the backend system telemetry services, launches the local desktop
environment server, and displays the running AUREON OS.
=============================================================================
"""

import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser
import importlib
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# Dynamically import system service
sys_service_mod = importlib.import_module("services.system-service.system_service")
run_system_service = sys_service_mod.run_service

PORT_HTTP = 8080
PORT_SYSTEM = 8765

def free_port(port):
    """Ensure port is not in use; if occupied, terminate process."""
    try:
        out = subprocess.check_output(['/usr/sbin/lsof', '-ti', f':{port}'], stderr=subprocess.DEVNULL)
        pids = [int(p.strip()) for p in out.decode().split() if p.strip()]
        for pid in pids:
            if pid != os.getpid():
                try:
                    os.kill(pid, 9)
                except Exception:
                    pass
        time.sleep(0.4)
    except Exception:
        pass

class AureonDesktopServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def guess_type(self, path):
        # Ensure correct MIME types for SVGs and JSON
        if path.endswith('.svg'):
            return 'image/svg+xml'
        elif path.endswith('.json'):
            return 'application/json'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.css'):
            return 'text/css'
        return super().guess_type(path)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        pass

def print_banner():
    banner = f"""
\033[1;34m========================================================================\033[0m
\033[1;36m       █████╗ ██╗   ██╗██████╗ ███████╗ ██████╗ ███╗   ██╗\033[0m
\033[1;36m      ██╔══██╗██║   ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║\033[0m
\033[1;34m      ███████║██║   ██║██████╔╝█████╗  ██║   ██║██╔██╗ ██║\033[0m
\033[1;34m      ██╔══██║██║   ██║██╔══██╗██╔══╝  ██║   ██║██║╚██╗██║\033[0m
\033[1;35m      ██║  ██║╚██████╔╝██║  ██║███████╗╚██████╔╝██║ ╚████║\033[0m
\033[1;35m      ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝\033[0m
\033[1;37m                       Dream • Create • Explore                         \033[0m
\033[1;34m========================================================================\033[0m
 \033[1;32m●\033[0m AUREON Desktop Shell:     \033[1;4;34mhttp://127.0.0.1:{PORT_HTTP}/apps/desktop-shell/desktop.html\033[0m
 \033[1;32m●\033[0m Boot Sequence:            \033[1;4;34mhttp://127.0.0.1:{PORT_HTTP}/apps/desktop-shell/boot.html\033[0m
 \033[1;32m●\033[0m Login Screen:              \033[1;4;34mhttp://127.0.0.1:{PORT_HTTP}/apps/desktop-shell/login.html\033[0m
 \033[1;32m●\033[0m System Telemetry Daemon:  \033[1;4;34mhttp://127.0.0.1:{PORT_SYSTEM}/metrics\033[0m
\033[1;34m========================================================================\033[0m
\033[0;32m[STATUS]\033[0m AUREON OS is now running live! Opening in your default browser...
\033[0;33m[TIP]\033[0m Press \033[1;37mCtrl+C\033[0m in this terminal to gracefully shut down the servers.
"""
    print(banner)

def start_services():
    # 1. Clean ports before binding
    free_port(PORT_HTTP)
    free_port(PORT_SYSTEM)

    # 2. Start system metrics service in background daemon thread
    t_sys = threading.Thread(target=run_system_service, kwargs={'port': PORT_SYSTEM}, daemon=True)
    t_sys.start()
    time.sleep(0.3)

    # 3. Start HTTP server
    httpd = HTTPServer(('127.0.0.1', PORT_HTTP), AureonDesktopServer)

    print_banner()

    # 4. Open in default browser on macOS / Linux
    desktop_url = f"http://127.0.0.1:{PORT_HTTP}/apps/desktop-shell/desktop.html"
    opened = False
    if sys.platform == 'darwin' and os.path.exists('/usr/bin/open'):
        try:
            subprocess.run(['/usr/bin/open', desktop_url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            opened = True
        except Exception:
            pass

    if not opened:
        try:
            webbrowser.open(desktop_url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Aureon OS] Shutting down services cleanly...")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    start_services()
