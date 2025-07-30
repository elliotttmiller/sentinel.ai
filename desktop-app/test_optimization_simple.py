#!/usr/bin/env python3
"""
Simplified AI Agent Optimization Test
Tests the optimization system without onnxruntime dependencies
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
            print("✅ Desktop app is running and accessible")
            return True
        else:
            print(f"❌ Desktop app responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to desktop app: {e}")
        return False

def test_mission_creation():
    """Test creating a mission with the new tools"""
    print("\n🚀 Testing Mission Creation...")
    try:
        # Create a test mission
        mission_data = {
            "prompt": """Create a simple Python script that demonstrates the new CrewAI tools:
            1. Create a file called 'test_optimization.py' with a simple function
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

def test_mission_details_api():
    """Test the mission details API functionality"""
    print("\n📋 Testing Mission Details API...")
    try:
        # Get all missions
        response = requests.get("http://localhost:8001/missions", timeout=10)
        if response.status_code == 200:
            missions = response.json()
            print(f"✅ Found {len(missions)} missions")
            
            if missions:
                # Test getting detailed mission info
                first_mission = missions[0]
                mission_id = first_mission.get('mission_id_str', first_mission.get('id'))
                
                response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
                if response.status_code == 200:
                    mission_details = response.json()
                    print("✅ Mission details API working")
                    
                    # Check key fields
                    fields_to_check = ['mission_id_str', 'title', 'status', 'agent_type', 'prompt', 'result', 'plan']
                    for field in fields_to_check:
                        value = mission_details.get(field)
                        if value is not None:
                            print(f"   ✅ {field}: {str(value)[:50]}...")
                        else:
                            print(f"   ⚠️ {field}: Not available")
                    
                    return True
                else:
                    print(f"❌ Failed to get mission details: {response.status_code}")
                    return False
            else:
                print("❌ No missions found to test")
                return False
        else:
            print(f"❌ Failed to get missions: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing mission details API: {e}")
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

def test_agent_tools():
    """Test the agent tools functionality"""
    print("\n🧪 Testing Agent Tools...")
    try:
        # Import tools without onnxruntime dependency
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from src.tools.crewai_tools import write_file_tool, read_file_tool
        
        # Test file creation
        test_content = f"# Test file created at {datetime.now()}\nprint('Hello from optimization test!')"
        result = write_file_tool._run("test_optimization_tools.py", test_content)
        print(f"   Write result: {result}")
        
        # Test file reading
        result = read_file_tool._run("test_optimization_tools.py")
        print(f"   Read result: {result[:100]}...")
        
        # Clean up
        if os.path.exists("test_optimization_tools.py"):
            os.remove("test_optimization_tools.py")
            print("   🧹 Cleaned up test file")
        
        print("✅ Agent tools working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Agent tools test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SIMPLIFIED AI AGENT OPTIMIZATION TEST")
    print("=" * 60)
    
    # Test 1: Desktop app connection
    app_working = test_desktop_app_connection()
    
    # Test 2: Mission details API
    api_working = test_mission_details_api()
    
    # Test 3: Web interface
    web_working = test_web_interface()
    
    # Test 4: Agent tools
    tools_working = test_agent_tools()
    
    # Test 5: Mission creation (if everything else works)
    mission_working = False
    if app_working and tools_working:
        mission_id = test_mission_creation()
        if mission_id:
            result = monitor_mission_status(mission_id, timeout=120)
            mission_working = result is not None and result.get('status') in ['completed', 'COMPLETED', 'SUCCESS']
    
    # Final assessment
    print("\n🎯 TEST SUMMARY:")
    print("=" * 30)
    print(f"✅ Desktop App: {'WORKING' if app_working else 'FAILED'}")
    print(f"✅ Mission Details API: {'WORKING' if api_working else 'FAILED'}")
    print(f"✅ Web Interface: {'WORKING' if web_working else 'FAILED'}")
    print(f"✅ Agent Tools: {'WORKING' if tools_working else 'FAILED'}")
    print(f"✅ Mission Creation: {'WORKING' if mission_working else 'FAILED'}")
    
    if all([app_working, api_working, web_working, tools_working]):
        print("\n🎉 OPTIMIZATION SYSTEM IS WORKING!")
        print("   You can now:")
        print("   - View detailed mission information in the web interface")
        print("   - See AI agent actions and thinking processes")
        print("   - Monitor real-time agent execution")
        print("   - Track performance and optimization opportunities")
    else:
        print("\n⚠️ Some components need attention:")
        if not app_working:
            print("   - Start the desktop app: python -m uvicorn src.main:app --host 0.0.0.0 --port 8001")
        if not tools_working:
            print("   - Check agent tool dependencies")
        if not api_working:
            print("   - Verify API endpoints are working")

if __name__ == "__main__":
    main() 