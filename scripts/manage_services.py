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
        self.ngrok_config_file = self.project_root / "ngrok.yml"
        self.load_config()

    def load_config(self):
        """Load service configuration from JSON file."""
        default_config = {
            "backend": {
                "port": 8080,
                "host": "0.0.0.0",
                "reload": True
            },
            "ngrok_backend": {
                "port": 8080,
                "subdomain": None
            },
            "ngrok_engine": {
                "port": 8001,
                "subdomain": None
            },
            "engine": {
                "port": 8001,
                "host": "0.0.0.0"
            },
            "ngrok_auth_token": None
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all required keys exist
                    self.config = default_config.copy()
                    self.config.update(loaded_config)
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

    def get_ngrok_auth_token(self) -> Optional[str]:
        """Get ngrok auth token from environment or config."""
        # First try environment variable
        auth_token = os.getenv('NGROK_AUTHTOKEN')
        if auth_token:
            return auth_token
        
        # Then try config file
        if self.config.get('ngrok_auth_token'):
            return self.config['ngrok_auth_token']
        
        return None

    def setup_ngrok_auth_token(self) -> bool:
        """Interactive setup for ngrok auth token."""
        print("\n" + "="*50)
        print("NGROK AUTH TOKEN SETUP")
        print("="*50)
        print("To use ngrok tunnels, you need an auth token from ngrok.com")
        print("1. Go to https://ngrok.com/ and sign up/login")
        print("2. Go to https://dashboard.ngrok.com/get-started/your-authtoken")
        print("3. Copy your auth token")
        print("="*50)
        
        current_token = self.get_ngrok_auth_token()
        if current_token and current_token != 'your-auth-token-here':
            print(f"\nCurrent auth token: {current_token[:10]}...")
            change = input("Do you want to change it? (y/N): ").lower()
            if change != 'y':
                return True
        
        auth_token = input("\nEnter your ngrok auth token: ").strip()
        if not auth_token:
            print("❌ No auth token provided. ngrok tunnels will not work.")
            return False
        
        # Save to config
        self.config['ngrok_auth_token'] = auth_token
        self.save_config()
        
        # Also set as environment variable for this session
        os.environ['NGROK_AUTHTOKEN'] = auth_token
        
        print("✅ ngrok auth token saved!")
        return True

    def check_ngrok_auth_token(self) -> bool:
        """Check if ngrok auth token is properly configured and valid."""
        auth_token = self.get_ngrok_auth_token()
        if not auth_token or auth_token == 'your-auth-token-here':
            print("⚠️  ngrok auth token not configured!")
            return self.setup_ngrok_auth_token()
        
        # Validate the token
        print("🔍 Validating ngrok auth token...")
        try:
            import requests
            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Ngrok-Version': '2'
            }
            response = requests.get('https://api.ngrok.com/tunnels', headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ ngrok auth token is valid!")
                return True
            elif response.status_code == 401:
                print("❌ ngrok auth token is invalid or expired!")
                print("🔄 Let's refresh your token...")
                return self.setup_ngrok_auth_token()
            elif response.status_code == 403:
                print("⚠️  ngrok auth token may be valid but lacks API permissions")
                print("💡 This is usually fine for basic tunneling - continuing...")
                return True
            else:
                print(f"⚠️  ngrok API returned status {response.status_code}")
                print("💡 Continuing anyway - token might still work for tunneling")
                return True
        except Exception as e:
            print(f"⚠️  Could not validate token: {e}")
            print("💡 Continuing anyway - token might still work for tunneling")
            return True

    def get_service_status(self, service_name: str) -> bool:
        """Check if a service is running."""
        if service_name not in self.processes:
            return False
        process = self.processes[service_name]
        if process is None:
            return False
        return process.poll() is None

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
        """Start ngrok tunnel (legacy method - now redirects to start_ngrok_backend)."""
        print("🔄 Redirecting to enhanced ngrok tunnel setup...")
        return self.start_ngrok_backend(port, subdomain)

    def start_ngrok_backend(self, port: Optional[int] = None, subdomain: Optional[str] = None) -> bool:
        """Start ngrok tunnel for backend."""
        if self.get_service_status("ngrok_backend"):
            print("ngrok backend tunnel is already running!")
            return True

        # Check and setup auth token if needed
        if not self.check_ngrok_auth_token():
            return False

        # Ensure config has required sections
        if "ngrok_backend" not in self.config:
            self.config["ngrok_backend"] = {"port": 8080, "subdomain": None}
        if "ngrok_engine" not in self.config:
            self.config["ngrok_engine"] = {"port": 8001, "subdomain": None}
            
        port = port or self.config["ngrok_backend"]["port"]
        subdomain = subdomain or self.config["ngrok_backend"]["subdomain"]

        print(f"Starting ngrok backend tunnel for port {port}...")
        
        try:
            # Create ngrok config file for multiple tunnels
            auth_token = self.get_ngrok_auth_token()
            if not auth_token:
                print("❌ No ngrok auth token available!")
                return False
                
            config_content = f"""version: "2"
authtoken: {auth_token}
tunnels:
  backend:
    addr: {port}
    proto: http
    subdomain: {subdomain or ''}
  engine:
    addr: 8001
    proto: http
"""
            
            # Ensure the config directory exists
            self.ngrok_config_file.parent.mkdir(exist_ok=True)
            
            with open(self.ngrok_config_file, 'w') as f:
                f.write(config_content)
            
            print(f"📝 Created ngrok config: {self.ngrok_config_file}")
            
            cmd = ["ngrok", "start", "--all", "--config", str(self.ngrok_config_file)]
            print(f"🚀 Running: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes["ngrok_backend"] = process
            print(f"✅ ngrok tunnels started (PID: {process.pid})")
            print("📱 Check ngrok web interface at http://localhost:4040 for public URLs")
            print("🔧 Configure your apps with the PUBLIC ngrok URLs:")
            print("   - Mobile app: EXPO_PUBLIC_API_URL=https://your-backend-url.ngrok-free.app")
            print("   - Backend: DESKTOP_TUNNEL_URL=https://your-engine-url.ngrok-free.app")
            return True
            
        except FileNotFoundError:
            print("❌ ngrok command not found! Please install ngrok from https://ngrok.com/download")
            return False
        except Exception as e:
            print(f"❌ Failed to start ngrok tunnels: {e}")
            return False

    def start_ngrok_engine(self, port: Optional[int] = None, subdomain: Optional[str] = None) -> bool:
        """Start ngrok tunnel for engine (deprecated - now handled by start_ngrok_backend)."""
        print("⚠️  Engine tunnel is now handled by the main ngrok session.")
        print("   Use 'Start ngrok Backend Tunnel' to start both tunnels.")
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
            cmd = ["uvicorn", "main:app", "--host", host, "--port", str(port), "--reload"]
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
        
        services = ["backend", "ngrok_backend", "ngrok_engine", "engine"]
        for service in services:
            status = "🟢 RUNNING" if self.get_service_status(service) else "🔴 STOPPED"
            pid = "N/A"
            if service in self.processes and self.processes[service] is not None:
                try:
                    pid = str(self.processes[service].pid)
                except:
                    pid = "N/A"
            print(f"{service.upper():<15} {status} (PID: {pid})")
        
        print("="*50)

    def configure_services(self):
        """Interactive configuration of service settings."""
        print("\n" + "="*50)
        print("SERVICE CONFIGURATION")
        print("="*50)
        
        # ngrok auth token configuration
        print("\nngrok Configuration:")
        if not self.check_ngrok_auth_token():
            print("⚠️  ngrok auth token setup failed!")
            return
        
        # Backend configuration
        print("\nBackend Configuration:")
        try:
            port = int(input(f"Port (current: {self.config['backend']['port']}): ") or self.config['backend']['port'])
            self.config['backend']['port'] = port
        except ValueError:
            print("Invalid port number, keeping current setting")
        
        reload = input(f"Auto-reload (current: {self.config['backend']['reload']}) [y/N]: ").lower() == 'y'
        self.config['backend']['reload'] = reload
        
        # ngrok backend configuration
        print("\nngrok Backend Configuration:")
        try:
            port = int(input(f"Port (current: {self.config['ngrok_backend']['port']}): ") or self.config['ngrok_backend']['port'])
            self.config['ngrok_backend']['port'] = port
        except ValueError:
            print("Invalid port number, keeping current setting")
        
        subdomain = input(f"Subdomain (current: {self.config['ngrok_backend']['subdomain'] or 'None'}): ").strip()
        self.config['ngrok_backend']['subdomain'] = subdomain if subdomain else None
        
        # ngrok engine configuration
        print("\nngrok Engine Configuration:")
        try:
            port = int(input(f"Port (current: {self.config['ngrok_engine']['port']}): ") or self.config['ngrok_engine']['port'])
            self.config['ngrok_engine']['port'] = port
        except ValueError:
            print("Invalid port number, keeping current setting")
        
        subdomain = input(f"Subdomain (current: {self.config['ngrok_engine']['subdomain'] or 'None'}): ").strip()
        self.config['ngrok_engine']['subdomain'] = subdomain if subdomain else None
        
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
        print("2. Start ngrok Tunnels (Backend + Engine)")
        print("3. Start Agent Engine")
        print("4. Start All Services")
        print("5. Stop Backend Server")
        print("6. Stop ngrok Tunnels")
        print("7. Stop Agent Engine")
        print("8. Stop All Services")
        print("9. Show Service Status")
        print("10. Configure Services")
        print("11. Setup ngrok Auth Token")
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
                    self.start_ngrok_backend()
                elif choice == "3":
                    self.start_engine()
                elif choice == "4":
                    print("Starting all services...")
                    self.start_backend()
                    time.sleep(2)
                    self.start_ngrok_backend()
                    time.sleep(1)
                    self.start_engine()
                elif choice == "5":
                    self.stop_service("backend")
                elif choice == "6":
                    self.stop_service("ngrok_backend")
                elif choice == "7":
                    self.stop_service("engine")
                elif choice == "8":
                    self.stop_all_services()
                elif choice == "9":
                    self.show_status()
                elif choice == "10":
                    self.configure_services()
                elif choice == "11":
                    self.setup_ngrok_auth_token()
                elif choice == "12":
                    print("\nStopping all services before exit...")
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
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

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
            manager.start_ngrok_backend()
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