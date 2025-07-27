from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from config import settings
from typing import List, Optional
from datetime import datetime
import uuid
import asyncio
from pathlib import Path

# Import agent-related modules
from agents.simple_test_agent import SimpleTestAgent
from core.agent_base import AgentContext, AgentRole
from core.genai_client import genai_client

app = FastAPI(title="Sentinel Orchestrator Backend")

class MissionRequest(BaseModel):
    """The request model for creating a new mission."""
    prompt: str

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

@app.get("/health", status_code=200, tags=["System"])
def health_check():
    """Endpoint for Railway health checks."""
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
def get_missions():
    """Get all missions."""
    return missions_db

@app.post("/missions", tags=["Missions"])
def create_mission(request: MissionRequest):
    """
    This endpoint is the main entrypoint for creating a new mission.
    It receives a raw user prompt, orchestrates the planning,
    and dispatches the final plan to the desktop engine.
    """
    print(f"Received new mission request: {request.prompt}")

    # Create a new mission
    mission = Mission(
        id=str(uuid.uuid4()),
        title=f"Mission: {request.prompt[:50]}...",
        description=request.prompt,
        status="pending",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    missions_db.append(mission)

    # --- Placeholder Logic (to be replaced with real orchestrator call) ---
    # In the next step, we will replace this with:
    # json_plan = generate_mission_plan(request.prompt)
    
    # For now, let's create a dummy plan to test the connection
    dummy_plan = {
        "mission_name": f"Dummy Mission for '{request.prompt}'",
        "tasks": [
            {"task_id": 1, "agent_role": "Logger", "description": "Log the received prompt."}
        ]
    }
    # ----------------------------------------------------------------------

    # Dispatch the plan to the desktop agent engine
    if settings.DESKTOP_TUNNEL_URL:
        try:
            desktop_url = f"{settings.DESKTOP_TUNNEL_URL}/execute-mission"
            print(f"Dispatching plan to desktop at: {desktop_url}")
            
            # Use a timeout to prevent the server from hanging indefinitely
            response = requests.post(desktop_url, json=dummy_plan, timeout=15)
            
            # Raise an exception if the desktop returns an error (e.g., 4xx or 5xx)
            response.raise_for_status()

            return {
                "message": "Mission plan dispatched successfully to desktop.",
                "dispatched_plan": dummy_plan,
                "mission": mission
            }

        except requests.exceptions.RequestException as e:
            # This handles connection errors, timeouts, etc.
            raise HTTPException(status_code=502, detail=f"Failed to connect to desktop engine: {e}")
        except Exception as e:
            # A general catch-all for other unexpected errors
            raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
    else:
        # If no desktop tunnel URL is configured, just return the plan
        return {
            "message": "Mission plan created successfully (desktop not configured).",
            "plan": dummy_plan,
            "mission": mission
        }

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
        return {
            "message": "Agent test failed",
            "error": str(e),
            "success": False
        }

@app.get("/genai/status", tags=["GenAI"])
async def get_genai_status():
    """
    Get the status of Google GenAI integration.
    """
    try:
        model_info = genai_client.get_model_info()
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
        response = await genai_client.generate_response(test_prompt)
        
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