#!/usr/bin/env python3
"""
Cognitive Forge Desktop App Startup Script
Advanced startup with environment validation and system checks
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import validate_environment, create_env_template, settings


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "crewai",
        "langchain-google-genai",
        "sqlalchemy",
        "chromadb",
        "loguru",
        "pydantic",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        "db",
        "logs", 
        "backups",
        "static/css",
        "static/js",
        "static/images",
        "static/fonts",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")


def check_environment():
    """Check and validate environment configuration"""
    print("🔍 Checking environment configuration...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  No .env file found")
        create_env_template()
        print("Please configure your .env file and run again")
        return False
    
    # Validate environment variables
    if not validate_environment():
        return False
    
    return True


def start_server():
    """Start the Cognitive Forge server"""
    print("🚀 Starting Cognitive Forge Desktop App...")
    
    try:
        # Import and run the server
        from src.main import app
        import uvicorn
        
        print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower()
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True


def main():
    """Main startup function"""
    print("🧠 Cognitive Forge Desktop App v3.0.0")
    print("=" * 50)
    
    # Step 1: Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Create directories
    print("📁 Creating directories...")
    create_directories()
    
    # Step 3: Check environment
    print("⚙️  Checking environment...")
    if not check_environment():
        sys.exit(1)
    
    # Step 4: Start server
    print("🚀 Starting server...")
    if not start_server():
        sys.exit(1)


if __name__ == "__main__":
    main() 