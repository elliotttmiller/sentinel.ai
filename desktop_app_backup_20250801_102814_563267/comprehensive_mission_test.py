#!/usr/bin/env python3
"""
Comprehensive Mission Test Script
Tests the complete mission workflow end-to-end with detailed logging and status tracking
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any

class ComprehensiveMissionTester:
    def __init__(self, backend_url: str = "http://localhost:8002"):
        self.backend_url = backend_url
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_health_check(self) -> bool:
        """Test backend health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Backend health check passed")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend health check error: {e}", "ERROR")
            return False
    
    def create_test_mission(self, title: str, prompt: str, agent_type: str = "developer") -> Dict[str, Any]:
        """Create a test mission and return mission data"""
        try:
            payload = {
                "prompt": prompt,
                "title": title,
                "agent_type": agent_type
            }
            
            self.log(f"🚀 Creating test mission: {title}")
            response = requests.post(f"{self.backend_url}/api/missions", json=payload, timeout=10)
            
            if response.status_code == 200:
                mission_data = response.json()
                self.log(f"✅ Mission created: {mission_data['mission_id']}")
                return mission_data
            else:
                self.log(f"❌ Mission creation failed: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Mission creation error: {e}", "ERROR")
            return None
    
    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Get current mission status"""
        try:
            response = requests.get(f"{self.backend_url}/missions", timeout=5)
            if response.status_code == 200:
                missions = response.json()
                for mission in missions:
                    if mission.get("mission_id_str") == mission_id:
                        return mission
                return None
            else:
                self.log(f"❌ Failed to get missions: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Error getting mission status: {e}", "ERROR")
            return None
    
    def monitor_mission_progress(self, mission_id: str, timeout_minutes: int = 5) -> Dict[str, Any]:
        """Monitor mission progress with detailed status tracking"""
        self.log(f"👀 Monitoring mission {mission_id} for {timeout_minutes} minutes...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_status = None
        
        while time.time() - start_time < timeout_seconds:
            mission_data = self.get_mission_status(mission_id)
            
            if mission_data:
                current_status = mission_data.get("status", "unknown")
                current_time = datetime.now().strftime("%H:%M:%S")
                
                if current_status != last_status:
                    self.log(f"🔄 Status change at {current_time}: {current_status}")
                    last_status = current_status
                
                if current_status == "completed":
                    self.log(f"✅ Mission {mission_id} completed successfully!")
                    return {"status": "completed", "data": mission_data}
                elif current_status == "failed":
                    self.log(f"❌ Mission {mission_id} failed!")
                    return {"status": "failed", "data": mission_data}
                elif current_status == "executing":
                    self.log(f"⚡ Mission {mission_id} is executing...")
                elif current_status == "pending":
                    self.log(f"⏳ Mission {mission_id} is pending...")
            
            time.sleep(10)  # Check every 10 seconds
        
        self.log(f"⏰ Mission {mission_id} monitoring timeout", "WARNING")
        return {"status": "timeout", "data": mission_data}
    
    def test_complete_workflow(self) -> Dict[str, Any]:
        """Test the complete mission workflow end-to-end"""
        self.log("🧪 Starting comprehensive mission workflow test")
        
        # Test 1: Health Check
        if not self.test_health_check():
            return {"success": False, "error": "Backend health check failed"}
        
        # Test 2: Create Mission
        test_prompt = "Create a simple Python function that prints 'Hello World' and returns the string"
        mission_data = self.create_test_mission(
            title="Comprehensive Test Mission",
            prompt=test_prompt,
            agent_type="developer"
        )
        
        if not mission_data:
            return {"success": False, "error": "Mission creation failed"}
        
        mission_id = mission_data["mission_id"]
        
        # Test 3: Monitor Mission Progress
        result = self.monitor_mission_progress(mission_id, timeout_minutes=5)
        
        # Test 4: Verify Final Status
        final_mission_data = self.get_mission_status(mission_id)
        
        test_result = {
            "success": result["status"] == "completed",
            "mission_id": mission_id,
            "final_status": result["status"],
            "execution_time": final_mission_data.get("execution_time") if final_mission_data else None,
            "result": final_mission_data.get("result") if final_mission_data else None,
            "error": result.get("error")
        }
        
        if test_result["success"]:
            self.log("🎉 Comprehensive test PASSED!")
        else:
            self.log(f"❌ Comprehensive test FAILED: {test_result['error']}", "ERROR")
        
        return test_result
    
    def run_multiple_tests(self, num_tests: int = 3) -> Dict[str, Any]:
        """Run multiple tests to verify system stability"""
        self.log(f"🧪 Running {num_tests} comprehensive tests...")
        
        results = []
        for i in range(num_tests):
            self.log(f"📋 Test {i+1}/{num_tests}")
            result = self.test_complete_workflow()
            results.append(result)
            
            if i < num_tests - 1:
                self.log("⏳ Waiting 30 seconds before next test...")
                time.sleep(30)
        
        # Analyze results
        successful_tests = sum(1 for r in results if r["success"])
        success_rate = (successful_tests / num_tests) * 100
        
        summary = {
            "total_tests": num_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "results": results
        }
        
        self.log(f"📊 Test Summary: {successful_tests}/{num_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 System stability test PASSED!")
        else:
            self.log("⚠️ System stability test needs attention", "WARNING")
        
        return summary

def main():
    """Main test execution"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE MISSION WORKFLOW TEST")
    print("=" * 60)
    
    tester = ComprehensiveMissionTester()
    
    # Run single comprehensive test
    result = tester.test_complete_workflow()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
    
    if result["success"]:
        print("\n🎉 All tests passed! System is working correctly.")
    else:
        print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")
    
    # Optionally run multiple tests for stability verification
    # Uncomment the following lines to run multiple tests:
    # print("\n" + "=" * 60)
    # print("🧪 STABILITY TEST (Multiple Runs)")
    # print("=" * 60)
    # stability_result = tester.run_multiple_tests(num_tests=3)
    # print(json.dumps(stability_result, indent=2, default=str))

if __name__ == "__main__":
    main() 