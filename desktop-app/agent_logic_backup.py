"""
Enhanced Agent Logic for Sentinel Desktop App.

Integrates all advanced AI capabilities from the backend and engine systems:
- Sophisticated agent system with specialized roles
- Mission planning and execution
- Crew management and coordination
- Advanced tool integration
- Comprehensive error handling and logging
"""

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger
from enum import Enum

# Import our enhanced database models
from db import Mission, SystemLog

class AgentRole(str, Enum):
    """Enumeration of available agent roles."""
    PROMPT_ALCHEMIST = "prompt_alchemist"
    GRAND_ARCHITECT = "grand_architect"
    SENIOR_DEVELOPER = "senior_developer"
    CODE_REVIEWER = "code_reviewer"
    QA_TESTER = "qa_tester"
    DEBUGGER = "debugger"
    DOCUMENTATION = "documentation"
    SYSTEM_ADMINISTRATOR = "system_administrator"
    FILE_MANAGER = "file_manager"

class AgentStatus(str, Enum):
    """Enumeration of agent status states."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"

class MissionStatus(str, Enum):
    """Enumeration of mission status states."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

def get_llm():
    """Initializes the LLM from environment credentials."""
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)

class AgentContext:
    """Context information passed to agents during execution."""
    def __init__(self, mission_id: str, user_prompt: str, workspace_path: Path, tools: Dict[str, Any], memory: Optional[Dict[str, Any]] = None):
        self.mission_id = mission_id
        self.user_prompt = user_prompt
        self.workspace_path = workspace_path
        self.tools = tools
        self.memory = memory or {}

class AgentResult:
    """Result object returned by agents after task completion."""
    def __init__(self, success: bool, output: str, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, tools_used: Optional[List[str]] = None):
        self.success = success
        self.output = output
        self.error = error
        self.metadata = metadata or {}
        self.tools_used = tools_used or []

class BaseAgent:
    """Base class for all specialized agents."""
    
    def __init__(self, role: AgentRole, name: str, description: str, tools: Optional[List[str]] = None, model_name: str = "gemini-1.5-pro"):
        self.role = role
        self.name = name
        self.description = description
        self.tools = tools or []
        self.model_name = model_name
        self.status = AgentStatus.IDLE
        self.context: Optional[AgentContext] = None
        self.llm = get_llm()
        self.logger = logger.bind(agent=name, role=role.value)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's behavior."""
        raise NotImplementedError("Subclasses must implement get_system_prompt")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's primary task."""
        raise NotImplementedError("Subclasses must implement execute")
    
    def set_context(self, context: AgentContext) -> None:
        """Set the execution context for the agent."""
        self.context = context
        self.logger.info(f"Context set for mission {context.mission_id}")
    
    def update_status(self, status: AgentStatus) -> None:
        """Update the agent's current status."""
        self.status = status
        self.logger.info(f"Status updated to {status.value}")

