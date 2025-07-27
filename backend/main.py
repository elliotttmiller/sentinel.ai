import json
import uuid
import asyncio
import requests
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from loguru import logger
from config import settings
from core.mission_planner import MissionPlanner, ExecutionPlan
from agents.agent_factory import AgentFactory
from core.agent_base import AgentContext, AgentRole
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from core.models import Mission as MissionORM, Base
from core.database import engine, Base, get_db
from sqlalchemy.orm import Session
from starlette.responses import Response

# --- Placeholder for ToolManager ---
class ToolManager:
    def get_available_tools(self):
        return {}
# ------------------------------------

# Utility for safe logging of request/response bodies
MAX_LOG_BODY = 2048  # bytes

def safe_log_body(body):
    if not body:
        return None
    if isinstance(body, (bytes, bytearray)):
        body = body.decode(errors="replace")
    if len(body) > MAX_LOG_BODY:
        return body[:MAX_LOG_BODY] + "... [truncated]"
    return body

app = FastAPI(title="Sentinel Orchestrator Backend", debug=True)
logger.add("logs/sentinel_backend.log", rotation="10 MB", level=settings.LOG_LEVEL)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Log config/env loads at startup
def log_config():
    logger.info(f"Loaded config: {settings.dict()}")
log_config()

def get_llm_client():
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        if settings.GOOGLE_API_KEY:
            return ChatGoogleGenerativeAI(
                model=settings.DEFAULT_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.7
            )
        elif settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
            from google.oauth2 import service_account
            creds_dict = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            credentials = service_account.Credentials.from_service_account_info(creds_dict)
            return ChatGoogleGenerativeAI(
                model=settings.DEFAULT_MODEL,
                credentials=credentials,
                temperature=0.7
            )
        else:
            raise ValueError("No Google API key or service account credentials provided.")
    except Exception as e:
        logger.error(f"FATAL: Could not initialize LLM Client. Error: {e}")
        raise

llm_client = get_llm_client()
tool_manager = ToolManager()
agent_factory = AgentFactory(llm_client=llm_client, tool_manager=tool_manager)
mission_planner = MissionPlanner(llm_client=llm_client)

class MissionRequest(BaseModel):
    prompt: str

class MissionDispatchResponse(BaseModel):
    message: str
    mission_id: str
    plan: dict
    execution_result: dict = None

class Mission(BaseModel):
    """The mission model for the mobile app."""
    id: str
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    steps: Optional[List[dict]] = None
    plan: Optional[dict] = None
    result: Optional[dict] = None

class Agent(BaseModel):
    """The agent model for the mobile app."""
    id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    status: str
    last_active: Optional[str] = None
    missions_completed: Optional[int] = None

class AgentExecutionRequest(BaseModel):
    """Request model for agent execution."""
    agent_type: str
    prompt: str
    mission_id: Optional[str] = None

class AgentExecutionResponse(BaseModel):
    """Response model for agent execution."""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: dict = {}

# In-memory storage for demo purposes
missions_db = []
agents_db = [
    Agent(
        id="agent-1",
        name="Code Reviewer",
        type="code_reviewer",
        description="Reviews code for quality and security issues",
        capabilities=["code_analysis", "security_scanning", "best_practices"],
        status="available",
        last_active=datetime.now().isoformat(),
        missions_completed=5
    ),
    Agent(
        id="agent-2", 
        name="Debugger",
        type="debugger",
        description="Analyzes and fixes code issues",
        capabilities=["error_analysis", "bug_fixing", "performance_optimization"],
        status="available",
        last_active=datetime.now().isoformat(),
        missions_completed=3
    ),
    Agent(
        id="agent-3",
        name="Mission Planner",
        type="planner", 
        description="Creates and manages mission plans",
        capabilities=["planning", "coordination", "execution_tracking"],
        status="busy",
        last_active=datetime.now().isoformat(),
        missions_completed=12
    ),
    Agent(
        id="agent-4",
        name="Simple Test Agent",
        type="simple_test",
        description="A basic test agent for validating the deployment system",
        capabilities=["text_processing", "basic_response_generation", "status_reporting", "activity_logging"],
        status="available",
        last_active=datetime.now().isoformat(),
        missions_completed=0
    )
]

