#!/usr/bin/env python3
"""
Sentinel Comprehensive System Service Manager
Advanced service management, monitoring, diagnostics, and system control for the Sentinel ecosystem.
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
import json
import threading
import webbrowser
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from colorama import init, Fore, Style, Back
import requests
import os
import logging
from loguru import logger

# Enhanced debug logging configuration
DEBUG_LOG_FILE = Path(__file__).parent.parent.parent / "logs" / "debug_services.log"
DEBUG_LOG_FILE.parent.mkdir(exist_ok=True)

# Configure advanced debug logging
logger.remove()
logger.add(
    DEBUG_LOG_FILE,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)

# Debug context manager for detailed logging


class DebugContext:
    def __init__(self, operation: str, service: str = None):
        self.operation = operation
        self.service = service
        self.start_time = time.time()
        self.details = {}

    def __enter__(self):
        logger.debug(
            f"🚀 Starting operation: {self.operation}"
            + (f" for service: {self.service}" if self.service else "")
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            logger.error(
                f"❌ Operation failed: {self.operation} after {duration:.2f}s - {exc_type.__name__}: {exc_val}"
            )
        else:
            logger.debug(f"✅ Operation completed: {self.operation} in {duration:.2f}s")
            if self.details:
                logger.debug(f"📊 Operation details: {json.dumps(self.details, indent=2)}")

    def add_detail(self, key: str, value: Any):
        self.details[key] = value
        logger.debug(f"📝 {key}: {value}")


# Enhanced HTTP request with detailed logging


def debug_request(method: str, url: str, **kwargs) -> requests.Response:
    with DebugContext(f"HTTP {method}", url) as ctx:
        ctx.add_detail("method", method)
        ctx.add_detail("url", url)
        ctx.add_detail("headers", kwargs.get("headers", {}))
        ctx.add_detail("timeout", kwargs.get("timeout", 30))

        try:
            response = requests.request(method, url, **kwargs)
            ctx.add_detail("status_code", response.status_code)
            ctx.add_detail("response_time", response.elapsed.total_seconds())
            ctx.add_detail("response_size", len(response.content))
            ctx.add_detail("response_headers", dict(response.headers))

            if response.status_code >= 400:
                logger.warning(f"⚠️ HTTP {method} {url} returned {response.status_code}")
                logger.debug(f"Response content: {response.text[:500]}...")
            else:
                logger.debug(f"✅ HTTP {method} {url} successful")

            return response
        except requests.exceptions.RequestException as e:
            ctx.add_detail("error", str(e))
            logger.error(f"❌ HTTP {method} {url} failed: {e}")
            raise


# Import debug killer system
try:
    from .debug_killer import (
        handle_error_with_debug_killer,
        run_comprehensive_system_scan,
        run_system_diagnostics,
        log_debug_event,
    )
except ImportError:
    # Fallback for direct script execution
    from debug_killer import (
        handle_error_with_debug_killer,
        run_comprehensive_system_scan,
        run_system_diagnostics,
        log_debug_event,
    )

# Import onnxruntime fix
try:
    from .onnxruntime_fix import get_onnxruntime, is_onnxruntime_available, get_onnxruntime_error
except ImportError:
    # Fallback for direct script execution
    from onnxruntime_fix import get_onnxruntime, is_onnxruntime_available, get_onnxruntime_error

init(autoreset=True)

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

APP_DIR = Path(__file__).parent.parent.parent
LOG_DIR = APP_DIR / "logs"
DESKTOP_APP_PORT = 8001
BACKEND_PORT = 8002
MOBILE_APP_PORT = 8081

REQUIRED_PYTHON_VERSION = (3, 9)
REQUIRED_PACKAGES = [
    "requests",
    "psutil",
    "uvicorn",
    "loguru",
    "sqlalchemy",
    "fastapi",
    "pydantic",
    "colorama",
    "python-dotenv",
]
OPTIONAL_PACKAGES = ["onnxruntime", "torch", "transformers", "openai"]
REQUIRED_EXECUTABLES = ["uvicorn", "python", "pip"]

ENV_FILE = APP_DIR / ".env"
LOG_FILE = LOG_DIR / "startup_debug.log"
CONFIG_FILE = APP_DIR / "service_config.json"

# Service definitions
SERVICES = {
    "desktop_app": {
        "name": "Desktop App",
        "port": DESKTOP_APP_PORT,
        "command": [
            "uvicorn",
            "src.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(DESKTOP_APP_PORT),
            "--reload",
        ],
        "cwd": APP_DIR,
        "health_endpoint": "/system-stats",
        "log_file": LOG_DIR / "desktop_app.log",
    },
    "backend": {
        "name": "Backend API (Railway)",
        "port": None,  # No local port since it's on Railway
        "url": "https://sentinelai-production.up.railway.app",  # Railway backend URL
        "health_endpoint": "/health",
        "log_file": LOG_DIR / "backend.log",
        "is_remote": True,
    },
    "cognitive_engine": {
        "name": "Cognitive AI Engine",
        "port": 8002,
        "command": [
            "uvicorn",
            "src.cognitive_engine:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8002",
            "--reload",
        ],
        "cwd": APP_DIR,
        "health_endpoint": "/health",
        "log_file": LOG_DIR / "cognitive_engine.log",
        "startup_delay": 5,
    },
}

# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class ServiceStatus:
    name: str
    port: int
    is_running: bool
    pid: Optional[int]
    memory_usage: Optional[float]
    cpu_usage: Optional[float]
    uptime: Optional[float]
    last_check: datetime.datetime


@dataclass
class SystemInfo:
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def print_header(title: str, level: int = 1):
    """Print formatted header with different levels"""
    if level == 1:
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{'='*20} {title.upper()} {'='*20}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    elif level == 2:
        print(f"\n{Fore.YELLOW}{'='*40} {title.upper()} {'='*40}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}{'='*30} {title.upper()} {'='*30}{Style.RESET_ALL}")


def print_success(msg: str):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")


def print_error(msg: str):
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")


def print_info(msg: str):
    print(f"{Fore.BLUE}💡 {msg}{Style.RESET_ALL}")


def print_warning(msg: str):
    print(f"{Fore.YELLOW}⚠️ {msg}{Style.RESET_ALL}")


def print_critical(msg: str):
    print(f"{Fore.RED}{Back.RED}{Style.BRIGHT}🚨 {msg}{Style.RESET_ALL}")


def print_colored(msg: str, color: str):
    print(f"{color}{msg}{Style.RESET_ALL}")


def print_table(headers: List[str], rows: List[List[str]]):
    """Print formatted table"""
    if not rows:
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Print header
    header_str = " | ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
    print(f"{Fore.CYAN}{header_str}{Style.RESET_ALL}")
    print("-" * len(header_str))

    # Print rows
    for row in rows:
        row_str = " | ".join(f"{str(cell):<{w}}" for cell, w in zip(row, widths))
        print(row_str)


# =============================================================================
# PROCESS MANAGEMENT
# =============================================================================


def find_process_by_port(port: int) -> Optional[psutil.Process]:
    """Find process using specific port"""
    for proc in psutil.process_iter(["pid", "name", "connections"]):
        try:
            for conn in proc.info.get("connections", []):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None


def get_process_info(pid: int) -> Dict[str, Any]:
    """Get detailed process information"""
    try:
        proc = psutil.Process(pid)
        return {
            "pid": pid,
            "name": proc.name(),
            "cmdline": " ".join(proc.cmdline()),
            "memory_percent": proc.memory_percent(),
            "cpu_percent": proc.cpu_percent(),
            "create_time": datetime.datetime.fromtimestamp(proc.create_time()),
            "status": proc.status(),
            "num_threads": proc.num_threads(),
            "connections": len(proc.connections()),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return {}


def stop_process(port: int, force: bool = False) -> bool:
    """Stop process by port with optional force kill"""
    proc = find_process_by_port(port)
    if not proc:
        print_success(f"No process found on port {port}")
        return True

    try:
        print_info(f"Stopping process {proc.pid} on port {port}...")
        proc.terminate()

        # Wait for graceful shutdown
        try:
            proc.wait(timeout=5)
            print_success(f"Process {proc.pid} stopped gracefully")
            return True
        except psutil.TimeoutExpired:
            if force:
                proc.kill()
                print_warning(f"Force killed process {proc.pid}")
                return True
            else:
                print_error(f"Process {proc.pid} did not stop gracefully")
                return False
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print_error(f"Error stopping process: {e}")
        return False


def kill_all_related_processes():
    """Kill all processes related to Sentinel services with enhanced detection and force killing"""
    killed_processes = []

    print_header("🔪 Enhanced Process Killer", 2)
    print_info("Scanning for all related processes...")

    # Define comprehensive process patterns to kill
    kill_patterns = [
        "uvicorn",
        "sentinel",
        "main:app",
        "cognitive_engine",
        "desktop_app",
        "fastapi",
        "python.*main",
        "python.*cognitive",
        "python.*desktop",
    ]

    # Define ports to check and kill processes on
    target_ports = [8000, 8001, 8002, 8080, 3000, 5000]

    # Phase 1: Kill processes by command line patterns
    print_info("Phase 1: Killing processes by command line patterns...")
    for proc in psutil.process_iter(["pid", "name", "cmdline", "exe"]):
        try:
            cmdline = " ".join(proc.cmdline()).lower()
            proc_name = proc.name().lower()

            # Check if process matches any kill pattern
            should_kill = any(pattern in cmdline for pattern in kill_patterns) or any(
                pattern in proc_name for pattern in ["uvicorn", "python"]
            )

            if should_kill:
                print_warning(f"Killing process: {proc.pid} ({proc.name()}) - {cmdline[:100]}")
                try:
                    proc.terminate()
                    killed_processes.append(proc.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Phase 2: Kill processes by port usage
    print_info("Phase 2: Killing processes using target ports...")
    for proc in psutil.process_iter(["pid", "name", "connections"]):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port in target_ports:
                    print_warning(
                        f"Killing process on port {conn.laddr.port}: {proc.pid} ({proc.name()})"
                    )
                    try:
                        proc.terminate()
                        killed_processes.append(proc.pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Phase 3: Force kill any remaining processes
    print_info("Phase 3: Force killing remaining processes...")
    time.sleep(3)  # Wait longer for graceful termination

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.cmdline()).lower()
            proc_name = proc.name().lower()

            should_kill = any(pattern in cmdline for pattern in kill_patterns) or any(
                pattern in proc_name for pattern in ["uvicorn", "python"]
            )

            if should_kill:
                print_critical(f"Force killing process: {proc.pid} ({proc.name()})")
                try:
                    proc.kill()
                    killed_processes.append(proc.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Phase 4: Kill processes by port usage (force kill)
    print_info("Phase 4: Force killing processes on target ports...")
    for proc in psutil.process_iter(["pid", "name", "connections"]):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port in target_ports:
                    print_critical(
                        f"Force killing process on port {conn.laddr.port}: {proc.pid} ({proc.name()})"
                    )
                    try:
                        proc.kill()
                        killed_processes.append(proc.pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Phase 5: Use system commands for stubborn processes
    print_info("Phase 5: Using system commands for stubborn processes...")
    try:
        # Windows specific commands
        if platform.system() == "Windows":
            # Kill processes by port using netstat and taskkill
            for port in target_ports:
                try:
                    # Find PID using port
                    result = subprocess.run(
                        f"netstat -ano | findstr :{port}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    if result.stdout:
                        for line in result.stdout.split("\n"):
                            if f":{port}" in line:
                                parts = line.split()
                                if len(parts) > 4:
                                    pid = parts[-1]
                                    print_critical(f"System killing process {pid} on port {port}")
                                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                                    killed_processes.append(int(pid))
                except Exception as e:
                    print_warning(f"System command failed for port {port}: {e}")
        else:
            # Linux/Mac specific commands
            for port in target_ports:
                try:
                    result = subprocess.run(
                        f"lsof -ti:{port}", shell=True, capture_output=True, text=True
                    )
                    if result.stdout:
                        pids = result.stdout.strip().split("\n")
                        for pid in pids:
                            if pid:
                                print_critical(f"System killing process {pid} on port {port}")
                                subprocess.run(f"kill -9 {pid}", shell=True)
                                killed_processes.append(int(pid))
                except Exception as e:
                    print_warning(f"System command failed for port {port}: {e}")
    except Exception as e:
        print_warning(f"System command execution failed: {e}")

    # Final verification
    print_info("Final verification: Checking for remaining processes...")
    remaining_processes = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.cmdline()).lower()
            if any(pattern in cmdline for pattern in kill_patterns):
                remaining_processes.append(f"{proc.pid} ({proc.name()})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if remaining_processes:
        print_warning(f"Remaining processes: {', '.join(remaining_processes)}")
    else:
        print_success("All related processes successfully terminated!")

    print_success(f"Killed {len(killed_processes)} processes")
    return killed_processes


# =============================================================================
# SYSTEM MONITORING
# =============================================================================


def get_system_info() -> SystemInfo:
    """Get comprehensive system information"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()

    # Count active connections
    active_connections = 0
    for proc in psutil.process_iter(["connections"]):
        try:
            active_connections += len(proc.info.get("connections", []))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return SystemInfo(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_usage=disk.percent,
        network_io={
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv,
        },
        active_connections=active_connections,
    )


