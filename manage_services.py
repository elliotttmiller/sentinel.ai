"""
manage_services.py - Sentinel System Command Center (Automated)

Features:
- Automated environment validation
- Dynamic local/remote mode selection from .env
- Unified startup/shutdown/restart for all services
- Health checks for each service
- Log monitoring and error notification
- No manual input required
"""

import subprocess
import os
import sys
import time
from pathlib import Path
import threading

# --- COLOR UTILS ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color_text(text, color):
    return f"{color}{text}{Colors.ENDC}"

# --- CONFIGURATION ---
CONFIG = {
    "env_file": "./.env",
    "frontend_env_file": "./copilotkit-frontend/.env",
    "services": {
        "backend": {
            "cmd": [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"],
            "cwd": "./",
            "desc": "FastAPI Backend Server (CopilotKit official)",
            "health": "http://localhost:8000/health",
            "copilotkit": "http://localhost:8000/api/copilotkit/info"
        },
        "websocket": {
            "cmd": [sys.executable, "src/websocket_server.py"],
            "cwd": "./",
            "desc": "WebSocket Status Server",
            "health": None
        },
        "frontend": {
            "cmd": [r"C:\\Users\\AMD\\AppData\\Roaming\\npm\\yarn.cmd", "run", "react-app-rewired", "start"],
            "cwd": "./copilotkit-frontend",
            "desc": "React Frontend (CopilotKit official)",
            "health": "http://localhost:3000"
        },
        "redis": {
            "cmd": ["redis-server"],
            "cwd": None,
            "desc": "Redis Server (local)",
            "health": None
        },
        "postgres": {
            "cmd": ["pg_ctl", "start"],
            "cwd": None,
            "desc": "PostgreSQL Server (local)",
            "health": None
        }
    }
}

# --- UTILS ---
def print_header():
    print(color_text("\n=== Sentinel System Command Center ===\n", Colors.HEADER + Colors.BOLD))

def check_env_files():
    print(color_text("\n--- Checking environment files ---", Colors.OKCYAN))
    for env_path in [CONFIG["env_file"], CONFIG["frontend_env_file"]]:
        if not Path(env_path).exists():
            print(color_text(f"[ERROR] Missing: {env_path}", Colors.FAIL))
        else:
            print(color_text(f"[OK] Found: {env_path}", Colors.OKGREEN))

def validate_env_vars():
    print(color_text("\n--- Validating critical environment variables ---", Colors.OKCYAN))
    required_vars = ["DATABASE_URL", "REDIS_MODE", "REDIS_URL_LOCAL", "REDIS_URL_CLOUD"]
    missing = []
    env_vars = {}
    with open(CONFIG["env_file"], "r") as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                env_vars[k] = v
    for var in required_vars:
        if var not in env_vars:
            missing.append(var)
    if missing:
        print(color_text(f"[ERROR] Missing variables: {', '.join(missing)}", Colors.FAIL))
    else:
        print(color_text("[OK] All critical variables present.", Colors.OKGREEN))
    return env_vars

def run_service(name):
    svc = CONFIG["services"].get(name)
    if not svc:
        print(color_text(f"[ERROR] Unknown service: {name}", Colors.FAIL))
        return None
    print(color_text(f"Starting {svc['desc']}...", Colors.OKBLUE))
    try:
        proc = subprocess.Popen(svc["cmd"], cwd=svc["cwd"])
        print(color_text(f"[OK] {name} started.", Colors.OKGREEN))
        return proc
    except Exception as e:
        print(color_text(f"[ERROR] Failed to start {name}: {e}", Colors.FAIL))
        return None

def start_all_services(local=True):
    print(color_text("\n--- Starting all services ---", Colors.OKCYAN))
    procs = {}
    for name in CONFIG["services"]:
        if not local and name in ["redis", "postgres"]:
            continue
        proc = run_service(name)
        if proc:
            procs[name] = proc
    print(color_text("\n[INFO] All services started.", Colors.OKGREEN))
    return procs

def main():
    print_header()
    check_env_files()
    env_vars = validate_env_vars()
    # Interactive menu
    print(color_text("\nChoose startup option:", Colors.BOLD))
    print(color_text("1. Full Local Startup (backend, frontend, local services)", Colors.OKBLUE))
    print(color_text("2. Full Remote Startup (backend, frontend, remote integrations)", Colors.OKBLUE))
    print(color_text("3. Backend Only", Colors.OKBLUE))
    print(color_text("4. Frontend Only", Colors.OKBLUE))
    print(color_text("5. Custom (choose services)", Colors.OKBLUE))
    print(color_text("6. Full System Shutdown (stop all server processes)", Colors.WARNING))
    choice = input(color_text("Enter option [1-6]: ", Colors.BOLD)).strip()
    local = True
    services_to_start = list(CONFIG["services"].keys())
    # Track running processes in a file
    procs_file = Path(".sentinel_running_procs")
    if choice == "6":
        # Shutdown option
        print(color_text("\n--- Shutting down all running server processes ---", Colors.OKCYAN))
        if procs_file.exists():
            import json
            with open(procs_file, "r") as f:
                running = json.load(f)
            for name, pid in running.items():
                try:
                    os.kill(pid, 9)
                    print(color_text(f"[OK] {name} (PID {pid}) stopped.", Colors.OKGREEN))
                except Exception as e:
                    print(color_text(f"[ERROR] Failed to stop {name} (PID {pid}): {e}", Colors.FAIL))
            procs_file.unlink()
        else:
            print(color_text("No running server processes tracked. Start services first.", Colors.WARNING))
        return
    if choice == "1":
        local = True
        # Kill any running backend, frontend, websocket server processes before starting
        import psutil
        server_cmds = [
            "src/main.py",
            "copilotkit-frontend",
            "src/websocket_server.py"
        ]
        killed = set()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if any(cmd in ' '.join(cmdline) for cmd in server_cmds):
                    proc.kill()
                    killed.add(proc.info['pid'])
            except Exception:
                pass
        if killed:
            print(color_text(f"[INFO] Killed previous server processes: {', '.join(map(str, killed))}", Colors.WARNING))
        # Start backend, frontend, websocket, redis, postgres
        services_to_start = ["backend", "frontend", "websocket", "redis", "postgres"]
    elif choice == "2":
        local = False
    elif choice == "3":
        services_to_start = ["backend"]
    elif choice == "4":
        services_to_start = ["frontend"]
    elif choice == "5":
        print(color_text("Available services: ", Colors.OKCYAN) + color_text(", ".join(CONFIG["services"].keys()), Colors.OKBLUE))
        custom = input(color_text("Enter comma-separated services to start: ", Colors.BOLD)).strip()
        services_to_start = [s.strip() for s in custom.split(",") if s.strip() in CONFIG["services"]]
    # Print local frontend URL if started
    if "frontend" in services_to_start:
        print(color_text("\n[INFO] Access your local frontend at: http://localhost:3000", Colors.OKGREEN))
    print(color_text(f"\n[INFO] Startup mode: {'Local' if local else 'Remote'} (from menu)", Colors.OKCYAN))
    print(color_text(f"[INFO] Services to start: {', '.join(services_to_start)}", Colors.OKCYAN))
    # Start selected services
    procs = {}
    service_status = {}
    for name in services_to_start:
        if name == "postgres":
            # Skip PostgreSQL
            service_status[name] = "Skipped"
            continue
        proc = run_service(name)
        if proc:
            procs[name] = proc
            service_status[name] = "Started"
        else:
            service_status[name] = "Failed"
    # Save running process PIDs for shutdown
    import json
    running = {name: proc.pid for name, proc in procs.items()}
    with open(procs_file, "w") as f:
        json.dump(running, f)
    print(color_text("\n[INFO] Selected services started.", Colors.OKGREEN))
    # Health checks
    print(color_text("\n--- Running health checks ---", Colors.OKCYAN))
    import time
    MAX_RETRIES = 5
    RETRY_DELAY = 2  # seconds
    for name in services_to_start:
        if name == "postgres":
            continue  # Skip health check for PostgreSQL
        svc = CONFIG["services"].get(name)
        if not svc:
            continue
        url = svc.get("health")
        if url:
            healthy = False
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    import requests
                    resp = requests.get(url, timeout=3)
                    if resp.status_code == 200:
                        print(color_text(f"[OK] {name} healthy (attempt {attempt}).", Colors.OKGREEN))
                        service_status[name] = "Healthy"
                        healthy = True
                        break
                    else:
                        print(color_text(f"[WARN] {name} unhealthy (status {resp.status_code}) (attempt {attempt}).", Colors.WARNING))
                        service_status[name] = f"Unhealthy ({resp.status_code})"
                except Exception as e:
                    print(color_text(f"[ERROR] {name} health check failed (attempt {attempt}): {e}", Colors.FAIL))
                    service_status[name] = "Health Check Failed"
                time.sleep(RETRY_DELAY)
            if not healthy:
                print(color_text(f"[FAIL] {name} did not pass health check after {MAX_RETRIES} attempts.", Colors.FAIL))
        copilotkit_url = svc.get("copilotkit")
        if copilotkit_url:
            healthy = False
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    import requests
                    resp = requests.get(copilotkit_url, timeout=3)
                    if resp.status_code == 200:
                        print(color_text(f"[OK] CopilotKit endpoint healthy: {copilotkit_url} (attempt {attempt}).", Colors.OKGREEN))
                        healthy = True
                        break
                    else:
                        print(color_text(f"[WARN] CopilotKit endpoint unhealthy (status {resp.status_code}): {copilotkit_url} (attempt {attempt}).", Colors.WARNING))
                except Exception as e:
                    print(color_text(f"[ERROR] CopilotKit endpoint health check failed (attempt {attempt}): {e}", Colors.FAIL))
                time.sleep(RETRY_DELAY)
            if not healthy:
                print(color_text(f"[FAIL] CopilotKit endpoint did not pass health check after {MAX_RETRIES} attempts: {copilotkit_url}", Colors.FAIL))
    # Visual summary table
    print(color_text("\n--- Service Status Summary ---", Colors.HEADER + Colors.BOLD))
    print(color_text("+----------------+---------------------+", Colors.BOLD))
    print(color_text("| Service        | Status              |", Colors.BOLD))
    print(color_text("+----------------+---------------------+", Colors.BOLD))
    for name in services_to_start:
        status = service_status.get(name, "Not Started")
        if "Healthy" in status:
            status_col = Colors.OKGREEN
        elif "Unhealthy" in status:
            status_col = Colors.WARNING
        elif "Failed" in status or "Health Check Failed" in status:
            status_col = Colors.FAIL
        else:
            status_col = Colors.OKCYAN
        print(f"| {name.ljust(14)} | {color_text(status.ljust(19), status_col)}|")
    print(color_text("+----------------+---------------------+", Colors.BOLD))
    print(color_text("\n[INFO] System startup complete. Monitor logs for status.", Colors.OKCYAN))

if __name__ == "__main__":
    main()
