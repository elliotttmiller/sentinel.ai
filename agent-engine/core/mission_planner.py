"""
Mission Planner for Project Sentinel.

Implements the two-phase planning system:
1. Prompt Alchemist - Optimizes and clarifies user prompts
2. Grand Architect - Creates detailed execution plans
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass

from pydantic import BaseModel, Field
from loguru import logger

from .agent_base import AgentContext, AgentResult


@dataclass
class OptimizedPrompt:
    """Result of the Prompt Alchemist's optimization."""
    original_prompt: str
    optimized_prompt: str
    technical_context: Dict[str, Any]
    success_criteria: List[str]
    constraints: List[str]
    assumptions: List[str]


class ExecutionStep(BaseModel):
    """A single step in the execution plan."""
    step_id: str = Field(description="Unique identifier for this step")
    agent_role: str = Field(description="Which agent should execute this step")
    task_description: str = Field(description="What this step should accomplish")
    required_tools: List[str] = Field(default_factory=list, description="Tools needed for this step")
    dependencies: List[str] = Field(default_factory=list, description="Steps that must complete first")
    expected_output: str = Field(description="What this step should produce")
    validation_criteria: List[str] = Field(default_factory=list, description="How to validate success")


class ExecutionPlan(BaseModel):
    """Complete execution plan for a mission."""
    mission_id: str = Field(description="Unique mission identifier")
    original_prompt: str = Field(description="User's original request")
    optimized_prompt: str = Field(description="Clarified and enhanced prompt")
    steps: List[ExecutionStep] = Field(description="Ordered list of execution steps")
    required_agents: List[str] = Field(description="List of agent roles needed")
    estimated_duration: str = Field(description="Estimated time to completion")
    success_criteria: List[str] = Field(description="Overall success criteria")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional plan metadata")


