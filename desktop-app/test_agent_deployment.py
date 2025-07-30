#!/usr/bin/env python3
"""
Agent Deployment Test Script
Tests the desktop app's ability to deploy AI agents and complete tasks on the computer
"""

import requests
import time
import json
import os
from datetime import datetime
from typing import Dict, Any

class AgentDeploymentTester:
    """Test agent deployment and task completion capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        
    def test_connection(self) -> bool:
        """Test if the desktop app is accessible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Desktop App is accessible")
                return True
            else:
                print(f"❌ Desktop App returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Desktop App: {e}")
            return False
    
    def create_test_mission(self, prompt: str, agent_type: str = "developer") -> Dict[str, Any]:
        """Create a test mission"""
        try:
            response = requests.post(
                f"{self.base_url}/advanced-mission",
                json={
                    "prompt": prompt,
                    "agent_type": agent_type,
                    "title": f"Test Mission - {datetime.now().strftime('%H:%M:%S')}"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mission created: {result['mission_id']}")
                return result
            else:
                print(f"❌ Failed to create mission: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating mission: {e}")
            return None
    
    def monitor_mission_status(self, mission_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Monitor mission status until completion or timeout"""
        print(f"🔍 Monitoring mission {mission_id}...")
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/mission/{mission_id}", timeout=5)
                
                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get("status", "unknown")
                    
                    # Print status changes
                    if current_status != last_status:
                        print(f"📊 Status: {current_status}")
                        last_status = current_status
                    
                    # Print latest updates
                    updates = status_data.get("updates", [])
                    if updates:
                        latest_update = updates[-1]
                        print(f"📝 {latest_update.get('message', 'No message')}")
                    
                    # Check if mission is complete
                    if current_status in ["COMPLETED", "SUCCESS", "FINISHED"]:
                        print("🎉 Mission completed successfully!")
                        return status_data
                    elif current_status in ["FAILED", "ERROR"]:
                        print("❌ Mission failed!")
                        return status_data
                    
                else:
                    print(f"⚠️ Status check failed: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
            
            time.sleep(2)  # Check every 2 seconds
        
        print("⏰ Mission monitoring timed out")
        return {"status": "TIMEOUT", "error": "Mission monitoring timed out"}
    
    def run_simple_test(self) -> bool:
        """Run a simple file system task test"""
        print("\n🧪 Running Simple File System Test...")
        
        # Test 1: Create a simple file
        prompt = """
        Create a test file on my desktop called 'sentinel_test.txt' with the following content:
        "This is a test file created by Sentinel AI Agent at {timestamp}"
        Then verify the file was created successfully.
        """
        
        mission = self.create_test_mission(prompt, "developer")
        if not mission:
            return False
        
        result = self.monitor_mission_status(mission["mission_id"], timeout=120)
        return result.get("status") in ["COMPLETED", "SUCCESS"]
    
    def run_code_generation_test(self) -> bool:
        """Run a code generation test"""
        print("\n🧪 Running Code Generation Test...")
        
        prompt = """
        Create a Python script that:
        1. Generates a random number between 1-100
        2. Saves it to a file called 'random_number.txt'
        3. Also prints the number to console
        4. Includes proper error handling
        
        Save this script as 'test_random_generator.py' in the current directory.
        """
        
        mission = self.create_test_mission(prompt, "developer")
        if not mission:
            return False
        
        result = self.monitor_mission_status(mission["mission_id"], timeout=180)
        return result.get("status") in ["COMPLETED", "SUCCESS"]
    
    def run_system_analysis_test(self) -> bool:
        """Run a system analysis test"""
        print("\n🧪 Running System Analysis Test...")
        
        prompt = """
        Analyze my computer system and create a report that includes:
        1. Available disk space
        2. Memory usage
        3. CPU information
        4. List of running processes (top 10)
        5. Network connections
        
        Save this report as 'system_analysis_report.txt' and also display a summary in the console.
        """
        
        mission = self.create_test_mission(prompt, "developer")
        if not mission:
            return False
        
        result = self.monitor_mission_status(mission["mission_id"], timeout=240)
        return result.get("status") in ["COMPLETED", "SUCCESS"]
    
    def run_multi_agent_test(self) -> bool:
        """Run a test requiring multiple agents"""
        print("\n🧪 Running Multi-Agent Test...")
        
        prompt = """
        Create a comprehensive project that demonstrates multiple AI agents working together:
        
        1. First, create a simple web application using Python Flask
        2. Include proper error handling and logging
        3. Add unit tests for the application
        4. Create documentation explaining how to run the app
        5. Generate a requirements.txt file
        6. Test the application to ensure it works
        
        This should involve multiple agents: developer, tester, and documentation specialist.
        Save everything in a folder called 'sentinel_multi_agent_demo'.
        """
        
        mission = self.create_test_mission(prompt, "developer")
        if not mission:
            return False
        
        result = self.monitor_mission_status(mission["mission_id"], timeout=300)
        return result.get("status") in ["COMPLETED", "SUCCESS"]
    
    def run_all_tests(self):
        """Run all agent deployment tests"""
        print("🚀 Starting Agent Deployment Tests...")
        print("=" * 50)
        
        # Test connection first
        if not self.test_connection():
            print("❌ Cannot proceed - Desktop App not accessible")
            return
        
        tests = [
            ("Simple File System Test", self.run_simple_test),
            ("Code Generation Test", self.run_code_generation_test),
            ("System Analysis Test", self.run_system_analysis_test),
            ("Multi-Agent Test", self.run_multi_agent_test)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                success = test_func()
                results[test_name] = "PASS" if success else "FAIL"
                print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                results[test_name] = "ERROR"
        
        # Print summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for result in results.values() if result == "PASS")
        total = len(results)
        
        for test_name, result in results.items():
            status_icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name}: {result}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your agent deployment system is working perfectly!")
        elif passed > 0:
            print("⚠️ Some tests passed. Your system is partially functional.")
        else:
            print("❌ No tests passed. There may be issues with your agent deployment system.")
        
        return results

def main():
    """Main test runner"""
    print("🤖 Sentinel Agent Deployment Test Suite")
    print("Testing AI agent deployment and task completion capabilities")
    print()
    
    # Check if desktop app is running
    tester = AgentDeploymentTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Save results to file
    with open("agent_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Test results saved to: agent_test_results.json")

if __name__ == "__main__":
    main() 