def get_service_status(service_name: str) -> ServiceStatus:
    """Get detailed status of a specific service with enhanced debug logging"""
    with DebugContext("get_service_status", service_name) as ctx:
        service_config = SERVICES.get(service_name)
        if not service_config:
            ctx.add_detail("error", f"Service {service_name} not found in SERVICES")
            return ServiceStatus(
                name=service_name,
                port=0,
                is_running=False,
                pid=None,
                memory_usage=None,
                cpu_usage=None,
                uptime=None,
                last_check=datetime.datetime.now(),
            )

        ctx.add_detail(
            "service_config",
            {
                "name": service_config["name"],
                "port": service_config.get("port"),
                "url": service_config.get("url"),
                "health_endpoint": service_config.get("health_endpoint"),
                "is_remote": service_config.get("is_remote", False),
            },
        )

        # Handle remote services (like Railway backend)
        if service_config.get("is_remote"):
            ctx.add_detail("service_type", "remote")
            try:
                # Check if remote service is accessible
                health_url = f"{service_config['url']}/health"
                ctx.add_detail("health_url", health_url)

                response = debug_request("GET", health_url, timeout=5)
                is_running = response.status_code == 200

                ctx.add_detail("response_status", response.status_code)
                ctx.add_detail("response_time", response.elapsed.total_seconds())
                ctx.add_detail("is_running", is_running)

                if not is_running:
                    logger.warning(
                        f"⚠️ Remote service {service_name} returned status {response.status_code}"
                    )
                    ctx.add_detail("error", f"HTTP {response.status_code}")

            except Exception as e:
                is_running = False
                ctx.add_detail("remote_error", str(e))
                logger.error(f"❌ Remote service {service_name} check failed: {e}")

            return ServiceStatus(
                name=service_config["name"],
                port=service_config.get("port", 0),
                is_running=is_running,
                pid=None,  # No local PID for remote services
                memory_usage=None,
                cpu_usage=None,
                uptime=None,
                last_check=datetime.datetime.now(),
            )

        # Handle local services
        ctx.add_detail("service_type", "local")
        port = service_config["port"]
        ctx.add_detail("port", port)

        proc = find_process_by_port(port)
        if proc:
            ctx.add_detail("process_found", True)
            ctx.add_detail("process_pid", proc.pid)
            ctx.add_detail("process_cmdline", " ".join(proc.cmdline()))

            try:
                memory_usage = proc.memory_percent()
                cpu_usage = proc.cpu_percent()
                uptime = time.time() - proc.create_time()

                ctx.add_detail("memory_usage", memory_usage)
                ctx.add_detail("cpu_usage", cpu_usage)
                ctx.add_detail("uptime", uptime)

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                memory_usage = cpu_usage = uptime = None
                ctx.add_detail("process_access_error", str(e))
                logger.warning(f"⚠️ Could not access process {proc.pid}: {e}")
        else:
            proc = None
            memory_usage = cpu_usage = uptime = None
            ctx.add_detail("process_found", False)

        ctx.add_detail("final_is_running", proc is not None)
        return ServiceStatus(
            name=service_config["name"],
            port=service_config["port"],
            is_running=proc is not None,
            pid=proc.pid if proc else None,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            uptime=uptime,
            last_check=datetime.datetime.now(),
        )


