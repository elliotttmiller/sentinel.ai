#!/usr/bin/env python3
"""
Cognitive Forge v5.0 Startup Script
Comprehensive system validation and launch
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import requests
import json

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*20} {title.upper()} {'='*20}")

def print_success(msg):
    """Print success message"""
    print(f"✅ {msg}")

def print_error(msg):
    """Print error message"""
    print(f"❌ {msg}")

def print_info(msg):
    """Print info message"""
    print(f"ℹ️  {msg}")

def print_warning(msg):
    """Print warning message"""
    print(f"⚠️  {msg}")

def check_environment():
    """Check environment configuration"""
    print_header("Environment Check")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print_error("Python 3.11+ required")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check required directories
    required_dirs = ["logs", "db", "static"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print_info(f"Created directory: {dir_name}")
        else:
            print_success(f"Directory exists: {dir_name}")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print_warning(".env file not found")
        print_info("Please create .env file with your configuration")
        return False
    print_success(".env file found")
    
    return True

def validate_dependencies():
    """Validate required dependencies"""
    print_header("Dependency Check")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "loguru",
        "sqlalchemy",
        "chromadb",
        "pydantic-settings"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT FOUND")
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_database_connection():
    """Test database connectivity"""
    print_header("Database Test")
    
    try:
        from src.models.advanced_database import db_manager
        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def test_hybrid_engine():
    """Test hybrid decision engine"""
    print_header("Hybrid Engine Test")
    
    try:
        from src.core.hybrid_decision_engine import hybrid_decision_engine
        
        # Test basic functionality
        test_prompt = "Hello world"
        decision = hybrid_decision_engine.make_hybrid_decision(test_prompt)
        
        if decision and "path" in decision:
            print_success("Hybrid decision engine working")
            print_info(f"Test decision: {decision['path']}")
            return True
        else:
            print_error("Hybrid engine returned invalid decision")
            return False
    except Exception as e:
        print_error(f"Hybrid engine test failed: {e}")
        return False

def test_cognitive_engine():
    """Test cognitive forge engine"""
    print_header("Cognitive Engine Test")
    
    try:
        from src.core.cognitive_forge_engine import cognitive_forge_engine
        print_success("Cognitive forge engine initialized")
        return True
    except Exception as e:
        print_error(f"Cognitive engine test failed: {e}")
        return False

def wait_for_server(url, timeout=30):
    """Wait for server to be ready"""
    print_info(f"Waiting for server at {url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print_success("Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    print_error("Server did not start within timeout")
    return False

def launch_server():
    """Launch the Cognitive Forge server"""
    print_header("Launching Server")
    
    print_success("Starting Sentinel Cognitive Forge v5.0")
    print_info("Server will be available at: http://localhost:8001")
    print_info("Press CTRL+C to shut down the server")
    print_info("Real-time logs will be streamed to the browser")
    
    try:
        # Launch server with uvicorn
        subprocess.run([
            "uvicorn", 
            "src.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print_header("Cognitive Forge v5.0 Startup")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print_info(f"Working directory: {os.getcwd()}")
    
    # Run validation checks
    checks = [
        ("Environment", check_environment),
        ("Dependencies", validate_dependencies),
        ("Database", test_database_connection),
        ("Hybrid Engine", test_hybrid_engine),
        ("Cognitive Engine", test_cognitive_engine)
    ]
    
    failed_checks = []
    for check_name, check_func in checks:
        if not check_func():
            failed_checks.append(check_name)
    
    if failed_checks:
        print_header("Validation Failed")
        print_error(f"Failed checks: {', '.join(failed_checks)}")
        print_info("Please fix the issues above before starting the server")
        return False
    
    print_header("All Systems Ready")
    print_success("✅ All validation checks passed")
    print_info("🚀 Ready to launch Cognitive Forge v5.0")
    
    # Launch server
    return launch_server()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1) 