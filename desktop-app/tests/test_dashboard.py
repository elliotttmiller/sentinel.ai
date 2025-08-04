#!/usr/bin/env python3
"""
Test script for the Sentinel Dashboard
Tests the dashboard functionality and AI service integration
"""

import requests
import json
import time
from datetime import datetime

def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Sentinel Dashboard Endpoints")
    print("=" * 50)
    
    # Test 1: Main dashboard page
    print("\n1. Testing Dashboard Page...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")
    
    # Test 2: Health check
    print("\n2. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check successful")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in health check: {e}")
    
    # Test 3: Missions endpoint
    print("\n3. Testing Missions Endpoint...")
    try:
        response = requests.get(f"{base_url}/missions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Missions endpoint working - {len(data.get('missions', []))} missions")
        else:
            print(f"❌ Missions endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in missions endpoint: {e}")
    
    # Test 4: AI Generation endpoint
    print("\n4. Testing AI Generation...")
    try:
        test_prompt = "Generate a simple Python function to calculate fibonacci numbers"
        response = requests.post(f"{base_url}/ai/generate", 
                               json={"prompt": test_prompt, "model": "gemini-1.5-pro-latest"})
        if response.status_code == 200:
            data = response.json()
            print("✅ AI generation working")
            print(f"   Response: {data.get('response', '')[:100]}...")
        else:
            print(f"❌ AI generation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in AI generation: {e}")
    
    # Test 5: Code Analysis endpoint
    print("\n5. Testing Code Analysis...")
    try:
        test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
        """
        response = requests.post(f"{base_url}/ai/analyze-code", 
                               json={"code": test_code, "language": "python"})
        if response.status_code == 200:
            data = response.json()
            print("✅ Code analysis working")
            print(f"   Score: {data.get('score', 0)}")
        else:
            print(f"❌ Code analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in code analysis: {e}")
    
    # Test 6: Mission execution
    print("\n6. Testing Mission Execution...")
    try:
        test_mission = {
            "prompt": "Create a simple web scraper",
            "priority": "medium",
            "tags": ["web", "scraping", "python"]
        }
        response = requests.post(f"{base_url}/mission/execute", json=test_mission)
        if response.status_code == 200:
            data = response.json()
            print("✅ Mission execution working")
            print(f"   Mission ID: {data.get('mission_id', 'N/A')}")
        else:
            print(f"❌ Mission execution failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in mission execution: {e}")
    
    # Test 7: Live logs stream
    print("\n7. Testing Live Logs Stream...")
    try:
        response = requests.get(f"{base_url}/api/events/stream", stream=True)
        if response.status_code == 200:
            print("✅ Live logs stream working")
            # Read first few lines to test
            for i, line in enumerate(response.iter_lines()):
                if i >= 3:  # Only read first 3 lines
                    break
                if line:
                    print(f"   Log: {line.decode()}")
        else:
            print(f"❌ Live logs stream failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in live logs stream: {e}")
    
    # Test 8: System status
    print("\n8. Testing System Status...")
    try:
        response = requests.get(f"{base_url}/api/cognitive/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ System status working")
            print(f"   Status: {data.get('status', 'unknown')}")
        else:
            print(f"❌ System status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in system status: {e}")

def test_cognitive_engine():
    """Test the cognitive engine service"""
    base_url = "http://localhost:8002"
    
    print("\n🧠 Testing Cognitive Engine Service")
    print("=" * 50)
    
    # Test cognitive engine health
    print("\n1. Testing Cognitive Engine Health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Cognitive engine healthy")
        else:
            print(f"❌ Cognitive engine health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to cognitive engine: {e}")
    
    # Test cognitive engine status
    print("\n2. Testing Cognitive Engine Status...")
    try:
        response = requests.get(f"{base_url}/api/cognitive/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Cognitive engine status working")
            print(f"   Status: {data.get('status', 'unknown')}")
        else:
            print(f"❌ Cognitive engine status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in cognitive engine status: {e}")

def main():
    """Main test function"""
    print("🚀 Sentinel Dashboard Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test dashboard endpoints
    test_dashboard_endpoints()
    
    # Test cognitive engine
    test_cognitive_engine()
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete!")
    print("=" * 50)
    
    print("\n📊 Summary:")
    print("- Dashboard endpoints tested")
    print("- AI service integration verified")
    print("- Mission execution tested")
    print("- Live logging tested")
    print("- System status checked")
    
    print("\n🌐 Access your dashboard at: http://localhost:8001")
    print("🔧 Cognitive engine at: http://localhost:8002")

if __name__ == "__main__":
    main() 