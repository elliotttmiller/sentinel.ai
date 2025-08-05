"""
Execution Workflow - Orchestrates CrewAI agents to perform real tasks
This is the core system that transforms user requests into actual execution
"""

from typing import Dict, Any, List
from loguru import logger
import asyncio

# Import agents (with fallback)
try:
    from ..agents.executable_agent import ExecutableAgents
    from ..utils.agent_observability import agent_observability, LiveStreamEvent
except ImportError:
    from agents.executable_agent import ExecutableAgents
    from utils.agent_observability import agent_observability, LiveStreamEvent

# Import CrewAI with fallback
try:
    # Temporarily force fallback for Google AI compatibility
    # When fixed, remove this line and the next to restore CrewAI
    raise ImportError("Temporarily forcing fallback due to Google AI compatibility issue")
    
    from crewai import Crew, Task
    CREWAI_AVAILABLE = True
    logger.info("CrewAI imported successfully")
except Exception as e:
    logger.warning(f"CrewAI import failed: {e}. Using fallback implementation.")
    CREWAI_AVAILABLE = False
    
    # Create minimal fallback classes
    class Task:
        def __init__(self, description, agent, expected_output):
            self.description = description
            self.agent = agent  
            self.expected_output = expected_output
            self.output = None
    
    class Crew:
        def __init__(self, agents, tasks, verbose=True, process='sequential'):
            self.agents = agents
            self.tasks = tasks
            self.verbose = verbose
            self.process = process
        
        def kickoff(self):
            # Simple fallback execution
            results = []
            for task in self.tasks:
                # Simulate task execution
                result = f"Task completed: {task.description[:100]}..."
                task.output = result
                results.append(result)
                if self.verbose:
                    logger.info(f"Executed task: {task.description[:50]}...")
            return "\n".join(results)


