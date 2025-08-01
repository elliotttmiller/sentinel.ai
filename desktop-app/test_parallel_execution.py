#!/usr/bin/env python3
"""
Test script for parallel execution and database JSON fixes
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_PROMPTS = {
    "standard": "Create a simple Python function to calculate fibonacci numbers",
    "complex": "Build a complete web application with user authentication, database integration, and API endpoints",
    "advanced": "Design and implement a distributed microservices architecture with load balancing, caching, monitoring, and automated deployment pipelines"
}

def test_standard_mission():
    """Test standard mission execution"""
    print("🧪 Testing Standard Mission...")
    
    payload = {
        "prompt": TEST_PROMPTS["standard"],
        "title": "Test Standard Mission",
        "agent_type": "developer",
        "complexity_level": "standard"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/parallel-missions", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Standard mission created: {result['mission_id']}")
            return result['mission_id']
        else:
            print(f"❌ Standard mission failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Standard mission error: {e}")
        return None

def test_complex_mission():
    """Test complex mission execution"""
    print("🧪 Testing Complex Mission...")
    
    payload = {
        "prompt": TEST_PROMPTS["complex"],
        "title": "Test Complex Mission",
        "agent_type": "developer",
        "complexity_level": "complex"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/parallel-missions", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Complex mission created: {result['mission_id']}")
            return result['mission_id']
        else:
            print(f"❌ Complex mission failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Complex mission error: {e}")
        return None

def test_advanced_mission():
    """Test advanced mission execution"""
    print("🧪 Testing Advanced Mission...")
    
    payload = {
        "prompt": TEST_PROMPTS["advanced"],
        "title": "Test Advanced Mission",
        "agent_type": "developer",
        "complexity_level": "advanced"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/parallel-missions", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Advanced mission created: {result['mission_id']}")
            return result['mission_id']
        else:
            print(f"❌ Advanced mission failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Advanced mission error: {e}")
        return None

def monitor_mission(mission_id, timeout=300):
    """Monitor mission progress"""
    print(f"📊 Monitoring mission: {mission_id}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/api/parallel-mission/{mission_id}")
            if response.status_code == 200:
                status = response.json()
                current_status = status.get('status', 'unknown')
                print(f"🔄 Mission {mission_id}: {current_status}")
                
                if current_status in ['completed', 'failed']:
                    print(f"🏁 Mission {mission_id} finished with status: {current_status}")
                    
                    # Check if result is properly stored as JSON
                    result = status.get('result')
                    if result:
                        try:
                            if isinstance(result, str):
                                json.loads(result)
                                print(f"✅ Result stored as valid JSON")
                            else:
                                print(f"✅ Result stored as object")
                        except json.JSONDecodeError:
                            print(f"❌ Result is not valid JSON: {result}")
                    
                    return current_status
                
                # Show recent updates
                updates = status.get('real_time_updates', [])
                if updates:
                    latest_update = updates[-1]
                    print(f"📝 Latest update: {latest_update.get('message', 'No message')}")
                
            else:
                print(f"⚠️ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
        
        time.sleep(5)  # Check every 5 seconds
    
    print(f"⏰ Mission {mission_id} timed out after {timeout} seconds")
    return "timeout"

def test_parallel_execution_stats():
    """Test parallel execution statistics"""
    print("📊 Testing Parallel Execution Statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/parallel-execution/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Parallel execution stats retrieved:")
            print(f"   Total parallel missions: {stats.get('total_parallel_missions', 0)}")
            print(f"   By complexity: {stats.get('by_complexity', {})}")
            print(f"   Success rates: {stats.get('success_rates', {})}")
            return True
        else:
            print(f"❌ Stats failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return False

def test_database_json_fix():
    """Test that database JSON storage is working correctly"""
    print("🔧 Testing Database JSON Fix...")
    
    # Test with a simple mission
    payload = {
        "prompt": "Test JSON storage fix",
        "title": "JSON Test Mission",
        "agent_type": "developer",
        "complexity_level": "standard"
    }
    
    try:
        # Create mission
        response = requests.post(f"{BASE_URL}/api/parallel-missions", json=payload)
        if response.status_code == 200:
            result = response.json()
            mission_id = result['mission_id']
            print(f"✅ Test mission created: {mission_id}")
            
            # Wait a bit for processing
            time.sleep(10)
            
            # Check mission status
            status_response = requests.get(f"{BASE_URL}/api/parallel-mission/{mission_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                result_data = status.get('result')
                
                if result_data:
                    try:
                        if isinstance(result_data, str):
                            parsed_result = json.loads(result_data)
                            print(f"✅ Result is valid JSON: {type(parsed_result)}")
                            
                            # Check for expected fields
                            expected_fields = ['summary', 'status', 'execution_time', 'timestamp']
                            missing_fields = [field for field in expected_fields if field not in parsed_result]
                            
                            if missing_fields:
                                print(f"⚠️ Missing expected fields: {missing_fields}")
                            else:
                                print(f"✅ All expected fields present in JSON result")
                                
                        else:
                            print(f"✅ Result is object: {type(result_data)}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Result is not valid JSON: {e}")
                        return False
                else:
                    print(f"⚠️ No result data available yet")
                
                return True
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
        else:
            print(f"❌ Mission creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ JSON test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Parallel Execution and Database Tests")
    print("=" * 60)
    
    # Test database JSON fix first
    print("\n1. Testing Database JSON Fix")
    json_test_passed = test_database_json_fix()
    
    # Test parallel execution statistics
    print("\n2. Testing Parallel Execution Statistics")
    stats_test_passed = test_parallel_execution_stats()
    
    # Test different complexity levels
    print("\n3. Testing Mission Complexity Levels")
    
    # Test standard mission
    standard_mission_id = test_standard_mission()
    if standard_mission_id:
        monitor_mission(standard_mission_id, timeout=60)
    
    # Test complex mission
    complex_mission_id = test_complex_mission()
    if complex_mission_id:
        monitor_mission(complex_mission_id, timeout=120)
    
    # Test advanced mission
    advanced_mission_id = test_advanced_mission()
    if advanced_mission_id:
        monitor_mission(advanced_mission_id, timeout=180)
    
    print("\n" + "=" * 60)
    print("🏁 Test Summary:")
    print(f"   Database JSON Fix: {'✅ PASSED' if json_test_passed else '❌ FAILED'}")
    print(f"   Parallel Stats: {'✅ PASSED' if stats_test_passed else '❌ FAILED'}")
    print(f"   Standard Mission: {'✅ CREATED' if standard_mission_id else '❌ FAILED'}")
    print(f"   Complex Mission: {'✅ CREATED' if complex_mission_id else '❌ FAILED'}")
    print(f"   Advanced Mission: {'✅ CREATED' if advanced_mission_id else '❌ FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main() 