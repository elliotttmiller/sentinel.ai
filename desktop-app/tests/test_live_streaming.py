#!/usr/bin/env python3
"""
Test script to add real server logs and test live streaming
"""

import requests
import time
import random

def add_server_log(server_port, level, message):
    """Add a log entry to a specific server"""
    try:
        response = requests.post(
            f"http://localhost:8001/api/logs/add-server-log",
            params={
                "server_port": server_port,
                "level": level,
                "message": message
            }
        )
        if response.status_code == 200:
            print(f"✅ Added {level} log to server {server_port}: {message}")
        else:
            print(f"❌ Failed to add log to server {server_port}: {response.status_code}")
    except Exception as e:
        print(f"❌ Error adding log to server {server_port}: {e}")

def test_live_streaming():
    """Test the live streaming functionality"""
    print("🚀 Testing Live Log Streaming System...")
    print("=" * 50)
    
    # Server 8001 logs (Desktop App)
    server_8001_logs = [
        ("INFO", "Desktop App server starting on port 8001"),
        ("INFO", "Database connection established"),
        ("INFO", "API endpoints initialized"),
        ("INFO", "WebSocket connections active"),
        ("WARNING", "High memory usage detected"),
        ("ERROR", "Failed to connect to external service"),
        ("INFO", "User authentication successful"),
        ("INFO", "Mission execution started"),
        ("INFO", "Background tasks running"),
        ("INFO", "Cache refreshed successfully")
    ]
    
    # Server 8002 logs (Cognitive Engine)
    server_8002_logs = [
        ("INFO", "Cognitive Engine server starting on port 8002"),
        ("INFO", "AI models loaded successfully"),
        ("INFO", "Neural networks initialized"),
        ("INFO", "Model inference running"),
        ("WARNING", "Model inference taking longer than expected"),
        ("ERROR", "Memory allocation failed"),
        ("INFO", "Agent execution completed"),
        ("INFO", "Learning algorithms active"),
        ("INFO", "Model weights updated"),
        ("INFO", "Prediction accuracy: 94.2%")
    ]
    
    print("📡 Adding Server 8001 logs...")
    for i, (level, message) in enumerate(server_8001_logs):
        add_server_log("8001", level, message)
        time.sleep(0.3)  # 300ms delay between logs
    
    print("\n📡 Adding Server 8002 logs...")
    for i, (level, message) in enumerate(server_8002_logs):
        add_server_log("8002", level, message)
        time.sleep(0.3)  # 300ms delay between logs
    
    print("\n✅ Live streaming test completed!")
    print("📊 Check your browser at http://localhost:8001")
    print("🎯 Look for the logs in the 'Live Event Feed' section")
    print("📱 They should appear in real-time with proper server categorization")

if __name__ == "__main__":
    test_live_streaming() 