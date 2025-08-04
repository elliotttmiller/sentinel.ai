#!/usr/bin/env python3
"""
Test Real Agent Execution
Comprehensive test to verify if agents are actually executing tasks.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8002"

def test_real_agent_execution():
    """Test if agents are actually executing tasks."""
    print("="*60)
    print(" 🤖 REAL AGENT EXECUTION TEST ".center(60, "="))
    print("="*60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Create a simple but realistic mission
    print("\n1. Creating realistic mission...")
    realistic_mission = {
        "prompt": "Create a Python function that calculates the factorial of a number and save it to a file called factorial.py",
        "title": "Real Agent Test - Factorial Function",
        "agent_type": "developer"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/missions",
            json=realistic_mission,
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
    
    # Step 2: Monitor the mission for a longer period
    print(f"\n2. Monitoring mission {mission_id} for 60 seconds...")
    
    start_time = time.time()
    max_wait = 60
    last_status = None
    status_changes = []
    
    while time.time() - start_time < max_wait:
        try:
            # Get all missions and find our specific one
            response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
            if response.status_code == 200:
                missions = response.json()
                
                # Find our specific mission
                target_mission = None
                for mission in missions:
                    if mission.get('mission_id_str') == mission_id:
                        target_mission = mission
                        break
                
                if target_mission:
                    current_status = target_mission.get('status', 'unknown')
                    current_time = datetime.now().strftime('%H:%M:%S')
                    
                    if current_status != last_status:
                        print(f"  [{current_time}] Status changed: {current_status}")
                        status_changes.append({
                            'time': current_time,
                            'status': current_status
                        })
                        last_status = current_status
                    
                    # Check if mission has a result
                    if target_mission.get('result'):
                        print(f"  [{current_time}] ✅ Mission has result!")
                        print(f"     Result: {target_mission.get('result')}")
                        return True
                    
                    # Check if mission failed
                    if current_status == 'failed':
                        print(f"  [{current_time}] ❌ Mission failed!")
                        return False
                    
                    # Check if mission completed
                    if current_status == 'completed':
                        print(f"  [{current_time}] 🎉 Mission completed!")
                        if target_mission.get('result'):
                            print(f"     Result: {target_mission.get('result')}")
                        return True
                
            time.sleep(5)
            
        except Exception as e:
            print(f"  Error monitoring mission: {e}")
            time.sleep(5)
    
    print(f"\n⏰ Monitoring timeout after {max_wait} seconds")
    print(f"Status changes observed: {len(status_changes)}")
    for change in status_changes:
        print(f"  - {change['time']}: {change['status']}")
    
    return False

def check_live_events_for_agent_activity():
    """Check live events for any agent activity."""
    print("\n3. Checking live events for agent activity...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/events/live", timeout=10)
        if response.status_code == 200:
            events = response.json()
            print(f"Found {len(events)} live events")
            
            # Look for agent-related events
            agent_events = []
            for event in events:
                message = event.get('message', '').lower()
                if any(keyword in message for keyword in ['agent', 'phase', 'executing', 'testing', 'planning']):
                    agent_events.append(event)
            
            if agent_events:
                print(f"✅ Found {len(agent_events)} agent-related events:")
                for event in agent_events[-5:]:  # Show last 5
                    timestamp = event.get('timestamp', 'N/A')
                    level = event.get('level', 'INFO')
                    message = event.get('message', 'No message')
                    print(f"  [{timestamp}] {level}: {message}")
            else:
                print("❌ No agent-related events found")
                print("   This suggests agents are not executing")
            
            return len(agent_events) > 0
        else:
            print(f"❌ Failed to get live events: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to check live events: {e}")
        return False

def main():
    """Main test execution."""
    try:
        # Test 1: Real agent execution
        agent_execution_success = test_real_agent_execution()
        
        # Test 2: Check for agent activity in events
        agent_activity_found = check_live_events_for_agent_activity()
        
        # Summary
        print("\n" + "="*60)
        print(" 📊 REAL AGENT EXECUTION TEST RESULTS ".center(60, "="))
        print("="*60)
        
        if agent_execution_success:
            print("🎉 SUCCESS: Agents are executing and completing missions!")
            print("✅ Your agent deployment system is fully operational!")
        else:
            print("❌ ISSUE: Agents are not executing properly")
            print("\nPossible causes:")
            print("1. Background task not being triggered")
            print("2. Agent initialization issues")
            print("3. Database connection problems")
            print("4. Missing dependencies or configuration")
        
        if agent_activity_found:
            print("✅ Agent activity detected in live events")
        else:
            print("❌ No agent activity detected in live events")
        
        print(f"\nRecommendations:")
        if not agent_execution_success:
            print("- Check server logs for detailed error messages")
            print("- Verify all dependencies are installed")
            print("- Check database connectivity")
            print("- Review agent configuration files")
        else:
            print("- Your agents are working! Try more complex missions")
            print("- Monitor the dashboard for real-time updates")
            print("- Check generated files in your workspace")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main() 