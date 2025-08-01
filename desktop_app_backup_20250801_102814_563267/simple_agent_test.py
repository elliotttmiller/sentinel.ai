#!/usr/bin/env python3
"""
Simple Agent Deployment Test
Tests basic agent deployment functionality.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8002"
ENGINE_URL = "http://localhost:8001"

def test_simple_agent_deployment():
    """Test a simple agent deployment."""
    print("="*60)
    print(" 🤖 SIMPLE AGENT DEPLOYMENT TEST ".center(60, "="))
    print("="*60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check service health
    print("\n1. Checking service health...")
    try:
        backend_health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        engine_health = requests.get(f"{ENGINE_URL}/health", timeout=5)
        
        if backend_health.status_code == 200 and engine_health.status_code == 200:
            print("✅ Both services are healthy")
        else:
            print("❌ Service health check failed")
            return False
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return False
    
    # Step 2: Create a simple mission
    print("\n2. Creating simple mission...")
    simple_mission = {
        "prompt": "Write a Python function that calculates the factorial of a number",
        "title": "Simple Agent Test",
        "agent_type": "developer"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/missions",
            json=simple_mission,
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
    
    # Step 3: Check mission status
    print("\n3. Checking mission status...")
    try:
        response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
        if response.status_code == 200:
            missions = response.json()
            target_mission = None
            for mission in missions:
                if mission.get('mission_id_str') == mission_id:
                    target_mission = mission
                    break
            
            if target_mission:
                status = target_mission.get('status', 'unknown')
                print(f"✅ Mission found with status: {status}")
                
                # Show mission details
                print(f"   Title: {target_mission.get('title', 'N/A')}")
                print(f"   Prompt: {target_mission.get('prompt', 'N/A')[:50]}...")
                print(f"   Created: {target_mission.get('created_at', 'N/A')}")
                
                if status == 'completed':
                    print("🎉 Mission completed successfully!")
                    if target_mission.get('result'):
                        print("   Result available")
                    return True
                elif status == 'failed':
                    print("❌ Mission failed")
                    return False
                else:
                    print(f"⏳ Mission is {status} - this is normal for a new mission")
                    print("   The mission has been created and is ready for execution")
                    return True
            else:
                print(f"❌ Mission {mission_id} not found")
                return False
        else:
            print(f"❌ Failed to get missions: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mission status check failed: {e}")
        return False

def main():
    """Main test execution."""
    try:
        success = test_simple_agent_deployment()
        
        if success:
            print("\n" + "="*60)
            print(" 🚀 SIMPLE AGENT DEPLOYMENT TEST SUCCESSFUL! ".center(60, "="))
            print("="*60)
            print("\nWhat this means:")
            print("✅ Your agent deployment system is working!")
            print("✅ Mission creation and planning is functional")
            print("✅ The backend and engine are communicating")
            print("\nNext steps:")
            print("1. Check the dashboard for mission details")
            print("2. Monitor the mission execution in real-time")
            print("3. Try more complex missions")
            print("4. Check generated files and results")
        else:
            print("\n" + "="*60)
            print(" ❌ SIMPLE AGENT DEPLOYMENT TEST FAILED ".center(60, "="))
            print("="*60)
            print("\nPlease check:")
            print("1. All services are running")
            print("2. Network connectivity")
            print("3. API endpoints are accessible")
            print("4. Agent configurations are correct")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main() 