def monitor_services_continuous():
    """Continuous monitoring of all services"""
    print_header("Continuous Service Monitoring", 2)
    print_info("Press Ctrl+C to stop monitoring")

    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print_header("Real-time Service Status", 2)

            # System info
            sys_info = get_system_info()
            print(
                f"CPU: {sys_info.cpu_percent:.1f}% | "
                f"Memory: {sys_info.memory_percent:.1f}% | "
                f"Disk: {sys_info.disk_usage:.1f}% | "
                f"Connections: {sys_info.active_connections}"
            )

            # Service status
            headers = ["Service", "Status", "PID", "Memory%", "CPU%", "Uptime"]
            rows = []

            for service_name in SERVICES:
                status = get_service_status(service_name)
                status_icon = "🟢" if status.is_running else "🔴"
                pid_str = str(status.pid) if status.pid else "N/A"
                memory_str = f"{status.memory_usage:.1f}%" if status.memory_usage else "N/A"
                cpu_str = f"{status.cpu_usage:.1f}%" if status.cpu_usage else "N/A"
                uptime_str = f"{status.uptime/60:.1f}m" if status.uptime else "N/A"

                rows.append(
                    [
                        status.name,
                        f"{status_icon} {'ONLINE' if status.is_running else 'OFFLINE'}",
                        pid_str,
                        memory_str,
                        cpu_str,
                        uptime_str,
                    ]
                )

            print_table(headers, rows)
            time.sleep(2)

    except KeyboardInterrupt:
        print_info("Monitoring stopped")


# =============================================================================
# SERVICE MANAGEMENT
# =============================================================================


def start_service(service_name: str, background: bool = True) -> bool:
    """Start a specific service"""
    service_config = SERVICES.get(service_name)
    if not service_config:
        print_error(f"Unknown service: {service_name}")
        return False

    # Handle remote services (like Railway backend)
    if service_config.get("is_remote"):
        print_info(f"Checking remote service: {service_config['name']}")
        try:
            response = requests.get(f"{service_config['url']}/health", timeout=10)
            if response.status_code == 200:
                print_success(f"{service_config['name']} is accessible")
                return True
            else:
                print_error(f"{service_config['name']} returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Failed to connect to {service_config['name']}: {e}")
            return False

    # Handle local services
    # Check if already running
    if find_process_by_port(service_config["port"]):
        print_success(f"{service_config['name']} is already running")
        return True

    # Check port availability
    if check_port_conflict(service_config["port"]):
        print_error(f"Port {service_config['port']} is already in use")
        return False

    print_info(f"Starting {service_config['name']} on port {service_config['port']}...")

    try:
        # Ensure log directory exists
        service_config["log_file"].parent.mkdir(parents=True, exist_ok=True)

        # Start process
        if background:
            log_file = open(service_config["log_file"], "w")
            process = subprocess.Popen(
                service_config["command"],
                cwd=service_config["cwd"],
                stdout=log_file,
                stderr=log_file,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            # Wait for startup
            time.sleep(3)

            if find_process_by_port(service_config["port"]):
                print_success(f"{service_config['name']} started successfully")
                return True
            else:
                print_error(f"{service_config['name']} failed to start")
                return False
        else:
            # Run in foreground
            subprocess.run(service_config["command"], cwd=service_config["cwd"])
            return True

    except Exception as e:
        print_error(f"Error starting {service_config['name']}: {e}")
        return False


def stop_service(service_name: str, force: bool = False) -> bool:
    """Stop a specific service"""
    service_config = SERVICES.get(service_name)
    if not service_config:
        print_error(f"Unknown service: {service_name}")
        return False

    return stop_process(service_config["port"], force)


def restart_service(service_name: str) -> bool:
    """Restart a specific service"""
    print_info(f"Restarting {service_name}...")

    # Stop service
    if not stop_service(service_name):
        print_warning(f"Could not stop {service_name}, attempting force stop")
        stop_service(service_name, force=True)

    # Wait a moment
    time.sleep(2)

    # Start service
    return start_service(service_name)


def start_all_services() -> Dict[str, bool]:
    """Start all services"""
    print_header("Starting All Services", 2)
    results = {}

    for service_name in SERVICES:
        print_info(f"Starting {service_name}...")
        results[service_name] = start_service(service_name)

    return results


def stop_all_services() -> Dict[str, bool]:
    """Stop all services"""
    print_header("Stopping All Services", 2)
    results = {}

    for service_name in SERVICES:
        print_info(f"Stopping {service_name}...")
        results[service_name] = stop_service(service_name)

    return results


def restart_all_services() -> Dict[str, bool]:
    """Restart all services"""
    print_header("Restarting All Services", 2)

    # Stop all services
    stop_results = stop_all_services()
    time.sleep(3)

    # Start all services
    start_results = start_all_services()

    return {name: start_results.get(name, False) for name in SERVICES}


def full_desktop_app_startup() -> Dict[str, bool]:
    """
    Comprehensive full desktop app system startup
    Starts all required services, servers, and the cognitive AI engine
    """
    print_header("🚀 FULL DESKTOP APP SYSTEM STARTUP", 1)
    print_info("Initializing complete Sentinel ecosystem...")

    results = {}

    # Phase 1: Pre-flight checks
    print_header("Phase 1: Pre-flight System Checks", 2)

    # Check dependencies
    print_info("Checking system dependencies...")
    dependencies = check_dependencies()
    missing_required = [
        pkg for pkg, installed in dependencies["required_packages"].items() if not installed
    ]

    if missing_required:
        print_warning(f"Missing required packages: {', '.join(missing_required)}")
        print_info("Attempting to install missing dependencies...")
        if not install_missing_dependencies():
            print_error("Failed to install required dependencies. Please install manually.")
            return {"error": "Dependency installation failed"}

    # Check environment
    print_info("Validating environment configuration...")
    if not ENV_FILE.exists():
        print_error("Environment file (.env) not found!")
        print_info("Please ensure .env file exists with required configuration.")
        return {"error": "Environment file missing"}

    # Check database connection
    print_info("Testing database connectivity...")
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE)
        import sqlalchemy
        from sqlalchemy import create_engine

        db_url = os.getenv("DATABASE_URL")
        if db_url:
            engine = create_engine(db_url, connect_args={"connect_timeout": 5})
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            print_success("Database connection successful")
        else:
            print_warning("DATABASE_URL not set - some features may be limited")
    except Exception as e:
        print_warning(f"Database connection failed: {e} - continuing with startup")

    # Check cognitive engine configuration
    print_info("Checking cognitive engine configuration...")
    try:
        if not check_cognitive_engine_config():
            print_warning(
                "Cognitive engine configuration issues detected - AI features may be limited"
            )
    except Exception as e:
        print_warning(f"Cognitive engine configuration check failed: {e}")
        print_info("Continuing with startup - AI features may be limited")

    # Phase 2: Start core services
    print_header("Phase 2: Starting Core Services", 2)

    # Check Railway backend
    print_info("Checking Railway Backend API...")
    results["backend"] = start_service("backend")
    if results["backend"]:
        print_success("Railway Backend API is accessible")
        time.sleep(2)  # Brief wait
    else:
        print_warning("Railway Backend API is not accessible - continuing with desktop app")

    # Start desktop app
    print_info("Starting Desktop App...")
    results["desktop_app"] = start_service("desktop_app")
    if results["desktop_app"]:
        print_success("Desktop App started successfully")
        time.sleep(3)  # Wait for desktop app to stabilize
    else:
        print_error("Desktop App failed to start")
        return results

    # Phase 3: Initialize Cognitive AI Engine
    print_header("Phase 3: Initializing Cognitive AI Engine", 2)

    print_info("Starting Cognitive AI Engine...")
    results["cognitive_engine"] = start_service("cognitive_engine")

    if results["cognitive_engine"]:
        print_success("Cognitive AI Engine started successfully")

        # Wait for cognitive engine to fully initialize
        cognitive_startup_delay = SERVICES["cognitive_engine"].get("startup_delay", 5)
        print_info(
            f"Waiting {cognitive_startup_delay} seconds for cognitive engine initialization..."
        )
        time.sleep(cognitive_startup_delay)

        # Test cognitive engine health
        try:
            response = requests.get(f"http://localhost:8002/health", timeout=10)
            if response.status_code == 200:
                print_success("Cognitive AI Engine health check passed")
            else:
                print_warning(f"Cognitive AI Engine health check returned {response.status_code}")
        except Exception as e:
            print_warning(f"Cognitive AI Engine health check failed: {e}")
    else:
        print_warning("Cognitive AI Engine failed to start - some AI features may be limited")

    # Phase 4: System validation and optimization
    print_header("Phase 4: System Validation", 2)

    # Comprehensive health check
    print_info("Performing comprehensive system health check...")
    health_results = comprehensive_health_check()

    # Check if all critical services are running
    critical_services = ["desktop_app"]
    all_critical_running = all(
        health_results.get(service, {}).get("status") in ["healthy", "running"]
        for service in critical_services
    )

    if all_critical_running:
        print_success("All critical services are running")
    else:
        print_warning("Some services may not be fully operational")

    # Phase 5: Open user interface
    print_header("Phase 5: Launching User Interface", 2)

    try:
        print_info("Opening desktop app in default browser...")
        webbrowser.open(f"http://localhost:{DESKTOP_APP_PORT}")
        print_success("Desktop app opened in browser")
    except Exception as e:
        print_warning(f"Could not open browser automatically: {e}")
        print_info(f"Please manually navigate to: http://localhost:{DESKTOP_APP_PORT}")

    # Phase 6: Final status report
    print_header("🎉 SYSTEM STARTUP COMPLETE", 1)

    # Show final status
    print(f"{Fore.CYAN}Final System Status:{Style.RESET_ALL}")
    for service_name, result in results.items():
        status_icon = "🟢" if result else "🔴"
        service_name_display = SERVICES[service_name]["name"]
        print(f"  {status_icon} {service_name_display}: {'ONLINE' if result else 'OFFLINE'}")

    # Show system resources
    sys_info = get_system_info()
    print(f"\n{Fore.CYAN}System Resources:{Style.RESET_ALL}")
    print(f"  CPU: {sys_info.cpu_percent:.1f}%")
    print(f"  Memory: {sys_info.memory_percent:.1f}%")
    print(f"  Disk: {sys_info.disk_usage:.1f}%")

    # Show available endpoints
    print(f"\n{Fore.CYAN}Available Endpoints:{Style.RESET_ALL}")
    print(f"  Desktop App: http://localhost:{DESKTOP_APP_PORT}")
    if results.get("backend"):
        print(f"  Backend API: {SERVICES['backend']['url']}")
    if results.get("cognitive_engine"):
        print(f"  Cognitive Engine: http://localhost:8002")

    print(f"\n{Fore.GREEN}✅ Full Desktop App System Startup Complete!{Style.RESET_ALL}")
    print_info("Your Sentinel ecosystem is now ready for AI-powered missions!")

    return results


