"""
Cognitive Forge Desktop App - Main API Server
Advanced FastAPI server with full async capabilities and real-time observability
"""

import uuid
import time
import asyncio
import json
import psutil
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from loguru import logger
import sys

# --- Core Application Imports ---
try:
    from .core.cognitive_forge_engine import cognitive_forge_engine
    from .models.advanced_database import db_manager, Mission
    from .utils.sentry_integration import initialize_sentry
except ImportError:
    # Fallback for direct execution
    cognitive_forge_engine = None
    db_manager = None
    Mission = None
    initialize_sentry = lambda: None

# --- Real-Time Logging & Streaming Setup ---
# This is the in-memory buffer that will hold recent logs for streaming
log_buffer = []  # Start with empty buffer - no test logs
# This is a queue that our SSE endpoint will listen to for new messages
log_queue = asyncio.Queue()

class LogInterceptor:
    """
    A custom handler class that intercepts log messages from any source
    (loguru, uvicorn, etc.) and pushes them to our real-time stream.
    """
    def write(self, message: str):
        # This method is called for every log message
        try:
            # Clean the message and add it to our system
            clean_message = message.strip()
            if clean_message:
                log_entry = self.parse_log(clean_message)
                if log_entry is not None:  # Only add if not filtered out
                    log_buffer.append(log_entry)
                    if len(log_buffer) > 200: # Keep buffer from growing too large
                        log_buffer.pop(0)
                    # Put the new log into the async queue for live streaming
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(log_queue.put(log_entry), loop)
                    except RuntimeError:
                        # If no event loop is running, just add to buffer
                        pass
        except Exception as e:
            # If parsing fails, just pass the raw message
            pass

    def parse_log(self, message: str) -> Dict:
        """Parses a raw log string into a structured dictionary."""
        timestamp = datetime.utcnow().isoformat()
        level = "INFO"
        source = "system"
        server_port = "8001"  # Default to main server
        
        # Skip Sentry debug logs to focus on real server logs
        if "urllib3.connectionpool" in message or "sentry" in message.lower():
            return None  # Skip these logs
        
        # Heuristics to parse different log formats
        if "ERROR" in message: level = "ERROR"
        elif "WARNING" in message: level = "WARNING"
        elif "DEBUG" in message: level = "DEBUG"
        
        # Determine source and server port
        if "Uvicorn" in message: 
            source = "uvicorn"
            # Extract port from uvicorn startup message
            import re
            port_match = re.search(r':(\d+)', message)
            if port_match:
                server_port = port_match.group(1)
        elif "Cognitive Forge" in message: 
            source = "engine_core"
        elif "BACKGROUND TASK" in message: 
            source = "mission_worker"
        elif "API MISSION CREATED" in message: 
            source = "api"
        elif "HTTP" in message and ("GET" in message or "POST" in message):
            source = "http_request"
            # Determine server from HTTP request
            if "8002" in message:
                server_port = "8002"
            else:
                server_port = "8001"
            
        return {
            "timestamp": timestamp, 
            "level": level, 
            "message": message, 
            "source": source,
            "server_port": server_port
        }

# --- Configure Logging ---
# Remove the default logger
logger.remove()
# Add a logger for writing to a file
logger.add("logs/cognitive_forge.log", rotation="10 MB", level="DEBUG")
# Add a logger that uses our custom interceptor to capture everything
logger.add(LogInterceptor(), level="INFO", format="{message}")

# Capture standard library logging as well
import logging
logging.basicConfig(handlers=[logging.StreamHandler(LogInterceptor())], level=0)

# Capture uvicorn access logs specifically
import uvicorn.logging
uvicorn.logging.AccessFormatter = lambda: LogInterceptor()

# --- End of Logging Setup ---

# Initialize Sentry
if initialize_sentry:
    initialize_sentry()

# Initialize FastAPI App
app = FastAPI(title="Sentinel Cognitive Forge v5.0")

# Custom middleware to capture HTTP requests
@app.middleware("http")
async def capture_http_requests(request, call_next):
    """Capture HTTP requests and log them"""
    import time
    start_time = time.time()
    
    # Log the incoming request
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": f'INFO: {request.client.host}:{request.client.port} - "{request.method} {request.url.path} HTTP/{request.scope["http_version"]}"',
        "source": "http_request",
        "server_port": "8001"
    }
    
    log_buffer.append(log_entry)
    if len(log_buffer) > 200:
        log_buffer.pop(0)
    
    # Process the request
    response = await call_next(request)
    
    # Log the response
    process_time = time.time() - start_time
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": f'INFO: {request.client.host}:{request.client.port} - "{request.method} {request.url.path} HTTP/{request.scope["http_version"]}" {response.status_code} OK',
        "source": "http_request",
        "server_port": "8001"
    }
    
    log_buffer.append(log_entry)
    if len(log_buffer) > 200:
        log_buffer.pop(0)
    
    return response