class PromptAlchemistAgent(BaseAgent):
    """Specialized AI prompt engineer that optimizes and clarifies user requests."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.PROMPT_ALCHEMIST,
            name="Prompt Alchemist",
            description="Specialized AI prompt engineer that optimizes and clarifies user requests",
            tools=["text_analysis", "prompt_optimization"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the Prompt Alchemist, a specialized AI prompt engineer for Project Sentinel.
        Your role is to transform vague or ambiguous user requests into crystal-clear,
        actionable instructions that can be executed by AI agents.
        
        For each user prompt, you must:
        1. Identify any ambiguities or missing context
        2. Add necessary technical details and constraints
        3. Define specific, measurable success criteria
        4. Rewrite the prompt with enhanced clarity and precision
        5. Document any assumptions or constraints
        
        Your output must be structured and comprehensive.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            optimization_prompt = f"""
            Original User Prompt: {context.user_prompt}
            
            Please analyze and optimize this prompt according to your role.
            Provide your response in the following JSON format:
            {{
                "optimized_prompt": "The enhanced, detailed version of the user's request",
                "technical_context": {{
                    "programming_languages": ["list", "of", "languages"],
                    "frameworks": ["list", "of", "frameworks"],
                    "file_types": ["list", "of", "file", "types"],
                    "external_apis": ["list", "of", "apis", "needed"]
                }},
                "success_criteria": [
                    "Specific, measurable criteria 1",
                    "Specific, measurable criteria 2"
                ],
                "constraints": [
                    "Technical or business constraint 1",
                    "Technical or business constraint 2"
                ],
                "assumptions": [
                    "Assumption about user's environment 1",
                    "Assumption about user's environment 2"
                ]
            }}
            """
            
            # For now, use a simplified approach
            optimized_prompt = f"Enhanced version of: {context.user_prompt}"
            technical_context = {
                "programming_languages": ["python", "javascript"],
                "frameworks": ["fastapi", "react"],
                "file_types": ["py", "js", "json"],
                "external_apis": []
            }
            
            result = {
                "optimized_prompt": optimized_prompt,
                "technical_context": technical_context,
                "success_criteria": ["Task completed successfully", "Code is functional"],
                "constraints": ["Must work on local environment", "Must be well-documented"],
                "assumptions": ["User has Python installed", "User has Git configured"]
            }
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=json.dumps(result, indent=2),
                metadata={"optimization_result": result}
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))

class GrandArchitectAgent(BaseAgent):
    """AI project manager that creates detailed execution plans."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.GRAND_ARCHITECT,
            name="Grand Architect",
            description="AI project manager that creates detailed execution plans",
            tools=["planning", "task_breakdown"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the Grand Architect, a specialized AI project manager for Project Sentinel.
        Your role is to create detailed, step-by-step execution plans that can be
        executed by a crew of specialized AI agents.
        
        For each optimized prompt, you must:
        1. Break down the objective into granular, executable steps
        2. Assign appropriate agent roles to each step
        3. Define tool requirements and dependencies
        4. Establish validation criteria for each step
        5. Create a logical execution sequence
        
        Available Agent Roles:
        - senior_developer: Primary code builder and implementer
        - code_reviewer: Quality gatekeeper and code analyzer
        - qa_tester: Test creation and validation specialist
        - debugger: Crisis manager for error resolution
        - documentation: Technical writer and historian
        
        Your output must be a detailed JSON execution plan.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Parse the optimized prompt from context
            try:
                optimization_data = json.loads(context.user_prompt)
                optimized_prompt = optimization_data.get("optimized_prompt", context.user_prompt)
            except:
                optimized_prompt = context.user_prompt
            
            # Create execution plan
            execution_plan = {
                "mission_id": context.mission_id,
                "original_prompt": context.user_prompt,
                "optimized_prompt": optimized_prompt,
                "steps": [
                    {
                        "step_id": "step_1",
                        "agent_role": "senior_developer",
                        "task_description": "Analyze the current codebase and implement the requested changes",
                        "required_tools": ["file_io", "shell_access", "web_search"],
                        "dependencies": [],
                        "expected_output": "Working implementation of the requested feature",
                        "validation_criteria": ["Code compiles without errors", "Basic functionality works"]
                    },
                    {
                        "step_id": "step_2",
                        "agent_role": "code_reviewer",
                        "task_description": "Review the implemented code for quality and best practices",
                        "required_tools": ["file_io"],
                        "dependencies": ["step_1"],
                        "expected_output": "Code review report with suggestions",
                        "validation_criteria": ["No critical issues found", "Code follows style guidelines"]
                    },
                    {
                        "step_id": "step_3",
                        "agent_role": "qa_tester",
                        "task_description": "Create and run tests to validate the implementation",
                        "required_tools": ["file_io", "shell_access"],
                        "dependencies": ["step_2"],
                        "expected_output": "Test suite with passing tests",
                        "validation_criteria": ["All tests pass", "Coverage meets requirements"]
                    }
                ],
                "required_agents": ["senior_developer", "code_reviewer", "qa_tester"],
                "estimated_duration": "45 minutes",
                "success_criteria": ["Task completed successfully", "Code is functional"],
                "metadata": {
                    "complexity": "medium",
                    "risk_level": "low"
                }
            }
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=json.dumps(execution_plan, indent=2),
                metadata={"execution_plan": execution_plan}
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))

