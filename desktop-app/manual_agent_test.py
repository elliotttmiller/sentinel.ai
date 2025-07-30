#!/usr/bin/env python3
"""
Manual Agent Test Script
Simple script to test individual agent tasks manually
"""

import requests
import time
import json
from datetime import datetime

def test_single_mission(prompt: str, agent_type: str = "developer"):
    """Test a single mission with the given prompt"""
    
    base_url = "http://localhost:8001"
    
    print(f"🤖 Testing Agent Mission")
    print(f"Prompt: {prompt[:100]}...")
    print(f"Agent Type: {agent_type}")
    print("-" * 50)
    
    # Create mission
    try:
        response = requests.post(
            f"{base_url}/advanced-mission",
            json={
                "prompt": prompt,
                "agent_type": agent_type,
                "title": f"Manual Test - {datetime.now().strftime('%H:%M:%S')}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            mission_id = result["mission_id"]
            print(f"✅ Mission created: {mission_id}")
            
            # Monitor progress
            print("\n📊 Monitoring mission progress...")
            print("=" * 50)
            
            while True:
                try:
                    status_response = requests.get(f"{base_url}/mission/{mission_id}", timeout=5)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get("status", "unknown")
                        
                        # Print latest update
                        updates = status_data.get("updates", [])
                        if updates:
                            latest_update = updates[-1]
                            print(f"📝 {latest_update.get('message', 'No message')}")
                        
                        # Check if complete
                        if current_status in ["COMPLETED", "SUCCESS", "FINISHED"]:
                            print("\n🎉 Mission completed successfully!")
                            print(f"Final result: {status_data.get('result', 'No result')}")
                            return True
                        elif current_status in ["FAILED", "ERROR"]:
                            print("\n❌ Mission failed!")
                            print(f"Error: {status_data.get('result', 'Unknown error')}")
                            return False
                        
                    else:
                        print(f"⚠️ Status check failed: {status_response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error checking status: {e}")
                
                time.sleep(2)  # Check every 2 seconds
                
        else:
            print(f"❌ Failed to create mission: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating mission: {e}")
        return False

def main():
    """Main function with example tests"""
    
    print("🤖 Sentinel Manual Agent Test")
    print("=" * 50)
    
    # Example test missions
    test_missions = [
        {
            "name": "Simple File Creation",
            "prompt": "Create a file called 'hello_sentinel.txt' on my desktop with the message 'Hello from Sentinel AI!'",
            "agent_type": "developer"
        },
        {
            "name": "System Information",
            "prompt": "Get information about my computer system including CPU, memory, and disk usage. Save this as 'system_info.txt'",
            "agent_type": "developer"
        },
        {
            "name": "Python Script Generation",
            "prompt": "Create a Python script that calculates the factorial of a number and saves the result to a file. Include error handling.",
            "agent_type": "developer"
        }
    ]
    
    print("Available test missions:")
    for i, mission in enumerate(test_missions, 1):
        print(f"{i}. {mission['name']}")
    
    print("\nOr enter your own custom prompt:")
    print("Enter 'custom' to create your own mission")
    
    choice = input("\nSelect a test (1-3) or 'custom': ").strip()
    
    if choice.lower() == "custom":
        prompt = input("Enter your custom prompt: ")
        agent_type = input("Enter agent type (developer/tester/documentation): ").strip() or "developer"
        test_single_mission(prompt, agent_type)
    elif choice in ["1", "2", "3"]:
        idx = int(choice) - 1
        mission = test_missions[idx]
        test_single_mission(mission["prompt"], mission["agent_type"])
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 