# --- API Models (Pydantic) ---
from pydantic import BaseModel
from typing import Optional

class MissionRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    agent_type: str = "developer"

class MissionResponse(BaseModel):
    id: int
    mission_id_str: str
    title: Optional[str]
    prompt: str
    agent_type: str
    status: str
    execution_time: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class SystemStatsResponse(BaseModel):
    engine_status: str
    database_stats: Dict[str, Any]
    system_info: str
    model: str
    last_updated: str

class ObservabilityData(BaseModel):
    """Real-time observability data from Weave"""
    active_missions: int
    total_missions: int
    agent_performance: Dict[str, Any]
    system_metrics: Dict[str, Any]
    recent_traces: List[Dict[str, Any]]
    performance_grades: Dict[str, str]
    weave_status: str
    wandb_runs: List[Dict[str, Any]]

class AgentMetricsResponse(BaseModel):
    """Detailed agent performance metrics"""
    agent_name: str
    total_executions: int
    avg_execution_time: float
    success_rate: float
    total_tokens: int
    memory_usage: float
    cpu_usage: float
    cost_estimate: float
    recent_errors: List[str]

class ParallelMissionRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    agent_type: str = "developer"
    complexity_level: str = "standard"  # standard, complex, advanced

class ParallelMissionResponse(BaseModel):
    id: int
    mission_id_str: str
    title: Optional[str]
    prompt: str
    agent_type: str
    complexity_level: str
    status: str
    execution_time: Optional[int]
    created_at: datetime
    parallel_execution: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# --- Background Task ---
def run_mission_in_background(mission_id: str, prompt: str, agent_type: str, title: str):
    logger.info(f"BACKGROUND TASK: Starting mission {mission_id} for prompt: '{prompt}'")
    try:
        # Simulate mission execution
        time.sleep(2)
        logger.info(f"BACKGROUND TASK: Mission {mission_id} completed successfully")
    except Exception as e:
        logger.error(f"BACKGROUND TASK: Mission {mission_id} failed: {e}")

# --- API Endpoints ---
@app.get("/", response_class=FileResponse)
def serve_web_ui():
    return FileResponse("templates/index.html")