# =============================================================================
# HEALTH CHECKS & DIAGNOSTICS
# =============================================================================


def check_port_conflict(port: int) -> bool:
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("localhost", port))
        return result == 0


def kill_process_on_port(port: int) -> bool:
    """Kill any process using the specified port"""
    print_warning(f"Killing process on port {port}...")

    killed = False

    # Method 1: Use psutil to find and kill process
    for proc in psutil.process_iter(["pid", "name", "connections"]):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port == port:
                    print_warning(f"Found process {proc.pid} ({proc.name()}) on port {port}")
                    try:
                        proc.terminate()
                        time.sleep(1)
                        proc.kill()  # Force kill if terminate didn't work
                        killed = True
                        print_success(f"Killed process {proc.pid} on port {port}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Method 2: Use system commands for stubborn processes
    try:
        if platform.system() == "Windows":
            # Windows: Use netstat and taskkill
            result = subprocess.run(
                f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True
            )
            if result.stdout:
                for line in result.stdout.split("\n"):
                    if f":{port}" in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            print_critical(f"System killing process {pid} on port {port}")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                            killed = True
        else:
            # Linux/Mac: Use lsof and kill
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
            if result.stdout:
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid:
                        print_critical(f"System killing process {pid} on port {port}")
                        subprocess.run(f"kill -9 {pid}", shell=True)
                        killed = True
    except Exception as e:
        print_warning(f"System command failed for port {port}: {e}")

    return killed


def health_check_service(service_name: str) -> Dict[str, Any]:
    """Perform comprehensive health check on a service with enhanced debug logging"""
    with DebugContext("health_check_service", service_name) as ctx:
        service_config = SERVICES.get(service_name)
        if not service_config:
            ctx.add_detail("error", f"Unknown service: {service_name}")
            return {"status": "unknown", "error": f"Unknown service: {service_name}"}

        ctx.add_detail(
            "service_config",
            {
                "name": service_config["name"],
                "port": service_config.get("port"),
                "url": service_config.get("url"),
                "health_endpoint": service_config.get("health_endpoint"),
                "is_remote": service_config.get("is_remote", False),
            },
        )

        health_info = {
            "service": service_name,
            "port": service_config.get("port"),
            "process_running": False,
            "port_accessible": False,
            "health_endpoint": False,
            "response_time": None,
            "memory_usage": None,
            "cpu_usage": None,
        }

        # Handle remote services (like Railway backend)
        if service_config.get("is_remote"):
            ctx.add_detail("service_type", "remote")
            try:
                health_url = f"{service_config['url']}{service_config['health_endpoint']}"
                ctx.add_detail("health_url", health_url)

                start_time = time.time()
                response = debug_request("GET", health_url, timeout=10)
                health_info["response_time"] = (time.time() - start_time) * 1000
                health_info["health_endpoint"] = response.status_code == 200
                health_info["status"] = "healthy" if health_info["health_endpoint"] else "unhealthy"

                ctx.add_detail("response_status", response.status_code)
                ctx.add_detail("response_time_ms", health_info["response_time"])
                ctx.add_detail("health_endpoint_ok", health_info["health_endpoint"])
                ctx.add_detail("final_status", health_info["status"])

                if not health_info["health_endpoint"]:
                    logger.warning(
                        f"⚠️ Remote service {service_name} health check failed: HTTP {response.status_code}"
                    )
                    ctx.add_detail("health_error", f"HTTP {response.status_code}")

            except Exception as e:
                health_info["health_endpoint_error"] = str(e)
                health_info["status"] = "unreachable"
                ctx.add_detail("remote_error", str(e))
                logger.error(f"❌ Remote service {service_name} health check failed: {e}")

            return health_info

        # Handle local services
        ctx.add_detail("service_type", "local")
        port = service_config["port"]
        ctx.add_detail("port", port)

        # Check if process is running
        proc = find_process_by_port(port)
        if proc:
            ctx.add_detail("process_found", True)
            ctx.add_detail("process_pid", proc.pid)
            health_info["process_running"] = True

            try:
                health_info["memory_usage"] = proc.memory_percent()
                health_info["cpu_usage"] = proc.cpu_percent()
                ctx.add_detail("memory_usage", health_info["memory_usage"])
                ctx.add_detail("cpu_usage", health_info["cpu_usage"])
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                ctx.add_detail("process_access_error", str(e))
                logger.warning(f"⚠️ Could not access process {proc.pid}: {e}")
        else:
            ctx.add_detail("process_found", False)

        # Check if port is accessible
        port_conflict = check_port_conflict(port)
        ctx.add_detail("port_conflict", port_conflict)
        if not port_conflict:
            health_info["port_accessible"] = True
            ctx.add_detail("port_accessible", True)
        else:
            ctx.add_detail("port_accessible", False)

        # Check health endpoint
        if health_info["process_running"] and health_info["port_accessible"]:
            try:
                health_url = f"http://localhost:{port}{service_config['health_endpoint']}"
                ctx.add_detail("local_health_url", health_url)

                start_time = time.time()
                response = debug_request("GET", health_url, timeout=5)
                health_info["response_time"] = (time.time() - start_time) * 1000
                health_info["health_endpoint"] = response.status_code == 200

                ctx.add_detail("health_response_status", response.status_code)
                ctx.add_detail("health_response_time_ms", health_info["response_time"])
                ctx.add_detail("health_endpoint_ok", health_info["health_endpoint"])

                if not health_info["health_endpoint"]:
                    logger.warning(
                        f"⚠️ Local service {service_name} health check failed: HTTP {response.status_code}"
                    )
                    ctx.add_detail("health_error", f"HTTP {response.status_code}")

            except Exception as e:
                ctx.add_detail("health_check_error", str(e))
                logger.error(f"❌ Local service {service_name} health check failed: {e}")

        # Determine final status
        if (
            health_info["process_running"]
            and health_info["port_accessible"]
            and health_info["health_endpoint"]
        ):
            health_info["status"] = "healthy"
        elif health_info["process_running"] and health_info["port_accessible"]:
            health_info["status"] = "unhealthy"
        elif health_info["process_running"]:
            health_info["status"] = "process_only"
        else:
            health_info["status"] = "offline"

        ctx.add_detail("final_status", health_info["status"])
        return health_info

    # Determine overall status
    if (
        health_info["process_running"]
        and health_info["port_accessible"]
        and health_info["health_endpoint"]
    ):
        health_info["status"] = "healthy"
    elif health_info["process_running"] and health_info["port_accessible"]:
        health_info["status"] = "running"
    elif health_info["process_running"]:
        health_info["status"] = "process_only"
    else:
        health_info["status"] = "stopped"

    return health_info


def comprehensive_health_check() -> Dict[str, Any]:
    """Perform comprehensive health check on all services"""
    print_header("Comprehensive Health Check", 2)

    results = {}
    system_info = get_system_info()

    # Check each service
    for service_name in SERVICES:
        print_info(f"Checking {service_name}...")
        results[service_name] = health_check_service(service_name)

    # Print results
    headers = ["Service", "Status", "Process", "Port", "Health", "Response Time"]
    rows = []

    for service_name, health in results.items():
        status_icons = {"healthy": "🟢", "running": "🟡", "process_only": "🟠", "stopped": "🔴"}

        rows.append(
            [
                health["service"],
                f"{status_icons.get(health['status'], '❓')} {health['status'].upper()}",
                "✅" if health["process_running"] else "❌",
                "✅" if health["port_accessible"] else "❌",
                "✅" if health["health_endpoint"] else "❌",
                f"{health['response_time']:.1f}ms" if health["response_time"] else "N/A",
            ]
        )

    print_table(headers, rows)

    # System health summary
    print_header("System Health Summary", 3)
    print(f"CPU Usage: {system_info.cpu_percent:.1f}%")
    print(f"Memory Usage: {system_info.memory_percent:.1f}%")
    print(f"Disk Usage: {system_info.disk_usage:.1f}%")
    print(f"Active Connections: {system_info.active_connections}")

    return results


# =============================================================================
# DEPENDENCY & ENVIRONMENT CHECKS
# =============================================================================


def check_dependencies() -> Dict[str, bool]:
    """Check all dependencies and environment"""
    print_header("Dependency & Environment Check", 2)

    results = {
        "python_version": False,
        "required_packages": {},
        "optional_packages": {},
        "executables": {},
        "env_file": False,
        "log_directory": False,
        "database_connection": False,
    }

    # Check Python version
    print_info("Checking Python version...")
    if sys.version_info >= REQUIRED_PYTHON_VERSION:
        print_success(f"Python {platform.python_version()} ✓")
        results["python_version"] = True
    else:
        print_error(f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required")

    # Check required packages
    print_info("Checking required packages...")
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            print_success(f"✓ {pkg}")
            results["required_packages"][pkg] = True
        except ImportError:
            print_error(f"✗ {pkg} (missing)")
            results["required_packages"][pkg] = False

    # Check optional packages
    print_info("Checking optional packages...")
    for pkg in OPTIONAL_PACKAGES:
        try:
            importlib.import_module(pkg)
            print_success(f"✓ {pkg}")
            results["optional_packages"][pkg] = True
        except ImportError:
            print_warning(f"⚠ {pkg} (optional)")
            results["optional_packages"][pkg] = False

    # Check executables
    print_info("Checking required executables...")
    for exe in REQUIRED_EXECUTABLES:
        if shutil.which(exe):
            print_success(f"✓ {exe}")
            results["executables"][exe] = True
        else:
            print_error(f"✗ {exe} (not found)")
            results["executables"][exe] = False

    # Check environment file
    print_info("Checking environment configuration...")
    if ENV_FILE.exists():
        print_success("✓ .env file found")
        results["env_file"] = True
    else:
        print_error("✗ .env file not found")

    # Check log directory
    print_info("Checking log directory...")
    if LOG_DIR.exists():
        print_success("✓ Log directory exists")
        results["log_directory"] = True
    else:
        print_warning("⚠ Log directory does not exist (will be created)")
        results["log_directory"] = False

    # Test database connection
    print_info("Testing database connection...")
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE)
        import sqlalchemy
        from sqlalchemy import create_engine

        db_url = os.getenv("DATABASE_URL")
        if db_url:
            engine = create_engine(db_url, connect_args={"connect_timeout": 5})
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            print_success("✓ Database connection successful")
            results["database_connection"] = True
        else:
            print_error("✗ DATABASE_URL not set")
    except Exception as e:
        print_error(f"✗ Database connection failed: {e}")

    return results


def install_missing_dependencies():
    """Install missing dependencies"""
    print_header("Installing Missing Dependencies", 2)

    dependencies = check_dependencies()
    missing_packages = []

    # Collect missing required packages
    for pkg, installed in dependencies["required_packages"].items():
        if not installed:
            missing_packages.append(pkg)

    if not missing_packages:
        print_success("All required dependencies are installed!")
        return True

    print_info(f"Installing missing packages: {', '.join(missing_packages)}")

    try:
        for pkg in missing_packages:
            print_info(f"Installing {pkg}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True
            )
            if result.returncode == 0:
                print_success(f"✓ {pkg} installed successfully")
            else:
                print_error(f"✗ Failed to install {pkg}: {result.stderr}")
                return False

        print_success("All missing dependencies installed!")
        return True
    except Exception as e:
        print_error(f"Error installing dependencies: {e}")
        return False


def check_cognitive_engine_config():
    """Check if cognitive engine is properly configured"""
    print_header("Cognitive AI Engine Configuration Check", 2)

    # Check if cognitive_engine.py exists
    cognitive_file = APP_DIR / "src" / "cognitive_engine.py"
    if not cognitive_file.exists():
        print_error("Cognitive engine cognitive_engine.py not found")
        return False

    # Check for required AI packages
    ai_packages = ["crewai", "langchain", "langchain_google_genai"]
    missing_ai_packages = []

    for pkg in ai_packages:
        try:
            importlib.import_module(pkg)
            print_success(f"✓ {pkg}")
        except ImportError:
            print_warning(f"⚠ {pkg} (required for AI features)")
            missing_ai_packages.append(pkg)

    # Check for optional AI packages with robust handling
    optional_ai_packages = ["torch", "transformers"]
    for pkg in optional_ai_packages:
        try:
            importlib.import_module(pkg)
            print_success(f"✓ {pkg} (optional)")
        except ImportError:
            print_info(f"ℹ {pkg} (optional - not installed)")

    # Special handling for onnxruntime
    if is_onnxruntime_available():
        print_success("✓ onnxruntime (optional)")
    else:
        error_msg = get_onnxruntime_error()
        print_info(f"ℹ onnxruntime (optional - {error_msg})")
        print_info("This is a common Windows DLL issue. AI features may be limited.")

    # Check for Google credentials
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE)

        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        google_api_key = os.getenv("GOOGLE_API_KEY")

        if google_creds or google_api_key:
            print_success("✓ Google AI credentials configured")
        else:
            print_warning("⚠ Google AI credentials not configured")
            print_info("Set GOOGLE_APPLICATION_CREDENTIALS_JSON or GOOGLE_API_KEY in .env")
    except Exception as e:
        print_warning(f"⚠ Could not check Google credentials: {e}")

    # Check for database configuration
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            print_success("✓ Database URL configured")
        else:
            print_warning("⚠ DATABASE_URL not set")
    except Exception as e:
        print_warning(f"⚠ Could not check database configuration: {e}")

    if missing_ai_packages:
        print_info("Installing missing AI packages...")
        for pkg in missing_ai_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg], check=True, capture_output=True
                )
                print_success(f"✓ {pkg} installed")
            except subprocess.CalledProcessError:
                print_error(f"✗ Failed to install {pkg}")
                return False

    return True