def check_service_health(url: str, timeout: int = 5) -> dict:
    """Check if a service is online."""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return {
            "status": "online" if response.status_code == 200 else "offline",
            "response_time": response.elapsed.total_seconds(),
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e),
            "response_time": None,
            "status_code": None
        }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_body = await request.body()
    logger.info(f"Incoming request: {request.method} {request.url} | Body: {safe_log_body(req_body)} | Headers: {dict(request.headers)}")
    try:
        response = await call_next(request)
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        logger.info(f"Response status: {response.status_code} for {request.method} {request.url} | Body: {safe_log_body(resp_body)} | Headers: {dict(response.headers)}")
        return Response(content=resp_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
    except Exception as e:
        logger.error(f"Exception during request: {request.method} {request.url} - {e}", exc_info=True)
        raise

@app.get("/", tags=["Root"])
def root():
    logger.info("Root endpoint hit")
    return {"message": "Sentinel backend is running"}

@app.get("/health", status_code=200, tags=["System"])
def health_check():
    logger.info("Healthcheck endpoint hit")
    return {"status": "ok", "service": "Sentinel Orchestrator Backend"}

@app.get("/system-status", tags=["System"])
def get_system_status():
    """Get status of all system components."""
    # Check desktop engine
    desktop_status = check_service_health("http://localhost:8001")
    
    # Check Railway (using the configured URL)
    railway_status = check_service_health("https://sentinalai-production.up.railway.app")
    
    # Check ngrok (using the configured URL)
    ngrok_status = check_service_health("https://thrush-real-lacewing.ngrok-free.app")
    
    return {
        "backend": "online",
        "desktop": desktop_status["status"],
        "railway": railway_status["status"],
        "ngrok": ngrok_status["status"],
        "details": {
            "desktop": desktop_status,
            "railway": railway_status,
            "ngrok": ngrok_status
        }
    }

@app.get("/missions", tags=["Missions"])
def get_missions(db: Session = Depends(get_db)):
    try:
        missions = db.query(MissionORM).all()
        # Convert SQLAlchemy objects to dicts, removing _sa_instance_state
        result = []
        for m in missions:
            d = m.__dict__.copy()
            d.pop('_sa_instance_state', None)
            # Convert datetimes to isoformat strings
            for k in ["created_at", "updated_at", "completed_at"]:
                if d.get(k):
                    d[k] = d[k].isoformat()
            result.append(d)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch missions: {e}")
        raise HTTPException(status_code=500, detail="Database query failed.")

@app.post("/missions", response_model=MissionDispatchResponse, tags=["Missions"])
async def create_and_dispatch_mission(request: MissionRequest, db: Session = Depends(get_db)):
    mission_id = f"mission_{uuid.uuid4()}"
    logger.info(f"Received new mission request. Assigning ID: {mission_id}")

    try:
        # Validate prompt
        if not request.prompt or len(request.prompt) < 5:
            raise ValueError("Prompt is too short.")

        # Planning phase
        plan: ExecutionPlan = await mission_planner.create_mission_plan(
            user_prompt=request.prompt,
            mission_id=mission_id
        )
        logger.info(f"Plan generated for mission {mission_id}.")

        # Dispatch to engine
        desktop_url = f"{settings.DESKTOP_TUNNEL_URL}/execute_mission"
        response = await asyncio.to_thread(
            requests.post,
            desktop_url,
            json=plan.model_dump(),
            timeout=20
        )
        response.raise_for_status()

        # Poll for result
        execution_result = None
        result_url = f"{settings.DESKTOP_TUNNEL_URL}/mission_result/{mission_id}"
        for _ in range(10):
            try:
                poll_resp = await asyncio.to_thread(requests.get, result_url, timeout=10)
                if poll_resp.status_code == 200:
                    execution_result = poll_resp.json()
                    if execution_result and execution_result.get("status") != "pending":
                        break
            except Exception as e:
                logger.warning(f"Polling for execution result failed: {e}")
            await asyncio.sleep(2)

        # Save mission to DB
        now = datetime.utcnow()
        mission = MissionORM(
            id=mission_id,
            title=request.prompt,
            description=request.prompt,
            status="completed" if execution_result and execution_result.get("status") == "success" else "failed",
            created_at=now,
            updated_at=now,
            completed_at=now if execution_result else None,
            steps=plan.model_dump().get("steps", []),
            plan=plan.model_dump(),
            result=execution_result,
        )
        db.add(mission)
        db.commit()

        return MissionDispatchResponse(
            mission_id=mission_id,
            message="Mission planned, dispatched, and executed.",
            plan=plan.model_dump(),
            execution_result=execution_result
        )

    except ValueError as e:
        logger.error(f"Planning failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except requests.exceptions.RequestException as e:
        logger.error(f"Dispatch to engine failed: {e}")
        raise HTTPException(status_code=502, detail=f"Could not connect to the desktop engine: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/agents", tags=["Agents"])
def get_agents():
    """Get all agents."""
    return agents_db

@app.post("/agents/execute", tags=["Agents"])
async def execute_agent(request: AgentExecutionRequest):
    """
    Execute an agent with the given prompt.
    
    This endpoint allows testing agent execution directly.
    """
    from agents.simple_test_agent import SimpleTestAgent
    try:
        # Create agent context
        context = AgentContext(
            mission_id=request.mission_id or str(uuid.uuid4()),
            user_prompt=request.prompt,
            workspace_path=Path.cwd(),
            tools={},
            memory={}
        )
        
        # Create and execute the simple test agent
        agent = SimpleTestAgent()
        agent.set_context(context)
        
        # Execute the agent
        result = await agent.execute(context)
        
        return AgentExecutionResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            metadata=result.metadata
        )
        
    except Exception as e:
        return AgentExecutionResponse(
            success=False,
            output="",
            error=f"Agent execution failed: {str(e)}",
            metadata={}
        )

@app.get("/agents/test", tags=["Agents"])
async def test_agent():
    """
    Test endpoint for the simple test agent.
    Returns a simple response to verify the agent is working.
    """
    from agents.simple_test_agent import SimpleTestAgent
    try:
        # Create a test context
        context = AgentContext(
            mission_id="test-mission",
            user_prompt="Hello, this is a test message",
            workspace_path=Path.cwd(),
            tools={},
            memory={}
        )
        
        # Create and execute the simple test agent
        agent = SimpleTestAgent()
        agent.set_context(context)
        
        # Execute the agent
        result = await agent.execute(context)
        
        return {
            "message": "Agent test completed successfully",
            "agent_response": result.output,
            "success": result.success,
            "metadata": result.metadata
        }
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[AGENT TEST ERROR] {e}\n{tb}")
        return {
            "message": "Agent test failed",
            "error": str(e),
            "traceback": tb,
            "success": False
        }

@app.get("/genai/status", tags=["GenAI"])
async def get_genai_status():
    """
    Get the status of Google GenAI integration.
    """
    try:
        model_info = llm_client.get_model_info()
        return {
            "message": "GenAI status retrieved successfully",
            "genai_status": model_info,
            "success": True
        }
    except Exception as e:
        return {
            "message": "Failed to get GenAI status",
            "error": str(e),
            "success": False
        }

@app.post("/genai/test", tags=["GenAI"])
async def test_genai():
    """
    Test Google GenAI integration with a simple prompt.
    """
    try:
        test_prompt = "Hello! Can you tell me about your capabilities?"
        response = await llm_client.generate_response(test_prompt)
        
        return {
            "message": "GenAI test completed successfully",
            "prompt": test_prompt,
            "response": response,
            "success": True
        }
    except Exception as e:
        return {
            "message": "GenAI test failed",
            "error": str(e),
            "success": False
        } 