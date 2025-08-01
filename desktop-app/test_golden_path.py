#!/usr/bin/env python3
"""
Golden Path Upgrade Testing Script
Comprehensive testing for the new dual-execution architecture
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class GoldenPathTester:
    """Comprehensive testing suite for Golden Path upgrade"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        
    async def test_golden_path_status(self) -> Dict[str, Any]:
        """Test Golden Path status endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/test/golden-path") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Golden Path Status: {data}")
                        return {"status": "success", "data": data}
                    else:
                        print(f"❌ Golden Path Status failed: {response.status}")
                        return {"status": "error", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Golden Path Status error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_mission_execution(self, prompt: str, title: str = "Test Mission") -> Dict[str, Any]:
        """Test mission execution via Golden Path"""
        try:
            payload = {
                "prompt": prompt,
                "title": title,
                "agent_type": "developer"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/test/mission",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Mission Execution: {data}")
                        return {"status": "success", "data": data}
                    else:
                        print(f"❌ Mission Execution failed: {response.status}")
                        return {"status": "error", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Mission Execution error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_mission_creation(self, prompt: str, title: str = "Test Mission") -> Dict[str, Any]:
        """Test full mission creation and execution"""
        try:
            payload = {
                "prompt": prompt,
                "title": title,
                "agent_type": "developer"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/missions",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Mission Creation: {data}")
                        
                        # Wait for execution to complete
                        mission_id = data.get("mission_id")
                        if mission_id:
                            await self.wait_for_mission_completion(mission_id)
                        
                        return {"status": "success", "data": data}
                    else:
                        print(f"❌ Mission Creation failed: {response.status}")
                        return {"status": "error", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Mission Creation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def wait_for_mission_completion(self, mission_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Wait for mission completion and check status"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    # Check mission status
                    async with session.get(f"{self.base_url}/missions") as response:
                        if response.status == 200:
                            missions = await response.json()
                            mission = next((m for m in missions if m.get("mission_id_str") == mission_id), None)
                            
                            if mission:
                                status = mission.get("status")
                                print(f"🔄 Mission {mission_id} status: {status}")
                                
                                if status in ["completed", "failed"]:
                                    print(f"✅ Mission {mission_id} completed with status: {status}")
                                    return {"status": "success", "mission_status": status}
                            
                            await asyncio.sleep(1)
                        else:
                            print(f"❌ Failed to check mission status: {response.status}")
                            break
            except Exception as e:
                print(f"❌ Error checking mission status: {e}")
                break
        
        print(f"⏰ Mission {mission_id} timed out after {timeout} seconds")
        return {"status": "timeout", "mission_id": mission_id}
    
    async def test_system_health(self) -> Dict[str, Any]:
        """Test overall system health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ System Health: {data}")
                        return {"status": "success", "data": data}
                    else:
                        print(f"❌ System Health failed: {response.status}")
                        return {"status": "error", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ System Health error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_live_logs(self) -> Dict[str, Any]:
        """Test live log streaming"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/logs/live") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Live Logs: {len(data.get('logs', []))} logs available")
                        return {"status": "success", "data": data}
                    else:
                        print(f"❌ Live Logs failed: {response.status}")
                        return {"status": "error", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Live Logs error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive Golden Path testing"""
        print("🚀 Starting Golden Path Comprehensive Testing")
        print("=" * 60)
        
        test_suite = [
            ("System Health", self.test_system_health),
            ("Golden Path Status", self.test_golden_path_status),
            ("Live Logs", self.test_live_logs),
            ("Simple Mission Test", lambda: self.test_mission_execution("Write a hello world function")),
            ("Complex Mission Test", lambda: self.test_mission_execution("Create a Python class for data processing")),
            ("Mission Creation Test", lambda: self.test_mission_creation("Write a function to calculate fibonacci numbers")),
        ]
        
        results = {}
        start_time = time.time()
        
        for test_name, test_func in test_suite:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                results[test_name] = result
                
                if result["status"] == "success":
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = {"status": "error", "error": str(e)}
        
        # Summary
        total_time = time.time() - start_time
        passed = sum(1 for r in results.values() if r.get("status") == "success")
        total = len(results)
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Total Time: {total_time:.2f} seconds")
        print("=" * 60)
        
        return {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": (passed/total)*100,
                "total_time": total_time
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main testing function"""
    print("🎯 Golden Path Upgrade Testing Suite")
    print("Testing the new dual-execution architecture")
    print()
    
    tester = GoldenPathTester()
    
    try:
        results = await tester.run_comprehensive_test()
        
        # Save results to file
        with open("golden_path_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to: golden_path_test_results.json")
        
        # Final recommendation
        if results["summary"]["success_rate"] >= 80:
            print("🎉 Golden Path upgrade is working well!")
        elif results["summary"]["success_rate"] >= 60:
            print("⚠️  Golden Path upgrade has some issues to address")
        else:
            print("❌ Golden Path upgrade needs significant attention")
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 