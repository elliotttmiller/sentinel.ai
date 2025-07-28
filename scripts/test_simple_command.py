#!/usr/bin/env python3
"""
Simple Command Test
Test a basic command execution on the engine.
"""
import requests
import json
import time

ENGINE_URL = "http://localhost:8001"

def test_simple_command():
    """Test a simple command execution."""
    print("🚀 Testing simple command execution...")
    
    # Very simple command
    task = {
        "mission_id": f"simple-test-{int(time.time())}",
        "steps": [
            {
                "step_id": "step-1",
                "agent_type": "simple_test",
                "action": "execute_desktop_task",
                "parameters": {
                    "task": "Create a simple test file",
                    "command": "echo 'Hello from Sentinel Engine' > C:\\temp\\sentinel_test.txt",
                    "description": "Simple test command"
                }
            }
        ],
        "metadata": {
            "test_mode": True,
            "timeout": 30
        }
    }
    
    print("Sending simple command to engine:")
    print(json.dumps(task, indent=2))
    
    try:
        response = requests.post(f"{ENGINE_URL}/execute_mission", json=task, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Task sent to engine!")
            
            # Wait for completion
            mission_id = task["mission_id"]
            max_wait = 30
            wait_time = 0
            
            print("Waiting for execution...")
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                
                result_response = requests.get(f"{ENGINE_URL}/mission_result/{mission_id}", timeout=5)
                print(f"Result status: {result_response.status_code}")
                print(f"Result: {result_response.text}")
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    if result.get('status') == 'completed':
                        print("🎉 Task completed successfully!")
                        print(f"Output: {result.get('output', 'No output')}")
                        return True
                    elif result.get('status') == 'failed':
                        print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
                        return False
                
                print(f"Waiting... ({wait_time}s/{max_wait}s)")
            
            print("⏰ Execution timeout")
            return False
        else:
            print(f"❌ Failed to send task: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_simple_command() 