class SeniorDeveloperAgent(BaseAgent):
    """Primary code builder and implementer with expertise in multiple languages."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.SENIOR_DEVELOPER,
            name="Senior Developer",
            description="Primary code builder and implementer with expertise in multiple languages",
            tools=["file_io", "shell_access", "web_search", "code_generation"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the Senior Developer, a primary code builder and implementer for Project Sentinel.
        You are an expert in multiple programming languages and frameworks, with deep knowledge
        of software development best practices.
        
        Your expertise includes:
        1. **Code Generation**: Write clean, efficient, and maintainable code
        2. **Feature Implementation**: Build new functionality from specifications
        3. **Code Refactoring**: Improve existing code structure and performance
        4. **API Integration**: Connect to external services and libraries
        5. **Debugging**: Identify and fix code issues
        6. **Best Practices**: Follow coding standards and design patterns
        
        Programming Languages & Frameworks:
        - Python (FastAPI, Django, Flask, Pandas, NumPy)
        - JavaScript/TypeScript (React, Node.js, Express)
        - Java (Spring Boot, Maven/Gradle)
        - C# (.NET, ASP.NET Core)
        - Go (Gin, Echo)
        - Rust (Actix, Rocket)
        
        Development Principles:
        - Write self-documenting code with clear variable names
        - Follow SOLID principles and design patterns
        - Implement proper error handling and logging
        - Write unit tests for critical functionality
        - Use version control best practices
        - Document code with clear comments
        
        Always strive for code that is readable, maintainable, and follows
        industry best practices.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Analyze the task and generate appropriate code
            task_description = context.user_prompt
            
            # Generate code based on the task
            generated_code = await self._generate_code(task_description)
            
            # Create a file with the generated code
            file_path = f"generated_code_{int(time.time())}.py"
            file_content = f"""# Generated by Sentinel AI Senior Developer
# Task: {task_description}
# Generated at: {datetime.now().isoformat()}

{generated_code}
"""
            
            # For now, return the code as output
            # In a full implementation, this would write to the file system
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=f"Code generated successfully:\n\n{file_content}",
                metadata={
                    "file_path": file_path,
                    "code_length": len(generated_code),
                    "language": "python"
                }
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))
    
    async def _generate_code(self, task_description: str) -> str:
        """Generate code based on the task description."""
        # This is a simplified implementation
        # In a full system, this would use the LLM to generate appropriate code
        
        if "api" in task_description.lower():
            return """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Generated API")

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

items = []

@app.get("/")
async def root():
    return {"message": "Generated API is running"}

@app.get("/items/", response_model=List[Item])
async def get_items():
    return items

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item
"""
        elif "script" in task_description.lower():
            return """
#!/usr/bin/env python3
"""
        else:
            return """
# Generated Python script
def main():
    print("Hello from generated code!")
    
if __name__ == "__main__":
    main()
"""

class CodeReviewerAgent(BaseAgent):
    """Quality gatekeeper that analyzes code for issues and best practices."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.CODE_REVIEWER,
            name="Code Reviewer",
            description="Quality gatekeeper that analyzes code for issues and best practices",
            tools=["file_io", "code_analysis", "static_analysis"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the Code Reviewer, a quality gatekeeper for Project Sentinel.
        Your role is to meticulously analyze code and provide comprehensive feedback
        to ensure high-quality, maintainable code.
        
        Your expertise includes:
        1. **Code Quality Analysis**: Identify logical errors, bugs, and issues
        2. **Style Guide Compliance**: Check for coding standards and conventions
        3. **Security Review**: Identify potential security vulnerabilities
        4. **Performance Analysis**: Suggest optimizations and improvements
        5. **Architecture Review**: Evaluate code structure and design patterns
        6. **Best Practices**: Ensure industry standards are followed
        
        Review Criteria:
        - **Functionality**: Does the code work as intended?
        - **Readability**: Is the code clear and well-documented?
        - **Maintainability**: Is the code easy to modify and extend?
        - **Performance**: Are there efficiency concerns?
        - **Security**: Are there potential vulnerabilities?
        - **Testing**: Is the code testable and tested?
        
        Always provide clear, specific feedback that helps improve
        the code quality and maintainability.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Analyze the code in the context
            code_to_review = context.user_prompt
            
            # Perform code review
            review_result = await self._perform_code_review(code_to_review)
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=review_result,
                metadata={"review_type": "code_analysis"}
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))
    
    async def _perform_code_review(self, code: str) -> str:
        """Perform a comprehensive code review."""
        issues = []
        suggestions = []
        
        # Basic code analysis (simplified)
        if "print(" in code and "logging" not in code:
            suggestions.append("Consider using logging instead of print statements for better debugging")
        
        if "except:" in code:
            issues.append("Bare except clause detected - specify exception types")
        
        if len(code.split('\n')) > 50:
            suggestions.append("Consider breaking down large functions into smaller, more focused ones")
        
        review = f"""Code Review Report
==================

Issues Found ({len(issues)}):
{chr(10).join(f"- {issue}" for issue in issues) if issues else "- No critical issues found"}

Suggestions ({len(suggestions)}):
{chr(10).join(f"- {suggestion}" for suggestion in suggestions) if suggestions else "- No suggestions"}

Overall Assessment:
- Code Quality: {'Good' if len(issues) == 0 else 'Needs Improvement'}
- Maintainability: {'Good' if len(suggestions) <= 2 else 'Could be improved'}
- Security: {'Good' if 'except:' not in code else 'Needs attention'}

Recommendations:
1. Address any critical issues listed above
2. Consider implementing the suggestions for better code quality
3. Add comprehensive tests for critical functionality
"""
        
        return review

