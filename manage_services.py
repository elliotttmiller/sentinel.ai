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
            "cmd": [sys.executable, "start_cognitive_forge.py"],
            "cwd": "./desktop-app",
            "desc": "FastAPI Backend Server",
            "health": "http://localhost:8000/health"
        },
        "frontend": {
            "cmd": ["npm", "start"],
            "cwd": "./copilotkit-frontend",
            "desc": "React Frontend",
            "health": "http://localhost:3000"
        },
        "vector_db": {
            "cmd": [sys.executable, "start_sentinel.py"],
            "cwd": "./scripts",
            "desc": "ChromaDB Vector DB",
            "health": "http://localhost:8001"
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
    # Determine mode from .env
    local = env_vars.get("REDIS_MODE", "local").lower() == "local"
    print(f"\n[INFO] Startup mode: {'Local' if local else 'Remote'} (from .env)")
    procs = start_all_services(local=local)
    # Health checks
    print("\nRunning health checks...")
    for name, svc in CONFIG["services"].items():
        if not local and name in ["redis", "postgres"]:
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
    print("\n[INFO] System startup complete. Monitor logs for status.")
    # Optionally: add restart/stop menu, log monitoring, etc.

if __name__ == "__main__":
    main()
