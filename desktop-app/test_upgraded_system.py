#!/usr/bin/env python3
"""
Test Upgraded System
Comprehensive test of the upgraded CrewAI tools system
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def test_desktop_app_connection():
    """Test if desktop app is running and accessible"""
    print("🔌 Testing Desktop App Connection...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Desktop App is running and accessible")
            return True
        else:
            print(f"❌ Desktop App responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Desktop App: {e}")
        return False

def test_mission_creation():
    """Test creating a mission with the new tools"""
    print("\n🚀 Testing Mission Creation with New Tools...")
    try:
        # Create a test mission that should use the new tools
        mission_data = {
            "prompt": """Create a Python script that demonstrates the new CrewAI tools:
            1. Create a file called 'demo_tools.py' with a simple function
            2. Write a test function that uses the tools
            3. Create a requirements.txt file for the demo
            4. Test the script to make sure it works
            This should actually create real files on the system.""",
            "agent_type": "developer"
        }
        
        response = requests.post(
            "http://localhost:8001/advanced-mission",
            json=mission_data,
            timeout=30
        )
        
        if response.status_code == 200:
            mission = response.json()
            mission_id = mission.get("mission_id_str")
            print(f"✅ Mission created successfully: {mission_id}")
            return mission_id
        else:
            print(f"❌ Failed to create mission: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating mission: {e}")
        return None

def monitor_mission_status(mission_id, timeout=300):
    """Monitor mission status until completion"""
    print(f"\n📊 Monitoring Mission: {mission_id}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
            if response.status_code == 200:
                mission = response.json()
                status = mission.get("status", "unknown")
                print(f"   Status: {status}")
                
                if status in ["completed", "COMPLETED", "SUCCESS"]:
                    print("✅ Mission completed successfully!")
                    return mission
                elif status in ["failed", "FAILED", "ERROR"]:
                    print("❌ Mission failed!")
                    error = mission.get("error_message", "Unknown error")
                    print(f"   Error: {error}")
                    return mission
                elif status in ["executing", "EXECUTING", "IN_PROGRESS"]:
                    print("   ⏳ Still executing...")
                else:
                    print(f"   ❓ Unknown status: {status}")
            else:
                print(f"   ❌ Failed to get mission status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error monitoring mission: {e}")
        
        time.sleep(5)  # Wait 5 seconds before checking again
    
    print("⏰ Mission monitoring timed out")
    return None

def check_for_created_files():
    """Check if the expected files were actually created"""
    print("\n🔍 Checking for Created Files...")
    
    expected_files = [
        "demo_tools.py",
        "requirements.txt"
    ]
    
    created_files = []
    for file in expected_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            created_files.append(f"✅ {file} ({size} bytes)")
            print(f"✅ {file} - EXISTS ({size} bytes)")
        else:
            print(f"❌ {file} - NOT FOUND")
    
    return len(created_files) > 0

def test_tools_directly():
    """Test the tools directly to ensure they work"""
    print("\n🧪 Testing Tools Directly...")
    
    try:
        # Import and test tools
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from src.tools.crewai_tools import write_file_tool, read_file_tool
        
        # Test file creation
        test_content = f"# Test file created at {datetime.now()}\nprint('Hello from upgraded tools!')"
        result = write_file_tool._run("test_upgrade.py", test_content)
        print(f"   Write result: {result}")
        
        # Test file reading
        result = read_file_tool._run("test_upgrade.py")
        print(f"   Read result: {result[:100]}...")
        
        # Clean up
        if os.path.exists("test_upgrade.py"):
            os.remove("test_upgrade.py")
            print("   🧹 Cleaned up test file")
        
        print("✅ Tools work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 UPGRADED SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Tools functionality
    tools_work = test_tools_directly()
    
    # Test 2: Desktop app connection
    app_running = test_desktop_app_connection()
    
    if not app_running:
        print("\n⚠️ Desktop App is not running. Please start it first.")
        print("   Run: python -m uvicorn src.main:app --host 0.0.0.0 --port 8001")
        return
    
    # Test 3: Mission creation with new tools
    mission_id = test_mission_creation()
    
    if mission_id:
        # Test 4: Monitor mission execution
        result = monitor_mission_status(mission_id)
        
        if result:
            # Test 5: Check for actual file creation
            files_created = check_for_created_files()
            
            # Final assessment
            print("\n🎯 FINAL ASSESSMENT:")
            print("=" * 40)
            print(f"✅ Tools Functionality: {'WORKING' if tools_work else 'FAILED'}")
            print(f"✅ Desktop App: {'RUNNING' if app_running else 'FAILED'}")
            print(f"✅ Mission Creation: {'SUCCESS' if mission_id else 'FAILED'}")
            print(f"✅ Mission Execution: {'SUCCESS' if result else 'FAILED'}")
            print(f"✅ File Creation: {'SUCCESS' if files_created else 'FAILED'}")
            
            if files_created:
                print("\n🎉 UPGRADE SUCCESSFUL! Agents can now perform real file operations!")
            else:
                print("\n⚠️ Upgrade partially successful. Tools work but agents may need adjustment.")
        else:
            print("\n❌ Mission execution failed or timed out")
    else:
        print("\n❌ Mission creation failed")

if __name__ == "__main__":
    main() 