import requests
import json
from config import settings

def test_dispatch():
    """Test dispatching a mission to the desktop engine."""
    try:
        # Test the desktop engine health
        print(f"Testing desktop engine at: {settings.DESKTOP_TUNNEL_URL}")
        
        health_url = f"{settings.DESKTOP_TUNNEL_URL}/health"
        print(f"Health check URL: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        print(f"Health check response: {response.status_code}")
        print(f"Health check content: {response.text}")
        
        # Test the execute_mission endpoint
        execute_url = f"{settings.DESKTOP_TUNNEL_URL}/execute_mission"
        print(f"Execute mission URL: {execute_url}")
        
        # Create a simple test mission
        test_mission = {
            "mission_id": "test_mission_123",
            "steps": [
                {
                    "step_id": "step_1",
                    "action": "create_file",
                    "parameters": {
                        "file_path": "C:/Users/AMD/Desktop/test_file.txt",
                        "content": "This is a test file created by Sentinel AI"
                    }
                }
            ]
        }
        
        print(f"Sending test mission: {json.dumps(test_mission, indent=2)}")
        
        response = requests.post(execute_url, json=test_mission, timeout=30)
        print(f"Execute mission response: {response.status_code}")
        print(f"Execute mission content: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dispatch() 