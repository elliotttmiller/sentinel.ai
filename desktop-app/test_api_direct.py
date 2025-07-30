#!/usr/bin/env python3
"""
Test API Directly
Simple test of the API endpoints
"""

import requests
import json

def test_api():
    """Test the API directly"""
    print("🧪 Testing API Directly...")
    
    try:
        # Test 1: Health check
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"Health status: {response.status_code}")
        
        # Test 2: Create a simple mission
        print("\n2️⃣ Testing mission creation...")
        mission_data = {
            "prompt": "Create a simple test file called 'test_api.txt' with the content 'Hello from API test!'",
            "agent_type": "developer"
        }
        
        response = requests.post(
            "http://localhost:8001/advanced-mission",
            json=mission_data,
            timeout=30
        )
        
        print(f"Mission creation status: {response.status_code}")
        if response.status_code == 200:
            mission = response.json()
            mission_id = mission.get("mission_id_str")
            print(f"Mission ID: {mission_id}")
            
            # Test 3: Get mission status
            print(f"\n3️⃣ Testing mission status for {mission_id}...")
            response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
            if response.status_code == 200:
                mission_details = response.json()
                status = mission_details.get("status", "unknown")
                print(f"Mission status: {status}")
                
                # Show result if available
                result = mission_details.get("result", "")
                if result:
                    print(f"Result preview: {result[:200]}...")
                
                # Show error if any
                error = mission_details.get("error_message", "")
                if error:
                    print(f"Error: {error}")
            else:
                print(f"Failed to get mission status: {response.status_code}")
        else:
            print(f"Failed to create mission: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api() 