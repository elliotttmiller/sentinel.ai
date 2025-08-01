#!/usr/bin/env python3
"""
Simple test to trigger agent execution and check for errors
"""

import requests
import time
import json

def test_agent_execution():
    """Test agent execution and check for errors"""
    print("🚀 Testing agent execution...")
    
    # Create a simple mission
    mission_data = {
        "prompt": "Create a simple Python function that prints 'Hello World'",
        "title": "Simple Test Mission",
        "agent_type": "developer"
    }
    
    try:
        # Create mission
        response = requests.post(
            "http://localhost:8002/api/missions",
            json=mission_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            mission_id = result.get("mission_id")
            print(f"✅ Mission created: {mission_id}")
            
            # Wait a moment for background task to start
            time.sleep(2)
            
            # Check mission status
            status_response = requests.get(
                "http://localhost:8002/missions",
                timeout=10
            )
            
            if status_response.status_code == 200:
                missions = status_response.json()
                for mission in missions:
                    if mission.get("id") == mission_id:
                        status = mission.get("status")
                        result = mission.get("result")
                        print(f"📊 Mission status: {status}")
                        if result:
                            print(f"📝 Result: {result[:200]}...")
                        break
            else:
                print(f"❌ Failed to get mission status: {status_response.status_code}")
                
        else:
            print(f"❌ Failed to create mission: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_agent_execution() 