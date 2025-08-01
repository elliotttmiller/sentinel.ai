#!/usr/bin/env python3
"""
First Real Agent Deployment Test
Tests the complete agent deployment workflow from mission creation to execution.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8002"
ENGINE_URL = "http://localhost:8001"

class AgentDeploymentTester:
    def __init__(self):
        self.test_results = {}
        
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
            "Backend": f"{BACKEND_URL}/health",
            "Engine": f"{ENGINE_URL}/health"
        }
        
        all_healthy = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"{name}: {data.get('status', 'unknown')}")
                else:
                    self.print_error(f"{name}: HTTP {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.print_error(f"{name}: {str(e)}")
                all_healthy = False
                
        return all_healthy
    
    def test_mission_creation(self) -> Dict[str, Any]:
        """Test creating a simple mission."""
        self.print_header("Mission Creation Test")
        
        # Simple test mission
        test_mission = {
            "prompt": "Create a simple Python script that prints 'Hello from Sentinel AI Agent!' and saves it to a file called hello_sentinel.py",
            "title": "First Agent Test Mission",
            "agent_type": "developer"
        }
        
        try:
            self.print_info(f"Creating mission: {test_mission['title']}")
            response = requests.post(
                f"{BACKEND_URL}/api/missions",
                json=test_mission,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Mission created successfully!")
                self.print_info(f"Mission ID: {result.get('mission_id', 'N/A')}")
                self.print_info(f"Status: {result.get('message', 'N/A')}")
                return result
            else:
                self.print_error(f"Failed to create mission: HTTP {response.status_code}")
                self.print_error(f"Response: {response.text}")
                return {}
                
        except Exception as e:
            self.print_error(f"Mission creation failed: {str(e)}")
            return {}
    
    def test_mission_execution(self, mission_id: str) -> bool:
        """Test mission execution and monitor progress."""
        self.print_header("Mission Execution Test")
        
        try:
            # Check mission status by getting all missions and finding the specific one
            self.print_info(f"Checking mission status: {mission_id}")
            response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
            
            if response.status_code == 200:
                missions = response.json()
                # Find our specific mission
                target_mission = None
                for mission in missions:
                    if mission.get('mission_id_str') == mission_id:
                        target_mission = mission
                        break
                
                if target_mission:
                    self.print_info(f"Mission Status: {target_mission.get('status', 'unknown')}")
                    self.print_info(f"Created: {target_mission.get('created_at', 'N/A')}")
                    
                    # Monitor execution for up to 2 minutes
                    max_wait = 120
                    start_time = time.time()
                    
                    while time.time() - start_time < max_wait:
                        response = requests.get(f"{BACKEND_URL}/missions", timeout=10)
                        if response.status_code == 200:
                            missions = response.json()
                            # Find our specific mission again
                            target_mission = None
                            for mission in missions:
                                if mission.get('mission_id_str') == mission_id:
                                    target_mission = mission
                                    break
                            
                            if target_mission:
                                status = target_mission.get('status', 'unknown')
                                self.print_info(f"Status: {status}")
                                
                                if status in ['completed', 'failed']:
                                    if status == 'completed':
                                        self.print_success("Mission completed successfully!")
                                        if target_mission.get('result'):
                                            self.print_info("Result available")
                                        return True
                                    else:
                                        self.print_error("Mission failed")
                                        return False
                        
                        time.sleep(5)
                    
                    self.print_warning("Mission execution timeout")
                    return False
                else:
                    self.print_error(f"Mission {mission_id} not found in mission list")
                    return False
            else:
                self.print_error(f"Failed to get missions: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Mission execution test failed: {str(e)}")
            return False
    
    def test_agent_registry(self) -> bool:
        """Test agent registry and availability."""
        self.print_header("Agent Registry Test")
        
        try:
            # Test getting available agents
            response = requests.get(f"{BACKEND_URL}/agents", timeout=10)
            if response.status_code == 200:
                agents = response.json()
                self.print_success(f"Found {len(agents)} registered agents")
                
                # Display agent information
                for agent in agents:
                    agent_type = agent.get('type', 'unknown')
                    agent_name = agent.get('name', 'unknown')
                    self.print_info(f"Agent: {agent_name} ({agent_type})")
                        
                return True
            else:
                self.print_error(f"Failed to get agents: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Agent registry test failed: {str(e)}")
            return False
    
    def test_live_events(self) -> bool:
        """Test live event monitoring."""
        self.print_header("Live Events Test")
        
        try:
            response = requests.get(f"{BACKEND_URL}/api/events/live", timeout=10)
            if response.status_code == 200:
                events = response.json()
                self.print_success(f"Found {len(events)} live events")
                
                # Show recent events
                for event in events[:5]:  # Show last 5 events
                    timestamp = event.get('timestamp', 'N/A')
                    level = event.get('level', 'INFO')
                    message = event.get('message', 'No message')
                    self.print_info(f"[{timestamp}] {level}: {message}")
                    
                return True
            else:
                self.print_warning(f"Live events endpoint returned HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Live events test failed: {str(e)}")
            return False
    
    def test_observability(self) -> bool:
        """Test observability endpoints."""
        self.print_header("Observability Test")
        
        try:
            response = requests.get(f"{BACKEND_URL}/api/observability/overview", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_success("Observability data retrieved")
                
                # Display observability metrics
                for service, metrics in data.items():
                    status = metrics.get('status', 'unknown')
                    self.print_info(f"{service.upper()}: {status}")
                    
                return True
            else:
                self.print_warning(f"Observability endpoint returned HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Observability test failed: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete agent deployment test suite."""
        self.print_header("FIRST REAL AGENT DEPLOYMENT TEST")
        self.print_info(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Service Health
        if not self.test_service_health():
            self.print_error("Service health check failed. Cannot proceed.")
            return False
        
        # Test 2: Agent Registry
        if not self.test_agent_registry():
            self.print_warning("Agent registry test failed, but continuing...")
        
        # Test 3: Observability
        if not self.test_observability():
            self.print_warning("Observability test failed, but continuing...")
        
        # Test 4: Live Events
        if not self.test_live_events():
            self.print_warning("Live events test failed, but continuing...")
        
        # Test 5: Mission Creation
        mission_result = self.test_mission_creation()
        if not mission_result:
            self.print_error("Mission creation failed. Cannot proceed.")
            return False
        
        mission_id = mission_result.get('mission_id')
        if not mission_id:
            self.print_error("No mission ID returned. Cannot proceed.")
            return False
        
        # Test 6: Mission Execution
        if not self.test_mission_execution(mission_id):
            self.print_error("Mission execution failed.")
            return False
        
        # Final Results
        self.print_header("TEST RESULTS")
        self.print_success("🎉 FIRST REAL AGENT DEPLOYMENT SUCCESSFUL!")
        self.print_info(f"Mission ID: {mission_id}")
        self.print_info("Your AI agents are working! Check the mission details in the dashboard.")
        
        return True

def main():
    """Main test execution."""
    tester = AgentDeploymentTester()
    
    try:
        success = tester.run_comprehensive_test()
        if success:
            print("\n" + "="*60)
            print(" 🚀 AGENT DEPLOYMENT TEST COMPLETED SUCCESSFULLY! ".center(60, "="))
            print("="*60)
            print("\nNext steps:")
            print("1. Check the dashboard for mission details")
            print("2. Review the generated files (hello_sentinel.py)")
            print("3. Monitor live events for agent activity")
            print("4. Try more complex missions!")
        else:
            print("\n" + "="*60)
            print(" ❌ AGENT DEPLOYMENT TEST FAILED ".center(60, "="))
            print("="*60)
            print("\nPlease check:")
            print("1. All services are running")
            print("2. Network connectivity")
            print("3. API endpoints are accessible")
            print("4. Agent configurations are correct")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main() 