#!/usr/bin/env python3
"""
Debug Agent Execution
Investigates why agents aren't executing and checks real-time status.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8002"
ENGINE_URL = "http://localhost:8001"

def check_service_health():
    """Check if all services are responding."""
    print("🔍 Checking service health...")
    
    try:
        backend_health = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Backend (8002): {backend_health.status_code}")
        
        # Try engine health with longer timeout
        try:
            engine_health = requests.get(f"{ENGINE_URL}/health", timeout=15)
            print(f"Engine (8001): {engine_health.status_code}")
        except Exception as engine_error:
            print(f"Engine (8001): Timeout/Error - {engine_error}")
            # Continue anyway since backend is working
        
        if backend_health.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return False

def check_recent_missions():
    """Check recent missions and their status."""
    print("\n🔍 Checking recent missions...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
        if response.status_code == 200:
            missions = response.json()
            print(f"Found {len(missions)} total missions")
            
            # Show last 5 missions
            recent_missions = missions[-5:] if len(missions) >= 5 else missions
            for mission in recent_missions:
                mission_id = mission.get('mission_id_str', 'N/A')
                title = mission.get('title', 'N/A')
                status = mission.get('status', 'N/A')
                created = mission.get('created_at', 'N/A')
                print(f"  - {mission_id}: {title} ({status}) - {created}")
            
            return missions
        else:
            print(f"❌ Failed to get missions: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Failed to get missions: {e}")
        return []

def check_live_events():
    """Check live events for agent activity."""
    print("\n🔍 Checking live events...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/events/live", timeout=10)
        if response.status_code == 200:
            events = response.json()
            print(f"Found {len(events)} live events")
            
            # Show last 10 events
            recent_events = events[-10:] if len(events) >= 10 else events
            for event in recent_events:
                timestamp = event.get('timestamp', 'N/A')
                level = event.get('level', 'INFO')
                message = event.get('message', 'No message')
                print(f"  [{timestamp}] {level}: {message}")
            
            return events
        else:
            print(f"❌ Failed to get live events: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Failed to get live events: {e}")
        return []

def check_mission_status(mission_id):
    """Check specific mission status."""
    print(f"\n🔍 Checking mission status: {mission_id}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
        if response.status_code == 200:
            missions = response.json()
            
            # Find the specific mission
            target_mission = None
            for mission in missions:
                if mission.get('mission_id_str') == mission_id:
                    target_mission = mission
                    break
            
            if target_mission:
                print(f"Mission found:")
                print(f"  ID: {target_mission.get('mission_id_str')}")
                print(f"  Title: {target_mission.get('title')}")
                print(f"  Status: {target_mission.get('status')}")
                print(f"  Created: {target_mission.get('created_at')}")
                print(f"  Prompt: {target_mission.get('prompt', 'N/A')[:100]}...")
                
                if target_mission.get('result'):
                    print(f"  Result: {target_mission.get('result')}")
                else:
                    print("  Result: None")
                
                return target_mission
            else:
                print(f"❌ Mission {mission_id} not found in database")
                return None
        else:
            print(f"❌ Failed to get missions: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Failed to check mission status: {e}")
        return None

def create_test_mission():
    """Create a new test mission to see if it gets processed."""
    print("\n🚀 Creating new test mission...")
    
    test_mission = {
        "prompt": "Create a simple Python function that prints 'Hello World'",
        "title": "Debug Test Mission",
        "agent_type": "developer"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/missions",
            json=test_mission,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            mission_id = result.get('mission_id')
            print(f"✅ Mission created successfully!")
            print(f"   Mission ID: {mission_id}")
            print(f"   Status: {result.get('message', 'N/A')}")
            return mission_id
        else:
            print(f"❌ Mission creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Mission creation failed: {e}")
        return None

def monitor_mission_execution(mission_id, max_wait=60):
    """Monitor a mission for execution progress."""
    print(f"\n👀 Monitoring mission {mission_id} for {max_wait} seconds...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        mission = check_mission_status(mission_id)
        if mission:
            current_status = mission.get('status', 'unknown')
            if current_status != last_status:
                print(f"  Status changed: {current_status} at {datetime.now().strftime('%H:%M:%S')}")
                last_status = current_status
            
            if current_status in ['completed', 'failed']:
                print(f"  Mission {current_status}!")
                return current_status
        
        time.sleep(5)
    
    print("  ⏰ Monitoring timeout - mission still pending")
    return 'timeout'

def main():
    """Main debug execution."""
    print("="*60)
    print(" 🔧 AGENT EXECUTION DEBUG ".center(60, "="))
    print("="*60)
    print(f"Debug started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check service health
    if not check_service_health():
        print("❌ Services are not healthy. Cannot proceed.")
        return
    
    # Step 2: Check recent missions
    missions = check_recent_missions()
    
    # Step 3: Check live events
    events = check_live_events()
    
    # Step 4: Create a new test mission
    mission_id = create_test_mission()
    if mission_id:
        # Step 5: Monitor the mission execution
        final_status = monitor_mission_execution(mission_id, max_wait=30)
        
        print(f"\n📊 DEBUG SUMMARY:")
        print(f"  - Services: ✅ Healthy")
        print(f"  - Total missions: {len(missions)}")
        print(f"  - Live events: {len(events)}")
        print(f"  - Test mission: {mission_id}")
        print(f"  - Final status: {final_status}")
        
        if final_status == 'pending':
            print("\n❌ ISSUE DETECTED: Mission is stuck in pending status")
            print("   This indicates the background task is not executing properly")
            print("   Possible causes:")
            print("   1. Background task not being triggered")
            print("   2. Async execution issue in the background task")
            print("   3. Database connection issue")
            print("   4. Agent initialization problem")
        elif final_status == 'completed':
            print("\n✅ SUCCESS: Mission completed successfully!")
        elif final_status == 'failed':
            print("\n❌ FAILURE: Mission failed during execution")
        else:
            print(f"\n⏳ TIMEOUT: Mission still pending after monitoring period")

if __name__ == "__main__":
    main() 