#!/usr/bin/env python3
"""
Direct Engine Test
Test if the engine can execute real desktop tasks.
"""
import requests
import json
import time
import os

ENGINE_URL = "http://localhost:8001"

def test_engine_direct():
    """Test direct engine execution of desktop tasks."""
    print("🚀 Testing direct engine execution...")
    
    # Simple desktop task
    task = {
        "mission_id": f"direct-test-{int(time.time())}",
        "steps": [
            {
                "step_id": "step-1",
                "agent_type": "simple_test",
                "action": "execute_desktop_task",
                "parameters": {
                    "task": "Create test file on desktop",
                    "command": "echo 'Direct Engine Test - $(Get-Date)' > $env:USERPROFILE\\Desktop\\sentinel_direct_test.txt",
                    "description": "Test direct engine execution"
                }
            }
        ],
        "metadata": {
            "test_mode": True,
            "timeout": 30
        }
    }
    
    print("Sending task to engine:")
    print(json.dumps(task, indent=2))
    
    try:
        response = requests.post(f"{ENGINE_URL}/execute_mission", json=task, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Task sent to engine!")
            print(json.dumps(result, indent=2))
            
            # Wait for completion
            mission_id = task["mission_id"]
            max_wait = 30
            wait_time = 0
            
            print("Waiting for execution...")
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                
                result_response = requests.get(f"{ENGINE_URL}/mission_result/{mission_id}", timeout=5)
                if result_response.status_code == 200:
                    result = result_response.json()
                    if result.get('status') == 'completed':
                        print("🎉 Task completed successfully!")
                        print(f"Output: {result.get('output', 'No output')}")
                        
                        # Check if file was created
                        desktop_path = os.path.expanduser("~/Desktop/sentinel_direct_test.txt")
                        if os.path.exists(desktop_path):
                            print(f"✅ File created: {desktop_path}")
                            with open(desktop_path, 'r') as f:
                                content = f.read()
                                print(f"Content: {content}")
                        else:
                            print("❌ File was not created")
                        
                        return True
                    elif result.get('status') == 'failed':
                        print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
                        return False
                
                print(f"Waiting... ({wait_time}s/{max_wait}s)")
            
            print("⏰ Execution timeout")
            return False
        else:
            print(f"❌ Failed to send task: HTTP {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_engine_direct() 