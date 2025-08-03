"""
Cognitive Forge v5.2 - Main API Server
Powered by a Unified Real-Time Event Bus
"""
import uuid
import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import asdict
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import sys
import os

# --- Fix Import Paths ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# --- Core Application Imports ---
# NOTE: Using fallback for demonstration purposes. In production, these would be real.
from utils.agent_observability import agent_observability, LiveStreamEvent

# --- Real-Time Logging Integration ---
class LogInterceptor:
    def write(self, message: str):
        try:
            event = LiveStreamEvent(
                event_type="system_log",
                source="uvicorn",
                server_port="8001",
                severity="INFO",
                message=message.strip()
            )
            agent_observability.push_event(event)
        except Exception: pass # Avoid logging loops

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add(LogInterceptor(), level="INFO", format="{message}")

# --- FastAPI App ---
app = FastAPI(title="Sentinel Cognitive Forge v5.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- MOCK DATA GENERATION ---
async def mock_data_generator():
    """Generates a continuous stream of mock events for demonstration."""
    while True:
        event_type = random.choice(['system_log', 'agent_action', 'mission_update'])
        
        if event_type == 'system_log':
            severities = ['INFO', 'SUCCESS', 'WARNING', 'ERROR']
            messages = [
                "API endpoint /api/missions accessed.",
                "Database connection pool health check: OK.",
                "High memory usage detected: 85%.",
                "Agent authentication successful.",
                "Failed to connect to external tool: 'Code Analyzer API'."
            ]
            agent_observability.push_event(LiveStreamEvent(
                event_type="system_log",
                server_port=random.choice(["8001", "8002"]),
                severity=random.choice(severities),
                message=random.choice(messages)
            ))
        
        elif event_type == 'agent_action':
            agents = ['Code Reviewer', 'Data Analyzer', 'System Monitor']
            actions = ['analyzing code', 'processing data', 'monitoring system health']
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action",
                source=f"agent_{random.randint(1,3)}",
                severity="INFO",
                message=f"{random.choice(agents)} started {random.choice(actions)}.",
                payload={"duration_ms": random.randint(500, 5000), "tokens_used": random.randint(100, 1000)}
            ))
            
        elif event_type == 'mission_update':
            mission_id = f"mission_{random.randint(1, 20):03d}"
            status = random.choice(['running', 'completed'])
            progress = 100 if status == 'completed' else random.randint(10, 99)
            agent_observability.push_event(LiveStreamEvent(
                event_type='mission_update',
                source='mission_control',
                severity='INFO',
                message=f"Mission {mission_id} progress update.",
                payload={
                    "id": mission_id,
                    "prompt": f"Mission {int(mission_id.split('_')[1])} - Analyze system performance and optimize database queries...",
                    "status": status,
                    "agent_type": ["developer", "analyst", "researcher"][int(mission_id.split('_')[1]) % 3],
                    "progress": progress,
                    "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(5,60))).isoformat(),
                    "priority": ["high", "medium", "low"][int(mission_id.split('_')[1]) % 3]
                }
            ))

        await asyncio.sleep(random.uniform(1.5, 4.0))


# --- API Endpoints ---
@app.get("/", response_class=FileResponse)
def serve_index(): return FileResponse("templates/index.html")

@app.get("/{page_name}", response_class=FileResponse)
def serve_page(page_name: str):
    file_path = f"templates/{page_name}.html"
    if ".." in file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(file_path)

@app.get("/api/events/stream")
async def stream_events():
    """Streams events from the central, unified live event bus."""
    async def event_generator():
        while True:
            try:
                event = await agent_observability.live_event_stream.get()
                yield f"data: {json.dumps(asdict(event))}\n\n"
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/missions")
async def list_missions_api():
    """List all missions (mock data for initial load)."""
    try:
        missions = []
        for i in range(20):
            status = ["running", "completed", "pending"][i % 3]
            missions.append({
                "id": f"mission_{i+1:03d}",
                "prompt": f"Mission {i+1} - Analyze system performance and optimize database queries for enhanced performance monitoring.",
                "status": status,
                "agent_type": ["developer", "analyst", "researcher", "optimizer"][i % 4],
                "progress": 100 if status == 'completed' else (i * 5 + 10) % 100,
                "created_at": (datetime.utcnow() - timedelta(minutes=i*15)).isoformat(),
                "priority": ["high", "medium", "low"][i % 3]
            })
        return {"success": True, "missions": missions}
    except Exception as e:
        logger.error(f"❌ Failed to list missions: {e}")
        return {"success": False, "missions": [], "error": str(e)}

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Sentinel Cognitive Forge v5.2 starting up...")
    agent_observability.push_event(LiveStreamEvent(
        event_type="system_log",
        severity="SUCCESS",
        message="Backend Server 8001 is online and fully operational."
    ))
    
    # Add a large number of test log entries to ensure scrolling works immediately
    for i in range(50): # INCREASED FROM 30 to 50
        agent_observability.push_event(LiveStreamEvent(
            event_type="system_log",
            severity=random.choice(["INFO", "WARNING", "SUCCESS", "ERROR"]),
            server_port=random.choice(["8001", "8002"]),
            message=f"Initial system check {i+1}/50 - This is a sample log to demonstrate scrolling."
        ))

    # Start the continuous mock data generator as a background task
    asyncio.create_task(mock_data_generator())
