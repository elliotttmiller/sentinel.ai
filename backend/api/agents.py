from fastapi import APIRouter, HTTPException
from core.schemas import AgentSchema, AgentExecutionRequest, AgentExecutionResponse
from core.models import Agent
from sqlalchemy.orm import Session
from fastapi import Depends
from core.database import get_db
from loguru import logger
import uuid
from pathlib import Path

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/", response_model=list[AgentSchema])
def get_agents(db: Session = Depends(get_db)):
    """Get all agents from the database."""
    try:
        agents = db.query(Agent).all()
        return [AgentSchema.from_orm(a) for a in agents]
    except Exception as e:
        logger.error(f"Failed to fetch agents: {e}")
        raise HTTPException(status_code=500, detail="Database query failed.")

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