#!/usr/bin/env python3
"""
Simple test to check background task execution
"""

import requests
import time
import json

def test_background_task():
    """Test if background tasks are running"""
    print("🔍 Testing background task execution...")
    
    # Create a simple mission
    mission_data = {
        "prompt": "Create a simple Python function that prints 'Hello World'",
        "title": "Background Task Test",
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
            
            # Check if there are any recent logs or events
            events_response = requests.get(
                "http://localhost:8002/api/events/live",
                timeout=5
            )
            
            if events_response.status_code == 200:
                events = events_response.json()
                print(f"📊 Found {len(events)} live events")
                
                # Look for events related to our mission
                for event in events:
                    if mission_id in str(event):
                        print(f"🔍 Found mission event: {event}")
            else:
                print(f"❌ Failed to get events: {events_response.status_code}")
                
        else:
            print(f"❌ Failed to create mission: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_background_task() 