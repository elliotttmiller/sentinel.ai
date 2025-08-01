#!/usr/bin/env python3
"""
Test Background Task
Simple test to trigger background task and check for errors.
"""

import requests
import time
import json

# Configuration
BACKEND_URL = "http://localhost:8002"

def test_background_task():
    """Test if background task is being triggered."""
    print("🚀 Testing background task execution...")
    
    # Create a simple mission
    test_mission = {
        "prompt": "Print 'Hello World'",
        "title": "Background Task Test",
        "agent_type": "developer"
    }
    
    try:
        print("Creating mission...")
        response = requests.post(
            f"{BACKEND_URL}/api/missions",
            json=test_mission,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            mission_id = result.get('mission_id')
            print(f"✅ Mission created: {mission_id}")
            
            # Wait a moment for background task to start
            print("Waiting 5 seconds for background task to start...")
            time.sleep(5)
            
            # Check mission status
            print("Checking mission status...")
            status_response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
            if status_response.status_code == 200:
                missions = status_response.json()
                
                # Find our mission
                target_mission = None
                for mission in missions:
                    if mission.get('mission_id_str') == mission_id:
                        target_mission = mission
                        break
                
                if target_mission:
                    status = target_mission.get('status', 'unknown')
                    print(f"Mission status: {status}")
                    
                    if status == 'pending':
                        print("❌ Background task not executing - mission still pending")
                        print("   This indicates the background task is not running")
                    elif status == 'completed':
                        print("✅ Background task executed successfully!")
                    elif status == 'failed':
                        print("❌ Background task failed")
                    else:
                        print(f"⏳ Background task status: {status}")
                else:
                    print("❌ Mission not found in database")
            else:
                print(f"❌ Failed to check mission status: {status_response.status_code}")
        else:
            print(f"❌ Mission creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def check_server_logs():
    """Check if there are any recent error logs."""
    print("\n🔍 Checking for recent server activity...")
    
    try:
        # Check live events for any errors
        events_response = requests.get(f"{BACKEND_URL}/api/events/live", timeout=10)
        if events_response.status_code == 200:
            events = events_response.json()
            print(f"Recent events: {len(events)}")
            
            # Look for error events
            error_events = [e for e in events if e.get('level') == 'ERROR']
            if error_events:
                print("❌ Found error events:")
                for event in error_events[-3:]:  # Show last 3 errors
                    print(f"  [{event.get('timestamp')}] {event.get('message')}")
            else:
                print("✅ No error events found")
        else:
            print(f"❌ Failed to get events: {events_response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to check events: {e}")

def main():
    """Main test execution."""
    print("="*60)
    print(" 🔧 BACKGROUND TASK TEST ".center(60, "="))
    print("="*60)
    
    # Test background task
    test_background_task()
    
    # Check for errors
    check_server_logs()
    
    print("\n" + "="*60)
    print(" 📊 TEST SUMMARY ".center(60, "="))
    print("="*60)
    print("If the mission remains 'pending', the background task is not executing.")
    print("This could be due to:")
    print("1. Background task not being triggered")
    print("2. Async execution issues")
    print("3. Missing dependencies")
    print("4. Database connection problems")
    print("\nCheck the server logs for any error messages.")

if __name__ == "__main__":
    main() 