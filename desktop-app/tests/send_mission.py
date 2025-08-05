#!/usr/bin/env python3
"""
Simple script to send a mission to the server.
Usage:
  python send_mission.py "Create a file named 'mission_test.txt' with the content 'Created by a mission'"
"""

import sys
import os
import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"

def send_mission(prompt):
    """Send a mission to the server."""
    print("="*60)
    print(" 🚀 SENDING MISSION ".center(60, "="))
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mission: {prompt}")
    
    mission_data = {
        "prompt": prompt,
        "title": f"Mission Test: {prompt[:30]}...",
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
            mission_info = result.get('mission', {})
            mission_id = mission_info.get('mission_id_str') if mission_info else None
            status = mission_info.get('status', 'N/A') if mission_info else 'N/A'
            
            print(f"✅ Mission sent successfully!")
            print(f"   Mission ID: {mission_id}")
            print(f"   Status: {status}")
            print("\nTo check results, look in the workspace directory.")
        else:
            print(f"❌ Mission creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Mission creation failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_mission.py \"Your mission prompt\"")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    send_mission(prompt)
