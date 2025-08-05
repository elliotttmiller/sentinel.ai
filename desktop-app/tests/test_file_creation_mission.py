#!/usr/bin/env python3
"""
Test script to send a file creation mission to the server
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8002"

def test_file_creation_mission():
    """Test if agents are actually executing tasks."""
    print("="*60)
    print(" 📁 FILE CREATION MISSION TEST ".center(60, "="))
    print("="*60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create a file creation mission
    print("\nCreating file creation mission...")
    mission_data = {
        "prompt": "Create a file named 'hello_world_test.txt' with the content 'This file was created by a fixed Sentinel agent.'",
        "title": "File Creation Test",
        "agent_type": "developer"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/missions",
            json=mission_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            mission_id = result.get('mission_id')
            print(f"✅ Mission created successfully!")
            print(f"   Mission ID: {mission_id}")
            print(f"   Status: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Mission creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Mission creation failed: {e}")
        return False
    
    # Wait for mission to complete
    print(f"\nWaiting for mission to complete...")
    time.sleep(5)
    
    # Check if the file was created
    print("\nChecking workspace for the created file...")
    import os
    workspace_dir = os.path.join(os.path.dirname(__file__), "workspace")
    file_path = os.path.join(workspace_dir, "hello_world_test.txt")
    
    if os.path.exists(file_path):
        print(f"✅ Success! File was created at: {file_path}")
        with open(file_path, 'r') as f:
            content = f.read()
        print(f"   Content: {content}")
        return True
    else:
        print(f"❌ File was not found at: {file_path}")
        print("   Files in workspace:")
        for f in os.listdir(workspace_dir):
            print(f"   - {f}")
        return False

if __name__ == "__main__":
    test_file_creation_mission()
