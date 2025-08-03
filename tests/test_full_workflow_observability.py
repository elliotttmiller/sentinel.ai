#!/usr/bin/env python3
"""
Comprehensive Full Workflow Test with Enhanced Observability
Tests the complete AI agent workflow with detailed tracking and monitoring.
"""

import asyncio
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# Test scenarios with increasing complexity
TEST_SCENARIOS = [
    {
        "name": "Simple Tax Calculation",
        "prompt": "Calculate the tax for a $50,000 annual income with standard deductions for 2024",
        "expected_path": "golden_path",
        "complexity": "low"
    },
    {
        "name": "Complex Tax Planning",
        "prompt": "Create a comprehensive tax planning strategy for a small business owner with $200,000 annual income, including deductions, credits, and retirement planning for 2024",
        "expected_path": "full_workflow",
        "complexity": "medium"
    },
    {
        "name": "Advanced Financial Architecture",
        "prompt": "Design a complete financial management system for a multi-million dollar corporation, including tax optimization, investment strategies, risk management, compliance frameworks, and automated reporting systems",
        "expected_path": "full_workflow",
        "complexity": "high"
    }
]

class FullWorkflowTester:
    """Comprehensive tester for full workflow with observability."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
    
    async def test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single scenario with comprehensive observability."""
        print(f"\n{'='*80}")
        print(f"🧪 TESTING: {scenario['name']}")
        print(f"📝 Prompt: {scenario['prompt']}")
        print(f"🎯 Expected Path: {scenario['expected_path']}")
        print(f"📊 Complexity: {scenario['complexity']}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # Step 1: Create mission
            print(f"\n📋 Step 1: Creating mission...")
            mission_response = requests.post(
                f"{self.base_url}/api/missions",
                json={
                    "prompt": scenario["prompt"],
                    "title": scenario["name"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if mission_response.status_code != 200:
                raise Exception(f"Failed to create mission: {mission_response.text}")
            
            mission_data = mission_response.json()
            mission_id = mission_data["mission_id"]
            
            print(f"✅ Mission created: {mission_id}")
            
            # Step 2: Monitor mission execution
            print(f"\n🚀 Step 2: Monitoring mission execution...")
            execution_start = time.time()
            
            # Poll for mission updates
            max_wait_time = 300  # 5 minutes
            poll_interval = 2  # 2 seconds
            
            while time.time() - execution_start < max_wait_time:
                # Check mission status
                status_response = requests.get(f"{self.base_url}/api/missions/{mission_id}")
                if status_response.status_code == 200:
                    mission_status = status_response.json()
                    
                    if mission_status["status"] in ["completed", "failed"]:
                        execution_time = time.time() - execution_start
                        print(f"✅ Mission completed in {execution_time:.2f}s")
                        print(f"📊 Status: {mission_status['status']}")
                        
                        # Get detailed observability data
                        observability_data = await self.get_mission_observability(mission_id)
                        
                        result = {
                            "scenario": scenario,
                            "mission_id": mission_id,
                            "status": mission_status["status"],
                            "execution_time": execution_time,
                            "result": mission_status.get("result", ""),
                            "observability_data": observability_data,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        self.test_results.append(result)
                        return result
                
                print(f"⏳ Waiting for completion... ({time.time() - execution_start:.1f}s)")
                await asyncio.sleep(poll_interval)
            
            raise Exception("Mission execution timed out")
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Test failed: {e}")
            
            result = {
                "scenario": scenario,
                "mission_id": mission_id if 'mission_id' in locals() else None,
                "status": "failed",
                "execution_time": execution_time,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(result)
            return result
    
    async def get_mission_observability(self, mission_id: str) -> Dict[str, Any]:
        """Get detailed observability data for a mission."""
        try:
            # Get mission observability
            mission_response = requests.get(f"{self.base_url}/api/observability/mission/{mission_id}")
            if mission_response.status_code == 200:
                mission_data = mission_response.json()
                
                # Get agent analytics
                analytics_response = requests.get(f"{self.base_url}/api/observability/agent-analytics")
                analytics_data = analytics_response.json() if analytics_response.status_code == 200 else {}
                
                # Get hybrid analytics
                hybrid_response = requests.get(f"{self.base_url}/api/hybrid/analytics")
                hybrid_data = hybrid_response.json() if hybrid_response.status_code == 200 else {}
                
                return {
                    "mission_data": mission_data.get("mission_data", {}),
                    "agent_analytics": analytics_data.get("analytics", {}),
                    "hybrid_analytics": hybrid_data.get("analytics", {})
                }
            
        except Exception as e:
            print(f"⚠️ Failed to get observability data: {e}")
        
        return {}
    
    def print_observability_summary(self, observability_data: Dict[str, Any]):
        """Print a comprehensive observability summary."""
        print(f"\n{'='*80}")
        print(f"📊 OBSERVABILITY SUMMARY")
        print(f"{'='*80}")
        
        mission_data = observability_data.get("mission_data", {})
        agent_analytics = observability_data.get("agent_analytics", {})
        hybrid_analytics = observability_data.get("hybrid_analytics", {})
        
        # Mission Overview
        if mission_data:
            print(f"\n🎯 MISSION OVERVIEW:")
            print(f"   • Mission ID: {mission_data.get('mission_id', 'N/A')}")
            print(f"   • Status: {mission_data.get('success', False)}")
            print(f"   • Duration: {mission_data.get('total_duration', 0):.2f}s")
            print(f"   • Total Cost: ${mission_data.get('total_cost', 0):.4f}")
            print(f"   • Total Tokens: {mission_data.get('total_tokens', 0):,}")
            
            # Agent Sessions
            agent_sessions = mission_data.get("agent_sessions", {})
            if agent_sessions:
                print(f"\n🤖 AGENT SESSIONS ({len(agent_sessions)}):")
                for session_id, session in agent_sessions.items():
                    print(f"   • {session.get('agent_name', 'Unknown')}:")
                    print(f"     - Duration: {session.get('total_duration', 0):.2f}s")
                    print(f"     - Success: {session.get('success', False)}")
                    print(f"     - Actions: {len(session.get('actions', []))}")
                    print(f"     - Tool Calls: {session.get('tool_call_count', 0)}")
                    print(f"     - Decisions: {session.get('decision_count', 0)}")
                    print(f"     - Avg Confidence: {session.get('avg_confidence', 0):.2f}")
        
        # Agent Performance
        if agent_analytics:
            print(f"\n📈 AGENT PERFORMANCE:")
            agent_performance = agent_analytics.get("agent_performance", {})
            for agent_name, performance in agent_performance.items():
                print(f"   • {agent_name}:")
                print(f"     - Sessions: {performance.get('total_sessions', 0)}")
                print(f"     - Success Rate: {performance.get('success_rate', 0):.2%}")
                print(f"     - Avg Duration: {performance.get('avg_session_duration', 0):.2f}s")
                print(f"     - Total Cost: ${performance.get('total_cost', 0):.4f}")
        
        # Hybrid Analytics
        if hybrid_analytics:
            print(f"\n🎯 HYBRID DECISION ANALYTICS:")
            system_performance = hybrid_analytics.get("system_performance", {})
            decision_metrics = hybrid_analytics.get("decision_metrics", {})
            
            print(f"   • Golden Path Success Rate: {system_performance.get('golden_path_success_rate', 0):.2%}")
            print(f"   • Full Workflow Success Rate: {system_performance.get('full_workflow_success_rate', 0):.2%}")
            print(f"   • Avg Golden Path Time: {system_performance.get('average_golden_path_time', 0):.2f}s")
            print(f"   • Avg Full Workflow Time: {system_performance.get('average_full_workflow_time', 0):.2f}s")
            print(f"   • Complexity Threshold: {decision_metrics.get('complexity_threshold', 0)}")
            print(f"   • Routing Accuracy: {decision_metrics.get('routing_accuracy', 0):.2%}")
    
    def print_detailed_agent_actions(self, observability_data: Dict[str, Any]):
        """Print detailed agent actions and decisions."""
        mission_data = observability_data.get("mission_data", {})
        agent_sessions = mission_data.get("agent_sessions", {})
        
        if not agent_sessions:
            return
        
        print(f"\n{'='*80}")
        print(f"🔍 DETAILED AGENT ACTIONS")
        print(f"{'='*80}")
        
        for session_id, session in agent_sessions.items():
            print(f"\n🤖 AGENT: {session.get('agent_name', 'Unknown')}")
            print(f"   Session ID: {session_id}")
            print(f"   Duration: {session.get('total_duration', 0):.2f}s")
            print(f"   Success: {session.get('success', False)}")
            print(f"   Actions: {len(session.get('actions', []))}")
            
            actions = session.get("actions", [])
            for i, action in enumerate(actions, 1):
                print(f"\n   📝 Action {i}: {action.get('action_type', 'unknown').upper()}")
                print(f"      • Timestamp: {action.get('timestamp', 'N/A')}")
                print(f"      • Duration: {action.get('duration', 0):.2f}s")
                print(f"      • Success: {action.get('success', False)}")
                print(f"      • Confidence: {action.get('confidence_score', 0):.2f}")
                print(f"      • Memory Usage: {action.get('memory_usage', 0):.1f}%")
                print(f"      • CPU Usage: {action.get('cpu_usage', 0):.1f}%")
                
                if action.get('reasoning'):
                    print(f"      • Reasoning: {action.get('reasoning', '')[:100]}...")
                
                if action.get('input_data'):
                    input_summary = str(action.get('input_data', {}))[:100]
                    print(f"      • Input: {input_summary}...")
                
                if action.get('output_data'):
                    output_summary = str(action.get('output_data', {}))[:100]
                    print(f"      • Output: {output_summary}...")
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite with all scenarios."""
        print(f"\n🚀 STARTING COMPREHENSIVE FULL WORKFLOW TEST")
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Testing {len(TEST_SCENARIOS)} scenarios with enhanced observability")
        
        start_time = time.time()
        
        # Test each scenario
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"\n{'='*80}")
            print(f"🧪 SCENARIO {i}/{len(TEST_SCENARIOS)}")
            print(f"{'='*80}")
            
            result = await self.test_scenario(scenario)
            
            # Print observability summary
            if result.get("observability_data"):
                self.print_observability_summary(result["observability_data"])
                
                # Print detailed agent actions for complex scenarios
                if scenario["complexity"] in ["medium", "high"]:
                    self.print_detailed_agent_actions(result["observability_data"])
        
        # Print final summary
        total_time = time.time() - start_time
        successful_tests = sum(1 for r in self.test_results if r["status"] == "completed")
        
        print(f"\n{'='*80}")
        print(f"📊 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"   • Total Tests: {len(self.test_results)}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Failed: {len(self.test_results) - successful_tests}")
        print(f"   • Success Rate: {successful_tests/len(self.test_results)*100:.1f}%")
        print(f"   • Total Time: {total_time:.2f}s")
        print(f"   • Average Time per Test: {total_time/len(self.test_results):.2f}s")
        
        # Save results
        with open("full_workflow_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: full_workflow_test_results.json")
        print(f"✅ Comprehensive test completed!")


async def main():
    """Main test execution."""
    tester = FullWorkflowTester()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main()) 