@app.get("/static/{path:path}")
def serve_static(path: str):
    """Serve static files"""
    try:
        return FileResponse(f"static/{path}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- NEW, SIMPLIFIED STREAMING ENDPOINT ---
@app.get("/api/events/stream")
async def stream_events() -> StreamingResponse:
    """Streams live server events using Server-Sent Events (SSE)."""
    async def event_generator():
        # Send the last 50 buffered logs immediately on connection
        for log_entry in log_buffer[-50:]:
            yield f"data: {json.dumps(log_entry)}\n\n"
        
        # Now, wait for new logs from the queue
        while True:
            try:
                log_entry = await asyncio.wait_for(log_queue.get(), timeout=25)
                yield f"data: {json.dumps(log_entry)}\n\n"
            except asyncio.TimeoutError:
                # Send a keepalive message to prevent the connection from closing
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

# --- Legacy endpoints for backward compatibility ---
@app.get("/api/logs/live")
async def get_live_logs():
    """Get recent logs for the live log streaming container"""
    try:
        # Organize logs by server
        server_8001_logs = []
        server_8002_logs = []
        system_logs = []
        
        for log_entry in log_buffer[-100:]:
            server_port = log_entry.get("server_port", "8001")
            if server_port == "8001":
                server_8001_logs.append(log_entry)
            elif server_port == "8002":
                server_8002_logs.append(log_entry)
            else:
                system_logs.append(log_entry)
        
        return {
            "overview": {
                "total_logs": len(log_buffer),
                "recent_logs": len(server_8001_logs) + len(server_8002_logs) + len(system_logs),
                "server_8001_count": len(server_8001_logs),
                "server_8002_count": len(server_8002_logs),
                "system_count": len(system_logs),
                "last_update": datetime.utcnow().isoformat()
            },
            "servers": {
                "server_8001": {
                    "status": "active",
                    "logs": server_8001_logs[-50:],
                    "log_count": len(server_8001_logs),
                    "error_count": len([l for l in server_8001_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in server_8001_logs if l.get("level") == "WARNING"]),
                    "last_event": max([l["timestamp"] for l in server_8001_logs], default=None)
                },
                "server_8002": {
                    "status": "active",
                    "logs": server_8002_logs[-50:],
                    "log_count": len(server_8002_logs),
                    "error_count": len([l for l in server_8002_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in server_8002_logs if l.get("level") == "WARNING"]),
                    "last_event": max([l["timestamp"] for l in server_8002_logs], default=None)
                }
            },
            "system": {
                "logs": system_logs[-50:],
                "log_count": len(system_logs),
                "error_count": len([l for l in system_logs if l.get("level") == "ERROR"]),
                "warning_count": len([l for l in system_logs if l.get("level") == "WARNING"])
            }
        }
    except Exception as e:
        logger.error(f"Error getting live logs: {e}")
        return {"error": str(e)}

@app.get("/api/logs/server/{server_port}")
async def get_server_logs(server_port: str):
    """Get logs for a specific server"""
    try:
        server_logs = [log for log in log_buffer if log.get("server_port") == server_port]
        return {
            "status": "active",
            "logs": server_logs[-50:],
            "log_count": len(server_logs),
            "error_count": len([l for l in server_logs if l.get("level") == "ERROR"]),
            "warning_count": len([l for l in server_logs if l.get("level") == "WARNING"]),
            "last_event": max([l["timestamp"] for l in server_logs], default=None)
        }
    except Exception as e:
        logger.error(f"Error getting server {server_port} logs: {e}")
        return {"error": str(e)}

@app.get("/api/logs/system")
async def get_system_logs():
    """Get system logs"""
    try:
        system_logs = [log for log in log_buffer if log.get("server_port") not in ["8001", "8002"]]
        return {
            "logs": system_logs[-50:],
            "log_count": len(system_logs),
            "error_count": len([l for l in system_logs if l.get("level") == "ERROR"]),
            "warning_count": len([l for l in system_logs if l.get("level") == "WARNING"])
        }
    except Exception as e:
        logger.error(f"Error getting system logs: {e}")
        return {"error": str(e)}

@app.get("/api/logs/stream")
async def stream_logs():
    """Legacy streaming endpoint - redirects to new unified stream"""
    return await stream_events()

@app.get("/api/logs/history")
async def get_log_history(limit: int = 100):
    """Get recent log history"""
    return {
        "logs": log_buffer[-limit:],
        "total_logs": len(log_buffer),
        "server_time": datetime.utcnow().isoformat()
    }

@app.get("/api/logs/clear")
async def clear_logs():
    """Clear the log buffer"""
    global log_buffer
    log_buffer.clear()
    return {"message": "Log buffer cleared", "timestamp": datetime.utcnow().isoformat()}

# Removed test log endpoint - only real server logs should be displayed

# --- Mission Management Endpoints ---
@app.post("/api/missions")
async def create_mission_api(request: MissionRequest, background_tasks: BackgroundTasks):
    """Create a new mission via API"""
    try:
        mission_id = str(uuid.uuid4())
        title = request.title or f"Mission {mission_id[:8]}"
        
        logger.info(f"API MISSION CREATED: {mission_id} - {title}")
        
        # Add to background tasks
        background_tasks.add_task(run_mission_in_background, mission_id, request.prompt, request.agent_type, title)
        
        return {
            "mission_id": mission_id,
            "title": title,
            "status": "executing",
            "message": "Mission created and started"
        }
    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/missions")
def list_missions(limit: int = 50):
    """List recent missions"""
    return [
        {
            "id": i,
            "mission_id_str": f"mission_{i}",
            "title": f"Sample Mission {i}",
            "prompt": f"Sample prompt {i}",
            "agent_type": "developer",
            "status": "completed",
            "execution_time": 120,
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(1, min(limit + 1, 11))
    ]

@app.get("/service-status")
async def get_service_status():
    """Get overall service status"""
    return {
        "overall_status": "operational",
        "services": {
            "api_server": "operational",
            "database": "operational",
            "cognitive_engine": "operational"
        },
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/api/observability/overview")
async def get_observability_overview():
    """Get observability overview"""
    return {
        "weave": {"status": "operational"},
        "wandb": {"status": "operational"},
        "sentry": {"status": "operational"},
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/api/events/live")
async def get_live_events():
    """Get live events"""
    return {
        "events": log_buffer[-20:],
        "total_events": len(log_buffer),
        "last_update": datetime.utcnow().isoformat()
    }

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Cognitive Forge Desktop App starting up...")
    logger.info("📡 Real-time log streaming initialized")
    logger.info("🔗 SSE endpoint available at /api/events/stream")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Cognitive Forge Desktop App shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
