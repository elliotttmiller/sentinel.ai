#!/usr/bin/env python3
"""
AI Agent Optimizer & Fine-Tuning System
Advanced system for testing, optimizing, and configuring specialized AI agents
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import requests
from loguru import logger

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.advanced_agents import PlannerAgents, WorkerAgents, MemoryAgents
from src.tools.crewai_tools import (
    write_file_tool, read_file_tool, list_files_tool,
    execute_shell_command_tool, analyze_python_file_tool, system_info_tool
)
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentType(Enum):
    """Types of agents we can optimize"""
    LEAD_ARCHITECT = "lead_architect"
    PLAN_VALIDATOR = "plan_validator"
    SENIOR_DEVELOPER = "senior_developer"
    QA_TESTER = "qa_tester"
    CODE_ANALYZER = "code_analyzer"
    SYSTEM_INTEGRATOR = "system_integrator"
    MEMORY_SYNTHESIZER = "memory_synthesizer"

@dataclass
class AgentPerformance:
    """Track agent performance metrics"""
    agent_type: str
    success_rate: float
    avg_execution_time: float
    avg_tokens_used: int
    common_failures: List[str]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]

@dataclass
class AgentTestResult:
    """Results from individual agent testing"""
    agent_type: str
    test_name: str
    success: bool
    execution_time: float
    tokens_used: int
    thinking_process: str
    decisions_made: List[str]
    tools_used: List[str]
    errors: List[str]
    output_quality: float  # 0-1 scale
    learning_insights: List[str]

class AIAgentOptimizer:
    """Advanced AI Agent Optimization System"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-1.5-pro-latest"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
        self.planner_agents = PlannerAgents()
        self.worker_agents = WorkerAgents()
        self.memory_agents = MemoryAgents()
        self.performance_data = {}
        self.test_results = []
        
    def create_agent(self, agent_type: AgentType) -> Agent:
        """Create an agent of the specified type"""
        if agent_type == AgentType.LEAD_ARCHITECT:
            return self.planner_agents.lead_architect(self.llm)
        elif agent_type == AgentType.PLAN_VALIDATOR:
            return self.planner_agents.plan_validator(self.llm)
        elif agent_type == AgentType.SENIOR_DEVELOPER:
            return self.worker_agents.senior_developer(self.llm)
        elif agent_type == AgentType.QA_TESTER:
            return self.worker_agents.qa_tester(self.llm)
        elif agent_type == AgentType.CODE_ANALYZER:
            return self.worker_agents.code_analyzer(self.llm)
        elif agent_type == AgentType.SYSTEM_INTEGRATOR:
            return self.worker_agents.system_integrator(self.llm)
        elif agent_type == AgentType.MEMORY_SYNTHESIZER:
            return self.memory_agents.memory_synthesizer(self.llm)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def test_agent_thinking_process(self, agent_type: AgentType, test_prompt: str) -> AgentTestResult:
        """Test an individual agent and capture their thinking process"""
        print(f"\n🧠 Testing {agent_type.value} thinking process...")
        
        start_time = time.time()
        agent = self.create_agent(agent_type)
        
        # Create a simple task to test the agent
        task = Task(
            description=test_prompt,
            expected_output="Detailed analysis and execution plan",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            # Capture the thinking process
            thinking_process = []
            decisions_made = []
            tools_used = []
            errors = []
            
            # Execute with detailed logging
            result = crew.kickoff()
            
            execution_time = time.time() - start_time
            
            # Analyze the result for quality
            output_quality = self.analyze_output_quality(result, test_prompt)
            
            # Extract learning insights
            learning_insights = self.extract_learning_insights(result, agent_type)
            
            return AgentTestResult(
                agent_type=agent_type.value,
                test_name=test_prompt[:50] + "...",
                success=True,
                execution_time=execution_time,
                tokens_used=self.estimate_tokens(result),
                thinking_process=result,
                decisions_made=decisions_made,
                tools_used=tools_used,
                errors=errors,
                output_quality=output_quality,
                learning_insights=learning_insights
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return AgentTestResult(
                agent_type=agent_type.value,
                test_name=test_prompt[:50] + "...",
                success=False,
                execution_time=execution_time,
                tokens_used=0,
                thinking_process=str(e),
                decisions_made=[],
                tools_used=[],
                errors=[str(e)],
                output_quality=0.0,
                learning_insights=[f"Agent failed: {str(e)}"]
            )

    def analyze_output_quality(self, output: str, original_prompt: str) -> float:
        """Analyze the quality of agent output"""
        quality_score = 0.0
        
        # Check for completeness
        if len(output) > 100:
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

    def extract_learning_insights(self, output: str, agent_type: AgentType) -> List[str]:
        """Extract learning insights from agent output"""
        insights = []
        
        # Analyze based on agent type
        if agent_type == AgentType.SENIOR_DEVELOPER:
            if 'def ' in output or 'class ' in output:
                insights.append("Agent successfully generated code structures")
            if 'import ' in output:
                insights.append("Agent understands dependency management")
            if 'error' in output.lower() or 'exception' in output.lower():
                insights.append("Agent considers error handling")
                
        elif agent_type == AgentType.QA_TESTER:
            if 'test' in output.lower():
                insights.append("Agent focuses on testing approach")
            if 'verify' in output.lower() or 'validate' in output.lower():
                insights.append("Agent emphasizes verification")
                
        elif agent_type == AgentType.LEAD_ARCHITECT:
            if 'plan' in output.lower() or 'strategy' in output.lower():
                insights.append("Agent demonstrates strategic thinking")
            if 'step' in output.lower() or 'phase' in output.lower():
                insights.append("Agent breaks down complex tasks")
                
        return insights

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def run_comprehensive_agent_tests(self) -> Dict[str, AgentPerformance]:
        """Run comprehensive tests on all agents"""
        print("🚀 Starting Comprehensive Agent Optimization...")
        
        test_scenarios = [
            {
                "name": "Code Generation",
                "prompt": "Create a Python function that calculates the Fibonacci sequence with proper error handling and documentation.",
                "target_agents": [AgentType.SENIOR_DEVELOPER, AgentType.CODE_ANALYZER]
            },
            {
                "name": "System Analysis",
                "prompt": "Analyze the current system performance and provide recommendations for optimization.",
                "target_agents": [AgentType.SYSTEM_INTEGRATOR, AgentType.CODE_ANALYZER]
            },
            {
                "name": "Quality Assurance",
                "prompt": "Design a comprehensive testing strategy for a web application with user authentication.",
                "target_agents": [AgentType.QA_TESTER, AgentType.SENIOR_DEVELOPER]
            },
            {
                "name": "Strategic Planning",
                "prompt": "Create a detailed plan for migrating a monolithic application to microservices architecture.",
                "target_agents": [AgentType.LEAD_ARCHITECT, AgentType.PLAN_VALIDATOR]
            },
            {
                "name": "Knowledge Synthesis",
                "prompt": "Analyze previous mission results and extract key learning patterns for future improvements.",
                "target_agents": [AgentType.MEMORY_SYNTHESIZER]
            }
        ]
        
        agent_performance = {}
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing Scenario: {scenario['name']}")
            
            for agent_type in scenario['target_agents']:
                result = self.test_agent_thinking_process(agent_type, scenario['prompt'])
                self.test_results.append(result)
                
                # Update performance data
                if agent_type.value not in agent_performance:
                    agent_performance[agent_type.value] = {
                        'successes': 0,
                        'total_tests': 0,
                        'execution_times': [],
                        'token_usage': [],
                        'output_qualities': [],
                        'errors': [],
                        'insights': []
                    }
                
                perf = agent_performance[agent_type.value]
                perf['total_tests'] += 1
                
                if result.success:
                    perf['successes'] += 1
                
                perf['execution_times'].append(result.execution_time)
                perf['token_usage'].append(result.tokens_used)
                perf['output_qualities'].append(result.output_quality)
                perf['errors'].extend(result.errors)
                perf['insights'].extend(result.learning_insights)
        
        # Calculate performance metrics
        performance_summary = {}
        for agent_type, data in agent_performance.items():
            success_rate = data['successes'] / data['total_tests'] if data['total_tests'] > 0 else 0
            avg_execution_time = sum(data['execution_times']) / len(data['execution_times']) if data['execution_times'] else 0
            avg_tokens = sum(data['token_usage']) / len(data['token_usage']) if data['token_usage'] else 0
            avg_quality = sum(data['output_qualities']) / len(data['output_qualities']) if data['output_qualities'] else 0
            
            # Analyze strengths and weaknesses
            strengths = self.analyze_agent_strengths(data)
            weaknesses = self.analyze_agent_weaknesses(data)
            improvements = self.generate_improvement_suggestions(agent_type, data)
            
            performance_summary[agent_type] = AgentPerformance(
                agent_type=agent_type,
                success_rate=success_rate,
                avg_execution_time=avg_execution_time,
                avg_tokens_used=int(avg_tokens),
                common_failures=data['errors'],
                strengths=strengths,
                weaknesses=weaknesses,
                improvement_suggestions=improvements
            )
        
        return performance_summary

    def analyze_agent_strengths(self, data: Dict) -> List[str]:
        """Analyze agent strengths based on performance data"""
        strengths = []
        
        if data['successes'] / data['total_tests'] > 0.8:
            strengths.append("High success rate")
        
        avg_quality = sum(data['output_qualities']) / len(data['output_qualities']) if data['output_qualities'] else 0
        if avg_quality > 0.7:
            strengths.append("High output quality")
        
        avg_time = sum(data['execution_times']) / len(data['execution_times']) if data['execution_times'] else 0
        if avg_time < 30:  # Less than 30 seconds
            strengths.append("Fast execution")
        
        if len(data['insights']) > len(data['errors']):
            strengths.append("Good learning capability")
        
        return strengths

    def analyze_agent_weaknesses(self, data: Dict) -> List[str]:
        """Analyze agent weaknesses based on performance data"""
        weaknesses = []
        
        if data['successes'] / data['total_tests'] < 0.6:
            weaknesses.append("Low success rate")
        
        avg_quality = sum(data['output_qualities']) / len(data['output_qualities']) if data['output_qualities'] else 0
        if avg_quality < 0.5:
            weaknesses.append("Low output quality")
        
        avg_time = sum(data['execution_times']) / len(data['execution_times']) if data['execution_times'] else 0
        if avg_time > 60:  # More than 60 seconds
            weaknesses.append("Slow execution")
        
        if len(data['errors']) > 0:
            weaknesses.append(f"Frequent errors: {len(data['errors'])} instances")
        
        return weaknesses

    def generate_improvement_suggestions(self, agent_type: str, data: Dict) -> List[str]:
        """Generate improvement suggestions for agents"""
        suggestions = []
        
        success_rate = data['successes'] / data['total_tests'] if data['total_tests'] > 0 else 0
        if success_rate < 0.8:
            suggestions.append("Improve error handling and validation")
        
        avg_quality = sum(data['output_qualities']) / len(data['output_qualities']) if data['output_qualities'] else 0
        if avg_quality < 0.7:
            suggestions.append("Enhance output structure and completeness")
        
        if len(data['errors']) > 0:
            suggestions.append("Implement better error recovery mechanisms")
        
        # Agent-specific suggestions
        if agent_type == "senior_developer":
            suggestions.append("Add more code examples and best practices")
        elif agent_type == "qa_tester":
            suggestions.append("Include more comprehensive test scenarios")
        elif agent_type == "lead_architect":
            suggestions.append("Improve strategic planning and risk assessment")
        
        return suggestions

    def generate_optimization_report(self, performance_data: Dict[str, AgentPerformance]) -> str:
        """Generate a comprehensive optimization report"""
        report = []
        report.append("# AI Agent Optimization Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall performance summary
        total_agents = len(performance_data)
        avg_success_rate = sum(p.success_rate for p in performance_data.values()) / total_agents
        report.append(f"## Overall Performance")
        report.append(f"- Total Agents Tested: {total_agents}")
        report.append(f"- Average Success Rate: {avg_success_rate:.2%}")
        report.append("")
        
        # Individual agent analysis
        for agent_type, performance in performance_data.items():
            report.append(f"## {agent_type.replace('_', ' ').title()}")
            report.append(f"- Success Rate: {performance.success_rate:.2%}")
            report.append(f"- Average Execution Time: {performance.avg_execution_time:.2f}s")
            report.append(f"- Average Tokens Used: {performance.avg_tokens_used}")
            report.append("")
            
            if performance.strengths:
                report.append("### Strengths")
                for strength in performance.strengths:
                    report.append(f"- {strength}")
                report.append("")
            
            if performance.weaknesses:
                report.append("### Areas for Improvement")
                for weakness in performance.weaknesses:
                    report.append(f"- {weakness}")
                report.append("")
            
            if performance.improvement_suggestions:
                report.append("### Optimization Suggestions")
                for suggestion in performance.improvement_suggestions:
                    report.append(f"- {suggestion}")
                report.append("")
        
        return "\n".join(report)

    def save_optimization_data(self, performance_data: Dict[str, AgentPerformance], report: str):
        """Save optimization data and report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save performance data
        data_file = f"optimization_data_{timestamp}.json"
        with open(data_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'performance_data': {k: {
                    'success_rate': v.success_rate,
                    'avg_execution_time': v.avg_execution_time,
                    'avg_tokens_used': v.avg_tokens_used,
                    'common_failures': v.common_failures,
                    'strengths': v.strengths,
                    'weaknesses': v.weaknesses,
                    'improvement_suggestions': v.improvement_suggestions
                } for k, v in performance_data.items()},
                'test_results': [{
                    'agent_type': r.agent_type,
                    'test_name': r.test_name,
                    'success': r.success,
                    'execution_time': r.execution_time,
                    'tokens_used': r.tokens_used,
                    'output_quality': r.output_quality,
                    'errors': r.errors,
                    'learning_insights': r.learning_insights
                } for r in self.test_results]
            }, f, indent=2, default=str)
        
        # Save report
        report_file = f"optimization_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ Optimization data saved to: {data_file}")
        print(f"✅ Optimization report saved to: {report_file}")

def main():
    """Main optimization process"""
    print("🧠 AI Agent Optimization & Fine-Tuning System")
    print("=" * 60)
    
    optimizer = AIAgentOptimizer()
    
    try:
        # Run comprehensive tests
        performance_data = optimizer.run_comprehensive_agent_tests()
        
        # Generate report
        report = optimizer.generate_optimization_report(performance_data)
        
        # Save results
        optimizer.save_optimization_data(performance_data, report)
        
        # Display summary
        print("\n🎯 Optimization Summary:")
        print("=" * 40)
        for agent_type, performance in performance_data.items():
            print(f"📊 {agent_type.replace('_', ' ').title()}:")
            print(f"   Success Rate: {performance.success_rate:.2%}")
            print(f"   Avg Time: {performance.avg_execution_time:.2f}s")
            print(f"   Strengths: {', '.join(performance.strengths)}")
            print(f"   Weaknesses: {', '.join(performance.weaknesses)}")
            print()
        
        print("✅ Optimization complete! Check the generated files for detailed analysis.")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 