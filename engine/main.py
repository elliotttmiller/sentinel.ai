# File: sentinel/engine/main.py

import asyncio
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
from datetime import datetime
import sys
from loguru import logger
from starlette.responses import Response

# Import our real AI components
from tools.tool_manager import ToolManager
from agents.agent_factory import AgentFactory
from core.crew_manager import CrewManager

# Import the core agent logic from our other file
from agent_logic import run_simple_agent_task

app = FastAPI(title="Sentinel Local Engine & Web UI")

# In-memory store for mission results (replace with DB for production)
mission_results: Dict[str, Any] = {}

# Initialize our AI components
tool_manager = ToolManager()
agent_factory = AgentFactory(tool_manager=tool_manager)
crew_manager = CrewManager(agent_factory=agent_factory, tool_manager=tool_manager)

# Configure loguru
logger.remove()
logger.add(sys.stdout, level="DEBUG", format="<green>{time}</green> <level>{level: <8}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

MAX_LOG_BODY = 2048

def safe_log_body(body):
    if not body:
        return None
    if isinstance(body, (bytes, bytearray)):
        body = body.decode(errors="replace")
    if len(body) > MAX_LOG_BODY:
        return body[:MAX_LOG_BODY] + "... [truncated]"
    return body

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

# Log service startup
logger.info("Sentinel Desktop Engine service started.")

class ExecutionPlan(BaseModel):
    """A simple model to receive the plan from the backend."""
    mission_id: str
    steps: list
    metadata: Dict[str, Any]

@app.post("/execute_mission")
async def execute_mission(plan: Dict):
    mission_id = plan.get("mission_id")
    if not mission_id:
        return {"error": "mission_id is required in the plan"}
    # Start real agent execution as a background task
    asyncio.create_task(run_real_agent_task(mission_id, plan))
    return {"message": f"Execution started for mission {mission_id}."}

async def run_real_agent_task(mission_id: str, plan: Dict):
    """Execute real agent tasks on the desktop using AI agents."""
    try:
        logger.info(f"ENGINE: Starting real AI agent execution for mission {mission_id}")
        
        # Use the CrewManager to execute the mission with real AI agents
        result = await crew_manager.execute_mission(plan)
        
        if result.get("success", False):
            mission_results[mission_id] = {
                "status": "completed",
                "output": result.get("summary", f"Mission {mission_id} completed successfully"),
                "details": {
                    "plan": plan,
                    "step_results": result.get("step_results", []),
                    "total_steps": result.get("total_steps", 0),
                    "completed_steps": result.get("completed_steps", 0),
                    "failed_steps": result.get("failed_steps", 0)
                }
            }
            logger.info(f"ENGINE: Mission {mission_id} completed successfully with AI agents")
        else:
            mission_results[mission_id] = {
                "status": "failed",
                "output": result.get("error", f"Mission {mission_id} failed"),
                "details": {
                    "plan": plan,
                    "error": result.get("error", "Unknown error")
                }
            }
            logger.error(f"ENGINE: Mission {mission_id} failed during AI agent execution")
        
    except Exception as e:
        logger.error(f"ENGINE: Mission {mission_id} execution failed: {str(e)}", exc_info=True)
        mission_results[mission_id] = {
            "status": "failed",
            "output": f"Mission execution failed: {str(e)}",
            "details": {
                "plan": plan,
                "error": str(e)
            }
        }

@app.get("/mission_result/{mission_id}")
async def mission_result(mission_id: str):
    result = mission_results.get(mission_id)
    if result:
        return result
    else:
        return {"status": "pending"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Sentinel Engine"}

@app.get("/", response_class=FileResponse)
def serve_web_ui():
    """Serves the main index.html file as the user interface."""
    return FileResponse("index.html")

# Add AgentRequest model for /run-agent endpoint
class AgentRequest(BaseModel):
    prompt: str

@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    """
    Receives a prompt from the web UI, runs the agent task, and returns the result.
    """
    logger.info(f"Received request to run agent with prompt: {request.prompt}")
    try:
        # FastAPI runs async, but CrewAI's kickoff is synchronous.
        # Running it in a threadpool prevents the server from blocking.
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, # Use the default thread pool
            run_simple_agent_task, # The function to run
            request.prompt # The argument to the function
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"An error occurred during agent execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 