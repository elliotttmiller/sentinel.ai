"""
Crew Manager for Project Sentinel.

Dynamically assembles and coordinates agent crews based on execution plans.
Handles agent instantiation, task assignment, and execution coordination.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field
from loguru import logger

from .agent_base import BaseAgent, AgentRole, AgentStatus, AgentContext, AgentResult
from .mission_planner import ExecutionPlan, ExecutionStep


class CrewStatus(str, Enum):
    """Status of the agent crew."""
    ASSEMBLING = "assembling"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class CrewMember:
    """Information about a crew member."""
    agent: BaseAgent
    current_step: Optional[ExecutionStep] = None
    status: AgentStatus = AgentStatus.IDLE


class CrewResult(BaseModel):
    """Result of crew execution."""
    success: bool = Field(description="Whether the crew completed successfully")
    completed_steps: List[str] = Field(default_factory=list, description="Steps that were completed")
    failed_steps: List[str] = Field(default_factory=list, description="Steps that failed")
    outputs: Dict[str, str] = Field(default_factory=dict, description="Outputs from each step")
    errors: Dict[str, str] = Field(default_factory=dict, description="Errors from failed steps")
    total_duration: float = Field(description="Total execution time in seconds")


class CrewManager:
    """
    Manages the assembly and execution of agent crews.
    
    Responsibilities:
    - Dynamically instantiate agents based on execution plans
    - Coordinate step execution and dependencies
    - Handle error recovery and debugging
    - Track crew status and progress
    """
    
    def __init__(self, agent_factory, tool_manager):
        self.agent_factory = agent_factory
        self.tool_manager = tool_manager
        self.logger = logger.bind(component="crew_manager")
        self.active_crews: Dict[str, Dict[str, CrewMember]] = {}
        
    async def assemble_crew(self, execution_plan: ExecutionPlan, workspace_path: Path) -> str:
        """
        Assemble a crew of agents for the given execution plan.
        
        Args:
            execution_plan: The plan defining required agents and steps
            workspace_path: Path to the workspace for this mission
            
        Returns:
            str: Crew ID for tracking
        """
        crew_id = f"crew_{execution_plan.mission_id}"
        self.logger.info(f"Assembling crew {crew_id} for mission {execution_plan.mission_id}")
        
        crew_members = {}
        
        # Instantiate required agents
        for agent_role in execution_plan.required_agents:
            try:
                agent = await self.agent_factory.create_agent(agent_role)
                crew_members[agent_role] = CrewMember(agent=agent)
                self.logger.info(f"Added {agent_role} to crew {crew_id}")
            except Exception as e:
                self.logger.error(f"Failed to create agent {agent_role}: {e}")
                raise
        
        self.active_crews[crew_id] = crew_members
        self.logger.info(f"Crew {crew_id} assembled with {len(crew_members)} members")
        return crew_id
    
    async def execute_mission(self, crew_id: str, execution_plan: ExecutionPlan, user_prompt: str) -> CrewResult:
        """
        Execute a mission using the assembled crew.
        
        Args:
            crew_id: ID of the assembled crew
            execution_plan: The execution plan to follow
            user_prompt: Original user prompt for context
            
        Returns:
            CrewResult: Result of the mission execution
        """
        if crew_id not in self.active_crews:
            raise ValueError(f"Crew {crew_id} not found")
        
        crew_members = self.active_crews[crew_id]
        self.logger.info(f"Starting mission execution for crew {crew_id}")
        
        # Create execution context
        context = AgentContext(
            mission_id=execution_plan.mission_id,
            user_prompt=user_prompt,
            workspace_path=Path.cwd(),  # TODO: Get actual workspace path
            tools=self.tool_manager.get_available_tools(),
            memory={}  # TODO: Load from memory manager
        )
        
        # Set context for all crew members
        for member in crew_members.values():
            member.agent.set_context(context)
        
        # Execute steps in dependency order
        completed_steps = []
        failed_steps = []
        outputs = {}
        errors = {}
        
        # Sort steps by dependencies (topological sort)
        sorted_steps = self._sort_steps_by_dependencies(execution_plan.steps)
        
        for step in sorted_steps:
            try:
                self.logger.info(f"Executing step {step.step_id} with {step.agent_role}")
                
                # Get the agent for this step
                agent = crew_members[step.agent_role].agent
                agent.update_status(AgentStatus.WORKING)
                
                # Execute the step
                result = await agent.execute(context)
                
                if result.success:
                    completed_steps.append(step.step_id)
                    outputs[step.step_id] = result.output
                    agent.update_status(AgentStatus.COMPLETED)
                    self.logger.info(f"Step {step.step_id} completed successfully")
                else:
                    failed_steps.append(step.step_id)
                    errors[step.step_id] = result.error or "Unknown error"
                    agent.update_status(AgentStatus.ERROR)
                    self.logger.error(f"Step {step.step_id} failed: {result.error}")
                    
                    # Trigger debugger agent if available
                    await self._handle_step_failure(crew_id, step, result, context)
                    
            except Exception as e:
                failed_steps.append(step.step_id)
                errors[step.step_id] = str(e)
                self.logger.error(f"Exception in step {step.step_id}: {e}")
                
                # Trigger debugger agent
                await self._handle_step_failure(crew_id, step, AgentResult(
                    success=False,
                    output="",
                    error=str(e)
                ), context)
        
        # Determine overall success
        success = len(failed_steps) == 0
        
        return CrewResult(
            success=success,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            outputs=outputs,
            errors=errors,
            total_duration=0.0  # TODO: Track actual duration
        )
    
    def _sort_steps_by_dependencies(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """
        Sort steps by their dependencies to ensure correct execution order.
        
        Args:
            steps: List of execution steps
            
        Returns:
            List[ExecutionStep]: Steps sorted by dependencies
        """
        # Create dependency graph
        step_map = {step.step_id: step for step in steps}
        dependencies = {step.step_id: set(step.dependencies) for step in steps}
        
        # Topological sort
        sorted_steps = []
        visited = set()
        temp_visited = set()
        
        def visit(step_id: str):
            if step_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {step_id}")
            if step_id in visited:
                return
            
            temp_visited.add(step_id)
            
            for dep in dependencies[step_id]:
                visit(dep)
            
            temp_visited.remove(step_id)
            visited.add(step_id)
            sorted_steps.append(step_map[step_id])
        
        for step in steps:
            if step.step_id not in visited:
                visit(step.step_id)
        
        return sorted_steps
    
    async def _handle_step_failure(
        self, 
        crew_id: str, 
        failed_step: ExecutionStep, 
        result: AgentResult, 
        context: AgentContext
    ):
        """
        Handle step failure by deploying debugger agent.
        
        Args:
            crew_id: ID of the crew
            failed_step: The step that failed
            result: Result from the failed step
            context: Execution context
        """
        self.logger.info(f"Handling failure of step {failed_step.step_id}")
        
        # Check if debugger agent is available
        if "debugger" in self.active_crews[crew_id]:
            debugger_agent = self.active_crews[crew_id]["debugger"].agent
            
            # Create debug context
            debug_context = AgentContext(
                mission_id=context.mission_id,
                user_prompt=f"Debug step {failed_step.step_id}: {result.error}",
                workspace_path=context.workspace_path,
                tools=context.tools,
                memory={
                    "failed_step": failed_step.dict(),
                    "error_details": result.error,
                    "step_output": result.output
                }
            )
            
            try:
                debugger_agent.set_context(debug_context)
                debugger_agent.update_status(AgentStatus.WORKING)
                
                debug_result = await debugger_agent.execute(debug_context)
                
                if debug_result.success:
                    self.logger.info(f"Debugger successfully resolved issue in step {failed_step.step_id}")
                    debugger_agent.update_status(AgentStatus.COMPLETED)
                else:
                    self.logger.error(f"Debugger failed to resolve issue: {debug_result.error}")
                    debugger_agent.update_status(AgentStatus.ERROR)
                    
            except Exception as e:
                self.logger.error(f"Debugger agent failed: {e}")
        else:
            self.logger.warning("No debugger agent available for failure recovery")
    
    def get_crew_status(self, crew_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a crew.
        
        Args:
            crew_id: ID of the crew
            
        Returns:
            Optional[Dict]: Crew status information
        """
        if crew_id not in self.active_crews:
            return None
        
        crew_members = self.active_crews[crew_id]
        member_statuses = {}
        
        for role, member in crew_members.items():
            member_statuses[role] = {
                "status": member.agent.status.value,
                "current_step": member.current_step.step_id if member.current_step else None
            }
        
        return {
            "crew_id": crew_id,
            "members": member_statuses,
            "total_members": len(crew_members)
        }
    
    def disband_crew(self, crew_id: str) -> None:
        """
        Disband a crew and clean up resources.
        
        Args:
            crew_id: ID of the crew to disband
        """
        if crew_id in self.active_crews:
            self.logger.info(f"Disbanding crew {crew_id}")
            del self.active_crews[crew_id]
        else:
            self.logger.warning(f"Crew {crew_id} not found for disbanding")
    
    def get_active_crews(self) -> List[str]:
        """Get list of active crew IDs."""
        return list(self.active_crews.keys()) 