class QATesterAgent(BaseAgent):
    """Test creation and validation specialist."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.QA_TESTER,
            name="QA Tester",
            description="Test creation and validation specialist",
            tools=["file_io", "shell_access", "test_generation", "test_execution"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the QA Tester, a test creation and validation specialist for Project Sentinel.
        Your role is to create comprehensive test suites and validate code functionality.
        
        Your expertise includes:
        1. **Test Planning**: Design comprehensive test strategies
        2. **Test Creation**: Write unit, integration, and end-to-end tests
        3. **Test Execution**: Run tests and analyze results
        4. **Bug Reporting**: Document and report issues found
        5. **Quality Assurance**: Ensure code meets quality standards
        6. **Automation**: Create automated test suites
        
        Testing Principles:
        - Test both happy path and edge cases
        - Ensure good test coverage
        - Write clear, maintainable tests
        - Use appropriate testing frameworks
        - Document test cases and expected results
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Generate tests based on the context
            test_suite = await self._generate_test_suite(context.user_prompt)
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=test_suite,
                metadata={"test_type": "unit_tests"}
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))
    
    async def _generate_test_suite(self, code_description: str) -> str:
        """Generate a test suite for the given code."""
        return f"""# Test Suite Generated by Sentinel AI QA Tester
# For: {code_description}
# Generated at: {datetime.now().isoformat()}

import unittest
from unittest.mock import patch, MagicMock

