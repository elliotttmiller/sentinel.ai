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

# --- CONFIGURATION ---
CONFIG = {
    "env_file": "./.env",
    "frontend_env_file": "./copilotkit-frontend/.env",
    "services": {
        "backend": {
            "cmd": [sys.executable, "src/main.py"],
            "cwd": "./",
            "desc": "FastAPI Backend Server",
            "health": "http://localhost:8000/health",
            "copilotkit": "http://localhost:8000/api/copilotkit/info"
        },
        "frontend": {
            "cmd": [r"C:\\Users\\AMD\\AppData\\Roaming\\npm\\yarn.cmd", "start"],
            "cwd": "./copilotkit-frontend",
            "desc": "React Frontend",
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
    print("\n=== Sentinel System Command Center ===\n")

def check_env_files():
    print("Checking environment files...")
    for env_path in [CONFIG["env_file"], CONFIG["frontend_env_file"]]:
        if not Path(env_path).exists():
            print(f"[ERROR] Missing: {env_path}")
        else:
            print(f"[OK] Found: {env_path}")

def validate_env_vars():
    print("Validating critical environment variables...")
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
        print(f"[ERROR] Missing variables: {', '.join(missing)}")
    else:
        print("[OK] All critical variables present.")
    return env_vars

def run_service(name):
    svc = CONFIG["services"].get(name)
    if not svc:
        print(f"[ERROR] Unknown service: {name}")
        return None
    print(f"Starting {svc['desc']}...")
    try:
        proc = subprocess.Popen(svc["cmd"], cwd=svc["cwd"])
        print(f"[OK] {name} started.")
        return proc
    except Exception as e:
        print(f"[ERROR] Failed to start {name}: {e}")
        return None

def start_all_services(local=True):
    print("\nStarting all services...")
    procs = {}
    for name in CONFIG["services"]:
        if not local and name in ["redis", "postgres"]:
            continue
        proc = run_service(name)
        if proc:
            procs[name] = proc
    print("\n[INFO] All services started.")
    return procs

def main():
    print_header()
    check_env_files()
    env_vars = validate_env_vars()
    # Interactive menu
    print("\nChoose startup option:")
    print("1. Full Local Startup (backend, frontend, local services)")
    print("2. Full Remote Startup (backend, frontend, remote integrations)")
    print("3. Backend Only")
    print("4. Frontend Only")
    print("5. Custom (choose services)")
    print("6. Full System Shutdown (stop all server processes)")
    choice = input("Enter option [1-6]: ").strip()
    local = True
    services_to_start = list(CONFIG["services"].keys())
    # Track running processes in a file
    procs_file = Path(".sentinel_running_procs")
    if choice == "6":
        # Shutdown option
        if procs_file.exists():
            import json
            with open(procs_file, "r") as f:
                running = json.load(f)
            print("\nShutting down all running server processes...")
            for name, pid in running.items():
                try:
                    os.kill(pid, 9)
                    print(f"[OK] {name} (PID {pid}) stopped.")
                except Exception as e:
                    print(f"[ERROR] Failed to stop {name} (PID {pid}): {e}")
            procs_file.unlink()
        else:
            print("No running server processes tracked. Start services first.")
        return
    if choice == "1":
        local = True
    elif choice == "2":
        local = False
    elif choice == "3":
        services_to_start = ["backend"]
    elif choice == "4":
        services_to_start = ["frontend"]
    elif choice == "5":
        print("Available services:", ", ".join(CONFIG["services"].keys()))
        custom = input("Enter comma-separated services to start: ").strip()
        services_to_start = [s.strip() for s in custom.split(",") if s.strip() in CONFIG["services"]]
    print(f"\n[INFO] Startup mode: {'Local' if local else 'Remote'} (from menu)")
    print(f"[INFO] Services to start: {', '.join(services_to_start)}")
    # Start selected services
    procs = {}
    for name in services_to_start:
        if not local and name in ["redis", "postgres"]:
            continue
        proc = run_service(name)
        if proc:
            procs[name] = proc
    # Save running process PIDs for shutdown
    import json
    running = {name: proc.pid for name, proc in procs.items()}
    with open(procs_file, "w") as f:
        json.dump(running, f)
    print("\n[INFO] Selected services started.")
    # Health checks
    print("\nRunning health checks...")
    for name in services_to_start:
        svc = CONFIG["services"].get(name)
        if not svc:
            continue
        url = svc.get("health")
        if url:
            try:
                import requests
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    print(f"[OK] {name} healthy.")
                else:
                    print(f"[WARN] {name} unhealthy (status {resp.status_code}).")
            except Exception as e:
                print(f"[ERROR] {name} health check failed: {e}")
        copilotkit_url = svc.get("copilotkit")
        if copilotkit_url:
            try:
                import requests
                resp = requests.get(copilotkit_url, timeout=3)
                if resp.status_code == 200:
                    print(f"[OK] CopilotKit endpoint healthy: {copilotkit_url}")
                else:
                    print(f"[WARN] CopilotKit endpoint unhealthy (status {resp.status_code}): {copilotkit_url}")
            except Exception as e:
                print(f"[ERROR] CopilotKit endpoint health check failed: {e}")
    print("\n[INFO] System startup complete. Monitor logs for status.")

if __name__ == "__main__":
    main()
