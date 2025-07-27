"""
Grand Architect Agent for Project Sentinel.

AI project manager that creates detailed, step-by-step execution plans
from optimized prompts provided by the Prompt Alchemist.
"""

from typing import Dict, Any, List, Optional
import json
from loguru import logger

from core.agent_base import BaseAgent, AgentRole, AgentContext, AgentResult, AgentStatus


class GrandArchitectAgent(BaseAgent):
    """
    Grand Architect - AI project manager and execution planner.
    
    Responsibilities:
    - Break down optimized prompts into granular, executable steps
    - Assign appropriate agent roles to each step
    - Define tool requirements and dependencies
    - Establish validation criteria for each step
    - Create logical execution sequences
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
        self.logger = logger.bind(agent="grand_architect")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the Grand Architect's behavior."""
        return """
        You are the Grand Architect, a specialized AI project manager for Project Sentinel.
        Your role is to create detailed, step-by-step execution plans that can be
        executed by a crew of specialized AI agents.
        
        Your expertise includes:
        1. **Task Breakdown**: Decompose complex objectives into manageable steps
        2. **Agent Assignment**: Match tasks to appropriate specialist agents
        3. **Dependency Management**: Establish logical execution sequences
        4. **Tool Requirements**: Identify necessary tools for each step
        5. **Validation Planning**: Define success criteria for each step
        
        Available Agent Roles:
        - senior_developer: Primary code builder and implementer
        - code_reviewer: Quality gatekeeper and code analyzer
        - qa_tester: Test creation and validation specialist
        - debugger: Crisis manager for error resolution
        - documentation: Technical writer and historian
        
        Available Tools:
        - file_io: Read and write files
        - shell_access: Execute shell commands
        - web_search: Search the internet for information
        - code_generation: Generate code snippets
        - code_analysis: Analyze existing code
        - static_analysis: Perform static code analysis
        - test_generation: Generate test cases
        - test_execution: Run tests
        - error_analysis: Analyze error messages
        - documentation_generation: Generate documentation
        
        Your output must be a detailed JSON execution plan that can be
        directly executed by the crew manager.
        """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the Grand Architect's planning process.
        
        Args:
            context: The execution context containing the optimized prompt
            
        Returns:
            AgentResult: The detailed execution plan
        """
        self.logger.info(f"Starting execution planning for mission {context.mission_id}")
        self.update_status(AgentStatus.WORKING)
        
        try:
            # Extract the optimized prompt from context
            optimized_prompt = context.user_prompt
            
            # Create detailed execution plan
            execution_plan = await self._create_execution_plan(optimized_prompt)
            
            # Create the result
            result = AgentResult(
                success=True,
                output=json.dumps(execution_plan, indent=2),
                metadata={
                    "plan_type": "execution_plan",
                    "steps_count": len(execution_plan.get("steps", [])),
                    "required_agents": execution_plan.get("required_agents", []),
                    "estimated_duration": execution_plan.get("estimated_duration", "unknown"),
                    "complexity": execution_plan.get("metadata", {}).get("complexity", "unknown")
                }
            )
            
            self.logger.info("Execution planning completed successfully")
            self.update_status(AgentStatus.COMPLETED)
            return result
            
        except Exception as e:
            self.logger.error(f"Execution planning failed: {e}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                success=False,
                output="",
                error=f"Execution planning failed: {str(e)}"
            )
    
    async def _create_execution_plan(self, optimized_prompt: str) -> Dict[str, Any]:
        """
        Create a detailed execution plan from the optimized prompt.
        
        Args:
            optimized_prompt: The optimized prompt from the Prompt Alchemist
            
        Returns:
            Dict[str, Any]: Detailed execution plan
        """
        self.logger.info("Creating detailed execution plan")
        
        # Create the planning prompt
        planning_prompt = f"""
        Optimized Prompt: {optimized_prompt}
        
        Please create a detailed execution plan for this optimized prompt.
        
        Provide your response in the following JSON format:
        {{
            "steps": [
                {{
                    "step_id": "step_1",
                    "agent_role": "senior_developer",
                    "task_description": "Detailed description of what this step should accomplish",
                    "required_tools": ["file_io", "shell_access"],
                    "dependencies": [],
                    "expected_output": "What this step should produce",
                    "validation_criteria": ["How to validate success"],
                    "estimated_duration": "5 minutes"
                }}
            ],
            "required_agents": ["senior_developer", "code_reviewer"],
            "estimated_duration": "30 minutes",
            "success_criteria": ["Overall success criteria"],
            "metadata": {{
                "complexity": "medium",
                "risk_level": "low",
                "priority": "normal"
            }}
        }}
        
        Guidelines:
        1. Break down the task into logical, sequential steps
        2. Assign appropriate agent roles based on task requirements
        3. Define clear dependencies between steps
        4. Specify required tools for each step
        5. Establish validation criteria for success
        6. Estimate realistic durations
        7. Consider error handling and recovery
        """
        
        # TODO: Implement actual LLM call
        # For now, return a placeholder execution plan
        return {
            "steps": [
                {
                    "step_id": "step_1",
                    "agent_role": "senior_developer",
                    "task_description": "Analyze the current codebase and implement the requested changes",
                    "required_tools": ["file_io", "shell_access", "web_search"],
                    "dependencies": [],
                    "expected_output": "Working implementation of the requested feature",
                    "validation_criteria": ["Code compiles without errors", "Basic functionality works"],
                    "estimated_duration": "15 minutes"
                },
                {
                    "step_id": "step_2",
                    "agent_role": "code_reviewer",
                    "task_description": "Review the implemented code for quality and best practices",
                    "required_tools": ["file_io", "code_analysis"],
                    "dependencies": ["step_1"],
                    "expected_output": "Code review report with suggestions",
                    "validation_criteria": ["No critical issues found", "Code follows style guidelines"],
                    "estimated_duration": "10 minutes"
                },
                {
                    "step_id": "step_3",
                    "agent_role": "qa_tester",
                    "task_description": "Create and run tests to validate the implementation",
                    "required_tools": ["file_io", "shell_access", "test_generation"],
                    "dependencies": ["step_2"],
                    "expected_output": "Test suite with passing tests",
                    "validation_criteria": ["All tests pass", "Coverage meets requirements"],
                    "estimated_duration": "10 minutes"
                },
                {
                    "step_id": "step_4",
                    "agent_role": "documentation",
                    "task_description": "Update documentation to reflect the changes",
                    "required_tools": ["file_io", "documentation_generation"],
                    "dependencies": ["step_3"],
                    "expected_output": "Updated README and documentation",
                    "validation_criteria": ["Documentation is clear and complete", "Examples are provided"],
                    "estimated_duration": "5 minutes"
                }
            ],
            "required_agents": ["senior_developer", "code_reviewer", "qa_tester", "documentation"],
            "estimated_duration": "40 minutes",
            "success_criteria": [
                "All requested features are implemented",
                "Code passes review and testing",
                "Documentation is updated",
                "No regressions introduced"
            ],
            "metadata": {
                "complexity": "medium",
                "risk_level": "low",
                "priority": "normal",
                "planning_method": "grand_architect"
            }
        }
    
    async def _analyze_task_complexity(self, prompt: str) -> str:
        """
        Analyze the complexity of the task.
        
        Args:
            prompt: The optimized prompt
            
        Returns:
            str: Complexity level (low, medium, high)
        """
        # TODO: Implement complexity analysis
        return "medium"
    
    async def _identify_required_agents(self, prompt: str) -> List[str]:
        """
        Identify which agents are required for the task.
        
        Args:
            prompt: The optimized prompt
            
        Returns:
            List[str]: List of required agent roles
        """
        # TODO: Implement agent requirement analysis
        return ["senior_developer", "code_reviewer", "qa_tester"]
    
    async def _estimate_duration(self, steps: List[Dict[str, Any]]) -> str:
        """
        Estimate the total duration for the execution plan.
        
        Args:
            steps: List of execution steps
            
        Returns:
            str: Estimated duration
        """
        # TODO: Implement duration estimation
        total_minutes = sum(
            int(step.get("estimated_duration", "5").split()[0])
            for step in steps
        )
        return f"{total_minutes} minutes"
    
    async def _validate_execution_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate the execution plan for completeness and consistency.
        
        Args:
            plan: The execution plan to validate
            
        Returns:
            bool: True if plan is valid
        """
        # Check required fields
        required_fields = ["steps", "required_agents", "estimated_duration"]
        for field in required_fields:
            if field not in plan:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Check steps
        if not plan["steps"]:
            self.logger.error("Execution plan has no steps")
            return False
        
        # Check step structure
        for step in plan["steps"]:
            required_step_fields = ["step_id", "agent_role", "task_description"]
            for field in required_step_fields:
                if field not in step:
                    self.logger.error(f"Step missing required field: {field}")
                    return False
        
        return True 