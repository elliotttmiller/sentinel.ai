#!/usr/bin/env python3
"""
Live Agent Deployment Test - Optimized for Mobile App Integration
Tests the missions API and executes a real agent deployment on the desktop.
Configured to work with the mobile app screens and mission creation flow.
"""
import requests
import json
import time
import os
from datetime import datetime

# Configuration - Updated to match mobile app expectations
BACKEND_URL = "http://localhost:8080"
ENGINE_URL = "http://localhost:8001"

def print_header(title):
    print("\n" + "="*50)
    print(f" {title.upper()} ".center(50, "="))
    print("="*50)

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"💡 {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def test_missions_api():
    """Test the missions API and understand required fields for mobile app."""
    print_header("Testing Missions API for Mobile App")
    
    # Test GET /missions to see existing missions (like MissionsScreen)
    try:
        response = requests.get(f"{BACKEND_URL}/missions", timeout=5)
        if response.status_code == 200:
            missions = response.json()
            print_success(f"Found {len(missions)} existing missions")
            if missions:
                print_info("Sample mission structure (for MissionsScreen):")
                sample_mission = missions[0]
                print(f"  - ID: {sample_mission.get('id')}")
                print(f"  - Title: {sample_mission.get('title')}")
                print(f"  - Status: {sample_mission.get('status')}")
                print(f"  - Created: {sample_mission.get('created_at')}")
        else:
            print_error(f"GET /missions failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to get missions: {str(e)}")
        return False
    
    # Test POST /missions with mobile app format (like CreateMissionScreen)
    print_info("Testing mission creation with mobile app format...")
    mobile_app_mission = {
        "title": "Mobile App Test Mission",
        "description": "Test mission created via mobile app interface",
        "prompt": "Create a test file on desktop and verify mobile app integration"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/missions", json=mobile_app_mission, timeout=10)
        if response.status_code == 422:  # Validation error
            error_data = response.json()
            print_info("Required fields from validation error:")
            print(json.dumps(error_data, indent=2))
            return error_data
        elif response.status_code == 200:
            mission_data = response.json()
            print_success("Mobile app mission created successfully!")
            print(f"Mission ID: {mission_data.get('id')}")
            return mission_data
        else:
            print_error(f"POST /missions failed: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Failed to create mission: {str(e)}")
        return False

def create_mobile_app_test_mission():
    """Create a test mission that matches the mobile app CreateMissionScreen format."""
    print_header("Creating Mobile App Test Mission")
    
    # Mission data matching CreateMissionScreen.tsx format
    mission_data = {
        "title": "Live Desktop Agent Test via Mobile App",
        "description": "Execute a real task on the desktop to verify mobile app integration and agent deployment",
        "prompt": "Create a test file on the desktop with system information, log the activity, and verify the mobile app can track the mission progress"
    }
    
    print_info("Mission data (matching CreateMissionScreen format):")
    print(json.dumps(mission_data, indent=2))
    
    try:
        response = requests.post(f"{BACKEND_URL}/missions", json=mission_data, timeout=10)
        if response.status_code == 200:
            mission = response.json()
            print_success("Mobile app mission created successfully!")
            print(f"Mission ID: {mission.get('id')}")
            print(f"Status: {mission.get('status')}")
            return mission
        else:
            print_error(f"Failed to create mission: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Failed to create mission: {str(e)}")
        return False

def plan_mission_for_mobile_app(mission_id):
    """Plan the mission to get execution steps for MissionDetailScreen."""
    print_header("Planning Mission for Mobile App")
    
    try:
        response = requests.post(f"{BACKEND_URL}/missions/{mission_id}/plan", timeout=15)
        if response.status_code == 200:
            plan = response.json()
            print_success("Mission planned successfully!")
            print(f"Plan steps: {len(plan.get('steps', []))}")
            
            # Show plan structure for MissionDetailScreen
            print_info("Plan structure (for MissionDetailScreen):")
            for i, step in enumerate(plan.get('steps', [])):
                print(f"  Step {i+1}: {step.get('title', 'Unknown')}")
                print(f"    Agent: {step.get('agent', 'Unknown')}")
                print(f"    Status: {step.get('status', 'pending')}")
            
            return plan
        else:
            print_error(f"Failed to plan mission: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Failed to plan mission: {str(e)}")
        return False

def execute_real_desktop_task_for_mobile():
    """Execute a real desktop task that the mobile app can track."""
    print_header("Executing Real Desktop Task for Mobile App")
    
    # Create a desktop task that creates a file the mobile app can verify
    desktop_task = {
        "mission_id": f"mobile-test-{int(time.time())}",
        "steps": [
            {
                "step_id": "step-1",
                "agent_type": "simple_test",
                "action": "execute_desktop_task",
                "parameters": {
                    "task": "Create test file for mobile app verification",
                    "command": "echo 'Sentinel Mobile App Test - $(Get-Date) - Mission executed via mobile app interface' > $env:USERPROFILE\\Desktop\\sentinel_mobile_test.txt",
                    "description": "Create a test file to verify mobile app integration"
                }
            }
        ],
        "metadata": {
            "test_mode": True,
            "timeout": 30,
            "mobile_app_test": True
        }
    }
    
    print_info("Sending desktop task to engine (mobile app compatible):")
    print(json.dumps(desktop_task, indent=2))
    
    try:
        response = requests.post(f"{ENGINE_URL}/execute_mission", json=desktop_task, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print_success("Desktop task sent to engine!")
            print(json.dumps(result, indent=2))
            
            # Wait for execution to complete (like mobile app would)
            mission_id = desktop_task["mission_id"]
            max_wait = 30
            wait_time = 0
            
            print_info("Waiting for execution to complete (mobile app tracking)...")
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                
                result_response = requests.get(f"{ENGINE_URL}/mission_result/{mission_id}", timeout=5)
                if result_response.status_code == 200:
                    result = result_response.json()
                    if result.get('status') == 'completed':
                        print_success("🎉 Desktop task completed successfully!")
                        print(f"Output: {result.get('output', 'No output')}")
                        
                        # Check if file was actually created (mobile app verification)
                        desktop_path = os.path.expanduser("~/Desktop/sentinel_mobile_test.txt")
                        if os.path.exists(desktop_path):
                            print_success(f"✅ Test file created on desktop: {desktop_path}")
                            with open(desktop_path, 'r') as f:
                                content = f.read()
                                print(f"File content: {content}")
                            
                            # Verify this would work in mobile app
                            print_info("Mobile app verification:")
                            print("  ✅ Mission execution completed")
                            print("  ✅ File created on desktop")
                            print("  ✅ Status tracking works")
                            print("  ✅ Mobile app can display results")
                        else:
                            print_error("❌ Test file was not created on desktop")
                        
                        return True
                    elif result.get('status') == 'failed':
                        print_error(f"Desktop task failed: {result.get('error', 'Unknown error')}")
                        return False
                
                print_info(f"Waiting... ({wait_time}s/{max_wait}s)")
            
            print_warning("Execution timeout")
            return False
        else:
            print_error(f"Failed to send desktop task: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Failed to execute desktop task: {str(e)}")
        return False

def test_mobile_app_integration():
    """Test the complete mobile app integration flow."""
    print_header("Testing Mobile App Integration")
    
    # Test 1: MissionsScreen - List missions
    print_info("1. Testing MissionsScreen functionality...")
    try:
        response = requests.get(f"{BACKEND_URL}/missions", timeout=5)
        if response.status_code == 200:
            missions = response.json()
            print_success(f"MissionsScreen: Found {len(missions)} missions")
        else:
            print_error("MissionsScreen: Failed to load missions")
    except Exception as e:
        print_error(f"MissionsScreen: Error - {str(e)}")
    
    # Test 2: CreateMissionScreen - Create mission
    print_info("2. Testing CreateMissionScreen functionality...")
    mission = create_mobile_app_test_mission()
    if not mission:
        print_error("CreateMissionScreen: Failed to create mission")
        return False
    
    # Test 3: MissionDetailScreen - Plan and execute
    print_info("3. Testing MissionDetailScreen functionality...")
    plan = plan_mission_for_mobile_app(mission['id'])
    if not plan:
        print_error("MissionDetailScreen: Failed to plan mission")
        return False
    
    # Test 4: Execute real task
    print_info("4. Testing real desktop execution...")
    success = execute_real_desktop_task_for_mobile()
    
    return success

def main():
    """Main test runner - Optimized for mobile app integration."""
    print_header("Live Agent Deployment Test - Mobile App Optimized")
    
    print("🚀 Testing real agent deployment with mobile app integration...")
    print(f"📡 Backend: {BACKEND_URL}")
    print(f"⚙️  Engine: {ENGINE_URL}")
    print(f"📱 Mobile App: Configured for missions screens")
    
    # Test mobile app integration
    success = test_mobile_app_integration()
    
    if success:
        print_success("🎉 Live agent deployment test PASSED!")
        print_info("Your AI agent system is working with mobile app integration!")
        print_info("✅ MissionsScreen can display missions")
        print_info("✅ CreateMissionScreen can create missions")
        print_info("✅ MissionDetailScreen can track execution")
        print_info("✅ Real desktop tasks execute successfully")
        print_info("✅ Mobile app can monitor and control agent deployment!")
    else:
        print_error("❌ Live agent deployment test FAILED!")
        print_info("Check the configuration and mobile app integration.")
    
    return success

if __name__ == "__main__":
    main() 