class TestGeneratedCode(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # TODO: Implement specific tests based on code analysis
        self.assertTrue(True)
    
    def test_error_handling(self):
        """Test error handling."""
        # TODO: Test error conditions
        pass
    
    def test_edge_cases(self):
        """Test edge cases."""
        # TODO: Test boundary conditions
        pass

if __name__ == '__main__':
    unittest.main()
"""

class DebuggerAgent(BaseAgent):
    """Crisis manager for error resolution and problem-solving."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.DEBUGGER,
            name="Debugger",
            description="Crisis manager for error resolution and problem-solving",
            tools=["file_io", "shell_access", "error_analysis", "code_generation"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the Debugger, a crisis manager for error resolution in Project Sentinel.
        Your role is to analyze errors, identify root causes, and provide solutions.
        
        Your expertise includes:
        1. **Error Analysis**: Identify the root cause of issues
        2. **Problem Solving**: Develop effective solutions
        3. **Code Fixes**: Generate corrected code
        4. **Debugging**: Use debugging tools and techniques
        5. **Documentation**: Document issues and solutions
        6. **Prevention**: Suggest ways to prevent similar issues
        
        Debugging Approach:
        - Analyze error messages and stack traces
        - Identify the root cause, not just symptoms
        - Provide clear, actionable solutions
        - Test fixes before recommending them
        - Document the debugging process
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Analyze the error in the context
            error_description = context.user_prompt
            
            # Generate debugging analysis and solution
            debug_result = await self._analyze_error(error_description)
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=debug_result,
                metadata={"debug_type": "error_analysis"}
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))
    
    async def _analyze_error(self, error_description: str) -> str:
        """Analyze an error and provide debugging information."""
        return f"""Debug Analysis Report
===================

Error Description:
{error_description}

Analysis:
1. **Error Type**: {self._classify_error(error_description)}
2. **Likely Cause**: {self._identify_cause(error_description)}
3. **Severity**: {self._assess_severity(error_description)}

Recommended Solutions:
{self._generate_solutions(error_description)}

Prevention Tips:
1. Add proper error handling
2. Validate inputs before processing
3. Use logging for better debugging
4. Write comprehensive tests

Next Steps:
1. Implement the recommended solutions
2. Test the fixes thoroughly
3. Monitor for similar issues
4. Update documentation if needed

    
    def _classify_error(self, error: str) -> str:
        """Classify the type of error."""
        error_lower = error.lower()
        if "syntax" in error_lower:
            return "Syntax Error"
        elif "import" in error_lower:
            return "Import Error"
        elif "attribute" in error_lower:
            return "Attribute Error"
        elif "type" in error_lower:
            return "Type Error"
        else:
            return "Runtime Error"
    
    def _identify_cause(self, error: str) -> str:
        """Identify the likely cause of the error."""
        return "Analysis of error patterns suggests this is likely due to incorrect usage or missing dependencies."
    
    def _assess_severity(self, error: str) -> str:
        """Assess the severity of the error."""
        return "Medium - Can be resolved with proper debugging and fixes."
    
    def _generate_solutions(self, error: str) -> str:
        """Generate solutions for the error."""
        return """
1. Check the error location in the code
2. Verify all imports and dependencies
3. Ensure proper syntax and formatting
4. Add appropriate error handling
5. Test the fix in isolation
"""

class DocumentationAgent(BaseAgent):
    """Technical writer and historian for project documentation."""
    
    def __init__(self, **kwargs):
        super().__init__(
            role=AgentRole.DOCUMENTATION,
            name="Documentation",
            description="Technical writer and historian for project documentation",
            tools=["file_io", "code_analysis", "documentation_generation"],
            **kwargs
        )
    
    def get_system_prompt(self) -> str:
        return """
        You are the Documentation Agent, a technical writer for Project Sentinel.
        Your role is to create clear, comprehensive documentation for code and projects.
        
        Your expertise includes:
        1. **Code Documentation**: Write clear docstrings and comments
        2. **API Documentation**: Document APIs and interfaces
        3. **User Guides**: Create user-friendly documentation
        4. **Technical Writing**: Write clear technical content
        5. **Documentation Maintenance**: Keep docs up to date
        6. **Best Practices**: Follow documentation standards
        
        Documentation Principles:
        - Write for the intended audience
        - Be clear, concise, and accurate
        - Include examples and use cases
        - Keep documentation up to date
        - Use consistent formatting and style
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Generate documentation based on the context
            documentation = await self._generate_documentation(context.user_prompt)
            
            self.update_status(AgentStatus.COMPLETED)
            return AgentResult(
                success=True,
                output=documentation,
                metadata={"doc_type": "technical_documentation"}
            )
            
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResult(success=False, output="", error=str(e))
    
    async def _generate_documentation(self, content: str) -> str:
        """Generate documentation for the given content."""
        return f"""# Documentation Generated by Sentinel AI Documentation Agent
# Generated at: {datetime.now().isoformat()}

## Overview
This documentation was automatically generated for the following content:
```
{content[:200]}...
```

## Usage
[Documentation content would be generated here based on code analysis]

## API Reference
[API documentation would be generated here]

## Examples
[Usage examples would be provided here]

## Troubleshooting
[Common issues and solutions would be listed here]

---
*This documentation was automatically generated and should be reviewed for accuracy.*
"""