# =============================================================================
# LOG ANALYSIS & DIAGNOSTICS
# =============================================================================


def analyze_log_file(log_path: Path, lines: int = 50) -> Dict[str, Any]:
    """Analyze log file for errors and patterns"""
    if not log_path.exists():
        return {"error": f"Log file {log_path} does not exist"}

    analysis = {
        "file_size": log_path.stat().st_size,
        "last_modified": datetime.datetime.fromtimestamp(log_path.stat().st_mtime),
        "total_lines": 0,
        "error_count": 0,
        "warning_count": 0,
        "recent_errors": [],
        "recent_warnings": [],
        "last_lines": [],
    }

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            analysis["total_lines"] = len(all_lines)

            # Analyze last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            analysis["last_lines"] = recent_lines

            for line in recent_lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ["error", "exception", "traceback"]):
                    analysis["error_count"] += 1
                    analysis["recent_errors"].append(line.strip())
                elif "warning" in line_lower:
                    analysis["warning_count"] += 1
                    analysis["recent_warnings"].append(line.strip())

    except Exception as e:
        analysis["error"] = f"Error reading log file: {e}"

    return analysis


def comprehensive_log_analysis():
    """Analyze all log files"""
    print_header("Comprehensive Log Analysis", 2)

    log_files = [LOG_FILE, LOG_DIR / "desktop_app.log", LOG_DIR / "backend.log"]

    for log_file in log_files:
        if log_file.exists():
            print_header(f"Analyzing {log_file.name}", 3)
            analysis = analyze_log_file(log_file)

            if "error" in analysis:
                print_error(analysis["error"])
                continue

            print(f"File Size: {analysis['file_size']} bytes")
            print(f"Last Modified: {analysis['last_modified']}")
            print(f"Total Lines: {analysis['total_lines']}")
            print(f"Recent Errors: {analysis['error_count']}")
            print(f"Recent Warnings: {analysis['warning_count']}")

            if analysis["recent_errors"]:
                print_info("Recent Errors:")
                for error in analysis["recent_errors"][-5:]:
                    print_colored(f"  {error}", Fore.RED)

            if analysis["recent_warnings"]:
                print_info("Recent Warnings:")
                for warning in analysis["recent_warnings"][-5:]:
                    print_colored(f"  {warning}", Fore.YELLOW)
        else:
            print_warning(f"Log file {log_file.name} does not exist")


