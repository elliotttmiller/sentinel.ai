#!/usr/bin/env python3
"""
Sentinel Service Manager (Lean & Intelligent)
Manages the local backend and engine servers and ensures the backend
knows the current ngrok URL for the engine.
"""
import subprocess
import time
import requests
import psutil
import sys
import shutil
import platform
import importlib
import socket
import re
import datetime
from pathlib import Path
from typing import Dict, List, Optional
from colorama import init, Fore, Style
init(autoreset=True)

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
ENGINE_DIR = PROJECT_ROOT / "engine"
LOG_DIR = PROJECT_ROOT / "logs"

SERVICES = {
    "backend": {"port": 8080, "cwd": BACKEND_DIR},
    "engine": {"port": 8001, "cwd": ENGINE_DIR},
}

# --- Helper Functions ---
def print_header(title): print(f"\n{'='*20} {title.upper()} {'='*20}")
def print_success(msg): print(f"✅ {msg}")
def print_error(msg): print(f"❌ {msg}")
def print_info(msg): print(f"💡 {msg}")

def find_process_by_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info.get('connections', []):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    return None

def stop_process(name, port):
    proc = find_process_by_port(port)
    if not proc:
        print_success(f"{name.capitalize()} is already stopped.")
        return
    print(f"🛑 Stopping {name.capitalize()} (PID: {proc.pid})...")
    proc.terminate()
    try: proc.wait(timeout=3)
    except psutil.TimeoutExpired: proc.kill()
    print_success(f"{name.capitalize()} stopped.")

# --- Diagnostics Utilities ---
DIAGNOSTICS_LOG = LOG_DIR / "diagnostics.log"
REQUIRED_PYTHON_VERSION = (3, 8)
REQUIRED_PACKAGES = ["requests", "psutil", "uvicorn", "colorama"]
REQUIRED_EXECUTABLES = ["ngrok", "uvicorn"]
REQUIRED_ENV_VARS = ["DESKTOP_TUNNEL_URL", "DATABASE_URL"]

def log_diagnostic(message, level='INFO'):
    with open(DIAGNOSTICS_LOG, 'a') as f:
        f.write(f"{datetime.datetime.now().isoformat()} [{level}] {message}\n")

def print_colored(msg, color):
    print(color + msg + Style.RESET_ALL)

def print_error(msg):
    print_colored(f"❌ {msg}", Fore.RED)
    log_diagnostic(msg, level='ERROR')

def print_warning(msg):
    print_colored(f"⚠️  {msg}", Fore.YELLOW)
    log_diagnostic(msg, level='WARNING')

def print_success(msg):
    print_colored(f"✅ {msg}", Fore.GREEN)
    log_diagnostic(msg, level='SUCCESS')

def print_info(msg):
    print_colored(f"💡 {msg}", Fore.CYAN)
    log_diagnostic(msg, level='INFO')

def analyze_log_file(log_path):
    if not log_path.exists():
        print_warning(f"Log file {log_path} does not exist.")
        return
    print_info(f"Last 20 lines of {log_path}:")
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()[-20:]
        for line in lines:
            if 'ERROR' in line or 'Traceback' in line or 'Exception' in line:
                print_colored(line.rstrip(), Fore.RED)
            else:
                print(line.rstrip())

