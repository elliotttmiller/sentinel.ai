#!/usr/bin/env python3
"""
Test Mission Details
Test the enhanced mission details functionality
"""

import requests
import json
import time

def test_mission_details():
    """Test the mission details functionality"""
    print("🧪 Testing Mission Details Functionality...")
    
    try:
        # Test 1: Get all missions
        print("\n1️⃣ Getting all missions...")
        response = requests.get("http://localhost:8001/missions", timeout=10)
        if response.status_code == 200:
            missions = response.json()
            print(f"✅ Found {len(missions)} missions")
            
            if missions:
                # Test 2: Get detailed mission info for the first mission
                first_mission = missions[0]
                mission_id = first_mission.get('mission_id_str', first_mission.get('id'))
                print(f"\n2️⃣ Getting detailed info for mission: {mission_id}")
                
                response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
                if response.status_code == 200:
                    mission_details = response.json()
                    print("✅ Mission details retrieved successfully!")
                    
                    # Display key information
                    print(f"\n📋 Mission Details:")
                    print(f"   ID: {mission_details.get('mission_id_str', mission_details.get('id'))}")
                    print(f"   Title: {mission_details.get('title', 'N/A')}")
                    print(f"   Status: {mission_details.get('status', 'N/A')}")
                    print(f"   Agent Type: {mission_details.get('agent_type', 'N/A')}")
                    print(f"   Created: {mission_details.get('created_at', 'N/A')}")
                    
                    # Check for plan
                    plan = mission_details.get('plan', {})
                    if plan and plan.get('steps'):
                        print(f"   Plan Steps: {len(plan['steps'])}")
                        for i, step in enumerate(plan['steps'][:3], 1):  # Show first 3 steps
                            print(f"     Step {i}: {step.get('agent_role', 'Unknown')} - {step.get('task_description', 'N/A')[:100]}...")
                    
                    # Check for result
                    result = mission_details.get('result', '')
                    if result:
                        print(f"   Result: {result[:200]}{'...' if len(result) > 200 else ''}")
                    else:
                        print("   Result: No result available")
                    
                    # Check for error
                    error = mission_details.get('error_message', '')
                    if error:
                        print(f"   Error: {error}")
                    
                    # Check for execution time
                    exec_time = mission_details.get('execution_time')
                    if exec_time:
                        print(f"   Execution Time: {exec_time} seconds")
                    
                    print("\n✅ Mission details test completed successfully!")
                    return True
                else:
                    print(f"❌ Failed to get mission details: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            else:
                print("❌ No missions found to test")
                return False
        else:
            print(f"❌ Failed to get missions: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing mission details: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface():
    """Test the web interface"""
    print("\n🌐 Testing Web Interface...")
    try:
        response = requests.get("http://localhost:8001/", timeout=10)
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            print("   Open http://localhost:8001 in your browser")
            print("   Go to the Missions tab and click 'View Details' on any mission")
            return True
        else:
            print(f"❌ Web interface not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing web interface: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Mission Details Test")
    print("=" * 50)
    
    # Test API functionality
    api_success = test_mission_details()
    
    # Test web interface
    web_success = test_web_interface()
    
    print("\n🎯 Test Summary:")
    print("=" * 30)
    print(f"✅ API Functionality: {'PASS' if api_success else 'FAIL'}")
    print(f"✅ Web Interface: {'PASS' if web_success else 'FAIL'}")
    
    if api_success and web_success:
        print("\n🎉 Mission Details Feature is Working!")
        print("   You can now view detailed mission information including:")
        print("   - AI execution plans with step-by-step breakdown")
        print("   - Agent actions and results")
        print("   - Performance metrics and timing")
        print("   - Error messages and debugging info")
        print("   - File operation details")
    else:
        print("\n⚠️ Some tests failed. Check the desktop app is running.") 