def analyze_debug_logs():
    """Analyze debug logs to pinpoint issues"""
    print_header("🔍 Advanced Debug Log Analysis", 2)

    debug_log_file = Path(__file__).parent.parent.parent / "logs" / "debug_services.log"
    if not debug_log_file.exists():
        print_error("Debug log file not found")
        return

    print_info("Analyzing debug logs for service connectivity issues...")

    # Read recent debug logs
    try:
        with open(debug_log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-100:]  # Last 100 lines

        # Analyze patterns
        http_requests = []
        service_checks = []
        errors = []

        for line in lines:
            if "HTTP GET" in line or "HTTP POST" in line:
                http_requests.append(line.strip())
            elif "get_service_status" in line or "health_check_service" in line:
                service_checks.append(line.strip())
            elif "ERROR" in line or "❌" in line:
                errors.append(line.strip())

        print(f"\n{Fore.CYAN}HTTP Request Analysis:{Style.RESET_ALL}")
        if http_requests:
            for req in http_requests[-5:]:  # Last 5 requests
                print(f"  {req}")
        else:
            print("  No HTTP requests found")

        print(f"\n{Fore.CYAN}Service Check Analysis:{Style.RESET_ALL}")
        if service_checks:
            for check in service_checks[-5:]:  # Last 5 checks
                print(f"  {check}")
        else:
            print("  No service checks found")

        print(f"\n{Fore.CYAN}Error Analysis:{Style.RESET_ALL}")
        if errors:
            for error in errors[-5:]:  # Last 5 errors
                print(f"  {error}")
        else:
            print("  No errors found")

        # Look for specific Railway backend issues
        railway_issues = [line for line in lines if "Railway" in line or "sentinel-backend" in line]
        if railway_issues:
            print(f"\n{Fore.YELLOW}Railway Backend Issues:{Style.RESET_ALL}")
            for issue in railway_issues[-3:]:
                print(f"  {issue}")

        # Network connectivity analysis
        network_errors = [line for line in lines if "ConnectionError" in line or "Timeout" in line]
        if network_errors:
            print(f"\n{Fore.RED}Network Connectivity Issues:{Style.RESET_ALL}")
            for error in network_errors[-3:]:
                print(f"  {error}")

        # DNS resolution issues
        dns_errors = [line for line in lines if "NameResolution" in line or "getaddrinfo" in line]
        if dns_errors:
            print(f"\n{Fore.RED}DNS Resolution Issues:{Style.RESET_ALL}")
            for error in dns_errors[-3:]:
                print(f"  {error}")

        # SSL/TLS issues
        ssl_errors = [line for line in lines if "SSL" in line or "certificate" in line]
        if ssl_errors:
            print(f"\n{Fore.RED}SSL/TLS Issues:{Style.RESET_ALL}")
            for error in ssl_errors[-3:]:
                print(f"  {error}")

        print(f"\n{Fore.GREEN}Debug log analysis complete. Check the full log at:{Style.RESET_ALL}")
        print(f"  {debug_log_file}")

    except Exception as e:
        print_error(f"Error analyzing debug logs: {e}")


