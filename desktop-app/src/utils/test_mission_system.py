#!/usr/bin/env python3
"""
Comprehensive Test Mission System v1.0
Provides detailed testing and validation of AI agent capabilities.
Integrates with the enhanced observability system for complete tracking.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from ..utils.agent_observability import AgentSession, agent_observability
from ..core.cognitive_forge_engine import CognitiveForgeEngine

@dataclass
class TestMission:
    """A test mission with predefined scenarios and expected outcomes."""
    mission_id: str = field(default_factory=lambda: f"test_mission_{uuid.uuid4().hex[:8]}")
    name: str = "Unknown Test Mission"
    description: str = "No description"
    category: str = "general"  # 'code_review', 'bug_fix', 'feature_dev', 'optimization', 'analysis'
    difficulty: str = "medium"  # 'easy', 'medium', 'hard', 'expert'
    test_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    expected_agents: List[str] = field(default_factory=list)
    expected_duration_minutes: int = 5
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TestExecution:
    """Results of a test mission execution."""
    execution_id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:8]}")
    test_mission: TestMission = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = False
    agent_sessions: Dict[str, AgentSession] = field(default_factory=dict)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Optional[Dict[str, Any]] = None
    error_messages: List[str] = field(default_factory=list)

class TestMissionSystem:
    """Manages test missions for evaluating agent capabilities."""
    
    def __init__(self):
        self.test_missions: Dict[str, TestMission] = {}
        self.executions: Dict[str, TestExecution] = {}
        self.cognitive_engine: Optional[CognitiveForgeEngine] = None
        self._load_default_test_missions()
    
    def _load_default_test_missions(self):
        """Load default test missions for various scenarios."""
        
        # Code Review Test Mission
        code_review_mission = TestMission(
            name="Code Review & Analysis",
            description="Test agent's ability to review code, identify issues, and suggest improvements",
            category="code_review",
            difficulty="medium",
            expected_agents=["CodeReviewer", "BugFinder", "Optimizer"],
            expected_duration_minutes=3,
            test_scenarios=[
                {
                    "name": "Syntax Error Detection",
                    "input": {
                        "code": """
