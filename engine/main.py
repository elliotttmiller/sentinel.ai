# File: sentinel/engine/main.py

import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any
import os
from datetime import datetime
import sys
from loguru import logger
from starlette.responses import Response

app = FastAPI(title="Sentinel Desktop Engine")

# In-memory store for mission results (replace with DB for production)
mission_results: Dict[str, Any] = {}

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
    """Execute real agent tasks on the desktop."""
    try:
        logger.info(f"Starting real agent execution for mission {mission_id}")
        
        # Get the steps from the plan
        steps = plan.get("steps", [])
        outputs = []
        
        for step in steps:
            step_id = step.get("step_id")
            agent_type = step.get("agent_type")
            action = step.get("action")
            parameters = step.get("parameters", {})
            
            logger.info(f"Executing step {step_id}: {action}")
            
            if action == "execute_desktop_task":
                # Execute real desktop command
                command = parameters.get("command")
                if command:
                    logger.info(f"Executing command: {command}")
                    
                    # Use subprocess to execute the command
                    import subprocess
                    import platform
                    
                    try:
                        if platform.system() == "Windows":
                            # Use PowerShell for Windows
                            result = subprocess.run(
                                ["powershell", "-Command", command],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                        else:
                            # Use bash for Unix-like systems
                            result = subprocess.run(
                                ["bash", "-c", command],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                        
                        if result.returncode == 0:
                            output = f"Command executed successfully: {result.stdout}"
                            logger.info(f"Step {step_id} completed successfully")
                        else:
                            output = f"Command failed: {result.stderr}"
                            logger.error(f"Step {step_id} failed: {result.stderr}")
                        
                        outputs.append({
                            "step_id": step_id,
                            "status": "completed" if result.returncode == 0 else "failed",
                            "output": output
                        })
                        
                    except subprocess.TimeoutExpired:
                        error_msg = f"Command timed out after 30 seconds"
                        logger.error(f"Step {step_id} timed out")
                        outputs.append({
                            "step_id": step_id,
                            "status": "failed",
                            "output": error_msg
                        })
                    except Exception as e:
                        error_msg = f"Command execution error: {str(e)}"
                        logger.error(f"Step {step_id} error: {str(e)}")
                        outputs.append({
                            "step_id": step_id,
                            "status": "failed",
                            "output": error_msg
                        })
                else:
                    error_msg = "No command specified in parameters"
                    logger.error(f"Step {step_id}: {error_msg}")
                    outputs.append({
                        "step_id": step_id,
                        "status": "failed",
                        "output": error_msg
                    })
            else:
                # Handle other action types
                output = f"Action '{action}' not implemented yet"
                logger.warning(f"Step {step_id}: {output}")
                outputs.append({
                    "step_id": step_id,
                    "status": "completed",
                    "output": output
                })
        
        # Determine overall mission status
        all_completed = all(output.get("status") == "completed" for output in outputs)
        
        mission_results[mission_id] = {
            "status": "completed" if all_completed else "failed",
            "output": f"Mission {mission_id} execution completed. Steps: {len(outputs)}",
            "details": {
                "plan": plan,
                "step_outputs": outputs
            }
        }
        
        logger.info(f"Mission {mission_id} completed with status: {mission_results[mission_id]['status']}")
        
    except Exception as e:
        logger.error(f"Mission {mission_id} execution failed: {str(e)}")
        mission_results[mission_id] = {
            "status": "failed",
            "output": f"Mission execution failed: {str(e)}",
            "details": plan
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

@app.get("/")
def root():
    return {"message": "Sentinel Desktop Engine is running", "endpoints": ["/health", "/execute_mission"]} 