def check_health_endpoint(url, service_name):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            print_success(f"{service_name} /health: {resp.text}")
        else:
            print_warning(f"{service_name} /health returned HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print_error(f"{service_name} /health check failed: {e}")

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
    print_info("Checking required environment variables...")
    env_path = BACKEND_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            env_lines = f.read()
        for var in REQUIRED_ENV_VARS:
            if re.search(rf"^{var}=", env_lines, re.MULTILINE):
                print_success(f"Env var '{var}' found in .env.")
            else:
                print_warning(f"Env var '{var}' missing in .env.")
    else:
        print_warning(".env file not found in backend directory.")

def check_port_conflict(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print_warning(f"Port {port} is already in use. Possible conflict.")
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info.get('connections', []):
                        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                            print_info(f"Port {port} is used by PID {proc.pid} ({proc.name()})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

def generate_diagnostic_report():
    report_path = LOG_DIR / "diagnostic_report.txt"
    with open(report_path, 'w') as f:
        f.write(f"System Diagnostic Report\nGenerated: {datetime.datetime.now().isoformat()}\n\n")
        f.write(f"Python version: {platform.python_version()}\n")
        f.write(f"Platform: {platform.platform()}\n\n")
        f.write("Recent diagnostics log:\n")
        if DIAGNOSTICS_LOG.exists():
            with open(DIAGNOSTICS_LOG) as diag:
                f.writelines(diag.readlines()[-50:])
        f.write("\nBackend log (last 20 lines):\n")
        backend_log = LOG_DIR / "backend.log"
        if backend_log.exists():
            with open(backend_log) as bl:
                f.writelines(bl.readlines()[-20:])
        f.write("\nEngine log (last 20 lines):\n")
        engine_log = LOG_DIR / "engine.log"
        if engine_log.exists():
            with open(engine_log) as el:
                f.writelines(el.readlines()[-20:])
        f.write("\nBackend .env:\n")
        env_path = BACKEND_DIR / ".env"
        if env_path.exists():
            with open(env_path) as envf:
                f.writelines(envf.readlines())
    print_info(f"Diagnostic report generated: {report_path}")

def kill_process_on_port(port):
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info.get('connections', []):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    print_warning(f"Port {port} is in use by PID {proc.pid} ({proc.name()}). Killing process...")
                    log_diagnostic(f"Killing process {proc.pid} ({proc.name()}) on port {port}.", level='WARNING')
                    proc.kill()
                    killed = True
                    print_success(f"Killed process {proc.pid} on port {port}.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if not killed:
        print_info(f"No process found using port {port}.")

# --- Main Service Manager Class ---
class ServiceManager:
    def get_ngrok_status(self) -> Dict:
        """Gets ngrok status from the local agent API."""
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
            if response.status_code == 200:
                tunnels = response.json().get("tunnels", [])
                return {"status": "online", "tunnels": tunnels}
        except requests.RequestException:
            pass # ngrok is not running
        return {"status": "offline", "tunnels": []}

    def configure_backend_with_engine_url(self) -> bool:
        """Fetches the dynamic engine URL and updates the backend's .env file."""
        print_info("Fetching live ngrok URL for the engine...")
        ngrok_data = self.get_ngrok_status()
        if ngrok_data['status'] != 'online':
            print_error("ngrok service is not running. Cannot configure backend.")
            print_info("Please start your 'always-on' ngrok service first.")
            return False

        engine_url = None
        for tunnel in ngrok_data['tunnels']:
            if "localhost:8001" in tunnel.get("config", {}).get("addr", ""):
                engine_url = tunnel.get("public_url")
                break
        
        if not engine_url:
            print_error("Could not find an ngrok tunnel forwarding to port 8001.")
            return False
            
        print_success(f"Found live engine URL: {engine_url}")
        
        backend_env_path = BACKEND_DIR / ".env"
        env_vars = {}
        if backend_env_path.exists():
            with open(backend_env_path, "r") as f:
                for line in f:
                    if "=" in line:
                        key, val = line.strip().split("=", 1)
                        env_vars[key] = val
        
        env_vars["DESKTOP_TUNNEL_URL"] = f'{engine_url}'
        
        with open(backend_env_path, "w") as f:
            for key, val in env_vars.items():
                f.write(f"{key}={val}\n")
        
        print_success("Backend '.env' file auto-configured with live engine URL.")
        return True

    def start_service(self, name, config):
        if find_process_by_port(config['port']):
            print_success(f"{name.capitalize()} is already running.")
            return
        print(f"🚀 Starting {name.capitalize()} on port {config['port']}...")
        log_file = open(LOG_DIR / f"{name}.log", "w")
        subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(config['port']), "--reload"],
            cwd=config['cwd'], stdout=log_file, stderr=log_file,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(3)
        if find_process_by_port(config['port']):
            print_success(f"{name.capitalize()} started in background. See logs/{name}.log.")
        else:
            print_error(f"{name.capitalize()} failed to start. Check logs/{name}.log.")
            
    def show_detailed_status(self):
        """Show detailed status of all services."""
        print_header("Detailed Service Status")
        
        # Local services
        for name, config in SERVICES.items():
            status = "🟢 ONLINE" if find_process_by_port(config['port']) else "🔴 OFFLINE"
            print(f"  - {name.capitalize()} (Port {config['port']}): {status}")
        
        # ngrok service
        ngrok_data = self.get_ngrok_status()
        ngrok_status = "🟢 ONLINE" if ngrok_data['status'] == 'online' else "🔴 OFFLINE"
        print(f"  - ngrok Service: {ngrok_status}")
        
        # Show tunnel URLs if ngrok is online
        if ngrok_data['status'] == 'online':
            print("\n📡 Tunnel URLs:")
            for tunnel in ngrok_data['tunnels']:
                name = tunnel.get('name', 'Unknown')
                url = tunnel.get('public_url', 'N/A')
                addr = tunnel.get('config', {}).get('addr', 'N/A')
                print(f"    {name}: {url} → {addr}")

    def start_individual_service(self, service_name):
        """Start a specific service."""
        if service_name not in SERVICES:
            print_error(f"Unknown service: {service_name}")
            return False
            
        config = SERVICES[service_name]
        if service_name == "backend":
            # Configure backend with engine URL first
            if not self.configure_backend_with_engine_url():
                return False
        
        self.start_service(service_name, config)
        return True

    def restart_service(self, service_name):
        """Restart a specific service."""
        if service_name not in SERVICES:
            print_error(f"Unknown service: {service_name}")
            return False
            
        config = SERVICES[service_name]
        print(f"🔄 Restarting {service_name.capitalize()}...")
        stop_process(service_name, config['port'])
        time.sleep(2)
        return self.start_individual_service(service_name)

    def start_all_servers(self):
        """Start all servers needed for remote mobile app access."""
        print_info("Starting all servers for remote mobile app access...")
        
        # Configure backend with live engine URL
        if not self.configure_backend_with_engine_url():
            print_error("Failed to configure backend. Cannot start servers.")
            return False
            
        # Start both services
        self.start_service("backend", SERVICES["backend"])
        self.start_service("engine", SERVICES["engine"])
        
        print_success("All servers started! Your mobile app can now connect remotely.")
        return True

    def start_individual_service_menu(self):
        """Menu for starting individual services."""
        print_header("Start Individual Service")
        print("1. Backend (Port 8080)")
        print("2. Engine (Port 8001)")
        print("3. Back to main menu")
        
        choice = input("\nChoose service to start: ").strip()
        
        if choice == "1":
            self.start_individual_service("backend")
        elif choice == "2":
            self.start_individual_service("engine")
        elif choice == "3":
            return
        else:
            print_error("Invalid choice.")

    def restart_service_menu(self):
        """Menu for restarting individual services."""
        print_header("Restart Service")
        print("1. Backend (Port 8080)")
        print("2. Engine (Port 8001)")
        print("3. Back to main menu")
        
        choice = input("\nChoose service to restart: ").strip()
        
        if choice == "1":
            self.restart_service("backend")
        elif choice == "2":
            self.restart_service("engine")
        elif choice == "3":
            return
        else:
            print_error("Invalid choice.")

    def test_system_configuration(self):
        """Test and auto-optimize system configuration for mobile app access."""
        print_header("Test & Auto-Optimize System Configuration")
        
        optimization_needed = False
        optimization_steps = []
        
        # Check if all services are online
        all_services_online = True
        for name, config in SERVICES.items():
            if not find_process_by_port(config['port']):
                print_error(f"{name.capitalize()} is not running.")
                all_services_online = False
                optimization_needed = True
                optimization_steps.append(f"Start {name} service")
        
        if not all_services_online:
            print_info("Auto-optimizing: Starting missing services...")
            for name, config in SERVICES.items():
                if not find_process_by_port(config['port']):
                    self.start_service(name, config)
            print_success("All services are now running.")
        
        # Check ngrok status
        ngrok_data = self.get_ngrok_status()
        if ngrok_data['status'] != 'online':
            print_error("ngrok service is not running.")
            print_info("Auto-optimizing: Please start ngrok service manually.")
            print_info("Run: ngrok service start")
            return False
        
        # Check for required tunnels and auto-configure backend
        backend_url = None
        engine_url = None
        for tunnel in ngrok_data['tunnels']:
            addr = tunnel.get("config", {}).get("addr", "")
            if "8080" in addr:
                backend_url = tunnel.get("public_url")
            elif "8001" in addr:
                engine_url = tunnel.get("public_url")
        
        if not backend_url:
            print_error("Backend tunnel is not available.")
            print_info("Auto-optimizing: Please check ngrok configuration.")
            return False
            
        if not engine_url:
            print_error("Engine tunnel is not available.")
            print_info("Auto-optimizing: Please check ngrok configuration.")
            return False
        
        # Auto-configure backend with current engine URL
        print_info("Auto-optimizing: Configuring backend with current engine URL...")
        if self.configure_backend_with_engine_url():
            print_success("Backend configuration updated.")
        else:
            print_error("Failed to configure backend.")
            return False
        
        # Test backend connectivity
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            if response.status_code != 200:
                print_error(f"Backend health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Backend connectivity test failed: {str(e)}")
            return False
        
        # Test engine connectivity
        try:
            response = requests.get(f"{engine_url}/health", timeout=5)
            if response.status_code != 200:
                print_error(f"Engine health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Engine connectivity test failed: {str(e)}")
            return False
        
        # All tests passed
        print_success("🎉 System Configuration Test PASSED!")
        print_info("All services are online and accessible:")
        print(f"  - Backend: {backend_url}")
        print(f"  - Engine:  {engine_url}")
        print_info("Your mobile app should be able to connect successfully.")
        
        if optimization_needed:
            print_success("Configuration has been auto-optimized! ✅")
        else:
            print_success("Configuration is already optimized! ✅")
        return True

    def setup_tunnels_and_system(self):
        """Setup tunnels and configure the entire system."""
        print_header("Setup Tunnels and System")
        
        print_info("This will configure your entire system for remote access:")
        print("  - Configure ngrok tunnels")
        print("  - Setup backend with engine URL")
        print("  - Start all services")
        
        confirm = input("\nProceed with setup? (y/N): ").strip().lower()
        if confirm != 'y':
            print_info("Setup cancelled.")
            return
            
        # Configure backend with engine URL
        if not self.configure_backend_with_engine_url():
            print_error("Failed to configure backend.")
            return
            
        # Start all services
        self.start_service("backend", SERVICES["backend"])
        self.start_service("engine", SERVICES["engine"])
        
        print_success("System setup complete! All services are running and configured.")

    def run(self):
        """The main orchestration logic."""
        while True:
            print_header("Sentinel Local Development Manager")
            
            # Quick status overview
            for name, config in SERVICES.items():
                status = "🟢 ONLINE" if find_process_by_port(config['port']) else "🔴 OFFLINE"
                print(f"  - {name.capitalize()} (Port {config['port']}): {status}")
            
            # ngrok status with individual tunnel URLs
            ngrok_data = self.get_ngrok_status()
            ngrok_status = "🟢 ONLINE" if ngrok_data['status'] == 'online' else "🔴 OFFLINE"
            print(f"  - ngrok Service: {ngrok_status}")
            
            # Show individual tunnel URLs
            if ngrok_data['status'] == 'online':
                backend_url = None
                engine_url = None
                for tunnel in ngrok_data['tunnels']:
                    addr = tunnel.get("config", {}).get("addr", "")
                    if "8080" in addr:
                        backend_url = tunnel.get("public_url")
                    elif "8001" in addr:
                        engine_url = tunnel.get("public_url")
                
                if backend_url:
                    print(f"    📡 Backend Tunnel: 🟢 ONLINE  {backend_url}")
                else:
                    print(f"    📡 Backend Tunnel: 🔴 OFFLINE")
                    
                if engine_url:
                    print(f"    📡 Engine Tunnel:  🟢 ONLINE  {engine_url}")
                else:
                    print(f"    📡 Engine Tunnel:  🔴 OFFLINE")
            else:
                print(f"    📡 Tunnels: 🔴 OFFLINE")

            print("\n--- Actions ---")
            print("1. Start All Servers (for remote mobile app)")
            print("2. Start Service")
            print("3. Restart Service")
            print("4. Setup Tunnels & System")
            print("5. Test System Configuration")
            print("6. Show Detailed Status")
            print("7. Shutdown All Services")
            print("8. Restart All Services")
            print("9. Full Mobile App Startup")
            print("0. Exit (Leave Services Running)")
            
            choice = input("\nChoose an option: ").strip()

            if choice == "1":
                self.start_all_servers()
            elif choice == "2":
                self.start_individual_service_menu()
            elif choice == "3":
                self.restart_service_menu()
            elif choice == "4":
                self.setup_tunnels_and_system()
            elif choice == "5":
                self.test_system_configuration()
            elif choice == "6":
                self.show_detailed_status()
            elif choice == "7":
                print("Shutting down all local services...")
                for name, config in SERVICES.items(): 
                    stop_process(name, config['port'])
                print("All services stopped. Goodbye!")
                break
            elif choice == "8":
                print("Restarting all services...")
                for name, config in SERVICES.items():
                    stop_process(name, config['port'])
                time.sleep(2)
                self.start_all_servers()
                print_info("Testing and optimizing system configuration...")
                self.test_system_configuration()
            elif choice == "9":
                print_header("Full Mobile App Startup")
                try:
                    print_info("Running pre-flight dependency and environment checks...")
                    check_dependencies()
                    print_info("Ensuring ngrok is running...")
                    ngrok_data = self.get_ngrok_status()
                    if ngrok_data['status'] != 'online':
                        print_error("ngrok is not running. Please start ngrok and try again.")
                        print_info("Troubleshooting: Make sure ngrok is installed and running. Run 'ngrok start --all' or check your ngrok.yml.")
                        generate_diagnostic_report()
                        return
                    print_info("Stopping backend and engine if running...")
                    for name, config in SERVICES.items():
                        try:
                            stop_process(name, config['port'])
                        except Exception as e:
                            print_error(f"Failed to stop {name}: {e}")
                            print_info(f"Possible cause: Service may not have been running, or permissions issue.")
                    time.sleep(2)
                    print_info("Checking for port conflicts and killing if needed...")
                    for name, config in SERVICES.items():
                        kill_process_on_port(config['port'])
                    print_info("Configuring backend with live engine URL...")
                    if not self.configure_backend_with_engine_url():
                        print_error("Failed to configure backend with engine URL.")
                        print_info("Troubleshooting: Ensure ngrok tunnel for engine is up and .env is writable.")
                        generate_diagnostic_report()
                        return
                    print_info("Starting backend and engine servers...")
                    for name in ["backend", "engine"]:
                        try:
                            self.start_service(name, SERVICES[name])
                            log_path = LOG_DIR / f"{name}.log"
                            analyze_log_file(log_path)
                            if name == "backend":
                                check_health_endpoint("http://localhost:8080/health", "Backend")
                            elif name == "engine":
                                check_health_endpoint("http://localhost:8001/health", "Engine")
                        except Exception as e:
                            print_error(f"Failed to start {name}: {e}")
                            print_info(f"Check logs/{name}.log for details. Possible causes: Port in use, code error, missing dependencies.")
                            analyze_log_file(LOG_DIR / f"{name}.log")
                            generate_diagnostic_report()
                    print_info("Testing and optimizing system configuration...")
                    try:
                        self.test_system_configuration()
                    except Exception as e:
                        print_error(f"System configuration test failed: {e}")
                        print_info("Troubleshooting: Check ngrok tunnels, backend/engine logs, and .env config.")
                        generate_diagnostic_report()
                    # Print summary with ngrok URLs
                    ngrok_data = self.get_ngrok_status()
                    backend_url = None
                    engine_url = None
                    for tunnel in ngrok_data['tunnels']:
                        addr = tunnel.get("config", {}).get("addr", "")
                        if "8080" in addr:
                            backend_url = tunnel.get("public_url")
                        elif "8001" in addr:
                            engine_url = tunnel.get("public_url")
                    print_header("Mobile App Remote Access URLs")
                    if backend_url:
                        print_success(f"Backend API: {backend_url}")
                    else:
                        print_error("Backend ngrok URL not found.")
                        print_info("Troubleshooting: Is ngrok tunnel for backend running?")
                    if engine_url:
                        print_success(f"Engine API:  {engine_url}")
                    else:
                        print_error("Engine ngrok URL not found.")
                        print_info("Troubleshooting: Is ngrok tunnel for engine running?")
                    print_info("Your mobile app is ready to connect remotely!")
                except Exception as e:
                    print_error(f"Full Mobile App Startup failed: {e}")
                    print_info("Troubleshooting: Check all logs, ngrok status, and .env configuration. If the problem persists, restart your machine and try again.")
                    generate_diagnostic_report()
            elif choice == "0":
                print("Exiting without stopping services...")
                print("Goodbye! All services continue running.")
                break
            else:
                print_error("Invalid choice.")

if __name__ == "__main__":
    LOG_DIR.mkdir(exist_ok=True)
    manager = ServiceManager()
    manager.run()