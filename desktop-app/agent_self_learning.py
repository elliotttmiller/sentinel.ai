#!/usr/bin/env python3
"""
Agent Self-Learning System
Continuous improvement of AI agents based on performance data and learning patterns
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import requests
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.advanced_agents import PlannerAgents, WorkerAgents, MemoryAgents
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process

# Load environment variables
load_dotenv()

@dataclass
class LearningPattern:
    """Pattern identified from agent performance"""
    pattern_type: str  # 'success', 'failure', 'optimization'
    agent_type: str
    context: str
    trigger_conditions: List[str]
    recommended_actions: List[str]
    confidence_score: float
    last_observed: datetime
    occurrence_count: int

@dataclass
class AgentImprovement:
    """Improvement suggestion for an agent"""
    agent_type: str
    improvement_type: str  # 'goal', 'backstory', 'tools', 'process'
    current_value: str
    suggested_value: str
    reasoning: str
    expected_impact: str
    priority: int  # 1-5, higher is more important

class AgentSelfLearning:
    """Self-learning system for continuous agent improvement"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-1.5-pro-latest"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
        self.planner_agents = PlannerAgents()
        self.worker_agents = WorkerAgents()
        self.memory_agents = MemoryAgents()
        
        self.learning_patterns = []
        self.improvement_suggestions = []
        self.performance_history = []
        
    def analyze_mission_history(self) -> List[LearningPattern]:
        """Analyze mission history to identify learning patterns"""
        print("🔍 Analyzing Mission History for Learning Patterns...")
        
        try:
            # Get recent missions from the API
            response = requests.get("http://localhost:8001/missions", timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to get missions: {response.status_code}")
                return []
            
            missions = response.json()
            print(f"✅ Found {len(missions)} missions to analyze")
            
            patterns = []
            
            # Analyze each mission for patterns
            for mission in missions:
                mission_id = mission.get('mission_id_str', mission.get('id'))
                
                # Get detailed mission info
                detail_response = requests.get(f"http://localhost:8001/mission/{mission_id}", timeout=10)
                if detail_response.status_code == 200:
                    mission_details = detail_response.json()
                    pattern = self.extract_learning_pattern(mission_details)
                    if pattern:
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            print(f"❌ Error analyzing mission history: {e}")
            return []

    def extract_learning_pattern(self, mission: Dict[str, Any]) -> Optional[LearningPattern]:
        """Extract learning pattern from a single mission"""
        try:
            agent_type = mission.get('agent_type', 'unknown')
            status = mission.get('status', 'unknown')
            result = mission.get('result', '')
            error = mission.get('error_message', '')
            execution_time = mission.get('execution_time', 0)
            
            # Determine pattern type
            if status == 'completed' and result:
                pattern_type = 'success'
                trigger_conditions = [
                    f"Agent type: {agent_type}",
                    f"Status: {status}",
                    f"Execution time: {execution_time}s"
                ]
                recommended_actions = [
                    "Reinforce successful patterns",
                    "Apply similar approaches to other agents",
                    "Document best practices"
                ]
                confidence_score = 0.8
                
            elif status == 'failed' or error:
                pattern_type = 'failure'
                trigger_conditions = [
                    f"Agent type: {agent_type}",
                    f"Status: {status}",
                    f"Error: {error[:100]}"
                ]
                recommended_actions = [
                    "Improve error handling",
                    "Add more validation",
                    "Enhance tool usage"
                ]
                confidence_score = 0.9
                
            else:
                pattern_type = 'optimization'
                trigger_conditions = [
                    f"Agent type: {agent_type}",
                    f"Execution time: {execution_time}s"
                ]
                recommended_actions = [
                    "Optimize performance",
                    "Streamline processes",
                    "Improve efficiency"
                ]
                confidence_score = 0.6
            
            return LearningPattern(
                pattern_type=pattern_type,
                agent_type=agent_type,
                context=f"Mission {mission.get('mission_id_str', mission.get('id'))}",
                trigger_conditions=trigger_conditions,
                recommended_actions=recommended_actions,
                confidence_score=confidence_score,
                last_observed=datetime.now(),
                occurrence_count=1
            )
            
        except Exception as e:
            print(f"❌ Error extracting pattern: {e}")
            return None

    def generate_improvement_suggestions(self, patterns: List[LearningPattern]) -> List[AgentImprovement]:
        """Generate improvement suggestions based on learning patterns"""
        print("💡 Generating Improvement Suggestions...")
        
        improvements = []
        
        # Group patterns by agent type
        agent_patterns = {}
        for pattern in patterns:
            if pattern.agent_type not in agent_patterns:
                agent_patterns[pattern.agent_type] = []
            agent_patterns[pattern.agent_type].append(pattern)
        
        # Generate improvements for each agent type
        for agent_type, agent_patterns_list in agent_patterns.items():
            agent_improvements = self.analyze_agent_patterns(agent_type, agent_patterns_list)
            improvements.extend(agent_improvements)
        
        return improvements

    def analyze_agent_patterns(self, agent_type: str, patterns: List[LearningPattern]) -> List[AgentImprovement]:
        """Analyze patterns for a specific agent type"""
        improvements = []
        
        # Count pattern types
        success_patterns = [p for p in patterns if p.pattern_type == 'success']
        failure_patterns = [p for p in patterns if p.pattern_type == 'failure']
        optimization_patterns = [p for p in patterns if p.pattern_type == 'optimization']
        
        # Generate improvements based on patterns
        if failure_patterns:
            # Agent has failures - suggest improvements
            improvements.append(AgentImprovement(
                agent_type=agent_type,
                improvement_type='goal',
                current_value='Current goal may be too broad',
                suggested_value='More specific, actionable goals with clear success criteria',
                reasoning=f"Agent has {len(failure_patterns)} failure patterns",
                expected_impact='Reduce failure rate and improve success',
                priority=4
            ))
            
            improvements.append(AgentImprovement(
                agent_type=agent_type,
                improvement_type='tools',
                current_value='Current tool set',
                suggested_value='Add more robust error handling and validation tools',
                reasoning='Multiple failure patterns suggest tool limitations',
                expected_impact='Better error handling and recovery',
                priority=5
            ))
        
        if optimization_patterns:
            # Agent needs optimization
            improvements.append(AgentImprovement(
                agent_type=agent_type,
                improvement_type='process',
                current_value='Current execution process',
                suggested_value='Streamlined process with better efficiency',
                reasoning=f"Agent has {len(optimization_patterns)} optimization patterns",
                expected_impact='Faster execution and better resource usage',
                priority=3
            ))
        
        if success_patterns:
            # Agent has successes - reinforce good patterns
            improvements.append(AgentImprovement(
                agent_type=agent_type,
                improvement_type='backstory',
                current_value='Current backstory',
                suggested_value='Enhanced backstory emphasizing successful patterns',
                reasoning=f"Agent has {len(success_patterns)} success patterns to reinforce",
                expected_impact='Maintain and improve success rate',
                priority=2
            ))
        
        return improvements

    def apply_improvements(self, improvements: List[AgentImprovement]) -> Dict[str, Any]:
        """Apply improvements to agent configurations"""
        print("🔧 Applying Agent Improvements...")
        
        applied_improvements = {}
        
        for improvement in improvements:
            if improvement.priority >= 4:  # High priority improvements
                print(f"🎯 Applying high-priority improvement to {improvement.agent_type}:")
                print(f"   Type: {improvement.improvement_type}")
                print(f"   Reasoning: {improvement.reasoning}")
                print(f"   Expected Impact: {improvement.expected_impact}")
                
                # Store the improvement for application
                if improvement.agent_type not in applied_improvements:
                    applied_improvements[improvement.agent_type] = []
                applied_improvements[improvement.agent_type].append(improvement)
        
        return applied_improvements

    def create_improved_agent(self, agent_type: str, improvements: List[AgentImprovement]) -> Agent:
        """Create an improved version of an agent based on learning"""
        print(f"🚀 Creating Improved {agent_type} Agent...")
        
        # Get base agent
        if agent_type == "senior_developer":
            base_agent = self.worker_agents.senior_developer(self.llm)
        elif agent_type == "qa_tester":
            base_agent = self.worker_agents.qa_tester(self.llm)
        elif agent_type == "code_analyzer":
            base_agent = self.worker_agents.code_analyzer(self.llm)
        elif agent_type == "system_integrator":
            base_agent = self.worker_agents.system_integrator(self.llm)
        elif agent_type == "lead_architect":
            base_agent = self.planner_agents.lead_architect(self.llm)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Apply improvements
        improved_goal = base_agent.goal
        improved_backstory = base_agent.backstory
        
        for improvement in improvements:
            if improvement.improvement_type == 'goal':
                improved_goal = improvement.suggested_value
            elif improvement.improvement_type == 'backstory':
                improved_backstory = improvement.suggested_value
        
        # Create improved agent
        improved_agent = Agent(
            role=base_agent.role,
            goal=improved_goal,
            backstory=improved_backstory,
            llm=self.llm,
            verbose=True,
            tools=base_agent.tools if hasattr(base_agent, 'tools') else [],
            allow_delegation=False,
        )
        
        return improved_agent

    def test_improved_agent(self, agent: Agent, test_prompt: str) -> Dict[str, Any]:
        """Test an improved agent with a specific prompt"""
        print(f"🧪 Testing Improved Agent: {agent.role}")
        
        start_time = time.time()
        
        task = Task(
            description=test_prompt,
            expected_output="Improved performance with better reasoning",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'execution_time': execution_time,
                'output': result,
                'quality_score': self.analyze_output_quality(result)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'quality_score': 0.0
            }

    def analyze_output_quality(self, output: str) -> float:
        """Analyze the quality of agent output"""
        quality_score = 0.0
        
        # Check for completeness
        if len(output) > 200:
            quality_score += 0.2
        
        # Check for structure
        if any(keyword in output.lower() for keyword in ['step', 'plan', 'analysis', 'recommendation']):
            quality_score += 0.2
        
        # Check for actionable content
        if any(keyword in output.lower() for keyword in ['create', 'implement', 'test', 'verify']):
            quality_score += 0.2
        
        # Check for technical depth
        if any(keyword in output.lower() for keyword in ['python', 'code', 'function', 'class', 'api']):
            quality_score += 0.2
        
        # Check for error handling
        if any(keyword in output.lower() for keyword in ['error', 'exception', 'try', 'catch']):
            quality_score += 0.2
        
        return min(quality_score, 1.0)

    def run_self_learning_cycle(self):
        """Run a complete self-learning cycle"""
        print("🧠 AGENT SELF-LEARNING CYCLE")
        print("=" * 60)
        
        # Step 1: Analyze mission history
        print("\n📊 Step 1: Analyzing Mission History...")
        patterns = self.analyze_mission_history()
        print(f"✅ Identified {len(patterns)} learning patterns")
        
        # Step 2: Generate improvements
        print("\n💡 Step 2: Generating Improvement Suggestions...")
        improvements = self.generate_improvement_suggestions(patterns)
        print(f"✅ Generated {len(improvements)} improvement suggestions")
        
        # Step 3: Apply improvements
        print("\n🔧 Step 3: Applying Improvements...")
        applied_improvements = self.apply_improvements(improvements)
        print(f"✅ Applied improvements to {len(applied_improvements)} agent types")
        
        # Step 4: Test improved agents
        print("\n🧪 Step 4: Testing Improved Agents...")
        test_results = {}
        
        test_prompts = {
            "senior_developer": "Create a robust Python function with comprehensive error handling and documentation.",
            "qa_tester": "Design a thorough testing strategy for a critical system component.",
            "code_analyzer": "Analyze the security implications of a web application's authentication system.",
            "system_integrator": "Design a scalable deployment strategy for a high-traffic application.",
            "lead_architect": "Create a comprehensive plan for modernizing a legacy system."
        }
        
        for agent_type, improvements_list in applied_improvements.items():
            if agent_type in test_prompts:
                print(f"\n🧪 Testing improved {agent_type}...")
                improved_agent = self.create_improved_agent(agent_type, improvements_list)
                test_result = self.test_improved_agent(improved_agent, test_prompts[agent_type])
                test_results[agent_type] = test_result
                
                print(f"   Success: {'✅' if test_result['success'] else '❌'}")
                print(f"   Execution Time: {test_result['execution_time']:.2f}s")
                print(f"   Quality Score: {test_result['quality_score']:.2f}")
        
        # Step 5: Generate learning report
        print("\n📊 Step 5: Generating Learning Report...")
        self.generate_learning_report(patterns, improvements, test_results)
        
        print("\n🎉 Self-learning cycle completed!")

    def generate_learning_report(self, patterns: List[LearningPattern], improvements: List[AgentImprovement], test_results: Dict[str, Any]):
        """Generate a comprehensive learning report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"self_learning_report_{timestamp}.json"
        
        report_data = {
            'timestamp': timestamp,
            'learning_patterns': [asdict(p) for p in patterns],
            'improvement_suggestions': [asdict(i) for i in improvements],
            'test_results': test_results,
            'summary': {
                'patterns_identified': len(patterns),
                'improvements_generated': len(improvements),
                'agents_tested': len(test_results),
                'successful_tests': sum(1 for r in test_results.values() if r['success'])
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"✅ Learning report saved to: {report_file}")
        
        # Display summary
        print(f"\n📊 Learning Summary:")
        print(f"   - Patterns Identified: {len(patterns)}")
        print(f"   - Improvements Generated: {len(improvements)}")
        print(f"   - Agents Tested: {len(test_results)}")
        print(f"   - Successful Tests: {sum(1 for r in test_results.values() if r['success'])}")

def main():
    """Main self-learning process"""
    print("🧠 Agent Self-Learning System")
    print("=" * 40)
    
    learner = AgentSelfLearning()
    
    try:
        # Run self-learning cycle
        learner.run_self_learning_cycle()
        
    except Exception as e:
        print(f"❌ Self-learning failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 