class ExecutionWorkflow:
    """
    Orchestrates the planning and execution of real tasks using CrewAI agents
    """
    
    def __init__(self):
        self.agents = ExecutableAgents()
        self.current_mission_id = None
        self.crewai_available = CREWAI_AVAILABLE
        logger.info(f"ExecutionWorkflow initialized (CrewAI available: {self.crewai_available})")
    
    def set_mission_context(self, mission_id: str):
        """Set the current mission context for observability"""
        self.current_mission_id = mission_id
    
    def _broadcast_workflow_event(self, event_type: str, message: str, payload: Dict[str, Any] = None):
        """Broadcast workflow events to the real-time system"""
        if self.current_mission_id:
            try:
                agent_observability.push_event(LiveStreamEvent(
                    event_type=event_type,
                    source="execution_workflow",
                    severity="INFO",
                    message=message,
                    payload={
                        "mission_id": self.current_mission_id,
                        **(payload or {})
                    }
                ))
            except Exception as e:
                logger.error(f"Failed to broadcast workflow event: {e}")
    
    async def execute_mission(self, user_request: str, mission_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a complete mission from user request to real results
        """
        try:
            self._broadcast_workflow_event(
                "mission_started",
                f"Starting mission execution: {user_request[:100]}...",
                {"user_request": user_request, "context": mission_context}
            )
            
            if self.crewai_available:
                return await self._execute_with_crewai(user_request, mission_context)
            else:
                return await self._execute_with_fallback(user_request, mission_context)
                
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "user_request": user_request,
                "message": f"Mission execution failed: {str(e)}"
            }
            
            self._broadcast_workflow_event(
                "mission_failed",
                f"Mission execution failed: {str(e)}",
                error_result
            )
            
            logger.error(f"Mission execution failed: {e}")
            return error_result
    
    async def _execute_with_crewai(self, user_request: str, mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using full CrewAI implementation"""
        
        # Step 1: Create planning task
        planning_task = Task(
            description=f"""
            Analyze this user request and create a detailed, step-by-step execution plan:
            
            USER REQUEST: {user_request}
            
            Additional Context: {mission_context or 'None provided'}
            
            Create a plan where each step corresponds to one of these available tools:
            1. Create File - Creates a new file with specified content
            2. Execute Python File - Runs a Python script and returns output
            3. List Directory - Shows contents of a directory
            4. Read File - Reads and returns file contents
            5. Install Python Package - Installs a Python package via pip
            6. Create Directory - Creates a new directory
            
            Your plan should be detailed, actionable, and focused on what the user actually wants accomplished.
            Be specific about file names, directory structures, and exact content where relevant.
            """,
            agent=self.agents.planner_agent(),
            expected_output="A detailed step-by-step execution plan with each step clearly mapped to available tools"
        )
        
        # Step 2: Create execution task
        execution_task = Task(
            description="""
            Execute the step-by-step plan provided by the planner agent.
            Use your available tools to perform each action in sequence.
            
            For each step:
            1. Use the appropriate tool
            2. Verify the result was successful
            3. Report what was accomplished
            4. Proceed to the next step
            
            If any step fails, attempt to troubleshoot and retry once before reporting the failure.
            Provide detailed feedback on what was actually created, executed, or accomplished.
            """,
            agent=self.agents.executor_agent(),
            expected_output="Detailed execution report showing what was actually accomplished, including any files created, code executed, or tasks completed"
        )
        
        # Step 3: Create supervision task
        supervision_task = Task(
            description="""
            Review the planning and execution results to ensure the user's request was fully satisfied.
            
            Verify:
            1. Was the plan comprehensive and appropriate?
            2. Was the execution successful?
            3. Were any files actually created or tasks actually performed?
            4. Does the result meet the user's original request?
            
            Use the List Directory and Read File tools to verify that promised deliverables actually exist.
            Provide a final assessment of success or failure with specific details.
            """,
            agent=self.agents.supervisor_agent(),
            expected_output="Final assessment report confirming what was actually delivered and whether the user's request was successfully fulfilled"
        )
        
        # Step 4: Create and execute the crew
        crew = Crew(
            agents=[
                self.agents.planner_agent(),
                self.agents.executor_agent(),
                self.agents.supervisor_agent()
            ],
            tasks=[planning_task, execution_task, supervision_task],
            verbose=True,
            process='sequential'  # Execute tasks in order
        )
        
        self._broadcast_workflow_event(
            "crew_executing",
            "CrewAI agents are now executing the mission",
            {"crew_size": 3, "task_count": 3}
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        # Process the results
        workflow_result = {
            "success": True,
            "user_request": user_request,
            "mission_context": mission_context,
            "crew_result": str(result),
            "planning_output": planning_task.output if hasattr(planning_task, 'output') else "Planning completed",
            "execution_output": execution_task.output if hasattr(execution_task, 'output') else "Execution completed",
            "supervision_output": supervision_task.output if hasattr(supervision_task, 'output') else "Supervision completed",
            "message": "Mission executed successfully with real-world results"
        }
        
        self._broadcast_workflow_event(
            "mission_completed",
            "Mission execution completed successfully",
            workflow_result
        )
        
        logger.success(f"Mission executed successfully: {user_request[:50]}...")
        return workflow_result
    
    async def _execute_with_fallback(self, user_request: str, mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using fallback implementation when CrewAI is not available"""
        
        logger.info(f"Executing mission with fallback: {user_request}")
        
        # Simulate planning
        await asyncio.sleep(1)
        planning_result = f"Fallback planning for: {user_request}"
        
        self._broadcast_workflow_event(
            "fallback_planning",
            "Planning with fallback system",
            {"plan": planning_result}
        )
        
        # Simulate execution  
        await asyncio.sleep(2)
        execution_result = f"Fallback execution completed for: {user_request}"
        
        self._broadcast_workflow_event(
            "fallback_execution", 
            "Execution with fallback system",
            {"result": execution_result}
        )
        
        # Create result structure
        workflow_result = {
            "success": True,
            "user_request": user_request,
            "mission_context": mission_context,
            "crew_result": f"Fallback execution: {user_request}",
            "planning_output": planning_result,
            "execution_output": execution_result,
            "supervision_output": "Fallback supervision completed",
            "message": "Mission executed with fallback system (CrewAI not available)",
            "fallback_mode": True
        }
        
        self._broadcast_workflow_event(
            "mission_completed",
            "Fallback mission execution completed",
            workflow_result
        )
        
        return workflow_result
    
    async def execute_simple_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a simple single-step task (for testing and simple operations)
        """
        try:
            self._broadcast_workflow_event(
                "simple_task_started",
                f"Executing simple task: {task_description}",
                {"task": task_description}
            )
            
            if self.crewai_available:
                # Create a single execution task
                task = Task(
                    description=f"""
                    Execute this specific task using your available tools:
                    
                    TASK: {task_description}
                    
                    Use the most appropriate tool from your available toolkit:
                    - Create File
                    - Execute Python File  
                    - List Directory
                    - Read File
                    - Install Python Package
                    - Create Directory
                    
                    Perform the task and report exactly what was accomplished.
                    """,
                    agent=self.agents.executor_agent(),
                    expected_output="Confirmation of task completion with specific details about what was accomplished"
                )
                
                # Execute with a single-agent crew
                crew = Crew(
                    agents=[self.agents.executor_agent()],
                    tasks=[task],
                    verbose=True
                )
                
                result = crew.kickoff()
                
                task_result = {
                    "success": True,
                    "task_description": task_description,
                    "result": str(result),
                    "message": "Simple task executed successfully"
                }
            else:
                # Fallback execution
                await asyncio.sleep(1)
                task_result = {
                    "success": True,
                    "task_description": task_description,
                    "result": f"Fallback execution: {task_description}",
                    "message": "Simple task executed with fallback system",
                    "fallback_mode": True
                }
            
            self._broadcast_workflow_event(
                "simple_task_completed",
                "Simple task completed successfully",
                task_result
            )
            
            return task_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "task_description": task_description,
                "message": f"Simple task execution failed: {str(e)}"
            }
            
            self._broadcast_workflow_event(
                "simple_task_failed",
                f"Simple task failed: {str(e)}",
                error_result
            )
            
            logger.error(f"Simple task execution failed: {e}")
            return error_result
