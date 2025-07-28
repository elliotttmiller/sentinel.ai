#!/usr/bin/env python3
"""
Sentinel AI Agent Deployment Test Suite
Comprehensive testing of the AI agent deployment and execution pipeline.
"""
import requests
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import os

# Configuration
BACKEND_URL = "https://aad14070078d.ngrok-free.app"
ENGINE_URL = "https://6d0cabb05ae8.ngrok-free.app"
LOCAL_BACKEND_URL = "http://localhost:8080"
LOCAL_ENGINE_URL = "http://localhost:8001"

class AgentDeploymentTester:
    def __init__(self):
        self.test_results = {}
        self.current_test = None
        
    def print_header(self, title: str):
        print("\n" + "="*60)
        print(f" {title.upper()} ".center(60, "="))
        print("="*60)
        
    def print_success(self, message: str):
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        print(f"❌ {message}")
        
    def print_info(self, message: str):
        print(f"💡 {message}")
        
    def print_warning(self, message: str):
        print(f"⚠️  {message}")
        
    def test_service_health(self) -> bool:
        """Test if all services are healthy and responding."""
        self.print_header("Service Health Check")
        
        services = {
            "Backend (Local)": LOCAL_BACKEND_URL,
            "Engine (Local)": LOCAL_ENGINE_URL,
            "Backend (Tunnel)": BACKEND_URL,
            "Engine (Tunnel)": ENGINE_URL
        }
        
        all_healthy = True
        for name, url in services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    self.print_success(f"{name}: {response.json()}")
                else:
                    self.print_error(f"{name}: HTTP {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.print_error(f"{name}: {str(e)}")
                all_healthy = False
                
        return all_healthy
    
    def test_agent_registry(self) -> bool:
        """Test agent registration and availability."""
        self.print_header("Agent Registry Test")
        
        try:
            # Test getting available agents
            response = requests.get(f"{BACKEND_URL}/agents", timeout=10)
            if response.status_code == 200:
                agents = response.json()
                self.print_success(f"Found {len(agents)} registered agents")
                
                # Check for specific agent types
                agent_types = [agent.get('type') for agent in agents]
                expected_types = ['code_reviewer', 'debugger', 'planner', 'simple_test']
                
                for expected_type in expected_types:
                    if expected_type in agent_types:
                        self.print_success(f"Agent type '{expected_type}' found")
                    else:
                        self.print_warning(f"Agent type '{expected_type}' not found")
                        
                return True
            else:
                self.print_error(f"Failed to get agents: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Agent registry test failed: {str(e)}")
            return False
    
    def test_mission_creation(self) -> bool:
        """Test mission creation and planning."""
        self.print_header("Mission Creation Test")
        
        test_mission = {
            "title": "Test Mission - Agent Deployment Verification",
            "description": "A comprehensive test to verify AI agent deployment and execution capabilities",
            "priority": "high",
            "complexity": "medium",
            "requirements": [
                "Create a simple Python script",
                "Test basic functionality",
                "Generate a status report"
            ]
        }
        
        try:
            # Create mission
            response = requests.post(f"{BACKEND_URL}/missions", json=test_mission, timeout=10)
            if response.status_code == 200:
                mission_data = response.json()
                mission_id = mission_data.get('id')
                self.print_success(f"Mission created with ID: {mission_id}")
                
                # Test mission planning
                plan_response = requests.post(f"{BACKEND_URL}/missions/{mission_id}/plan", timeout=15)
                if plan_response.status_code == 200:
                    plan_data = plan_response.json()
                    self.print_success("Mission planning completed")
                    self.print_info(f"Plan steps: {len(plan_data.get('steps', []))}")
                    return True
                else:
                    self.print_error(f"Mission planning failed: HTTP {plan_response.status_code}")
                    return False
            else:
                self.print_error(f"Mission creation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Mission creation test failed: {str(e)}")
            return False
    
    def test_agent_execution(self) -> bool:
        """Test actual agent execution on the engine."""
        self.print_header("Agent Execution Test")
        
        test_execution_plan = {
            "mission_id": "test-execution-001",
            "steps": [
                {
                    "step_id": "step-1",
                    "agent_type": "simple_test",
                    "action": "generate_response",
                    "parameters": {
                        "message": "Hello from Sentinel AI Agent Test",
                        "task": "Verify agent is working correctly"
                    }
                }
            ],
            "metadata": {
                "test_mode": True,
                "timeout": 30
            }
        }
        
        try:
            # Send execution plan to engine
            response = requests.post(f"{ENGINE_URL}/execute_mission", json=test_execution_plan, timeout=10)
            if response.status_code == 200:
                self.print_success("Execution plan sent to engine")
                
                # Wait for execution to complete
                mission_id = test_execution_plan["mission_id"]
                max_wait = 30
                wait_time = 0
                
                while wait_time < max_wait:
                    time.sleep(2)
                    wait_time += 2
                    
                    result_response = requests.get(f"{ENGINE_URL}/mission_result/{mission_id}", timeout=5)
                    if result_response.status_code == 200:
                        result = result_response.json()
                        if result.get('status') == 'completed':
                            self.print_success("Agent execution completed successfully")
                            self.print_info(f"Output: {result.get('output', 'No output')}")
                            return True
                        elif result.get('status') == 'failed':
                            self.print_error(f"Agent execution failed: {result.get('error', 'Unknown error')}")
                            return False
                    
                    self.print_info(f"Waiting for execution... ({wait_time}s/{max_wait}s)")
                
                self.print_warning("Execution timeout - agent may still be processing")
                return False
            else:
                self.print_error(f"Failed to send execution plan: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Agent execution test failed: {str(e)}")
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow from mission creation to execution."""
        self.print_header("End-to-End Workflow Test")
        
        try:
            # 1. Create a mission
            mission_data = {
                "title": "E2E Test - Complete Workflow",
                "description": "Testing the complete workflow from mission creation to agent execution",
                "priority": "high",
                "complexity": "low",
                "requirements": [
                    "Generate a test response",
                    "Log the activity",
                    "Return success status"
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/missions", json=mission_data, timeout=10)
            if response.status_code != 200:
                self.print_error("Failed to create mission for E2E test")
                return False
                
            mission = response.json()
            mission_id = mission['id']
            self.print_success(f"Mission created: {mission_id}")
            
            # 2. Plan the mission
            plan_response = requests.post(f"{BACKEND_URL}/missions/{mission_id}/plan", timeout=15)
            if plan_response.status_code != 200:
                self.print_error("Failed to plan mission")
                return False
                
            plan = plan_response.json()
            self.print_success("Mission planned successfully")
            
            # 3. Execute the mission
            exec_response = requests.post(f"{ENGINE_URL}/execute_mission", json=plan, timeout=10)
            if exec_response.status_code != 200:
                self.print_error("Failed to start mission execution")
                return False
                
            self.print_success("Mission execution started")
            
            # 4. Wait for completion
            max_wait = 45
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(3)
                wait_time += 3
                
                result_response = requests.get(f"{ENGINE_URL}/mission_result/{mission_id}", timeout=5)
                if result_response.status_code == 200:
                    result = result_response.json()
                    if result.get('status') == 'completed':
                        self.print_success("🎉 End-to-end workflow completed successfully!")
                        return True
                    elif result.get('status') == 'failed':
                        self.print_error(f"Workflow failed: {result.get('error', 'Unknown error')}")
                        return False
                
                self.print_info(f"Waiting for completion... ({wait_time}s/{max_wait}s)")
            
            self.print_warning("E2E test timeout")
            return False
            
        except Exception as e:
            self.print_error(f"E2E workflow test failed: {str(e)}")
            return False
    
    def test_performance_metrics(self) -> Dict:
        """Test performance metrics and response times."""
        self.print_header("Performance Metrics Test")
        
        metrics = {}
        
        # Test response times
        endpoints = [
            ("/health", "Health Check"),
            ("/agents", "Agent Registry"),
            ("/missions", "Mission List")
        ]
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                metrics[name] = {
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    self.print_success(f"{name}: {response_time:.2f}ms")
                else:
                    self.print_error(f"{name}: HTTP {response.status_code} ({response_time:.2f}ms)")
                    
            except Exception as e:
                self.print_error(f"{name}: Failed - {str(e)}")
                metrics[name] = {"error": str(e)}
        
        return metrics
    
    def generate_report(self, results: Dict):
        """Generate a comprehensive test report."""
        self.print_header("Test Report")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        if passed_tests == total_tests:
            self.print_success("🎉 All tests passed! Your AI agent deployment is working correctly.")
        else:
            self.print_warning("⚠️  Some tests failed. Please check the configuration and try again.")
    
    def run_all_tests(self):
        """Run all tests and generate a comprehensive report."""
        self.print_header("Sentinel AI Agent Deployment Test Suite")
        
        print("🚀 Starting comprehensive AI agent deployment tests...")
        print(f"📡 Backend URL: {BACKEND_URL}")
        print(f"⚙️  Engine URL: {ENGINE_URL}")
        
        # Run all tests
        test_results = {
            "Service Health": self.test_service_health(),
            "Agent Registry": self.test_agent_registry(),
            "Mission Creation": self.test_mission_creation(),
            "Agent Execution": self.test_agent_execution(),
            "End-to-End Workflow": self.test_end_to_end_workflow()
        }
        
        # Performance metrics
        performance = self.test_performance_metrics()
        
        # Generate report
        self.generate_report(test_results)
        
        # Performance summary
        if performance:
            self.print_header("Performance Summary")
            for name, metrics in performance.items():
                if "response_time_ms" in metrics:
                    print(f"   {name}: {metrics['response_time_ms']}ms")
        
        return test_results

def main():
    """Main test runner."""
    tester = AgentDeploymentTester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if all(results.values()):
            print("\n🎯 All tests passed! Your AI agent deployment is optimized and ready.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Please review the configuration.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 