def run_network_diagnostics():
    """Run comprehensive network diagnostics"""
    print_header("🌐 Network Diagnostics", 2)

    with DebugContext("network_diagnostics") as ctx:
        # Test basic connectivity
        print_info("Testing basic internet connectivity...")
        try:
            response = debug_request("GET", "https://httpbin.org/get", timeout=10)
            ctx.add_detail("internet_connectivity", "OK")
            print_success("✅ Internet connectivity: OK")
        except Exception as e:
            ctx.add_detail("internet_connectivity", f"FAILED: {e}")
            print_error(f"❌ Internet connectivity failed: {e}")

        # Test DNS resolution
        print_info("Testing DNS resolution...")
        try:
            import socket

            ip = socket.gethostbyname("sentinelai-production.up.railway.app")
            ctx.add_detail("dns_resolution", f"OK: {ip}")
            print_success(f"✅ DNS resolution: OK ({ip})")
        except Exception as e:
            ctx.add_detail("dns_resolution", f"FAILED: {e}")
            print_error(f"❌ DNS resolution failed: {e}")

        # Test Railway backend connectivity
        print_info("Testing Railway backend connectivity...")
        try:
            response = debug_request(
                "GET", "https://sentinelai-production.up.railway.app/health", timeout=10
            )
            ctx.add_detail("railway_connectivity", f"OK: HTTP {response.status_code}")
            print_success(f"✅ Railway backend: OK (HTTP {response.status_code})")
        except Exception as e:
            ctx.add_detail("railway_connectivity", f"FAILED: {e}")
            print_error(f"❌ Railway backend failed: {e}")

        # Test local services
        print_info("Testing local service connectivity...")
        local_services = ["desktop_app", "cognitive_engine"]
        for service in local_services:
            if service in SERVICES:
                service_config = SERVICES[service]
                if "health_endpoint" in service_config:
                    try:
                        url = f"http://localhost:{service_config['port']}{service_config['health_endpoint']}"
                        response = debug_request("GET", url, timeout=5)
                        ctx.add_detail(
                            f"{service}_connectivity", f"OK: HTTP {response.status_code}"
                        )
                        print_success(f"✅ {service}: OK (HTTP {response.status_code})")
                    except Exception as e:
                        ctx.add_detail(f"{service}_connectivity", f"FAILED: {e}")
                        print_error(f"❌ {service} failed: {e}")

        # Network interface analysis
        print_info("Analyzing network interfaces...")
        try:
            import psutil

            interfaces = psutil.net_if_addrs()
            for interface, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ctx.add_detail(f"interface_{interface}", addr.address)
                        print_info(f"  {interface}: {addr.address}")
        except Exception as e:
            ctx.add_detail("interface_analysis_error", str(e))
            print_error(f"❌ Interface analysis failed: {e}")

        print_success("Network diagnostics complete!")


# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================


def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print_warning(f"Error loading config: {e}")
    return {}


def save_config(config: Dict[str, Any]):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print_success("Configuration saved")
    except Exception as e:
        print_error(f"Error saving config: {e}")


def backup_configuration():
    """Create backup of current configuration"""
    print_header("Backup Configuration", 2)

    config = {
        "timestamp": datetime.datetime.now().isoformat(),
        "services": SERVICES,
        "system_info": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture(),
        },
    }

    backup_file = (
        APP_DIR / f"config_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    try:
        with open(backup_file, "w") as f:
            json.dump(config, f, indent=2)
        print_success(f"Configuration backed up to {backup_file}")
    except Exception as e:
        print_error(f"Error creating backup: {e}")


# =============================================================================
# MAIN MENU SYSTEM
# =============================================================================


def show_main_menu():
    """Display the main menu"""
    print_header("Sentinel Comprehensive System Service Manager", 1)

    # Show current status
    print(f"{Fore.CYAN}Current System Status:{Style.RESET_ALL}")
    sys_info = get_system_info()
    print(
        f"  CPU: {sys_info.cpu_percent:.1f}% | "
        f"Memory: {sys_info.memory_percent:.1f}% | "
        f"Disk: {sys_info.disk_usage:.1f}%"
    )

    # Show service status using comprehensive health checks
    print(f"{Fore.CYAN}Service Status:{Style.RESET_ALL}")
    for service_name in SERVICES:
        health = health_check_service(service_name)
        
        # Determine status based on comprehensive health check
        if health["status"] == "healthy":
            status_icon = "🟢"
            status_text = "ONLINE"
        elif health["status"] == "running":
            status_icon = "🟡"
            status_text = "RUNNING"
        elif health["status"] == "process_only":
            status_icon = "🟠"
            status_text = "PROCESS_ONLY"
        else:
            status_icon = "🔴"
            status_text = "OFFLINE"
        
        print(f"  {status_icon} {SERVICES[service_name]['name']}: {status_text}")

    print(f"\n{Fore.YELLOW}Available Actions:{Style.RESET_ALL}")
    print("1.  🚀 Full Desktop App System Startup")
    print("2.  Start All Services")
    print("3.  Stop All Services")
    print("4.  Restart All Services")
    print("5.  Monitor Services (Real-time)")
    print("6.  Health Check (All Services)")
    print("7.  Check Dependencies")
    print("8.  Install Missing Dependencies")
    print("9.  Analyze Logs")
    print("10. Backup Configuration")
    print("11. Kill All Related Processes")
    print("12. Service Management (Individual)")
    print("13. System Diagnostics")
    print("14. Check Cognitive Engine Config")
    print("15. 🔧 Debug Killer Optimization")
    print("16. 🔍 Advanced Debug Log Analysis")
    print("17. 🌐 Network Diagnostics")
    print("0.  Exit")


def service_management_menu():
    """Individual service management menu"""
    while True:
        print_header("Individual Service Management", 2)

        # Show service status
        headers = ["#", "Service", "Status", "Port", "PID"]
        rows = []

        for i, service_name in enumerate(SERVICES, 1):
            status = get_service_status(service_name)
            status_icon = "🟢" if status.is_running else "🔴"
            pid_str = str(status.pid) if status.pid else "N/A"

            rows.append(
                [
                    str(i),
                    status.name,
                    f"{status_icon} {'ONLINE' if status.is_running else 'OFFLINE'}",
                    str(status.port),
                    pid_str,
                ]
            )

        print_table(headers, rows)

        print(f"\n{Fore.YELLOW}Actions:{Style.RESET_ALL}")
        print("1-{}. Manage specific service".format(len(SERVICES)))
        print("0. Back to main menu")

        choice = input(f"\nChoose service (1-{len(SERVICES)}) or 0 to go back: ").strip()

        if choice == "0":
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(SERVICES):
            service_name = list(SERVICES.keys())[int(choice) - 1]
            manage_individual_service(service_name)
        else:
            print_error("Invalid choice")


def manage_individual_service(service_name: str):
    """Manage individual service"""
    service_config = SERVICES[service_name]

    while True:
        print_header(f"Managing {service_config['name']}", 3)

        status = get_service_status(service_name)
        print(f"Status: {'🟢 ONLINE' if status.is_running else '🔴 OFFLINE'}")
        if status.pid:
            print(f"PID: {status.pid}")
            print(f"Memory: {status.memory_usage:.1f}%" if status.memory_usage else "Memory: N/A")
            print(f"CPU: {status.cpu_usage:.1f}%" if status.cpu_usage else "CPU: N/A")
            print(f"Uptime: {status.uptime/60:.1f} minutes" if status.uptime else "Uptime: N/A")

        print(f"\n{Fore.YELLOW}Actions:{Style.RESET_ALL}")
        print("1. Start Service")
        print("2. Stop Service")
        print("3. Restart Service")
        print("4. Health Check")
        print("5. View Logs")
        print("0. Back")

        choice = input("\nChoose action: ").strip()

        if choice == "1":
            start_service(service_name)
        elif choice == "2":
            stop_service(service_name)
        elif choice == "3":
            restart_service(service_name)
        elif choice == "4":
            health = health_check_service(service_name)
            print_info(f"Health Status: {health['status']}")
        elif choice == "5":
            if service_config["log_file"].exists():
                analysis = analyze_log_file(service_config["log_file"])
                if "last_lines" in analysis:
                    print_info("Last 10 log lines:")
                    for line in analysis["last_lines"][-10:]:
                        print(line.rstrip())
            else:
                print_warning("Log file does not exist")
        elif choice == "0":
            break
        else:
            print_error("Invalid choice")


def system_diagnostics_menu():
    """System diagnostics menu"""
    while True:
        print_header("System Diagnostics", 2)

        print("1. System Information")
        print("2. Process Analysis")
        print("3. Network Analysis")
        print("4. Port Scanner")
        print("5. Performance Metrics")
        print("0. Back to main menu")

        choice = input("\nChoose diagnostic: ").strip()

        if choice == "1":
            show_system_information()
        elif choice == "2":
            show_process_analysis()
        elif choice == "3":
            show_network_analysis()
        elif choice == "4":
            scan_ports()
        elif choice == "5":
            show_performance_metrics()
        elif choice == "0":
            break
    else:
        print_error("Invalid choice")


def show_system_information():
    """Display detailed system information"""
    print_header("System Information", 3)

    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Implementation: {platform.python_implementation()}")

    # Memory info
    memory = psutil.virtual_memory()
    print(f"\nMemory:")
    print(f"  Total: {memory.total / (1024**3):.2f} GB")
    print(f"  Available: {memory.available / (1024**3):.2f} GB")
    print(f"  Used: {memory.percent:.1f}%")

    # Disk info
    disk = psutil.disk_usage("/")
    print(f"\nDisk:")
    print(f"  Total: {disk.total / (1024**3):.2f} GB")
    print(f"  Used: {disk.used / (1024**3):.2f} GB")
    print(f"  Free: {disk.free / (1024**3):.2f} GB")
    print(f"  Usage: {disk.percent:.1f}%")


def show_process_analysis():
    """Show detailed process analysis"""
    print_header("Process Analysis", 3)

    # Get all processes
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by CPU usage
    processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

    headers = ["PID", "Name", "CPU%", "Memory%"]
    rows = []

    for proc in processes[:20]:  # Top 20 processes
        rows.append(
            [
                str(proc["pid"]),
                proc["name"][:20],
                f"{proc['cpu_percent']:.1f}" if proc["cpu_percent"] else "0.0",
                f"{proc['memory_percent']:.1f}" if proc["memory_percent"] else "0.0",
            ]
        )

    print_table(headers, rows)


def show_network_analysis():
    """Show network analysis"""
    print_header("Network Analysis", 3)

    # Network interfaces
    print("Network Interfaces:")
    for interface, addresses in psutil.net_if_addrs().items():
        print(f"  {interface}:")
        for addr in addresses:
            print(f"    {addr.family.name}: {addr.address}")

    # Network connections
    print(f"\nActive Connections:")
    connections = []
    for proc in psutil.process_iter(["pid", "name", "connections"]):
        try:
            for conn in proc.info.get("connections", []):
                connections.append(
                    {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        "status": conn.status,
                    }
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if connections:
        headers = ["PID", "Process", "Local", "Remote", "Status"]
        rows = []
        for conn in connections[:20]:  # Show first 20 connections
            rows.append(
                [str(conn["pid"]), conn["name"][:15], conn["local"], conn["remote"], conn["status"]]
            )
        print_table(headers, rows)
        print_info("No active connections found")
        print_info("No active connections found")


def scan_ports():
    """Scan for open ports"""
    print_header("Port Scanner", 3)

    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8000, 8001, 8080, 8443]

    print("Scanning common ports...")
    open_ports = []

    for port in common_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("localhost", port))
            if result == 0:
                open_ports.append(port)
                print_success(f"Port {port} is open")

    if not open_ports:
        print_info("No common ports are open")


