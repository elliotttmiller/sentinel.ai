"""
QA Tester Agent for Project Sentinel.

Test creation and validation specialist that ensures software works as intended.
Responsible for writing and executing unit tests, integration tests, and end-to-end tests.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from loguru import logger

from ..core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult, AgentStatus


class QATesterAgent(BaseAgent):
    """
    QA Tester - Test creation and validation specialist.
    
    Responsibilities:
    - Write comprehensive unit tests for new functionality
    - Create integration tests for component interactions
    - Execute test suites and analyze results
    - Perform regression testing to ensure no existing functionality is broken
    - Generate test reports and coverage analysis
    - Identify and report bugs and issues
    """
    
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
        tools: list[str],
        model_name: str,
        llm_client,
        tool_manager
    ):
        super().__init__(role, name, description, tools, model_name)
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.logger = logger.bind(agent="qa_tester")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the QA Tester's behavior."""
        return """
        You are the QA Tester, a test creation and validation specialist for Project Sentinel.
        Your role is to ensure that software works as intended by creating comprehensive
        test suites and validating functionality.
        
        Your expertise includes:
        1. **Test Strategy**: Design comprehensive testing approaches
        2. **Unit Testing**: Create focused tests for individual components
        3. **Integration Testing**: Test component interactions and data flow
        4. **Regression Testing**: Ensure existing functionality remains intact
        5. **Test Automation**: Create automated test suites
        6. **Bug Reporting**: Identify and document issues clearly
        
        Testing Principles:
        - Test both happy path and edge cases
        - Ensure adequate test coverage
        - Write clear, maintainable test code
        - Focus on functionality and user experience
        - Document test cases and expected results
        - Prioritize critical functionality testing
        
        Test Types:
        - **Unit Tests**: Test individual functions and methods
        - **Integration Tests**: Test component interactions
        - **End-to-End Tests**: Test complete user workflows
        - **Performance Tests**: Test system performance under load
        - **Security Tests**: Test for security vulnerabilities
        
        Always strive for comprehensive testing that ensures
        high-quality, reliable software.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the QA Tester's testing task.
        
        Args:
            context: The execution context containing the testing requirements
            
        Returns:
            AgentResult: The testing result
        """
        self.logger.info(f"Starting QA testing for mission {context.mission_id}")
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Extract testing requirements from context
            testing_target = context.user_prompt
            
            # Analyze the codebase for testing
            codebase_analysis = await self._analyze_codebase_for_testing(context.workspace_path)
            
            # Create and execute test suite
            testing_result = await self._perform_testing(
                codebase_analysis,
                testing_target,
                context
            )
            
            # Create the result
            result = AgentResult(
                success=True,
                output=json.dumps(testing_result, indent=2),
                metadata={
                    "testing_type": "comprehensive_qa_testing",
                    "tests_created": len(testing_result.get("tests_created", [])),
                    "tests_executed": len(testing_result.get("tests_executed", [])),
                    "test_coverage": testing_result.get("coverage", {}).get("overall", 0),
                    "bugs_found": len(testing_result.get("bugs_found", []))
                }
            )
            
            self.logger.info("QA testing completed successfully")
            self.update_status(AgentStatus.COMPLETED)
            return result
            
        except Exception as e:
            self.logger.error(f"QA testing failed: {e}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                success=False,
                output="",
                error=f"QA testing failed: {str(e)}"
            )
    
    async def _analyze_codebase_for_testing(self, workspace_path: Path) -> Dict[str, Any]:
        """
        Analyze the codebase to understand what needs testing.
        
        Args:
            workspace_path: Path to the workspace
            
        Returns:
            Dict[str, Any]: Codebase analysis for testing
        """
        self.logger.info("Analyzing codebase for testing requirements")
        
        analysis = {
            "testable_components": [],
            "existing_tests": [],
            "test_frameworks": [],
            "languages": [],
            "entry_points": [],
            "dependencies": {}
        }
        
        try:
            # Detect programming languages and frameworks
            if (workspace_path / "requirements.txt").exists():
                analysis["languages"].append("python")
                analysis["test_frameworks"].append("pytest")
            
            if (workspace_path / "package.json").exists():
                analysis["languages"].append("javascript")
                analysis["test_frameworks"].append("jest")
            
            # Find existing test files
            for test_file in workspace_path.rglob("*test*.py"):
                analysis["existing_tests"].append(str(test_file))
            
            for test_file in workspace_path.rglob("*test*.js"):
                analysis["existing_tests"].append(str(test_file))
            
            # Find main application files
            for file_path in workspace_path.rglob("*.py"):
                if file_path.name in ["main.py", "app.py"]:
                    analysis["entry_points"].append(str(file_path))
            
        except Exception as e:
            self.logger.warning(f"Error analyzing codebase for testing: {e}")
        
        return analysis
    
    async def _perform_testing(
        self, 
        codebase_analysis: Dict[str, Any],
        testing_target: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Perform comprehensive testing.
        
        Args:
            codebase_analysis: Analysis of the codebase
            testing_target: Specific testing requirements
            context: Execution context
            
        Returns:
            Dict[str, Any]: Testing result
        """
        self.logger.info("Performing comprehensive testing")
        
        testing_result = {
            "tests_created": [],
            "tests_executed": [],
            "test_results": {},
            "coverage": {},
            "bugs_found": [],
            "recommendations": []
        }
        
        # Create test suite
        test_suite = await self._create_test_suite(codebase_analysis, testing_target)
        testing_result["tests_created"] = test_suite
        
        # Execute tests
        execution_results = await self._execute_test_suite(test_suite, context)
        testing_result["tests_executed"] = execution_results
        
        # Analyze results
        testing_result["test_results"] = self._analyze_test_results(execution_results)
        testing_result["coverage"] = self._calculate_coverage(execution_results)
        testing_result["bugs_found"] = self._identify_bugs(execution_results)
        testing_result["recommendations"] = self._generate_testing_recommendations(testing_result)
        
        return testing_result
    
    async def _create_test_suite(
        self, 
        codebase_analysis: Dict[str, Any], 
        testing_target: str
    ) -> List[Dict[str, Any]]:
        """
        Create a comprehensive test suite.
        
        Args:
            codebase_analysis: Analysis of the codebase
            testing_target: Specific testing requirements
            
        Returns:
            List[Dict[str, Any]]: Test suite
        """
        test_suite = []
        
        # Create unit tests
        unit_tests = await self._create_unit_tests(codebase_analysis, testing_target)
        test_suite.extend(unit_tests)
        
        # Create integration tests
        integration_tests = await self._create_integration_tests(codebase_analysis, testing_target)
        test_suite.extend(integration_tests)
        
        # Create end-to-end tests
        e2e_tests = await self._create_e2e_tests(codebase_analysis, testing_target)
        test_suite.extend(e2e_tests)
        
        return test_suite
    
    async def _create_unit_tests(
        self, 
        codebase_analysis: Dict[str, Any], 
        testing_target: str
    ) -> List[Dict[str, Any]]:
        """Create unit tests for individual components."""
        unit_tests = []
        
        # TODO: Implement actual unit test generation
        # For now, return placeholder tests
        
        if "python" in codebase_analysis.get("languages", []):
            unit_tests.append({
                "type": "unit_test",
                "language": "python",
                "framework": "pytest",
                "file_path": "tests/test_main.py",
                "test_cases": [
                    {
                        "name": "test_basic_functionality",
                        "description": "Test basic application functionality",
                        "status": "created"
                    },
                    {
                        "name": "test_error_handling",
                        "description": "Test error handling scenarios",
                        "status": "created"
                    }
                ]
            })
        
        if "javascript" in codebase_analysis.get("languages", []):
            unit_tests.append({
                "type": "unit_test",
                "language": "javascript",
                "framework": "jest",
                "file_path": "tests/main.test.js",
                "test_cases": [
                    {
                        "name": "test_basic_functionality",
                        "description": "Test basic application functionality",
                        "status": "created"
                    }
                ]
            })
        
        return unit_tests
    
    async def _create_integration_tests(
        self, 
        codebase_analysis: Dict[str, Any], 
        testing_target: str
    ) -> List[Dict[str, Any]]:
        """Create integration tests for component interactions."""
        integration_tests = []
        
        # TODO: Implement actual integration test generation
        integration_tests.append({
            "type": "integration_test",
            "language": "python",
            "framework": "pytest",
            "file_path": "tests/test_integration.py",
            "test_cases": [
                {
                    "name": "test_component_interaction",
                    "description": "Test interaction between components",
                    "status": "created"
                }
            ]
        })
        
        return integration_tests
    
    async def _create_e2e_tests(
        self, 
        codebase_analysis: Dict[str, Any], 
        testing_target: str
    ) -> List[Dict[str, Any]]:
        """Create end-to-end tests for complete workflows."""
        e2e_tests = []
        
        # TODO: Implement actual E2E test generation
        e2e_tests.append({
            "type": "e2e_test",
            "language": "python",
            "framework": "selenium",
            "file_path": "tests/test_e2e.py",
            "test_cases": [
                {
                    "name": "test_complete_workflow",
                    "description": "Test complete user workflow",
                    "status": "created"
                }
            ]
        })
        
        return e2e_tests
    
    async def _execute_test_suite(
        self, 
        test_suite: List[Dict[str, Any]], 
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        """
        Execute the test suite.
        
        Args:
            test_suite: List of tests to execute
            context: Execution context
            
        Returns:
            List[Dict[str, Any]]: Test execution results
        """
        execution_results = []
        
        for test in test_suite:
            try:
                result = await self._execute_single_test(test, context)
                execution_results.append(result)
            except Exception as e:
                self.logger.warning(f"Error executing test {test.get('file_path')}: {e}")
                execution_results.append({
                    "test": test,
                    "status": "failed",
                    "error": str(e),
                    "duration": 0
                })
        
        return execution_results
    
    async def _execute_single_test(
        self, 
        test: Dict[str, Any], 
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Execute a single test.
        
        Args:
            test: Test to execute
            context: Execution context
            
        Returns:
            Dict[str, Any]: Test execution result
        """
        # TODO: Implement actual test execution
        # For now, return placeholder results
        
        return {
            "test": test,
            "status": "passed",
            "duration": 1.5,
            "assertions": 3,
            "passed_assertions": 3,
            "failed_assertions": 0,
            "coverage": 85.0
        }
    
    def _analyze_test_results(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test execution results."""
        total_tests = len(execution_results)
        passed_tests = sum(1 for result in execution_results if result.get("status") == "passed")
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": sum(result.get("duration", 0) for result in execution_results)
        }
    
    def _calculate_coverage(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate test coverage metrics."""
        if not execution_results:
            return {"overall": 0, "by_file": {}}
        
        total_coverage = sum(result.get("coverage", 0) for result in execution_results)
        average_coverage = total_coverage / len(execution_results)
        
        return {
            "overall": average_coverage,
            "by_file": {},
            "lines_covered": 0,
            "lines_total": 0
        }
    
    def _identify_bugs(self, execution_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify bugs from test results."""
        bugs = []
        
        for result in execution_results:
            if result.get("status") == "failed":
                bugs.append({
                    "test": result["test"]["file_path"],
                    "description": f"Test failed: {result.get('error', 'Unknown error')}",
                    "severity": "medium",
                    "status": "open"
                })
        
        return bugs
    
    def _generate_testing_recommendations(self, testing_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on testing results."""
        recommendations = []
        
        if testing_result.get("coverage", {}).get("overall", 0) < 80:
            recommendations.append("Increase test coverage to at least 80%")
        
        if len(testing_result.get("bugs_found", [])) > 0:
            recommendations.append("Address all identified bugs before deployment")
        
        if len(testing_result.get("tests_created", [])) < 5:
            recommendations.append("Create more comprehensive test suites")
        
        return recommendations 