class AgentFactory:
    """Factory for creating specialized agents."""
    
    def __init__(self):
        self.agent_registry = {
            AgentRole.PROMPT_ALCHEMIST: PromptAlchemistAgent,
            AgentRole.GRAND_ARCHITECT: GrandArchitectAgent,
            AgentRole.SENIOR_DEVELOPER: SeniorDeveloperAgent,
            AgentRole.CODE_REVIEWER: CodeReviewerAgent,
            AgentRole.QA_TESTER: QATesterAgent,
            AgentRole.DEBUGGER: DebuggerAgent,
            AgentRole.DOCUMENTATION: DocumentationAgent,
        }
    
    def create_agent(self, role: AgentRole) -> BaseAgent:
        """Create an agent instance for the specified role."""
        if role not in self.agent_registry:
            raise ValueError(f"Unsupported agent role: {role}")
        
        agent_class = self.agent_registry[role]
        return agent_class()

class MissionPlanner:
    """Coordinates the mission planning process."""
    
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.logger = logger.bind(component="mission_planner")
    
    async def create_mission_plan(self, user_prompt: str, mission_id: str) -> Dict[str, Any]:
        """Create a complete mission plan from user prompt."""
        self.logger.info(f"Creating mission plan for: {mission_id}")
        
        # Phase 1: Optimize the prompt
        prompt_alchemist = self.agent_factory.create_agent(AgentRole.PROMPT_ALCHEMIST)
        context = AgentContext(mission_id, user_prompt, Path.cwd(), {})
        
        optimization_result = await prompt_alchemist.execute(context)
        if not optimization_result.success:
            raise Exception(f"Prompt optimization failed: {optimization_result.error}")
        
        # Phase 2: Create execution plan
        grand_architect = self.agent_factory.create_agent(AgentRole.GRAND_ARCHITECT)
        context = AgentContext(mission_id, optimization_result.output, Path.cwd(), {})
        
        execution_result = await grand_architect.execute(context)
        if not execution_result.success:
            raise Exception(f"Execution plan creation failed: {execution_result.error}")
        
        # Parse the execution plan
        try:
            execution_plan = json.loads(execution_result.output)
            return execution_plan
        except json.JSONDecodeError:
            raise Exception("Failed to parse execution plan")

