#!/usr/bin/env python3
"""
Live Agent Monitor
Real-time monitoring of AI agent thinking processes and decision-making
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.advanced_agents import PlannerAgents, WorkerAgents
from src.tools.crewai_tools import (
    write_file_tool, read_file_tool, list_files_tool,
    execute_shell_command_tool, analyze_python_file_tool
)
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process

# Load environment variables
load_dotenv()

class LiveAgentMonitor:
    """Real-time monitoring of AI agent thinking processes"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-1.5-pro-latest"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
        self.planner_agents = PlannerAgents()
        self.worker_agents = WorkerAgents()
        self.monitoring_data = []
        
    def create_monitored_agent(self, agent_type: str) -> Agent:
        """Create an agent with monitoring capabilities"""
        if agent_type == "senior_developer":
            return self.worker_agents.senior_developer(self.llm)
        elif agent_type == "qa_tester":
            return self.worker_agents.qa_tester(self.llm)
        elif agent_type == "code_analyzer":
            return self.worker_agents.code_analyzer(self.llm)
        elif agent_type == "system_integrator":
            return self.worker_agents.system_integrator(self.llm)
        elif agent_type == "lead_architect":
            return self.planner_agents.lead_architect(self.llm)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def monitor_agent_execution(self, agent_type: str, prompt: str) -> Dict[str, Any]:
        """Monitor an agent's execution in real-time"""
        print(f"\n🧠 LIVE MONITORING: {agent_type.upper()}")
        print("=" * 60)
        
        start_time = time.time()
        agent = self.create_monitored_agent(agent_type)
        
        # Create task with detailed monitoring
        task = Task(
            description=f"""
            {prompt}
            
            IMPORTANT: Please think out loud and explain your reasoning process step by step.
            Show your analysis, decision-making, and any tools you would use.
            """,
            expected_output="Detailed analysis with reasoning process",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        monitoring_data = {
            'agent_type': agent_type,
            'prompt': prompt,
            'start_time': datetime.now().isoformat(),
            'thinking_process': [],
            'decisions': [],
            'tools_considered': [],
            'challenges_faced': [],
            'execution_time': 0,
            'success': False,
            'output': '',
            'quality_score': 0.0
        }
        
        try:
            print(f"🎯 Agent: {agent.role}")
            print(f"🎯 Goal: {agent.goal[:100]}...")
            print(f"🎯 Available Tools: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
            print(f"🎯 Prompt: {prompt}")
            print("\n🚀 Starting execution...")
            print("-" * 40)
            
            # Execute with monitoring
            result = crew.kickoff()
            
            execution_time = time.time() - start_time
            monitoring_data['execution_time'] = execution_time
            monitoring_data['success'] = True
            monitoring_data['output'] = result
            
            # Analyze the thinking process
            thinking_analysis = self.analyze_thinking_process(result)
            monitoring_data.update(thinking_analysis)
            
            print(f"\n✅ Execution completed in {execution_time:.2f}s")
            print(f"📊 Quality Score: {monitoring_data['quality_score']:.2f}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            monitoring_data['execution_time'] = execution_time
            monitoring_data['success'] = False
            monitoring_data['challenges_faced'].append(str(e))
            
            print(f"\n❌ Execution failed after {execution_time:.2f}s")
            print(f"❌ Error: {e}")
        
        self.monitoring_data.append(monitoring_data)
        return monitoring_data

    def analyze_thinking_process(self, output: str) -> Dict[str, Any]:
        """Analyze the agent's thinking process from output"""
        analysis = {
            'thinking_process': [],
            'decisions': [],
            'tools_considered': [],
            'challenges_faced': [],
            'quality_score': 0.0
        }
        
        # Extract thinking process
        lines = output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect thinking indicators
            if any(indicator in line.lower() for indicator in ['i think', 'i believe', 'i consider', 'analyzing', 'thinking']):
                analysis['thinking_process'].append(line)
            elif any(indicator in line.lower() for indicator in ['decision', 'choose', 'select', 'decide']):
                analysis['decisions'].append(line)
            elif any(indicator in line.lower() for indicator in ['tool', 'use', 'execute', 'run']):
                analysis['tools_considered'].append(line)
            elif any(indicator in line.lower() for indicator in ['challenge', 'difficulty', 'problem', 'issue', 'error']):
                analysis['challenges_faced'].append(line)
        
        # Calculate quality score
        quality_factors = [
            len(analysis['thinking_process']) > 0,  # Shows reasoning
            len(analysis['decisions']) > 0,  # Shows decision-making
            len(analysis['tools_considered']) > 0,  # Shows tool usage
            len(output) > 200,  # Substantial output
            any(keyword in output.lower() for keyword in ['step', 'plan', 'approach']),  # Structured thinking
        ]
        
        analysis['quality_score'] = sum(quality_factors) / len(quality_factors)
        
        return analysis

    def run_live_monitoring_session(self):
        """Run a comprehensive live monitoring session"""
        print("🧠 LIVE AGENT MONITORING SESSION")
        print("=" * 60)
        
        test_scenarios = [
            {
                "agent": "senior_developer",
                "prompt": "Create a Python script that implements a simple web server using Flask. Think through the requirements, design decisions, and implementation steps.",
                "focus": "Code generation and architectural thinking"
            },
            {
                "agent": "qa_tester",
                "prompt": "Design a comprehensive testing strategy for a user authentication system. Consider security, edge cases, and validation approaches.",
                "focus": "Testing strategy and quality assurance"
            },
            {
                "agent": "code_analyzer",
                "prompt": "Analyze the performance and security implications of using synchronous vs asynchronous database operations in a web application.",
                "focus": "Code analysis and optimization"
            },
            {
                "agent": "system_integrator",
                "prompt": "Design a deployment strategy for a microservices application that needs to handle high traffic and maintain 99.9% uptime.",
                "focus": "System integration and deployment"
            },
            {
                "agent": "lead_architect",
                "prompt": "Create a comprehensive plan for migrating a monolithic application to a cloud-native microservices architecture. Consider all aspects including data migration, service decomposition, and risk mitigation.",
                "focus": "Strategic planning and architecture"
            }
        ]
        
        session_results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 Scenario {i}/{len(test_scenarios)}: {scenario['focus']}")
            print(f"🎯 Agent: {scenario['agent']}")
            print(f"🎯 Focus: {scenario['focus']}")
            
            result = self.monitor_agent_execution(scenario['agent'], scenario['prompt'])
            session_results.append(result)
            
            # Brief pause between tests
            time.sleep(2)
        
        # Generate session report
        self.generate_monitoring_report(session_results)

    def generate_monitoring_report(self, session_results: List[Dict[str, Any]]):
        """Generate a comprehensive monitoring report"""
        print("\n📊 LIVE MONITORING REPORT")
        print("=" * 60)
        
        total_agents = len(session_results)
        successful_executions = sum(1 for r in session_results if r['success'])
        avg_execution_time = sum(r['execution_time'] for r in session_results) / total_agents
        avg_quality_score = sum(r['quality_score'] for r in session_results) / total_agents
        
        print(f"📈 Overall Performance:")
        print(f"   - Total Agents Monitored: {total_agents}")
        print(f"   - Successful Executions: {successful_executions}/{total_agents}")
        print(f"   - Average Execution Time: {avg_execution_time:.2f}s")
        print(f"   - Average Quality Score: {avg_quality_score:.2f}")
        print()
        
        # Individual agent analysis
        for result in session_results:
            print(f"🧠 {result['agent_type'].upper()} ANALYSIS:")
            print(f"   - Success: {'✅' if result['success'] else '❌'}")
            print(f"   - Execution Time: {result['execution_time']:.2f}s")
            print(f"   - Quality Score: {result['quality_score']:.2f}")
            print(f"   - Thinking Steps: {len(result['thinking_process'])}")
            print(f"   - Decisions Made: {len(result['decisions'])}")
            print(f"   - Tools Considered: {len(result['tools_considered'])}")
            print(f"   - Challenges Faced: {len(result['challenges_faced'])}")
            
            if result['thinking_process']:
                print(f"   - Key Thinking: {result['thinking_process'][0][:100]}...")
            
            if result['challenges_faced']:
                print(f"   - Main Challenge: {result['challenges_faced'][0]}")
            
            print()
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"live_monitoring_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'summary': {
                    'total_agents': total_agents,
                    'successful_executions': successful_executions,
                    'avg_execution_time': avg_execution_time,
                    'avg_quality_score': avg_quality_score
                },
                'detailed_results': session_results
            }, f, indent=2, default=str)
        
        print(f"✅ Detailed report saved to: {report_file}")

def main():
    """Main monitoring process"""
    print("🧠 Live Agent Monitor")
    print("=" * 40)
    
    monitor = LiveAgentMonitor()
    
    try:
        # Run live monitoring session
        monitor.run_live_monitoring_session()
        
        print("\n🎉 Live monitoring session completed!")
        print("Check the generated report for detailed analysis.")
        
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 