def calculate_sum(a, b:
    return a + b
                        """,
                        "language": "python"
                    },
                    "expected_output": {
                        "issues_found": 1,
                        "syntax_errors": 1,
                        "suggestions": ["Fix missing closing parenthesis"]
                    }
                },
                {
                    "name": "Logic Error Detection",
                    "input": {
                        "code": """
def find_max(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num
                        """,
                        "language": "python"
                    },
                    "expected_output": {
                        "issues_found": 1,
                        "logic_errors": 1,
                        "suggestions": ["Handle empty list case"]
                    }
                },
                {
                    "name": "Performance Analysis",
                    "input": {
                        "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
                        """,
                        "language": "python"
                    },
                    "expected_output": {
                        "performance_issues": 1,
                        "suggestions": ["Use memoization or iterative approach"]
                    }
                }
            ],
            success_criteria={
                "min_issues_detected": 3,
                "max_false_positives": 0,
                "response_time_seconds": 30
            }
        )
        
        # Bug Fix Test Mission
        bug_fix_mission = TestMission(
            name="Bug Fix & Debugging",
            description="Test agent's ability to identify and fix bugs in code",
            category="bug_fix",
            difficulty="hard",
            expected_agents=["Debugger", "BugFinder", "CodeFixer"],
            expected_duration_minutes=5,
            test_scenarios=[
                {
                    "name": "Runtime Error Fix",
                    "input": {
                        "code": """
def divide_numbers(a, b):
    return a / b
                        """,
                        "error_message": "ZeroDivisionError: division by zero",
                        "test_cases": [{"a": 10, "b": 0}]
                    },
                    "expected_output": {
                        "fix_applied": True,
                        "error_handling": True,
                        "test_passes": True
                    }
                },
                {
                    "name": "Memory Leak Fix",
                    "input": {
                        "code": """
def process_large_data():
                            data = []
                            for i in range(1000000):
                                data.append(i)
                            return data
                        """,
                        "issue": "Potential memory leak with large data processing"
                    },
                    "expected_output": {
                        "fix_applied": True,
                        "memory_optimized": True,
                        "performance_improved": True
                    }
                }
            ],
            success_criteria={
                "min_fixes_applied": 2,
                "max_response_time_seconds": 60,
                "all_tests_pass": True
            }
        )
        
        # Feature Development Test Mission
        feature_dev_mission = TestMission(
            name="Feature Development",
            description="Test agent's ability to implement new features",
            category="feature_dev",
            difficulty="medium",
            expected_agents=["SeniorDeveloper", "CodeReviewer", "QATester"],
            expected_duration_minutes=8,
            test_scenarios=[
                {
                    "name": "API Endpoint Creation",
                    "input": {
                        "feature": "Create a new REST API endpoint for user authentication",
                        "requirements": [
                            "POST /api/auth/login",
                            "Input: username, password",
                            "Output: JWT token",
                            "Error handling for invalid credentials"
                        ]
                    },
                    "expected_output": {
                        "endpoint_created": True,
                        "tests_passing": True,
                        "documentation_updated": True
                    }
                },
                {
                    "name": "Database Schema Update",
                    "input": {
                        "feature": "Add user profile fields to database",
                        "requirements": [
                            "Add fields: bio, avatar_url, preferences",
                            "Create migration script",
                            "Update model classes",
                            "Add validation rules"
                        ]
                    },
                    "expected_output": {
                        "schema_updated": True,
                        "migration_created": True,
                        "models_updated": True
                    }
                }
            ],
            success_criteria={
                "all_features_implemented": True,
                "tests_passing": True,
                "documentation_complete": True
            }
        )
        
        # Performance Optimization Test Mission
        performance_mission = TestMission(
            name="Performance Optimization",
            description="Test agent's ability to optimize code performance",
            category="optimization",
            difficulty="hard",
            expected_agents=["PerformanceOptimizer", "CodeAnalyzer", "Profiler"],
            expected_duration_minutes=6,
            test_scenarios=[
                {
                    "name": "Algorithm Optimization",
                    "input": {
                        "code": """
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates
                        """,
                        "performance_issue": "O(n²) time complexity"
                    },
                    "expected_output": {
                        "optimization_applied": True,
                        "complexity_improved": True,
                        "performance_measured": True
                    }
                },
                {
                    "name": "Database Query Optimization",
                    "input": {
                        "query": "SELECT * FROM users WHERE age > 18 AND city = 'New York'",
                        "issue": "Missing indexes, inefficient query"
                    },
                    "expected_output": {
                        "indexes_created": True,
                        "query_optimized": True,
                        "performance_improved": True
                    }
                }
            ],
            success_criteria={
                "performance_improved": True,
                "complexity_reduced": True,
                "benchmarks_passing": True
            }
        )
        
        # Security Analysis Test Mission
        security_mission = TestMission(
            name="Security Analysis",
            description="Test agent's ability to identify and fix security vulnerabilities",
            category="security",
            difficulty="expert",
            expected_agents=["SecurityScanner", "VulnerabilityAnalyzer", "SecurityFixer"],
            expected_duration_minutes=7,
            test_scenarios=[
                {
                    "name": "SQL Injection Detection",
                    "input": {
                        "code": """
def get_user_by_id(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)
                        """,
                        "vulnerability": "SQL injection vulnerability"
                    },
                    "expected_output": {
                        "vulnerability_detected": True,
                        "fix_applied": True,
                        "security_improved": True
                    }
                },
                {
                    "name": "XSS Prevention",
                    "input": {
                        "code": """
def display_user_input(user_input):
    return f"<div>{user_input}</div>"
                        """,
                        "vulnerability": "Cross-site scripting (XSS)"
                    },
                    "expected_output": {
                        "vulnerability_detected": True,
                        "sanitization_applied": True,
                        "security_improved": True
                    }
                }
            ],
            success_criteria={
                "all_vulnerabilities_detected": True,
                "all_fixes_applied": True,
                "security_audit_passed": True
            }
        )
        
        # Add missions to the system
        self.test_missions[code_review_mission.mission_id] = code_review_mission
        self.test_missions[bug_fix_mission.mission_id] = bug_fix_mission
        self.test_missions[feature_dev_mission.mission_id] = feature_dev_mission
        self.test_missions[performance_mission.mission_id] = performance_mission
        self.test_missions[security_mission.mission_id] = security_mission

    def set_cognitive_engine(self, engine: CognitiveForgeEngine):
        """Set the cognitive engine for real agent execution."""
        self.cognitive_engine = engine
        logger.info("Cognitive engine set for test mission system")

    async def run_test_mission(self, mission_id: str, user_request: str = None) -> TestExecution:
        """Run a test mission with real agent execution."""
        if mission_id not in self.test_missions:
            raise ValueError(f"Test mission {mission_id} not found")
        
        test_mission = self.test_missions[mission_id]
        execution = TestExecution(test_mission=test_mission)
        
        # Store execution for tracking
        self.executions[execution.execution_id] = execution
        
        # Use the enhanced observability system
        with agent_observability.mission_observability(
            execution.execution_id, 
            user_request or f"Test Mission: {test_mission.name}",
            test_mode=True
        ) as mission_data:
            
            try:
                logger.info(f"🚀 Starting test mission: {test_mission.name}")
                
                # Create a test start event
                test_start_event = agent_observability._create_live_stream_event(
                    event_type="test_start",
                    mission_id=execution.execution_id,
                    event_data={
                        "test_mission_name": test_mission.name,
                        "test_mission_id": mission_id,
                        "scenarios_count": len(test_mission.test_scenarios),
                        "expected_duration_minutes": test_mission.expected_duration_minutes,
                        "difficulty": test_mission.difficulty,
                        "category": test_mission.category,
                        "test_mode": True,
                        "user_request": user_request or f"Test Mission: {test_mission.name}"
                    },
                    severity="info",
                    tags=["test", "mission", "start"]
                )
                
                # Execute each test scenario with real agents
                for i, scenario in enumerate(test_mission.test_scenarios):
                    logger.info(f"📋 Executing scenario {i+1}: {scenario['name']}")
                    
                    # Create scenario start event
                    scenario_start_event = agent_observability._create_live_stream_event(
                        event_type="scenario_start",
                        mission_id=execution.execution_id,
                        event_data={
                            "scenario_name": scenario['name'],
                            "scenario_index": i + 1,
                            "total_scenarios": len(test_mission.test_scenarios),
                            "scenario_input": scenario.get('input', {}),
                            "expected_output": scenario.get('expected_output', {}),
                            "test_mode": True
                        },
                        severity="info",
                        tags=["test", "scenario", "start"]
                    )
                    
                    # Execute scenario with real cognitive engine
                    test_result = await self._execute_test_scenario_with_real_agents(scenario, execution.execution_id)
                    
                    # Ensure test_result is JSON serializable
                    serializable_result = self._make_serializable(test_result)
                    execution.test_results.append(serializable_result)
                    
                    # Create scenario complete event
                    scenario_complete_event = agent_observability._create_live_stream_event(
                        event_type="scenario_complete",
                        mission_id=execution.execution_id,
                        event_data={
                            "scenario_name": scenario['name'],
                            "scenario_index": i + 1,
                            "test_result": serializable_result,
                            "success": test_result.get('success', True),
                            "duration_ms": test_result.get('duration_ms', 0),
                            "test_mode": True
                        },
                        severity="info",
                        tags=["test", "scenario", "complete"]
                    )
                
                # Calculate final metrics
                execution.end_time = datetime.utcnow()
                execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
                execution.success = self._evaluate_test_success(execution, test_mission.success_criteria)
                execution.performance_metrics = self._calculate_execution_performance(execution)
                
                # Create test completion event
                test_complete_event = agent_observability._create_live_stream_event(
                    event_type="test_complete",
                    mission_id=execution.execution_id,
                    event_data={
                        "test_mission_name": test_mission.name,
                        "success": execution.success,
                        "duration_seconds": execution.duration_seconds,
                        "scenarios_executed": len(execution.test_results),
                        "performance_metrics": execution.performance_metrics,
                        "test_mode": True
                    },
                    severity="info",
                    tags=["test", "mission", "complete"]
                )
                
                logger.info(f"✅ Test mission completed: {test_mission.name} - Success: {execution.success}")
                
            except Exception as e:
                logger.error(f"❌ Test mission failed: {e}")
                execution.error_messages.append(str(e))
                execution.success = False
                execution.end_time = datetime.utcnow()
                execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
        
        return execution

    async def _execute_test_scenario_with_real_agents(self, scenario: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute a test scenario using real cognitive engine agents."""
        start_time = time.time()
        
        try:
            if not self.cognitive_engine:
                raise ValueError("Cognitive engine not available for real agent execution")
            
            # Create a prompt based on the scenario
            scenario_prompt = self._create_scenario_prompt(scenario)
            
            # Execute with real cognitive engine
            result = await self.cognitive_engine.run_mission_simple(scenario_prompt, execution_id)
            
            # Analyze the result against expected output
            analysis_result = self._analyze_scenario_result(result, scenario)
            
            test_result = {
                "scenario_name": scenario['name'],
                "success": analysis_result.get('success', False),
                "duration_ms": (time.time() - start_time) * 1000,
                "input": scenario.get('input', {}),
                "output": result,
                "analysis": analysis_result,
                "performance_metrics": {
                    "memory_usage_mb": result.get('memory_usage', 0),
                    "cpu_usage_percent": result.get('cpu_usage', 0),
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "tokens_used": result.get('tokens_used', 0)
                }
            }
            
            return test_result
            
        except Exception as e:
            logger.error(f"Error executing scenario {scenario['name']}: {e}")
            return {
                "scenario_name": scenario['name'],
                "success": False,
                "duration_ms": (time.time() - start_time) * 1000,
                "input": scenario.get('input', {}),
                "output": {},
                "error_message": str(e),
                "analysis": {"success": False, "error": str(e)}
            }

    def _create_scenario_prompt(self, scenario: Dict[str, Any]) -> str:
        """Create a prompt for the cognitive engine based on the scenario."""
        scenario_name = scenario['name']
        scenario_input = scenario.get('input', {})
        expected_output = scenario.get('expected_output', {})
        
        if scenario_name == "Syntax Error Detection":
            code = scenario_input.get('code', '')
            return f"""
            Analyze this Python code for syntax errors and provide fixes:
            
            {code}
            
            Please identify any syntax errors and provide corrected code.
            """
        
        elif scenario_name == "Runtime Error Fix":
            code = scenario_input.get('code', '')
            error_message = scenario_input.get('error_message', '')
            return f"""
            Fix this code that produces a runtime error:
            
            Code:
            {code}
            
            Error: {error_message}
            
            Please provide a fixed version that handles the error properly.
            """
        
        elif scenario_name == "API Endpoint Creation":
            requirements = scenario_input.get('requirements', [])
            return f"""
            Create a REST API endpoint with these requirements:
            
            {chr(10).join(requirements)}
            
            Please provide the complete implementation including error handling and validation.
            """
        
        elif scenario_name == "Algorithm Optimization":
            code = scenario_input.get('code', '')
            issue = scenario_input.get('performance_issue', '')
            return f"""
            Optimize this algorithm for better performance:
            
            {code}
            
            Issue: {issue}
            
            Please provide an optimized version with improved time/space complexity.
            """
        
        elif scenario_name == "SQL Injection Detection":
            code = scenario_input.get('code', '')
            vulnerability = scenario_input.get('vulnerability', '')
            return f"""
            Identify and fix this security vulnerability:
            
            Code:
            {code}
            
            Vulnerability: {vulnerability}
            
            Please provide a secure version that prevents this vulnerability.
            """
        
        else:
            # Generic scenario prompt
            return f"""
            Execute this test scenario: {scenario_name}
            
            Input: {scenario_input}
            Expected Output: {expected_output}
            
            Please provide a solution that meets the expected output criteria.
            """

    def _analyze_scenario_result(self, result: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the cognitive engine result against expected output."""
        expected_output = scenario.get('expected_output', {})
        scenario_name = scenario['name']
        
        analysis = {
            "success": False,
            "criteria_met": [],
            "criteria_failed": [],
            "score": 0.0
        }
        
        # Basic success check
        if result.get('status') == 'completed' and result.get('result'):
            analysis["success"] = True
            analysis["score"] = 0.5  # Base score for completion
        
        # Scenario-specific analysis
        if scenario_name == "Syntax Error Detection":
            result_text = result.get('result', '')
            if 'syntax' in result_text.lower() or 'error' in result_text.lower():
                analysis["criteria_met"].append("syntax_error_detected")
                analysis["score"] += 0.3
            if 'fix' in result_text.lower() or 'correct' in result_text.lower():
                analysis["criteria_met"].append("fix_provided")
                analysis["score"] += 0.2
        
        elif scenario_name == "Runtime Error Fix":
            result_text = result.get('result', '')
            if 'try' in result_text.lower() or 'except' in result_text.lower():
                analysis["criteria_met"].append("error_handling_added")
                analysis["score"] += 0.4
            if 'zero' in result_text.lower() or 'division' in result_text.lower():
                analysis["criteria_met"].append("specific_error_handled")
                analysis["score"] += 0.3
        
        elif scenario_name == "API Endpoint Creation":
            result_text = result.get('result', '')
            if 'def' in result_text.lower() and 'route' in result_text.lower():
                analysis["criteria_met"].append("endpoint_created")
                analysis["score"] += 0.4
            if 'post' in result_text.lower() or 'get' in result_text.lower():
                analysis["criteria_met"].append("http_method_specified")
                analysis["score"] += 0.3
        
        # Cap score at 1.0
        analysis["score"] = min(analysis["score"], 1.0)
        
        return analysis

    def _evaluate_test_success(self, execution: TestExecution, criteria: Dict[str, Any]) -> bool:
        """Evaluate if the test execution meets success criteria."""
        if not execution.test_results:
            return False
        
        # Check basic success criteria
        all_scenarios_successful = all(result.get('success', False) for result in execution.test_results)
        
        # Check specific criteria
        if 'min_issues_detected' in criteria:
            total_issues = sum(result.get('issues_found', 0) for result in execution.test_results)
            if total_issues < criteria['min_issues_detected']:
                return False
        
        if 'max_false_positives' in criteria:
            false_positives = sum(1 for result in execution.test_results if result.get('false_positive', False))
            if false_positives > criteria['max_false_positives']:
                return False
        
        if 'response_time_seconds' in criteria:
            max_duration = criteria['response_time_seconds'] * 1000  # Convert to ms
            if execution.duration_seconds * 1000 > max_duration:
                return False
        
        return all_scenarios_successful

    def _calculate_execution_performance(self, execution: TestExecution) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics for the test execution."""
        if not execution.test_results:
            return {}
        
        return {
            "total_scenarios": len(execution.test_results),
            "successful_scenarios": sum(1 for r in execution.test_results if r.get('success', False)),
            "avg_scenario_duration_ms": sum(r.get('duration_ms', 0) for r in execution.test_results) / len(execution.test_results),
            "total_issues_found": sum(r.get('issues_found', 0) for r in execution.test_results),
            "total_suggestions": sum(len(r.get('suggestions', [])) for r in execution.test_results),
            "execution_duration_seconds": execution.duration_seconds,
            "success_rate": sum(1 for r in execution.test_results if r.get('success', False)) / len(execution.test_results),
            "avg_score": sum(r.get('analysis', {}).get('score', 0) for r in execution.test_results) / len(execution.test_results)
        }

    def get_available_test_missions(self) -> List[Dict[str, Any]]:
        """Get list of available test missions."""
        return [
            {
                "mission_id": mission.mission_id,
                "name": mission.name,
                "description": mission.description,
                "category": mission.category,
                "difficulty": mission.difficulty,
                "expected_duration_minutes": mission.expected_duration_minutes,
                "scenario_count": len(mission.test_scenarios)
            }
            for mission in self.test_missions.values()
        ]

    def get_test_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a specific test execution."""
        if execution_id not in self.executions:
            return None
        
        execution = self.executions[execution_id]
        return self._make_execution_serializable(execution)

    def get_test_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of all test executions."""
        return [self._make_execution_serializable(execution) for execution in self.executions.values()]

    def get_agent_performance_analysis(self) -> Dict[str, Any]:
        """Get comprehensive analysis of test mission performance."""
        if not self.executions:
            return {"message": "No test executions available"}
        
        total_executions = len(self.executions)
        successful_executions = sum(1 for e in self.executions.values() if e.success)
        
        # Calculate average metrics
        avg_duration = sum(e.duration_seconds for e in self.executions.values()) / total_executions
        avg_success_rate = sum(
            sum(1 for r in e.test_results if r.get('success', False)) / len(e.test_results) 
            for e in self.executions.values() if e.test_results
        ) / total_executions
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "overall_success_rate": successful_executions / total_executions,
            "avg_execution_duration_seconds": avg_duration,
            "avg_scenario_success_rate": avg_success_rate,
            "executions_by_category": self._group_executions_by_category(),
            "executions_by_difficulty": self._group_executions_by_difficulty()
        }

    def _group_executions_by_category(self) -> Dict[str, Any]:
        """Group executions by test mission category."""
        categories = {}
        for execution in self.executions.values():
            category = execution.test_mission.category
            if category not in categories:
                categories[category] = {"count": 0, "successful": 0}
            categories[category]["count"] += 1
            if execution.success:
                categories[category]["successful"] += 1
        
        return categories

    def _group_executions_by_difficulty(self) -> Dict[str, Any]:
        """Group executions by test mission difficulty."""
        difficulties = {}
        for execution in self.executions.values():
            difficulty = execution.test_mission.difficulty
            if difficulty not in difficulties:
                difficulties[difficulty] = {"count": 0, "successful": 0}
            difficulties[difficulty]["count"] += 1
            if execution.success:
                difficulties[difficulty]["successful"] += 1
        
        return difficulties

    def export_test_data(self, execution_id: Optional[str] = None) -> Dict[str, Any]:
        """Export test data for analysis."""
        if execution_id:
            execution = self.executions.get(execution_id)
            if not execution:
                return {"error": "Execution not found"}
            return self._make_execution_serializable(execution)
        else:
            return {
                "test_missions": self.get_available_test_missions(),
                "executions": self.get_test_execution_history(),
                "analysis": self.get_agent_performance_analysis(),
                "export_timestamp": datetime.utcnow().isoformat()
            }

    def _make_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj

    def _make_execution_serializable(self, execution: TestExecution) -> Dict[str, Any]:
        """Convert execution object to serializable format."""
        return {
            "execution_id": execution.execution_id,
            "test_mission": {
                "mission_id": execution.test_mission.mission_id,
                "name": execution.test_mission.name,
                "description": execution.test_mission.description,
                "category": execution.test_mission.category,
                "difficulty": execution.test_mission.difficulty
            },
            "start_time": execution.start_time.isoformat() if execution.start_time else None,
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "duration_seconds": execution.duration_seconds,
            "success": execution.success,
            "test_results": execution.test_results,
            "performance_metrics": execution.performance_metrics,
            "error_messages": execution.error_messages
        } 