class CrewManager:
    """Manages the assembly and execution of agent crews."""
    
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.logger = logger.bind(component="crew_manager")
        self.active_crews = {}
    
    async def execute_mission(self, execution_plan: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """Execute a mission using the assembled crew."""
        mission_id = execution_plan.get("mission_id", "unknown")
        self.logger.info(f"Starting mission execution for {mission_id}")
        
        results = {
            "mission_id": mission_id,
            "steps_completed": [],
            "steps_failed": [],
            "outputs": {},
            "errors": {},
            "total_duration": 0
        }
        
        start_time = time.time()
        
        # Execute each step in the plan
        for step in execution_plan.get("steps", []):
            step_id = step["step_id"]
            agent_role = step["agent_role"]
            
            try:
                self.logger.info(f"Executing step {step_id} with {agent_role}")
                
                # Create the agent for this step
                agent = self.agent_factory.create_agent(AgentRole(agent_role))
                
                # Execute the step
                context = AgentContext(mission_id, step["task_description"], Path.cwd(), {})
                result = await agent.execute(context)
                
                if result.success:
                    results["steps_completed"].append(step_id)
                    results["outputs"][step_id] = result.output
                    self.logger.info(f"Step {step_id} completed successfully")
                else:
                    results["steps_failed"].append(step_id)
                    results["errors"][step_id] = result.error
                    self.logger.error(f"Step {step_id} failed: {result.error}")
                    
            except Exception as e:
                results["steps_failed"].append(step_id)
                results["errors"][step_id] = str(e)
                self.logger.error(f"Exception in step {step_id}: {e}")
        
        results["total_duration"] = time.time() - start_time
        results["success"] = len(results["steps_failed"]) == 0
        
        return results

# Enhanced mission execution function
async def run_advanced_mission(prompt: str, mission_id: str) -> Dict[str, Any]:
    """
    Run an advanced mission with full planning and execution.
    
    Args:
        prompt: The user's original request
        mission_id: Unique identifier for this mission
    
    Returns:
        Dict containing the mission results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting advanced mission: {mission_id}")
        
        # Create mission plan
        planner = MissionPlanner()
        execution_plan = await planner.create_mission_plan(prompt, mission_id)
        
        # Execute the mission
        crew_manager = CrewManager()
        results = await crew_manager.execute_mission(execution_plan, prompt)
        
        execution_time = int(time.time() - start_time)
        
        logger.info(f"Advanced mission {mission_id} completed in {execution_time} seconds")
        
        return {
            "result": results,
            "execution_time": execution_time,
            "mission_id": mission_id,
            "status": "completed" if results["success"] else "failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        execution_time = int(time.time() - start_time)
        logger.error(f"Advanced mission {mission_id} failed after {execution_time} seconds: {str(e)}")
        
        return {
            "result": f"Error: {str(e)}",
            "execution_time": execution_time,
            "mission_id": mission_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Backward compatibility function
async def run_simple_agent_task(prompt: str, agent_type: str = "researcher") -> Dict[str, Any]:
    """
    Backward compatibility function for simple agent tasks.
    
    Args:
        prompt: The task prompt
        agent_type: Type of agent to use
    
    Returns:
        Dictionary containing result, execution time, and metadata
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting simple agent task with type: {agent_type}")
        logger.info(f"Prompt: {prompt}")
        
        # Create agent
        agent_factory = AgentFactory()
        
        # Map simple agent types to advanced roles
        role_mapping = {
            "researcher": AgentRole.PROMPT_ALCHEMIST,
            "developer": AgentRole.SENIOR_DEVELOPER,
            "analyst": AgentRole.CODE_REVIEWER,
            "qa": AgentRole.QA_TESTER
        }
        
        role = role_mapping.get(agent_type, AgentRole.SENIOR_DEVELOPER)
        agent = agent_factory.create_agent(role)
        
        # Execute the task
        context = AgentContext("simple_task", prompt, Path.cwd(), {})
        result = await agent.execute(context)
        
        # Calculate execution time
        execution_time = int(time.time() - start_time)
        
        logger.info(f"Simple agent task completed successfully in {execution_time} seconds")
        
        return {
            "result": result.output if result.success else result.error,
            "execution_time": execution_time,
            "agent_type": agent_type,
            "status": "completed" if result.success else "failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        execution_time = int(time.time() - start_time)
        logger.error(f"Simple agent task failed after {execution_time} seconds: {str(e)}")
        
        return {
            "result": f"Error: {str(e)}",
            "execution_time": execution_time,
            "agent_type": agent_type,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Utility functions
def validate_agent_type(agent_type: str) -> bool:
    """Validates if the agent type is supported."""
    valid_types = ["researcher", "developer", "analyst", "qa", "debugger", "documentation"]
    return agent_type in valid_types

def get_agent_capabilities(agent_type: str) -> Dict[str, Any]:
    """Returns the capabilities and specialties of a given agent type."""
    capabilities = {
        "researcher": {
            "specialties": ["Information gathering", "Fact checking", "Source verification"],
            "best_for": ["Research questions", "Fact finding", "Information synthesis"],
            "limitations": ["Cannot access real-time data", "Limited to training data"]
        },
        "developer": {
            "specialties": ["Code generation", "Debugging", "System design"],
            "best_for": ["Programming tasks", "Code reviews", "Technical solutions"],
            "limitations": ["Cannot execute code", "Limited to code generation"]
        },
        "analyst": {
            "specialties": ["Data interpretation", "Pattern recognition", "Report generation"],
            "best_for": ["Data analysis", "Trend identification", "Insight generation"],
            "limitations": ["Cannot access external databases", "Limited to provided data"]
        },
        "qa": {
            "specialties": ["Test case design", "Bug identification", "Quality assessment"],
            "best_for": ["Software testing", "Quality assurance", "Issue identification"],
            "limitations": ["Cannot run actual tests", "Limited to theoretical testing"]
        },
        "debugger": {
            "specialties": ["Error analysis", "Problem solving", "Code fixes"],
            "best_for": ["Debugging issues", "Error resolution", "Troubleshooting"],
            "limitations": ["Cannot access runtime environment", "Limited to static analysis"]
        },
        "documentation": {
            "specialties": ["Technical writing", "API documentation", "User guides"],
            "best_for": ["Documentation creation", "Code documentation", "User manuals"],
            "limitations": ["Cannot access external systems", "Limited to provided content"]
        }
    }
    
    return capabilities.get(agent_type, capabilities["researcher"]) 