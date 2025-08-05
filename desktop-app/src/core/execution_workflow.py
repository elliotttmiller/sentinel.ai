"""
Execution Workflow - Orchestrates CrewAI agents to perform real tasks.
This is the core system that transforms user requests into actual execution.
VERSION 5.0: Fallback logic has been completely removed for a production-focused, real-execution-only model.
"""

from typing import Dict, Any
from loguru import logger
import asyncio

# --- Core Imports ---
# We now assume a stable environment where these imports will succeed.
# If they fail, the application will raise an exception on startup, which is the desired behavior.
try:
    from ..agents.executable_agent import ExecutableAgents
    from ..utils.agent_observability import agent_observability, LiveStreamEvent
    from ..utils.google_ai_wrapper import crewai_llm # Directly import the configured LLM
except ImportError:
    from agents.executable_agent import ExecutableAgents
    from utils.agent_observability import agent_observability, LiveStreamEvent
    from utils.google_ai_wrapper import crewai_llm

from crewai import Crew, Task, Process

logger.success("✅ Core components for ExecutionWorkflow loaded successfully.")

class ExecutionWorkflow:
    """
    Orchestrates the planning and execution of real tasks using CrewAI agents.
    This workflow is now streamlined to only use the real CrewAI agent execution path.
    """

    def __init__(self):
        if not crewai_llm:
            # This is a critical failure. The wrapper should have logged the error.
            # We raise an exception to prevent the application from starting in a broken state.
            raise ImportError("CrewAI-compatible LLM failed to initialize. The system cannot proceed.")

        # Initialize agents with the globally configured, compatible LLM.
        self.agents = ExecutableAgents(llm=crewai_llm)
        self.current_mission_id = None
        logger.success("✅ ExecutionWorkflow initialized with real CrewAI agents.")

    def set_mission_context(self, mission_id: str):
        """Sets the current mission context for observability and logging."""
        self.current_mission_id = mission_id
        logger.info(f"Set mission context to: {mission_id}")

    def _broadcast_workflow_event(self, event_type: str, message: str, payload: Dict[str, Any] = None):
        """Broadcasts workflow events to the real-time system via the observability manager."""
        if self.current_mission_id:
            try:
                agent_observability.push_event(LiveStreamEvent(
                    event_type=event_type,
                    source="execution_workflow",
                    severity="INFO",
                    message=message,
                    payload={"mission_id": self.current_mission_id, **(payload or {})},
                ))
            except Exception as e:
                logger.error(f"❌ Failed to broadcast workflow event: {e}")

    async def execute_mission(self, user_request: str, mission_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a complete mission from user request to real results using CrewAI.
        This is the single entry point for mission execution.
        """
        self._broadcast_workflow_event(
            "mission_started",
            f"Starting mission: {user_request[:100]}...",
            {"user_request": user_request, "context": mission_context}
        )

        try:
            logger.info(f"🚀 Kicking off CrewAI execution for: {user_request[:100]}...")
            
            # Define the tasks for the crew
            planning_task = self._create_planning_task(user_request, mission_context)
            execution_task = self._create_execution_task()
            
            # Assemble and run the crew
            crew = Crew(
                agents=[self.agents.planner_agent(), self.agents.executor_agent()],
                tasks=[planning_task, execution_task],
                verbose=True,
                process=Process.sequential,
                manager_llm=crewai_llm # Use the same LLM for the manager
            )

            self._broadcast_workflow_event("crew_executing", "CrewAI agents are now executing the mission.")
            
            # The result of the crew's work
            result = crew.kickoff()

            workflow_result = {
                "success": True,
                "user_request": user_request,
                "crew_result": str(result),
                "message": "Mission executed successfully by CrewAI.",
            }

            self._broadcast_workflow_event("mission_completed", "Mission execution completed successfully.", workflow_result)
            logger.success(f"✅ Mission '{user_request[:50]}...' completed successfully.")
            return workflow_result

        except Exception as e:
            error_message = f"❌ Mission execution failed due to a critical error: {e}"
            logger.error(error_message, exc_info=True)
            
            error_result = {
                "success": False,
                "error": str(e),
                "user_request": user_request,
                "message": "A critical error occurred during mission execution.",
            }
            
            self._broadcast_workflow_event("mission_failed", error_message, error_result)
            return error_result

    def _create_planning_task(self, user_request: str, mission_context: Dict[str, Any]) -> Task:
        """Creates the planning task for the Planner Agent."""
        return Task(
            description=f"""
            Analyze the following user request and create a detailed, step-by-step execution plan.
            The plan must only use the tools available to the Executor Agent.

            **User Request:**
            "{user_request}"

            **Additional Context:**
            {mission_context or 'None provided.'}

            **Instructions:**
            1.  Break down the request into small, atomic steps.
            2.  For each step, specify the exact tool to use (e.g., `create_file`, `execute_python_file`).
            3.  Provide precise arguments for each tool call (e.g., file names, content, commands).
            4.  The final output of this task must be a clear, numbered list of steps for the executor to follow.
            """,
            agent=self.agents.planner_agent(),
            expected_output="A detailed, step-by-step execution plan ready for the Executor Agent."
        )

    def _create_execution_task(self) -> Task:
        """Creates the execution task for the Executor Agent."""
        return Task(
            description="""
            Execute the step-by-step plan provided by the Planner Agent.
            You must follow the plan exactly as written, using your available tools to perform each action.

            **Instructions:**
            1.  Execute each step in the plan sequentially.
            2.  Confirm the outcome of each step.
            3.  If a step fails, stop execution and report the failure. Do not improvise or deviate from the plan.
            4.  The final output of this task must be a summary of the execution results, detailing what was done at each step.
            """,
            agent=self.agents.executor_agent(),
            expected_output="A detailed report of the execution, confirming the completion of each step from the plan."
        )
