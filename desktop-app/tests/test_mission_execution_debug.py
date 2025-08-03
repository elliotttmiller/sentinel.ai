#!/usr/bin/env python3
"""
Comprehensive mission execution debug test
"""

import requests
import time
import json
from datetime import datetime

def test_mission_execution_debug():
    """Test mission execution with detailed debugging"""
    print("🔍 COMPREHENSIVE MISSION EXECUTION DEBUG")
    print("=" * 50)
    
    # Step 1: Check service health
    print("\n1️⃣ Checking service health...")
    try:
        backend_response = requests.get("http://localhost:8002/health", timeout=5)
        engine_response = requests.get("http://localhost:8001/health", timeout=5)
        
        print(f"   Backend: {backend_response.status_code}")
        print(f"   Engine: {engine_response.status_code}")
        
        if backend_response.status_code == 200 and engine_response.status_code == 200:
            print("   ✅ Services are healthy")
        else:
            print("   ❌ Service health issues detected")
            return
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Step 2: Create a test mission
    print("\n2️⃣ Creating test mission...")
    mission_data = {
        "prompt": "Create a simple Python function that prints 'Hello World'",
        "title": "Debug Test Mission",
        "agent_type": "developer"
    }
    
    try:
        response = requests.post(
            "http://localhost:8002/api/missions",
            json=mission_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            mission_id = result.get("mission_id")
            print(f"   ✅ Mission created: {mission_id}")
            print(f"   📝 Status: {result.get('status')}")
            print(f"   📅 Created: {result.get('created_at')}")
        else:
            print(f"   ❌ Mission creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Mission creation error: {e}")
        return
    
    # Step 3: Monitor mission execution
    print("\n3️⃣ Monitoring mission execution...")
    start_time = time.time()
    max_wait_time = 60  # 60 seconds
    
    while time.time() - start_time < max_wait_time:
        try:
            # Check mission status
            status_response = requests.get(
                "http://localhost:8002/missions",
                timeout=5
            )
            
            if status_response.status_code == 200:
                missions = status_response.json()
                
                # Find our mission
                for mission in missions:
                    if mission.get("id") == mission_id:
                        status = mission.get("status")
                        result = mission.get("result")
                        updated_at = mission.get("updated_at")
                        
                        elapsed = time.time() - start_time
                        print(f"   ⏱️  {elapsed:.1f}s - Status: {status}")
                        
                        if result:
                            print(f"   📝 Result: {result[:200]}...")
                            print("   ✅ Mission completed!")
                            return
                        
                        if status == "failed":
                            print(f"   ❌ Mission failed!")
                            return
                        
                        break
                else:
                    print(f"   ⏱️  {time.time() - start_time:.1f}s - Mission not found in list")
            
            # Wait before next check
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            time.sleep(2)
    
    print(f"   ⏰ Timeout after {max_wait_time} seconds")
    print("   ❌ Mission did not complete within expected time")
    
    # Step 4: Check for any errors in recent logs
    print("\n4️⃣ Checking for execution errors...")
    print("   💡 Check the server logs for any error messages during mission execution")
    print("   💡 Look for messages containing the mission ID:", mission_id)

if __name__ == "__main__":
    test_mission_execution_debug() 