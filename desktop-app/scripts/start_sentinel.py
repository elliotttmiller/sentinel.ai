#!/usr/bin/env python3
"""
Sentinel Automated Startup System
Handles complete initialization, dependency checks, database migration, and service startup
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path
from datetime import datetime
import requests
import json

class SentinelStartup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services = {}
        self.running = True
        
    def print_banner(self):
        """Print startup banner"""
        print("=" * 60)
        print("🚀 SENTINEL AUTOMATED STARTUP SYSTEM")
        print("=" * 60)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Project root: {self.project_root}")
        print("=" * 60)
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("🔍 Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    
    def check_dependencies(self):
        """Check and install required dependencies"""
        print("\n📦 Checking dependencies...")
        
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary",
            "python-dotenv", "loguru", "requests", "pydantic",
            "crewai", "langchain-google-genai", "colorama"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package} ✓")
            except ImportError:
                print(f"❌ {package} ✗")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", *missing_packages
                ], check=True, capture_output=True)
                print("✅ Dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                return False
        else:
            print("✅ All dependencies are installed!")
        
        return True
    
    def setup_environment(self):
        """Setup environment and directories"""
        print("\n🔧 Setting up environment...")
        
        # Create necessary directories
        directories = ["logs", "db", "static", "templates"]
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
        
        # Check for .env file
        env_file = self.project_root / ".env"
        if not env_file.exists():
            print("⚠️ No .env file found. Creating default configuration...")
            self.create_default_env()
        
        print("✅ Environment setup complete!")
        return True
    
    def create_default_env(self):
        """Create default .env file"""
        env_content = """# Sentinel Configuration
DATABASE_URL=sqlite:///db/sentinel_missions.db
LLM_MODEL=gemini-1.5-pro-latest
LLM_TEMPERATURE=0.7
GOOGLE_API_KEY=your_google_api_key_here
"""
        with open(self.project_root / ".env", "w") as f:
            f.write(env_content)
        print("✅ Created default .env file")
    
    def migrate_database(self):
        """Run database migration"""
        print("\n🗄️ Running database migration...")
        try:
            result = subprocess.run([
                sys.executable, "fix_database_schema.py"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Database migration completed!")
                return True
            else:
                print(f"⚠️ Database migration had issues: {result.stderr}")
                return True  # Continue anyway
        except Exception as e:
            print(f"❌ Database migration failed: {e}")
            return False
    
    def start_service(self, name, command, port, health_url):
        """Start a service and monitor it"""
        print(f"\n🚀 Starting {name} on port {port}...")
        
        try:
            process = subprocess.Popen(
                command,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.services[name] = {
                "process": process,
                "port": port,
                "health_url": health_url,
                "start_time": datetime.now()
            }
            
            # Wait for service to start
            time.sleep(3)
            
            # Test health endpoint
            if self.test_service_health(health_url):
                print(f"✅ {name} started successfully!")
                return True
            else:
                print(f"⚠️ {name} started but health check failed")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def test_service_health(self, url, timeout=10):
        """Test service health endpoint"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def start_all_services(self):
        """Start all Sentinel services"""
        print("\n🚀 Starting Sentinel services...")
        
        services_config = [
            {
                "name": "Desktop App",
                "command": [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
                "port": 8001,
                "health_url": "http://localhost:8001/health"
            },
            {
                "name": "Cognitive Engine",
                "command": [sys.executable, "-m", "uvicorn", "src.cognitive_engine_service:app", "--host", "0.0.0.0", "--port", "8002", "--reload"],
                "port": 8002,
                "health_url": "http://localhost:8002/health"
            }
        ]
        
        all_started = True
        for service in services_config:
            if not self.start_service(**service):
                all_started = False
        
        return all_started
    
    def monitor_services(self):
        """Monitor running services"""
        print("\n👀 Monitoring services...")
        print("Press Ctrl+C to stop all services")
        
        while self.running:
            try:
                print("\n" + "=" * 60)
                print(f"📊 Service Status - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)
                
                for name, service in self.services.items():
                    status = "🟢 ONLINE" if self.test_service_health(service["health_url"]) else "🔴 OFFLINE"
                    uptime = datetime.now() - service["start_time"]
                    print(f"{name} ({service['port']}): {status} - Uptime: {uptime}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Shutting down services...")
                self.shutdown_services()
                break
    
    def shutdown_services(self):
        """Shutdown all running services"""
        print("\n🛑 Stopping all services...")
        
        for name, service in self.services.items():
            try:
                service["process"].terminate()
                service["process"].wait(timeout=5)
                print(f"✅ Stopped {name}")
            except:
                try:
                    service["process"].kill()
                    print(f"⚠️ Force killed {name}")
                except:
                    print(f"❌ Failed to stop {name}")
        
        self.running = False
    
    def run(self):
        """Run the complete startup sequence"""
        try:
            self.print_banner()
            
            # Step 1: Check Python version
            if not self.check_python_version():
                return False
            
            # Step 2: Check dependencies
            if not self.check_dependencies():
                return False
            
            # Step 3: Setup environment
            if not self.setup_environment():
                return False
            
            # Step 4: Migrate database
            if not self.migrate_database():
                return False
            
            # Step 5: Start services
            if not self.start_all_services():
                print("⚠️ Some services failed to start, but continuing...")
            
            # Step 6: Show status
            print("\n" + "=" * 60)
            print("🎉 SENTINEL STARTUP COMPLETE!")
            print("=" * 60)
            print("📱 Desktop App: http://localhost:8001/")
            print("🧠 Cognitive Engine: http://localhost:8002/")
            print("🔧 Service Manager: python src/utils/manage_services.py")
            print("=" * 60)
            
            # Step 7: Monitor services
            self.monitor_services()
            
        except KeyboardInterrupt:
            print("\n🛑 Startup interrupted by user")
            self.shutdown_services()
        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            self.shutdown_services()
            return False
        
        return True

def main():
    """Main entry point"""
    startup = SentinelStartup()
    success = startup.run()
    
    if success:
        print("\n✅ Sentinel startup completed successfully!")
    else:
        print("\n❌ Sentinel startup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 