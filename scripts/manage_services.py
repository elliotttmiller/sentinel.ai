#!/usr/bin/env python3
"""
Sentinel Service Manager
A comprehensive script to manage all Sentinel services on Windows.
"""

import subprocess
import sys
import os
import time
import json
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Optional

class ServiceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.engine_dir = self.project_root / "engine"
        self.processes: Dict[str, subprocess.Popen] = {}
        self.config_file = self.project_root / "scripts" / "service_config.json"
        self.load_config()

    def load_config(self):
        """Load service configuration from JSON file."""
        default_config = {
            "backend": {
                "port": 8080,
                "host": "0.0.0.0",
                "reload": True
            },
            "ngrok": {
                "port": 8080,
                "subdomain": None
            },
            "engine": {
                "port": 8001,
                "host": "0.0.0.0"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Invalid config file, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save current configuration to JSON file."""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_service_status(self, service_name: str) -> bool:
        """Check if a service is running."""
        return service_name in self.processes and self.processes[service_name].poll() is None

    def start_backend(self, port: Optional[int] = None) -> bool:
        """Start the backend server."""
        if self.get_service_status("backend"):
            print("Backend server is already running!")
            return True

        port = port or self.config["backend"]["port"]
        host = self.config["backend"]["host"]
        reload_flag = "--reload" if self.config["backend"]["reload"] else ""

        print(f"Starting backend server on {host}:{port}...")
        
        try:
            cmd = ["uvicorn", "main:app", "--host", host, "--port", str(port)]
            if reload_flag:
                cmd.append(reload_flag)
            
            process = subprocess.Popen(
                cmd,
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes["backend"] = process
            print(f"✅ Backend server started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False

    def start_ngrok(self, port: Optional[int] = None, subdomain: Optional[str] = None) -> bool:
        """Start ngrok tunnel."""
        if self.get_service_status("ngrok"):
            print("ngrok tunnel is already running!")
            return True

        port = port or self.config["ngrok"]["port"]
        subdomain = subdomain or self.config["ngrok"]["subdomain"]

        print(f"Starting ngrok tunnel for port {port}...")
        
        try:
            cmd = ["ngrok", "http", str(port)]
            if subdomain:
                cmd.extend(["--subdomain", subdomain])
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes["ngrok"] = process
            print(f"✅ ngrok tunnel started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start ngrok tunnel: {e}")
            return False

    def start_engine(self, port: Optional[int] = None) -> bool:
        """Start the agent engine."""
        if self.get_service_status("engine"):
            print("Agent engine is already running!")
            return True

        port = port or self.config["engine"]["port"]
        host = self.config["engine"]["host"]

        print(f"Starting agent engine on {host}:{port}...")
        
        try:
            cmd = ["python", "main.py"]
            process = subprocess.Popen(
                cmd,
                cwd=self.engine_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes["engine"] = process
            print(f"✅ Agent engine started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start agent engine: {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.processes:
            print(f"Service '{service_name}' is not running.")
            return True

        process = self.processes[service_name]
        try:
            process.terminate()
            process.wait(timeout=5)
            del self.processes[service_name]
            print(f"✅ {service_name} stopped")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            del self.processes[service_name]
            print(f"⚠️ {service_name} force-killed")
            return True
        except Exception as e:
            print(f"❌ Failed to stop {service_name}: {e}")
            return False

    def stop_all_services(self):
        """Stop all running services."""
        print("Stopping all services...")
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

    def show_status(self):
        """Show status of all services."""
        print("\n" + "="*50)
        print("SERVICE STATUS")
        print("="*50)
        
        services = ["backend", "ngrok", "engine"]
        for service in services:
            status = "🟢 RUNNING" if self.get_service_status(service) else "🔴 STOPPED"
            pid = self.processes[service].pid if service in self.processes else "N/A"
            print(f"{service.upper():<12} {status} (PID: {pid})")
        
        print("="*50)

    def configure_services(self):
        """Interactive configuration of service settings."""
        print("\n" + "="*50)
        print("SERVICE CONFIGURATION")
        print("="*50)
        
        # Backend configuration
        print("\nBackend Configuration:")
        try:
            port = int(input(f"Port (current: {self.config['backend']['port']}): ") or self.config['backend']['port'])
            self.config['backend']['port'] = port
        except ValueError:
            print("Invalid port number, keeping current setting")
        
        reload = input(f"Auto-reload (current: {self.config['backend']['reload']}) [y/N]: ").lower() == 'y'
        self.config['backend']['reload'] = reload
        
        # ngrok configuration
        print("\nngrok Configuration:")
        try:
            port = int(input(f"Port (current: {self.config['ngrok']['port']}): ") or self.config['ngrok']['port'])
            self.config['ngrok']['port'] = port
        except ValueError:
            print("Invalid port number, keeping current setting")
        
        subdomain = input(f"Subdomain (current: {self.config['ngrok']['subdomain'] or 'None'}): ").strip()
        self.config['ngrok']['subdomain'] = subdomain if subdomain else None
        
        # Engine configuration
        print("\nEngine Configuration:")
        try:
            port = int(input(f"Port (current: {self.config['engine']['port']}): ") or self.config['engine']['port'])
            self.config['engine']['port'] = port
        except ValueError:
            print("Invalid port number, keeping current setting")
        
        self.save_config()
        print("\n✅ Configuration saved!")

    def show_menu(self):
        """Display the main menu."""
        print("\n" + "="*50)
        print("SENTINEL SERVICE MANAGER")
        print("="*50)
        print("1. Start Backend Server")
        print("2. Start ngrok Tunnel")
        print("3. Start Agent Engine")
        print("4. Start All Services")
        print("5. Stop Backend Server")
        print("6. Stop ngrok Tunnel")
        print("7. Stop Agent Engine")
        print("8. Stop All Services")
        print("9. Show Service Status")
        print("10. Configure Services")
        print("11. Start Services in Background")
        print("12. Exit")
        print("="*50)

    def run_interactive(self):
        """Run the interactive menu."""
        while True:
            self.show_menu()
            try:
                choice = input("\nChoose an option (1-12): ").strip()
                
                if choice == "1":
                    self.start_backend()
                elif choice == "2":
                    self.start_ngrok()
                elif choice == "3":
                    self.start_engine()
                elif choice == "4":
                    print("Starting all services...")
                    self.start_backend()
                    time.sleep(2)
                    self.start_ngrok()
                    time.sleep(1)
                    self.start_engine()
                elif choice == "5":
                    self.stop_service("backend")
                elif choice == "6":
                    self.stop_service("ngrok")
                elif choice == "7":
                    self.stop_service("engine")
                elif choice == "8":
                    self.stop_all_services()
                elif choice == "9":
                    self.show_status()
                elif choice == "10":
                    self.configure_services()
                elif choice == "11":
                    print("Starting services in background...")
                    self.start_backend()
                    time.sleep(2)
                    self.start_ngrok()
                    time.sleep(1)
                    self.start_engine()
                    print("\n✅ All services started in background!")
                    print("Use 'python scripts/manage_services.py --status' to check status")
                    print("Use 'python scripts/manage_services.py --stop-all' to stop all services")
                    break
                elif choice == "12":
                    print("Stopping all services before exit...")
                    self.stop_all_services()
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\nStopping all services before exit...")
                self.stop_all_services()
                print("Goodbye!")
                break

def main():
    """Main entry point."""
    manager = ServiceManager()
    
    # Handle command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--status":
            manager.show_status()
        elif arg == "--start-all":
            manager.start_backend()
            time.sleep(2)
            manager.start_ngrok()
            time.sleep(1)
            manager.start_engine()
            print("✅ All services started!")
        elif arg == "--stop-all":
            manager.stop_all_services()
        elif arg == "--start-backend":
            manager.start_backend()
        elif arg == "--start-ngrok":
            manager.start_ngrok()
        elif arg == "--start-engine":
            manager.start_engine()
        elif arg == "--config":
            manager.configure_services()
        else:
            print(f"Unknown argument: {arg}")
            print("Available arguments: --status, --start-all, --stop-all, --start-backend, --start-ngrok, --start-engine, --config")
    else:
        # Run interactive mode
        manager.run_interactive()

if __name__ == "__main__":
    main() 