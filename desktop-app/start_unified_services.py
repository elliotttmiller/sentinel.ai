#!/usr/bin/env python3
"""
Unified Service Startup Script
Runs both Desktop App and Cognitive Engine together
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_services():
    """Start both services in parallel"""
    print("🚀 Starting Unified Sentinel Services...")
    
    # Change to desktop-app directory
    os.chdir(Path(__file__).parent)
    
    # Start Desktop App on port 8001
    print("📱 Starting Desktop App on port 8001...")
    desktop_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "src.main:app", 
        "--host", "0.0.0.0", "--port", "8001", "--reload"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment for desktop app to start
    time.sleep(3)
    
    # Start Cognitive Engine on port 8002
    print("🧠 Starting Cognitive Engine on port 8002...")
    engine_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "src.cognitive_engine_service:app", 
        "--host", "0.0.0.0", "--port", "8002", "--reload"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("✅ Both services started!")
    print("📱 Desktop App: http://localhost:8001")
    print("🧠 Cognitive Engine: http://localhost:8002")
    print("🔧 Service Manager: python src/utils/manage_services.py")
    print("\nPress Ctrl+C to stop all services...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        desktop_process.terminate()
        engine_process.terminate()
        print("✅ Services stopped.")

if __name__ == "__main__":
    start_services() 