class MissionPlanner:
    """
    Coordinates the two-phase planning process.
    
    Phase 1: Prompt Alchemist optimizes the user's request
    Phase 2: Grand Architect creates detailed execution plan
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.logger = logger.bind(component="mission_planner")
        
    async def create_mission_plan(self, user_prompt: str, mission_id: str) -> ExecutionPlan:
        """
        Create a complete mission plan from user prompt.
        
        Args:
            user_prompt: The user's original request
            mission_id: Unique identifier for this mission
            
        Returns:
            ExecutionPlan: Complete execution plan
        """
        self.logger.info(f"Creating mission plan for: {mission_id}")
        
        # Phase 1: Optimize the prompt
        optimized_prompt = await self._optimize_prompt(user_prompt)
        
        # Phase 2: Create execution plan
        execution_plan = await self._create_execution_plan(
            optimized_prompt, mission_id
        )
        
        self.logger.info(f"Mission plan created with {len(execution_plan.steps)} steps")
        return execution_plan
    
    async def _optimize_prompt(self, user_prompt: str) -> OptimizedPrompt:
        """
        Phase 1: Optimize and clarify the user's prompt.
        
        This is the "Prompt Alchemist" phase that:
        - Analyzes the prompt for ambiguity
        - Adds necessary technical context
        - Defines clear success criteria
        - Rewrites into detailed instructions
        """
        self.logger.info("Starting prompt optimization phase")
        
        prompt_alchemist_system = """
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
        
        optimization_prompt = f"""
        Original User Prompt: {user_prompt}
        
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
        
        # TODO: Implement actual LLM call
        # For now, return a placeholder optimization
        return OptimizedPrompt(
            original_prompt=user_prompt,
            optimized_prompt=f"Enhanced version of: {user_prompt}",
            technical_context={
                "programming_languages": ["python", "javascript"],
                "frameworks": ["fastapi", "react"],
                "file_types": ["py", "js", "json"],
                "external_apis": []
            },
            success_criteria=["Task completed successfully", "Code is functional"],
            constraints=["Must work on local environment", "Must be well-documented"],
            assumptions=["User has Python installed", "User has Git configured"]
        )
    
    async def _create_execution_plan(
        self, optimized_prompt: OptimizedPrompt, mission_id: str
    ) -> ExecutionPlan:
        """
        Phase 2: Create detailed execution plan.
        
        This is the "Grand Architect" phase that:
        - Breaks down the optimized prompt into granular steps
        - Defines which agents are needed for each step
        - Creates a detailed JSON execution blueprint
        - Establishes dependencies and validation criteria
        """
        self.logger.info("Starting execution plan creation phase")
        
        grand_architect_system = """
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
        
        planning_prompt = f"""
        Optimized Prompt: {optimized_prompt.optimized_prompt}
        Technical Context: {json.dumps(optimized_prompt.technical_context, indent=2)}
        Success Criteria: {json.dumps(optimized_prompt.success_criteria, indent=2)}
        Constraints: {json.dumps(optimized_prompt.constraints, indent=2)}
        
        Please create a detailed execution plan. Provide your response in the following JSON format:
        {{
            "steps": [
                {{
                    "step_id": "step_1",
                    "agent_role": "senior_developer",
                    "task_description": "Detailed description of what this step should accomplish",
                    "required_tools": ["file_io", "shell_access"],
                    "dependencies": [],
                    "expected_output": "What this step should produce",
                    "validation_criteria": ["How to validate success"]
                }}
            ],
            "required_agents": ["senior_developer", "code_reviewer"],
            "estimated_duration": "30 minutes",
            "success_criteria": ["Overall success criteria"],
            "metadata": {{
                "complexity": "medium",
                "risk_level": "low"
            }}
        }}
        """
        
        # TODO: Implement actual LLM call
        # For now, return a placeholder execution plan
        steps = [
            ExecutionStep(
                step_id="step_1",
                agent_role="senior_developer",
                task_description="Analyze the current codebase and implement the requested changes",
                required_tools=["file_io", "shell_access", "web_search"],
                dependencies=[],
                expected_output="Working implementation of the requested feature",
                validation_criteria=["Code compiles without errors", "Basic functionality works"]
            ),
            ExecutionStep(
                step_id="step_2",
                agent_role="code_reviewer",
                task_description="Review the implemented code for quality and best practices",
                required_tools=["file_io"],
                dependencies=["step_1"],
                expected_output="Code review report with suggestions",
                validation_criteria=["No critical issues found", "Code follows style guidelines"]
            ),
            ExecutionStep(
                step_id="step_3",
                agent_role="qa_tester",
                task_description="Create and run tests to validate the implementation",
                required_tools=["file_io", "shell_access"],
                dependencies=["step_2"],
                expected_output="Test suite with passing tests",
                validation_criteria=["All tests pass", "Coverage meets requirements"]
            )
        ]
        
        return ExecutionPlan(
            mission_id=mission_id,
            original_prompt=optimized_prompt.original_prompt,
            optimized_prompt=optimized_prompt.optimized_prompt,
            steps=steps,
            required_agents=["senior_developer", "code_reviewer", "qa_tester"],
            estimated_duration="45 minutes",
            success_criteria=optimized_prompt.success_criteria,
            metadata={
                "complexity": "medium",
                "risk_level": "low",
                "optimization_metadata": {
                    "technical_context": optimized_prompt.technical_context,
                    "constraints": optimized_prompt.constraints,
                    "assumptions": optimized_prompt.assumptions
                }
            }
        )
    
    def validate_execution_plan(self, plan: ExecutionPlan) -> bool:
        """
        Validate the execution plan for completeness and consistency.
        
        Args:
            plan: The execution plan to validate
            
        Returns:
            bool: True if plan is valid
        """
        if not plan.steps:
            self.logger.error("Execution plan has no steps")
            return False
        
        # Check for circular dependencies
        step_ids = {step.step_id for step in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    self.logger.error(f"Step {step.step_id} depends on non-existent step {dep}")
                    return False
        
        # Check that required agents are actually used
        used_agents = {step.agent_role for step in plan.steps}
        for agent in plan.required_agents:
            if agent not in used_agents:
                self.logger.warning(f"Required agent {agent} not used in any step")
        
        return True 