def show_performance_metrics():
    """Show performance metrics"""
    print_header("Performance Metrics", 3)

    # CPU usage over time
    print("CPU Usage (5 samples):")
    for i in range(5):
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"  Sample {i+1}: {cpu_percent:.1f}%")

    # Memory usage
    memory = psutil.virtual_memory()
    print(f"\nMemory Usage: {memory.percent:.1f}%")

    # Disk I/O
    disk_io = psutil.disk_io_counters()
    if disk_io:
        print(f"\nDisk I/O:")
        print(f"  Read bytes: {disk_io.read_bytes / (1024**2):.2f} MB")
        print(f"  Write bytes: {disk_io.write_bytes / (1024**2):.2f} MB")
        print(f"  Read count: {disk_io.read_count}")
        print(f"  Write count: {disk_io.write_count}")


def debug_killer_interface():
    """Debug Killer Optimization Interface"""
    print_header("🔧 DEBUG KILLER OPTIMIZATION SYSTEM", 1)

    while True:
        print(f"\n{Fore.CYAN}Debug Killer Options:{Style.RESET_ALL}")
        print("1. 🚨 Handle Current Error")
        print("2. 🔍 Run System Scan")
        print("3. 📊 View System Diagnostics")
        print("4. 📋 View Error Log")
        print("5. 🛠️ Auto-Fix Common Issues")
        print("6. 🔄 Reset Debug System")
        print("0. Back to Main Menu")

        choice = input(f"\n{Fore.GREEN}Choose option: {Style.RESET_ALL}").strip()

        if choice == "1":
            error_msg = input("Enter error message: ").strip()
            if error_msg:
                try:
                    # Simulate the error
                    raise Exception(error_msg)
                except Exception as e:
                    handle_error_with_debug_killer(e, "Manual Error Handling")

        elif choice == "2":
            scan_results = run_comprehensive_system_scan()

        elif choice == "3":
            diagnostic = run_system_diagnostics()

        elif choice == "4":
            debug_log_file = Path(__file__).parent.parent.parent / "logs" / "debug_killer.log"
            if debug_log_file.exists():
                print_info("Recent debug log entries:")
                try:
                    with open(debug_log_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()[-20:]  # Last 20 lines
                        for line in lines:
                            print(line.rstrip())
                except Exception as e:
                    print_error(f"Error reading log: {e}")
            else:
                print_info("No debug log found")

        elif choice == "5":
            print_header("Auto-Fix Common Issues", 2)
            print_info("Checking for common issues...")

            # Check and fix missing packages
            try:
                import crewai

                print_success("✓ crewai package found")
            except ImportError:
                print_info("Installing crewai...")
                subprocess.run([sys.executable, "-m", "pip", "install", "crewai"])

            # Check and fix port conflicts
            common_ports = [8000, 8001, 8002]
            for port in common_ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex(("localhost", port))
                        if result == 0:
                            print_info(f"Fixing port conflict on {port}")
                            kill_process_on_port(port)
                except BaseException:
                    pass

            print_success("Auto-fix completed!")

        elif choice == "6":
            print_header("Reset Debug System", 2)
            debug_log_file = Path(__file__).parent.parent.parent / "logs" / "debug_killer.log"
            if debug_log_file.exists():
                debug_log_file.unlink()
                print_success("Debug log cleared")
            print_success("Debug system reset complete!")

        elif choice == "0":
            break

        else:
            print_error("Invalid choice")

        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def main():
    """Main function with enhanced menu system"""
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            show_main_menu()
            choice = input(f"\n{Fore.GREEN}Choose an option: {Style.RESET_ALL}").strip()

            if choice == "1":
                full_desktop_app_startup()
            elif choice == "2":
                start_all_services()
            elif choice == "3":
                stop_all_services()
            elif choice == "4":
                restart_all_services()
            elif choice == "5":
                monitor_services_continuous()
            elif choice == "6":
                comprehensive_health_check()
            elif choice == "7":
                check_dependencies()
            elif choice == "8":
                install_missing_dependencies()
            elif choice == "9":
                comprehensive_log_analysis()
            elif choice == "10":
                backup_configuration()
            elif choice == "11":
                killed = kill_all_related_processes()
                print_info(f"Killed {len(killed)} related processes")
            elif choice == "12":
                service_management_menu()
            elif choice == "13":
                system_diagnostics_menu()
            elif choice == "14":
                check_cognitive_engine_config()
            elif choice == "15":
                debug_killer_interface()
            elif choice == "16":
                analyze_debug_logs()
            elif choice == "17":
                run_network_diagnostics()
            elif choice == "0":
                print_success("Exiting. Services continue running if not stopped.")
                break
            else:
                print_error("Invalid choice. Please try again.")

            if choice != "5":  # Don't pause for continuous monitoring
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        except KeyboardInterrupt:
            print_info("\nInterrupted by user")
            break
        except Exception as e:
            print_critical(f"Unexpected error: {e}")
            # Use debug killer to handle the error
            if handle_error_with_debug_killer(e, "Main Service Manager"):
                print_success("Error was automatically resolved!")
            else:
                print_warning(
                    "Error could not be automatically resolved. Manual intervention may be required."
                )
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
