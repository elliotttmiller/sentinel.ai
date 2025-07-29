#!/usr/bin/env python3
"""
Sentinel Desktop App Service Manager
Manages the local desktop app server, checks dependencies, analyzes logs, and provides diagnostics.
"""
import subprocess
import time
import psutil
import sys
import shutil
import platform
import importlib
import socket
import re
import datetime
from pathlib import Path
from typing import Dict
from colorama import init, Fore, Style
import requests
import os
init(autoreset=True)

APP_DIR = Path(__file__).parent
LOG_DIR = APP_DIR
DESKTOP_APP_PORT = 8001
REQUIRED_PYTHON_VERSION = (3, 9)
REQUIRED_PACKAGES = ["requests", "psutil", "uvicorn", "loguru", "sqlalchemy", "onnxruntime"]
REQUIRED_EXECUTABLES = ["uvicorn"]
ENV_FILE = APP_DIR / ".env"
LOG_FILE = APP_DIR / "startup_debug.log"

# --- Helper Functions ---
def print_header(title): print(f"\n{'='*20} {title.upper()} {'='*20}")
def print_success(msg): print(f"✅ {msg}")
def print_error(msg): print(f"❌ {msg}")
def print_info(msg): print(f"💡 {msg}")
def print_colored(msg, color): print(color + msg + Style.RESET_ALL)

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info.get('connections', []):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    return None

def stop_process(port):
    proc = find_process_by_port(port)
    if not proc:
        print_success(f"Desktop app is already stopped.")
        return
    print(f"🛑 Stopping Desktop App (PID: {proc.pid})...")
    proc.terminate()
    try: proc.wait(timeout=3)
    except psutil.TimeoutExpired: proc.kill()
    print_success(f"Desktop app stopped.")

def check_port_conflict(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print_error(f"Port {port} is already in use. Possible conflict.")
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info.get('connections', []):
                        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                            print_info(f"Port {port} is used by PID {proc.pid} ({proc.name()})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return True
    return False

def check_dependencies():
    print_info("Checking Python version...")
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        print_error(f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required. You have {platform.python_version()}.")
    else:
        print_success(f"Python version OK: {platform.python_version()}")
    print_info("Checking required packages...")
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            print_success(f"Package '{pkg}' is installed.")
        except ImportError:
            print_error(f"Package '{pkg}' is missing. Run 'pip install {pkg}'")
    print_info("Checking required executables...")
    for exe in REQUIRED_EXECUTABLES:
        if shutil.which(exe):
            print_success(f"Executable '{exe}' found.")
        else:
            print_error(f"Executable '{exe}' not found in PATH.")
    print_info("Checking .env file...")
    if ENV_FILE.exists():
        print_success(".env file found.")
    else:
        print_error(".env file not found in desktop-app directory.")

def check_db_connection():
    print_info("Testing database connection...")
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE)
        import sqlalchemy
        from sqlalchemy import create_engine
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise Exception("DATABASE_URL not set in .env file.")
        engine = create_engine(db_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        print_success("Database connection successful.")
    except Exception as e:
        print_error(f"Database connection failed: {e}")

def analyze_log_file(log_path):
    if not log_path.exists():
        print_error(f"Log file {log_path} does not exist.")
        return
    print_info(f"Last 20 lines of {log_path}:")
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()[-20:]
        for line in lines:
            if 'ERROR' in line or 'Traceback' in line or 'Exception' in line:
                print_colored(line.rstrip(), Fore.RED)
            else:
                print(line.rstrip())

def start_desktop_app():
    if find_process_by_port(DESKTOP_APP_PORT):
        print_success("Desktop app is already running.")
        return
    print(f"🚀 Starting Desktop App on port {DESKTOP_APP_PORT}...")
    log_file = open(LOG_DIR / "desktop_app.log", "w")
    subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(DESKTOP_APP_PORT), "--reload"],
        cwd=APP_DIR, stdout=log_file, stderr=log_file,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    time.sleep(3)
    if find_process_by_port(DESKTOP_APP_PORT):
        print_success(f"Desktop app started in background. See desktop_app.log.")
    else:
        print_error(f"Desktop app failed to start. Check desktop_app.log.")

def show_detailed_status():
    print_header("Detailed Service Status")
    status = "🟢 ONLINE" if find_process_by_port(DESKTOP_APP_PORT) else "🔴 OFFLINE"
    print(f"  - Desktop App (Port {DESKTOP_APP_PORT}): {status}")
    # Show health check
    try:
        resp = requests.get(f"http://localhost:{DESKTOP_APP_PORT}/system-stats", timeout=3)
        if resp.status_code == 200:
            print_success(f"/system-stats: {resp.json()}")
        else:
            print_error(f"/system-stats returned HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print_error(f"/system-stats check failed: {e}")
    analyze_log_file(LOG_FILE)
    analyze_log_file(LOG_DIR / "desktop_app.log")

def main():
    while True:
        print_header("Sentinel Desktop App Service Manager")
        status = "🟢 ONLINE" if find_process_by_port(DESKTOP_APP_PORT) else "🔴 OFFLINE"
        print(f"  - Desktop App (Port {DESKTOP_APP_PORT}): {status}")
        print("\n--- Actions ---")
        print("1. Start Desktop App Server")
        print("2. Stop Desktop App Server")
        print("3. Restart Desktop App Server")
        print("4. Show Detailed Status & Logs")
        print("5. Check Dependencies & Environment")
        print("6. Test Database Connection")
        print("0. Exit")
        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            start_desktop_app()
        elif choice == "2":
            stop_process(DESKTOP_APP_PORT)
        elif choice == "3":
            stop_process(DESKTOP_APP_PORT)
            time.sleep(2)
            start_desktop_app()
        elif choice == "4":
            show_detailed_status()
        elif choice == "5":
            check_dependencies()
        elif choice == "6":
            check_db_connection()
        elif choice == "0":
            print("Exiting. Services continue running if not stopped.")
            break
        else:
            print_error("Invalid choice.")

if __name__ == "__main__":
    main() 