#!/usr/bin/env python3
"""
Sentinel Service Manager (Optimized)
A robust script to manage the local development environment for Project Sentinel.
"""
import subprocess
import sys
import os
import time
import json
import requests
import psutil
from pathlib import Path
from typing import Dict, List, Optional

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
ENGINE_DIR = PROJECT_ROOT / "engine"
NGROK_CONFIG_FILE = Path(os.path.expanduser("~/.config/ngrok/ngrok.yml"))
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# --- Helper Functions ---
def print_header(title: str):
    print("\n" + "="*50)
    print(f" {title.upper()} ".center(50, "="))
    print("="*50)

def print_success(message: str):
    print(f"✅ {message}")

def print_error(message: str):
    print(f"❌ {message}")

def print_info(message: str):
    print(f"💡 {message}")

def find_process_by_port(port: int) -> Optional[psutil.Process]:
    """Finds a process listening on a given port."""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info['connections']:
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, KeyError):
            pass
    return None

class ServiceManager:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.ngrok_config = self._load_ngrok_config()

    def _load_ngrok_config(self) -> Dict:
        """Loads ngrok static domains from the user's default ngrok config."""
        try:
            import yaml
            if NGROK_CONFIG_FILE.exists():
                with open(NGROK_CONFIG_FILE, 'r') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print_error(f"Could not load ngrok config: {e}")
        return {}

    def get_service_status(self, service_name: str, port: int) -> bool:
        """Checks if a service is running by checking its port."""
        return find_process_by_port(port) is not None

    def _start_service(self, name: str, command: List[str], cwd: Path, port: int) -> bool:
        """Generic function to start a uvicorn service."""
        if self.get_service_status(name, port):
            print_success(f"{name.capitalize()} server is already running.")
            return True

        print(f"🚀 Starting {name.capitalize()} server on port {port}...")
        try:
            # Open log files for stdout and stderr
            stdout_log = open(LOG_DIR / f"{name}_stdout.log", "w")
            stderr_log = open(LOG_DIR / f"{name}_stderr.log", "w")

            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=stdout_log,
                stderr=stderr_log,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.processes[name] = process
            # Give it a moment to start up
            time.sleep(3)
            if process.poll() is None:
                print_success(f"{name.capitalize()} server started (PID: {process.pid}). Logs at {LOG_DIR}")
                return True
            else:
                print_error(f"{name.capitalize()} server failed to start. Check logs at {LOG_DIR}")
                return False
        except Exception as e:
            print_error(f"Failed to start {name.capitalize()} server: {e}")
            return False

    def start_backend(self) -> bool:
        return self._start_service("backend", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"], BACKEND_DIR, 8080)

    def start_engine(self) -> bool:
        return self._start_service("engine", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"], ENGINE_DIR, 8001)

    def start_ngrok(self) -> bool:
        """Starts the ngrok service, which should be configured to run as a service."""
        print("🚀 Attempting to manage ngrok service...")
        if self.get_ngrok_status().get('status') == 'online':
            print_success("ngrok service is already running.")
            return True
        try:
            # Try to start the service as an admin
            print_info("Attempting to start ngrok Windows service...")
            subprocess.run(["sc", "start", "ngrok"], capture_output=True, check=True)
            time.sleep(5) # Give service time to start
            status = self.get_ngrok_status()
            if status.get('status') == 'online':
                print_success("ngrok service started successfully.")
                self._print_ngrok_urls(status.get('tunnels', []))
                return True
            else:
                raise Exception("Service started but tunnels are not online.")
        except Exception as e:
            print_error(f"Failed to start ngrok service: {e}")
            print_info("Please ensure ngrok is installed as a service pointing to your default ngrok.yml.")
            print_info("You can run it manually in another terminal: ngrok start --all")
            return False

    def _stop_service(self, name: str, port: int) -> bool:
        """Generic function to stop a service by its port."""
        proc = find_process_by_port(port)
        if not proc:
            print_success(f"{name.capitalize()} is already stopped.")
            return True
        
        try:
            print(f"🛑 Stopping {name.capitalize()} (PID: {proc.pid})...")
            proc.terminate()
            proc.wait(timeout=5)
            print_success(f"{name.capitalize()} stopped.")
            return True
        except psutil.NoSuchProcess:
             print_success(f"{name.capitalize()} was already stopped.")
             return True
        except (psutil.TimeoutExpired, Exception) as e:
            print(f"Force-killing {name.capitalize()} (PID: {proc.pid})...")
            proc.kill()
            print_success(f"{name.capitalize()} stopped.")
            return False

    def stop_backend(self) -> bool:
        return self._stop_service("backend", 8080)

    def stop_engine(self) -> bool:
        return self._stop_service("engine", 8001)

    def stop_ngrok(self) -> bool:
        print("🛑 To stop the 'always-on' ngrok tunnel, run this in an ADMIN terminal:")
        print("   ngrok service stop")
        return True

    def stop_all(self):
        print_header("Stopping All Services")
        self.stop_backend()
        self.stop_engine()
        self.stop_ngrok()

    def get_ngrok_status(self) -> Dict:
        """Gets ngrok status from the local agent API."""
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
            if response.status_code == 200:
                tunnels = response.json().get("tunnels", [])
                return {"status": "online", "tunnels": tunnels}
        except requests.ConnectionError:
            pass # ngrok is not running
        except Exception as e:
            print_error(f"Error checking ngrok status: {e}")
        return {"status": "offline", "tunnels": []}

    def _print_ngrok_urls(self, tunnels: List[Dict]):
        backend_url = "Not found"
        engine_url = "Not found"
        for tunnel in tunnels:
            addr = tunnel.get("config", {}).get("addr", "")
            if "8080" in addr:
                backend_url = tunnel.get("public_url", "Error")
            elif "8001" in addr:
                engine_url = tunnel.get("public_url", "Error")
        
        print_info("--- Tunnel URLs ---")
        print(f"  Backend: {backend_url}")
        print(f"  Engine:  {engine_url}")
        print("---------------------")

    def show_status(self):
        print_header("Sentinel Service Status")
        backend_status = "🟢 ONLINE" if self.get_service_status("backend", 8080) else "🔴 OFFLINE"
        engine_status = "🟢 ONLINE" if self.get_service_status("engine", 8001) else "🔴 OFFLINE"
        ngrok_data = self.get_ngrok_status()
        ngrok_status = f"🟢 ONLINE ({len(ngrok_data['tunnels'])} tunnels)" if ngrok_data['status'] == 'online' else "🔴 OFFLINE"
        
        print(f"  Backend (port 8080): {backend_status}")
        print(f"  Engine  (port 8001): {engine_status}")
        print(f"  ngrok   (service):   {ngrok_status}")
        
        if ngrok_data['status'] == 'online':
            self._print_ngrok_urls(ngrok_data['tunnels'])

    def run_interactive(self):
        while True:
            print_header("Sentinel Local Development Manager")
            self.show_status()
            print("\n--- Actions ---")
            print("1. Start All Services")
            print("2. Stop All Services")
            print("3. Start Backend only")
            print("4. Start Engine only")
            print("5. Exit")
            
            choice = input("\nChoose an option: ").strip()
            if choice == "1":
                self.start_backend()
                self.start_engine()
                self.start_ngrok()
            elif choice == "2":
                self.stop_all()
            elif choice == "3":
                self.start_backend()
            elif choice == "4":
                self.start_engine()
            elif choice == "5":
                print("Stopping all services before exit...")
                self.stop_all()
                print("Goodbye!")
                break
            else:
                print_error("Invalid choice.")

if __name__ == "__main__":
    manager = ServiceManager()
    manager.run_interactive() 