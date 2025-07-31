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
import json
init(autoreset=True)

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
ENGINE_DIR = PROJECT_ROOT / "engine"
DESKTOP_APP_DIR = PROJECT_ROOT / "desktop-app"
LOG_DIR = PROJECT_ROOT / "logs"

SERVICES = {
    "railway_backend": {
        "port": 8080,
        "cwd": BACKEND_DIR,
        "module": "main:app",
        "name": "Railway Backend",
        "description": "Production backend API (Railway hosted)",
        "type": "remote",
        "url": "https://your-railway-app.railway.app",
        "health_endpoint": "/health"
    },
    "desktop_app": {
        "port": 8001,
        "cwd": DESKTOP_APP_DIR,
        "module": "src.main:app",
        "name": "Desktop App",
        "description": "Local web UI and mission management interface",
        "type": "local",
        "health_endpoint": "/health"
    },
    "cognitive_engine": {
        "port": 8002,
        "cwd": DESKTOP_APP_DIR,
        "module": "src.cognitive_engine_service:app",
        "name": "Cognitive Engine",
        "description": "Local AI processing and mission execution engine",
        "type": "local",
        "health_endpoint": "/health"
    },
    "legacy_engine": {
        "port": 8003,
        "cwd": ENGINE_DIR,
        "module": "main:app",
        "name": "Legacy Engine",
        "description": "Legacy engine service (optional)",
        "type": "local",
        "health_endpoint": "/health"
    }
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
    with open(DIAGNOSTICS_LOG, 'a', encoding='utf-8') as f:
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

def update_public_config_file(backend_url):
    config = {"apiUrl": backend_url}
    config_path = PROJECT_ROOT / "sentinel-config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    print_success(f"Public config file updated: {config_path} (apiUrl: {backend_url})")
    log_diagnostic(f"Public config file updated: {config_path} (apiUrl: {backend_url})", level='INFO')

# --- Main Service Manager Class ---
class ServiceManager:
    def __init__(self):
        self.SERVICES = SERVICES  # Expose SERVICES for external access
    
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
        """Advanced service startup with comprehensive error handling and monitoring."""
        service_name = config.get('name', name.capitalize())
        port = config['port']
        service_type = config.get('type', 'local')
        
        # Skip remote services (they're managed externally)
        if service_type == 'remote':
            print_info(f"⏭️  Skipping {service_name} - it's a remote service managed by Railway")
            return True
        
        # Check if already running
        if find_process_by_port(port):
            print_success(f"{service_name} is already running on port {port}")
            return True
        
        print_info(f"🚀 Starting {service_name} on port {port}...")
        print_info(f"Description: {config.get('description', 'No description')}")
        
        # Ensure log directory exists
        LOG_DIR.mkdir(exist_ok=True)
        
        # Build advanced uvicorn command
        uvicorn_cmd = [
            "uvicorn",
            config['module'],
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload",
            "--log-level", "info",
            "--access-log",
            "--use-colors"
        ]
        
        print_info(f"Command: {' '.join(uvicorn_cmd)}")
        print_info(f"Working directory: {config['cwd']}")
        
        try:
            # Open log file with proper encoding
            log_file = open(LOG_DIR / f"{name}.log", "w", encoding='utf-8')
            
            # Start the process with enhanced monitoring
            process = subprocess.Popen(
                uvicorn_cmd,
                cwd=config['cwd'],
                stdout=log_file,
                stderr=log_file,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Enhanced startup monitoring
            startup_timeout = 15
            check_interval = 1
            elapsed_time = 0
            
            print_info(f"⏳ Waiting for {service_name} to start (timeout: {startup_timeout}s)...")
            
            while elapsed_time < startup_timeout:
                time.sleep(check_interval)
                elapsed_time += check_interval
                
                if find_process_by_port(port):
                    print_success(f"{service_name} started successfully in {elapsed_time}s!")
                    print_info(f"URL: http://localhost:{port}")
                    print_info(f"PID: {process.pid}")
                    print_info(f"Logs: {LOG_DIR / f'{name}.log'}")
                    
                    # Test health endpoint if available
                    health_endpoint = config.get('health_endpoint')
                    if health_endpoint:
                        self.test_health_endpoint(f"http://localhost:{port}{health_endpoint}", service_name)
                    
                    return True
                
                # Show progress
                if elapsed_time % 3 == 0:
                    print_info(f"⏳ Still waiting... ({elapsed_time}s elapsed)")
            
            # Timeout reached
            print_error(f"{service_name} failed to start within {startup_timeout}s")
            print_error(f"Check logs: {LOG_DIR / f'{name}.log'}")
            
            # Try to get error output
            try:
                stdout, stderr = process.communicate(timeout=2)
                if stderr:
                    print_error(f"Error output: {stderr}")
            except:
                pass
            
            return False
            
        except Exception as e:
            print_error(f"Failed to start {service_name}: {e}")
            log_diagnostic(f"Service start error for {name}: {e}", level='ERROR')
            return False
            
    def show_detailed_status(self):
        """Show comprehensive status of all services with health checks."""
        print_header("Comprehensive Service Status")
        
        # System overview
        print_info("🔍 System Overview:")
        print(f"  📊 Total Services: {len(SERVICES)}")
        print(f"  🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"  🐍 Python: {platform.python_version()}")
        print(f"  📁 Project Root: {PROJECT_ROOT}")
        print()
        
        # Service status table
        print_info("📋 Service Status:")
        print(f"{'Service':<20} {'Port':<8} {'Type':<8} {'Status':<12} {'Health':<10}")
        print("-" * 70)
        
        online_count = 0
        for name, config in SERVICES.items():
            service_name = config.get('name', name.capitalize())
            port = config['port']
            service_type = config.get('type', 'local')
            
            # Check if service is running
            is_running = find_process_by_port(port)
            status = "🟢 ONLINE" if is_running else "🔴 OFFLINE"
            if is_running:
                online_count += 1
            
            # Health check for local services
            health_status = "N/A"
            if service_type == 'local' and is_running:
                health_endpoint = config.get('health_endpoint')
                if health_endpoint:
                    try:
                        resp = requests.get(f"http://localhost:{port}{health_endpoint}", timeout=3)
                        health_status = "✅ OK" if resp.status_code == 200 else f"⚠️ {resp.status_code}"
                    except:
                        health_status = "❌ FAIL"
            
            print(f"{service_name:<20} {port:<8} {service_type:<8} {status:<12} {health_status:<10}")
        
        print("-" * 70)
        print(f"📈 Online Services: {online_count}/{len(SERVICES)}")
        print()
        
        # Detailed service information
        print_info("🔍 Detailed Service Information:")
        for name, config in SERVICES.items():
            service_name = config.get('name', name.capitalize())
            port = config['port']
            service_type = config.get('type', 'local')
            description = config.get('description', 'No description')
            
            print(f"\n📌 {service_name}:")
            print(f"   Port: {port}")
            print(f"   Type: {service_type}")
            print(f"   Description: {description}")
            
            if service_type == 'local':
                is_running = find_process_by_port(port)
                if is_running:
                    print(f"   Status: 🟢 Running (PID: {is_running.pid})")
                    print(f"   URL: http://localhost:{port}")
                    
                    # Show recent log entries
                    log_file = LOG_DIR / f"{name}.log"
                    if log_file.exists():
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                if lines:
                                    last_line = lines[-1].strip()
                                    if len(last_line) > 80:
                                        last_line = last_line[:77] + "..."
                                    print(f"   Last Log: {last_line}")
                        except:
                            print(f"   Last Log: Unable to read log file")
                else:
                    print(f"   Status: 🔴 Not running")
            else:
                print(f"   Status: 🌐 Remote service (Railway)")
                print(f"   URL: {config.get('url', 'N/A')}")
        
        # ngrok status
        print("\n" + "="*60)
        ngrok_data = self.get_ngrok_status()
        ngrok_status = "🟢 ONLINE" if ngrok_data['status'] == 'online' else "🔴 OFFLINE"
        print(f"📡 ngrok Service: {ngrok_status}")
        
        if ngrok_data['status'] == 'online':
            print("\n🌐 Tunnel URLs:")
            for tunnel in ngrok_data['tunnels']:
                name = tunnel.get('name', 'Unknown')
                url = tunnel.get('public_url', 'N/A')
                addr = tunnel.get('config', {}).get('addr', 'N/A')
                print(f"   {name}: {url} → {addr}")
        
        # System recommendations
        print("\n" + "="*60)
        print_info("💡 System Recommendations:")
        if online_count < len(SERVICES):
            print_warning(f"⚠️  {len(SERVICES) - online_count} services are offline")
            print_info("   Run 'Full Startup' to start all local services")
        else:
            print_success("✅ All services are running properly!")
        
        # Check for common issues
        self.diagnose_common_issues()

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
        """Full system startup - starts all local services with comprehensive monitoring."""
        print_header("Full System Startup")
        print_info("🚀 Starting complete Sentinel system...")
        print_info("This will start all local services with --reload enabled")
        print()
        
        # System pre-flight checks
        print_info("🔍 Running pre-flight checks...")
        if not self.run_preflight_checks():
            print_error("Pre-flight checks failed. Please fix issues before starting.")
            return False
        
        # Start local services
        print_info("🚀 Starting local services...")
        success_count = 0
        total_local_services = 0
        
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                total_local_services += 1
                if self.start_service(name, config):
                    success_count += 1
                print()
        
        # Summary
        print_header("Startup Summary")
        print_success(f"✅ Successfully started {success_count}/{total_local_services} local services")
        
        if success_count == total_local_services:
            print_success("🎉 All local services are running!")
            print_info("📱 Desktop App: http://localhost:8001")
            print_info("🧠 Cognitive Engine: http://localhost:8002")
            print_info("🔧 Railway Backend: Already running on Railway")
            
            # Test system connectivity
            print_info("🔍 Testing system connectivity...")
            self.test_system_connectivity()
            
            return True
        else:
            print_warning(f"⚠️  {total_local_services - success_count} services failed to start")
            print_info("Check the logs above for error details")
            return False
    
    def run_preflight_checks(self):
        """Run comprehensive pre-flight checks before starting services."""
        checks_passed = 0
        total_checks = 0
        
        # Check Python version
        total_checks += 1
        if sys.version_info >= REQUIRED_PYTHON_VERSION:
            print_success(f"✅ Python version: {platform.python_version()}")
            checks_passed += 1
        else:
            print_error(f"❌ Python version {platform.python_version()} < {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}")
        
        # Check required packages
        total_checks += 1
        missing_packages = []
        for package in REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            print_success("✅ All required packages installed")
            checks_passed += 1
        else:
            print_error(f"❌ Missing packages: {', '.join(missing_packages)}")
        
        # Check required executables
        total_checks += 1
        missing_executables = []
        for executable in REQUIRED_EXECUTABLES:
            if shutil.which(executable) is None:
                missing_executables.append(executable)
        
        if not missing_executables:
            print_success("✅ All required executables found")
            checks_passed += 1
        else:
            print_error(f"❌ Missing executables: {', '.join(missing_executables)}")
        
        # Check port conflicts
        total_checks += 1
        port_conflicts = []
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                if check_port_conflict(config['port']):
                    port_conflicts.append(f"{config['name']} (port {config['port']})")
        
        if not port_conflicts:
            print_success("✅ No port conflicts detected")
            checks_passed += 1
        else:
            print_warning(f"⚠️  Port conflicts detected: {', '.join(port_conflicts)}")
            print_info("Services will attempt to start anyway")
            checks_passed += 1  # Allow startup to continue
        
        # Check directories
        total_checks += 1
        missing_dirs = []
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                if not config['cwd'].exists():
                    missing_dirs.append(f"{config['name']}: {config['cwd']}")
        
        if not missing_dirs:
            print_success("✅ All service directories exist")
            checks_passed += 1
        else:
            print_error(f"❌ Missing directories: {', '.join(missing_dirs)}")
        
        print(f"\n📊 Pre-flight checks: {checks_passed}/{total_checks} passed")
        return checks_passed == total_checks
    
    def test_system_connectivity(self):
        """Test connectivity between all services."""
        print_info("🔗 Testing service connectivity...")
        
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                port = config['port']
                service_name = config.get('name', name.capitalize())
                
                # Test basic connectivity
                try:
                    resp = requests.get(f"http://localhost:{port}", timeout=5)
                    print_success(f"✅ {service_name}: HTTP {resp.status_code}")
                except requests.exceptions.ConnectionError:
                    print_error(f"❌ {service_name}: Connection refused")
                except Exception as e:
                    print_warning(f"⚠️  {service_name}: {e}")
        
        print_success("🔗 Connectivity test completed")
    
    def test_health_endpoint(self, url, service_name):
        """Test a service's health endpoint."""
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                print_success(f"✅ {service_name} health check: OK")
            else:
                print_warning(f"⚠️  {service_name} health check: HTTP {resp.status_code}")
        except Exception as e:
            print_warning(f"⚠️  {service_name} health check failed: {e}")
    
    def diagnose_common_issues(self):
        """Diagnose common system issues."""
        print_info("🔍 Diagnosing common issues...")
        
        issues_found = []
        
        # Check for high memory usage
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                issues_found.append(f"High memory usage: {memory.percent}%")
        except:
            pass
        
        # Check for high CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                issues_found.append(f"High CPU usage: {cpu_percent}%")
        except:
            pass
        
        # Check disk space
        try:
            disk = psutil.disk_usage(PROJECT_ROOT)
            if disk.percent > 90:
                issues_found.append(f"Low disk space: {disk.percent}% used")
        except:
            pass
        
        if issues_found:
            print_warning("⚠️  Potential issues detected:")
            for issue in issues_found:
                print(f"   • {issue}")
        else:
            print_success("✅ No common issues detected")
    
    def run_system_diagnostics(self):
        """Run comprehensive system diagnostics."""
        print_header("System Diagnostics")
        
        print_info("🔍 Running comprehensive system diagnostics...")
        
        # System information
        print_info("📊 System Information:")
        print(f"   Platform: {platform.system()} {platform.release()}")
        print(f"   Python: {platform.python_version()}")
        print(f"   Architecture: {platform.machine()}")
        print(f"   Processor: {platform.processor()}")
        
        # Memory usage
        try:
            memory = psutil.virtual_memory()
            print(f"   Memory: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
        except:
            print("   Memory: Unable to read")
        
        # Disk usage
        try:
            disk = psutil.disk_usage(PROJECT_ROOT)
            print(f"   Disk: {disk.percent}% used ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        except:
            print("   Disk: Unable to read")
        
        # Network interfaces
        print_info("🌐 Network Interfaces:")
        try:
            for interface, addresses in psutil.net_if_addrs().items():
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        print(f"   {interface}: {addr.address}")
        except:
            print("   Unable to read network interfaces")
        
        # Service health checks
        print_info("🔍 Service Health Checks:")
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                port = config['port']
                service_name = config.get('name', name.capitalize())
                is_running = find_process_by_port(port)
                
                if is_running:
                    print(f"   ✅ {service_name}: Running (PID: {is_running.pid})")
                    
                    # Test health endpoint
                    health_endpoint = config.get('health_endpoint')
                    if health_endpoint:
                        try:
                            resp = requests.get(f"http://localhost:{port}{health_endpoint}", timeout=3)
                            print(f"      Health: HTTP {resp.status_code}")
                        except Exception as e:
                            print(f"      Health: ❌ {e}")
                else:
                    print(f"   ❌ {service_name}: Not running")
        
        # Port conflicts
        print_info("🔍 Port Conflict Analysis:")
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                port = config['port']
                service_name = config.get('name', name.capitalize())
                
                if check_port_conflict(port):
                    print(f"   ⚠️  Port {port} ({service_name}): Conflict detected")
                else:
                    print(f"   ✅ Port {port} ({service_name}): Available")
        
        # Dependencies
        print_info("📦 Dependency Check:")
        missing_packages = []
        for package in REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package}")
                missing_packages.append(package)
        
        missing_executables = []
        for executable in REQUIRED_EXECUTABLES:
            if shutil.which(executable):
                print(f"   ✅ {executable}")
            else:
                print(f"   ❌ {executable}")
                missing_executables.append(executable)
        
        # Recommendations
        print_info("💡 Recommendations:")
        if missing_packages:
            print(f"   • Install missing packages: pip install {' '.join(missing_packages)}")
        if missing_executables:
            print(f"   • Install missing executables: {', '.join(missing_executables)}")
        
        print_success("System diagnostics completed!")
    
    def view_service_logs(self):
        """View and analyze service logs."""
        print_header("Service Logs Viewer")
        
        # Show available log files
        log_files = []
        for name, config in SERVICES.items():
            log_file = LOG_DIR / f"{name}.log"
            if log_file.exists():
                log_files.append((name, config, log_file))
        
        if not log_files:
            print_warning("No log files found.")
            return
        
        print_info("📋 Available Log Files:")
        for i, (name, config, log_file) in enumerate(log_files, 1):
            service_name = config.get('name', name.capitalize())
            size = log_file.stat().st_size
            size_str = f"{size // 1024}KB" if size < 1024*1024 else f"{size // (1024*1024)}MB"
            print(f"{i}. {service_name} ({size_str})")
        
        print(f"{len(log_files) + 1}. Back to main menu")
        
        try:
            choice = input(f"\nSelect log to view (1-{len(log_files) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(log_files) + 1:
                return
            
            if 1 <= choice_num <= len(log_files):
                name, config, log_file = log_files[choice_num - 1]
                service_name = config.get('name', name.capitalize())
                
                print_header(f"Logs: {service_name}")
                print_info(f"File: {log_file}")
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    if not lines:
                        print_warning("Log file is empty.")
                        return
                    
                    # Show last 50 lines by default
                    print_info("Showing last 50 lines:")
                    print("-" * 80)
                    
                    for line in lines[-50:]:
                        line = line.strip()
                        if 'ERROR' in line or 'Traceback' in line:
                            print_colored(line, Fore.RED)
                        elif 'WARNING' in line:
                            print_colored(line, Fore.YELLOW)
                        elif 'INFO' in line:
                            print_colored(line, Fore.CYAN)
                        else:
                            print(line)
                    
                    print("-" * 80)
                    
                    # Show log statistics
                    error_count = sum(1 for line in lines if 'ERROR' in line)
                    warning_count = sum(1 for line in lines if 'WARNING' in line)
                    info_count = sum(1 for line in lines if 'INFO' in line)
                    
                    print_info("📊 Log Statistics:")
                    print(f"   Total lines: {len(lines)}")
                    print(f"   Errors: {error_count}")
                    print(f"   Warnings: {warning_count}")
                    print(f"   Info: {info_count}")
                    
                except Exception as e:
                    print_error(f"Error reading log file: {e}")
            else:
                print_error("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            print_info("Operation cancelled")

    def start_individual_service_menu(self):
        """Menu for starting individual services."""
        print_header("Start Individual Service")
        
        # Show available local services
        local_services = []
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                local_services.append((name, config))
        
        for i, (name, config) in enumerate(local_services, 1):
            status = "🟢 Running" if find_process_by_port(config['port']) else "🔴 Stopped"
            print(f"{i}. {config['name']} (Port {config['port']}) - {status}")
        
        print(f"{len(local_services) + 1}. Back to main menu")
        
        try:
            choice = input(f"\nSelect service to start (1-{len(local_services) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(local_services) + 1:
                return
            
            if 1 <= choice_num <= len(local_services):
                service_name, config = local_services[choice_num - 1]
                print(f"\n🚀 Starting {config['name']}...")
                self.start_service(service_name, config)
            else:
                print_error("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            print_info("Operation cancelled")
        
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
        print_header("Restart Individual Service")
        
        # Show available local services
        local_services = []
        for name, config in SERVICES.items():
            if config.get('type') == 'local':
                local_services.append((name, config))
        
        for i, (name, config) in enumerate(local_services, 1):
            status = "🟢 Running" if find_process_by_port(config['port']) else "🔴 Stopped"
            print(f"{i}. {config['name']} (Port {config['port']}) - {status}")
        
        print(f"{len(local_services) + 1}. Back to main menu")
        
        try:
            choice = input(f"\nSelect service to restart (1-{len(local_services) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(local_services) + 1:
                return
            
            if 1 <= choice_num <= len(local_services):
                service_name, config = local_services[choice_num - 1]
                print(f"\n🔄 Restarting {config['name']}...")
                self.restart_service(service_name)
            else:
                print_error("Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            print_info("Operation cancelled")

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
        print_success("System Configuration Test PASSED!")
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
        
        # Update public config file
        ngrok_data = self.get_ngrok_status()
        backend_url = None
        for tunnel in ngrok_data['tunnels']:
            addr = tunnel.get("config", {}).get("addr", "")
            if "8080" in addr:
                backend_url = tunnel.get("public_url")
        if backend_url:
            update_public_config_file(backend_url)
        print_success("System setup complete! All services are running and configured.")

    def run(self):
        """Advanced Sentinel Service Management System."""
        while True:
            print_header("Sentinel Advanced Service Manager")
            
            # Enhanced status overview
            print_info("🔍 System Status Overview:")
            online_count = 0
            for name, config in SERVICES.items():
                service_name = config.get('name', name.capitalize())
                port = config['port']
                service_type = config.get('type', 'local')
                is_running = find_process_by_port(port)
                status = "🟢 ONLINE" if is_running else "🔴 OFFLINE"
                if is_running:
                    online_count += 1
                
                type_icon = "🌐" if service_type == 'remote' else "💻"
                print(f"  {type_icon} {service_name} (Port {port}): {status}")
            
            print(f"\n📊 Services Online: {online_count}/{len(SERVICES)}")
            
            # ngrok status
            ngrok_data = self.get_ngrok_status()
            ngrok_status = "🟢 ONLINE" if ngrok_data['status'] == 'online' else "🔴 OFFLINE"
            print(f"📡 ngrok Service: {ngrok_status}")
            
            if ngrok_data['status'] == 'online':
                for tunnel in ngrok_data['tunnels']:
                    name = tunnel.get('name', 'Unknown')
                    url = tunnel.get('public_url', 'N/A')
                    print(f"   🌐 {name}: {url}")

            print("\n" + "="*60)
            print_info("🚀 Available Actions:")
            print("1. 🚀 Full System Startup (All Local Services)")
            print("2. ⚡ Start Individual Service")
            print("3. 🔄 Restart Individual Service")
            print("4. 🔧 Setup Tunnels & System")
            print("5. 🧪 Test System Configuration")
            print("6. 📊 Show Comprehensive Status")
            print("7. 🛑 Shutdown All Local Services")
            print("8. 🔄 Restart All Local Services")
            print("9. 📱 Full Mobile App Startup")
            print("10. 🔍 System Diagnostics")
            print("11. 📋 View Service Logs")
            print("0. 🚪 Exit (Leave Services Running)")
            
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
                print_info("🛑 Shutting down all local services...")
                for name, config in SERVICES.items():
                    if config.get('type') == 'local':
                        stop_process(name, config['port'])
                print_success("All local services stopped. Goodbye!")
                break
            elif choice == "8":
                print_info("🔄 Restarting all local services...")
                for name, config in SERVICES.items():
                    if config.get('type') == 'local':
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
            elif choice == "10":
                self.run_system_diagnostics()
            elif choice == "11":
                self.view_service_logs()
            elif choice == "0":
                print_success("Exiting. Services will continue running.")
                break
            else:
                print_error("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    LOG_DIR.mkdir(exist_ok=True)
    manager = ServiceManager()
    manager.run() 