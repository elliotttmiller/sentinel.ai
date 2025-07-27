from fastapi import APIRouter, HTTPException
from core.schemas import Agent, AgentExecutionRequest, AgentExecutionResponse
from loguru import logger
import uuid
from pathlib import Path

router = APIRouter(prefix="/agents", tags=["Agents"])

# In-memory storage for demo purposes (replace with DB in future)
agents_db = [
    Agent(
        id="agent-1",
        name="Code Reviewer",
        type="code_reviewer",
        description="Reviews code for quality and security issues",
        capabilities=["code_analysis", "security_scanning", "best_practices"],
        status="available",
        last_active=None,
        missions_completed=5
    ),
    Agent(
        id="agent-2",
        name="Debugger",
        type="debugger",
        description="Analyzes and fixes code issues",
        capabilities=["error_analysis", "bug_fixing", "performance_optimization"],
        status="available",
        last_active=None,
        missions_completed=3
    ),
    Agent(
        id="agent-3",
        name="Mission Planner",
        type="planner",
        description="Creates and manages mission plans",
        capabilities=["planning", "coordination", "execution_tracking"],
        status="busy",
        last_active=None,
        missions_completed=12
    ),
    Agent(
        id="agent-4",
        name="Simple Test Agent",
        type="simple_test",
        description="A basic test agent for validating the deployment system",
        capabilities=["text_processing", "basic_response_generation", "status_reporting", "activity_logging"],
        status="available",
        last_active=None,
        missions_completed=0
    )
]

@router.get("/", response_model=list[Agent])
def get_agents():
    """Get all agents."""
    return agents_db

@router.post("/execute", response_model=AgentExecutionResponse)
async def execute_agent(request: AgentExecutionRequest):
    """Execute an agent with the given prompt."""
    from agents.simple_test_agent import SimpleTestAgent
    try:
        context = {
            "mission_id": request.mission_id or str(uuid.uuid4()),
            "user_prompt": request.prompt,
            "workspace_path": Path.cwd(),
            "tools": {},
            "memory": {}
        }
        agent = SimpleTestAgent()
        agent.set_context(context)
        result = await agent.execute(context)
        return AgentExecutionResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            metadata=result.metadata
        )
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return AgentExecutionResponse(
            success=False,
            output="",
            error=f"Agent execution failed: {str(e)}",
            metadata={}
        )

@router.get("/test")
async def test_agent():
    """Test endpoint for the simple test agent."""
    from agents.simple_test_agent import SimpleTestAgent
    try:
        context = {
            "mission_id": "test-mission",
            "user_prompt": "Hello, this is a test message",
            "workspace_path": Path.cwd(),
            "tools": {},
            "memory": {}
        }
        agent = SimpleTestAgent()
        agent.set_context(context)
        result = await agent.execute(context)
        return {
            "message": "Agent test completed successfully",
            "agent_response": result.output,
            "success": result.success,
            "metadata": result.metadata
        }
    except Exception as e:
        logger.error(f"Agent test failed: {e}")
        return {
            "message": "Agent test failed",
            "error": str(e),
            "success": False
        } 