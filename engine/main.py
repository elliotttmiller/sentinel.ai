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
    # Simulate real agent execution (replace with your actual logic)
    await asyncio.sleep(5)  # Simulate work
    # Example: You could call your agent classes here
    # result = await MyAgent().execute(plan)
    mission_results[mission_id] = {
        "status": "completed",
        "output": f"Task for mission {mission_id} executed successfully!",
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