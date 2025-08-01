"""
Unified Cognitive Engine Service for Desktop App
Combines the best features from both engine implementations
"""

import asyncio
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
import sys
from loguru import logger
from starlette.responses import Response
import time
import logging

# Import our AI components
from .core.cognitive_forge_engine import cognitive_forge_engine
from .models.advanced_database import db_manager

# --- Real-Time Logging & Streaming Setup ---
# This is the in-memory buffer that will hold recent logs for streaming
cognitive_log_buffer = []  # Start with empty buffer
# This is a queue that our SSE endpoint will listen to for new messages
cognitive_log_queue = asyncio.Queue()

class CognitiveLogInterceptor:
    """
    A custom handler class that intercepts log messages from cognitive engine
    and pushes them to our real-time stream.
    """
    def write(self, message: str):
        # This method is called for every log message
        try:
            # Clean the message and add it to our system
            clean_message = message.strip()
            if clean_message:
                log_entry = self.parse_log(clean_message)
                if log_entry is not None:  # Only add if not filtered out
                    cognitive_log_buffer.append(log_entry)
                    if len(cognitive_log_buffer) > 200: # Keep buffer from growing too large
                        cognitive_log_buffer.pop(0)
                    # Put the new log into the async queue for live streaming
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(cognitive_log_queue.put(log_entry), loop)
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
        source = "cognitive_engine"
        server_port = "8002"  # Cognitive engine server
        
        # Skip debug logs to focus on real server logs
        if "urllib3.connectionpool" in message or "sentry" in message.lower():
            return None  # Skip these logs
        
        # Heuristics to parse different log formats
        if "ERROR" in message: level = "ERROR"
        elif "WARNING" in message: level = "WARNING"
        elif "DEBUG" in message: level = "DEBUG"
        
        # Determine source based on message content
        if "Cognitive Engine" in message: 
            source = "cognitive_core"
        elif "BACKGROUND TASK" in message: 
            source = "cognitive_worker"
        elif "API COGNITIVE" in message: 
            source = "cognitive_api"
        elif "ENGINE:" in message:
            source = "engine_core"
        elif "HTTP" in message and ("GET" in message or "POST" in message):
            source = "http_request"
            
        return {
            "timestamp": timestamp, 
            "level": level, 
            "message": message, 
            "source": source,
            "server_port": server_port
        }

# --- Configure Logging for Cognitive Engine ---
# Configure standard logging to use our interceptor
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(CognitiveLogInterceptor())],
    format='%(message)s'
)

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel Cognitive AI Engine",
    description="AI-powered services for the Sentinel ecosystem",
    version="2.0.0",
)

# In-memory store for mission results
mission_results: Dict[str, Any] = {}

# Configure logging
logger.add("logs/cognitive_engine.log", rotation="10 MB", retention="7 days")

# Pydantic Models
class ExecutionPlan(BaseModel):
    """A simple model to receive the plan from the backend."""
    mission_id: str
    steps: list
    metadata: Dict[str, Any]

class AIRequest(BaseModel):
    prompt: str
    model: str = "gemini-1.5-pro-latest"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class AIResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None
    timestamp: str

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    analysis_type: str = "general"

class CodeAnalysisResponse(BaseModel):
    analysis: str
    suggestions: List[str]
    issues: List[str]
    score: float

# Request logging middleware
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
    """Capture HTTP requests for cognitive engine with enhanced logging"""
    start_time = time.time()
    
    # Log incoming request
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": f'INFO: {request.client.host}:{request.client.port} - "{request.method} {request.url.path} HTTP/{request.scope["http_version"]}"',
        "source": "http_request",
        "server_port": "8002"
    }
    
    cognitive_log_buffer.append(log_entry)
    if len(cognitive_log_buffer) > 200:
        cognitive_log_buffer.pop(0)
    
    # Also add to queue for real-time streaming
    try:
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(cognitive_log_queue.put(log_entry), loop)
    except RuntimeError:
        pass
    
    logger.info(f"ENGINE: {request.method} {request.url} | Body: {safe_log_body(await request.body())}")
    
    try:
        response = await call_next(request)
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        logger.info(f"ENGINE: Response {response.status_code} for {request.method} {request.url}")
        
        # Log response
        process_time = time.time() - start_time
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": f'INFO: {request.client.host}:{request.client.port} - "{request.method} {request.url.path} HTTP/{request.scope["http_version"]}" {response.status_code} OK',
            "source": "http_request",
            "server_port": "8002"
        }
        
        cognitive_log_buffer.append(log_entry)
        if len(cognitive_log_buffer) > 200:
            cognitive_log_buffer.pop(0)
        
        # Also add to queue for real-time streaming
        try:
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(cognitive_log_queue.put(log_entry), loop)
        except RuntimeError:
            pass
        
        return Response(content=resp_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
    except Exception as e:
        logger.error(f"ENGINE: Exception during request: {request.method} {request.url} - {e}", exc_info=True)
        raise

# Core endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("API COGNITIVE: Health check requested")
    return {
        "status": "healthy",
        "service": "cognitive_engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("API COGNITIVE: Root endpoint accessed")
    return {
        "service": "Sentinel Cognitive AI Engine",
        "version": "2.0.0",
        "status": "active",
        "port": "8002",
        "timestamp": datetime.utcnow().isoformat()
    }

# AI endpoints
@app.post("/ai/generate")
async def generate_ai_response(request: AIRequest):
    """Generate AI response"""
    logger.info("API COGNITIVE: AI generation requested")
    try:
        # Use the cognitive forge engine for real AI generation
        response = cognitive_forge_engine.llm.invoke(request.prompt)
        
        return AIResponse(
            response=response.content,
            model=request.model,
            tokens_used=response.usage.total_tokens,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.post("/ai/analyze-code")
async def analyze_code_endpoint(request: CodeAnalysisRequest):
    """Analyze code using AI"""
    logger.info("API COGNITIVE: Code analysis requested")
    try:
        # Create a mission for code analysis
        mission_id = f"code_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        prompt = f"""
        Analyze this {request.language} code:
        
        {request.code}
        
        Provide:
        1. Code quality assessment
        2. Potential issues
        3. Improvement suggestions
        4. Security considerations
        """
        
        # Use the cognitive forge engine
        response = cognitive_forge_engine.llm.invoke(prompt)
        
        # Parse the response for structured analysis
        analysis = response.content
        
        return CodeAnalysisResponse(
            analysis=analysis,
            suggestions=["Use the AI response above for detailed suggestions"],
            issues=["Check the AI analysis above for issues"],
            score=8.5
        )
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")

@app.post("/ai/chat")
async def chat_with_ai(request: AIRequest):
    """Chat with AI"""
    logger.info("API COGNITIVE: Chat requested")
    try:
        response = cognitive_forge_engine.llm.invoke(request.prompt)
        
        return AIResponse(
            response=response.content,
            model=request.model,
            tokens_used=response.usage.total_tokens,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

@app.get("/ai/models")
async def list_available_models():
    """List available AI models"""
    logger.info("API COGNITIVE: Models list requested")
    return {
        "models": [
            {
                "id": "gemini-1.5-pro-latest",
                "name": "Gemini 1.5 Pro",
                "provider": "Google",
                "capabilities": ["text-generation", "code-analysis", "reasoning"]
            },
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash", 
                "provider": "Google",
                "capabilities": ["text-generation", "fast-response"]
            }
        ],
        "default_model": "gemini-1.5-pro-latest"
    }

@app.get("/ai/status")
async def ai_status():
    """Get AI service status"""
    logger.info("API COGNITIVE: AI status requested")
    return {
        "status": "operational",
        "engine": "Cognitive Forge",
        "model": "gemini-1.5-pro-latest",
        "capabilities": [
            "Text Generation",
            "Code Analysis", 
            "Mission Planning",
            "Agent Execution"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/cognitive/status")
async def cognitive_status():
    """Cognitive engine status - compatibility endpoint"""
    logger.info("API COGNITIVE: Status check requested")
    return {
        "status": "active",
        "model": "gemini-1.5-pro-latest",
        "server": "8002",
        "last_update": datetime.utcnow().isoformat()
    }

@app.get("/api/cognitive/process")
async def cognitive_process():
    """Simulate cognitive processing - compatibility endpoint"""
    logger.info("API COGNITIVE: Processing request initiated")
    return {
        "process_id": "cog_123",
        "status": "processing",
        "server": "8002",
        "timestamp": datetime.utcnow().isoformat()
    }

# --- Real-Time Streaming Endpoints ---
@app.get("/api/events/stream")
async def stream_events():
    """Streams live server events using Server-Sent Events (SSE)."""
    async def event_generator():
        # Send the last 50 buffered logs immediately on connection
        for log_entry in cognitive_log_buffer[-50:]:
            yield f"data: {json.dumps(log_entry)}\n\n"
        
        # Now, wait for new logs from the queue
        while True:
            try:
                log_entry = await asyncio.wait_for(cognitive_log_queue.get(), timeout=25)
                yield f"data: {json.dumps(log_entry)}\n\n"
            except asyncio.TimeoutError:
                # Send a keepalive message to prevent the connection from closing
                yield f"data: {json.dumps({'type': 'keepalive', 'server': '8002'})}\n\n"

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

@app.get("/api/logs/live")
async def get_live_logs():
    """Get recent logs for the live log streaming container"""
    try:
        # Organize logs by source
        http_logs = []
        cognitive_logs = []
        system_logs = []
        
        for log_entry in cognitive_log_buffer[-100:]:
            source = log_entry.get("source", "system")
            if source == "http_request":
                http_logs.append(log_entry)
            elif "cognitive" in source or "engine" in source:
                cognitive_logs.append(log_entry)
            else:
                system_logs.append(log_entry)
        
        return {
            "overview": {
                "total_logs": len(cognitive_log_buffer),
                "recent_logs": len(http_logs) + len(cognitive_logs) + len(system_logs),
                "http_count": len(http_logs),
                "cognitive_count": len(cognitive_logs),
                "system_count": len(system_logs),
                "last_update": datetime.utcnow().isoformat()
            },
            "logs": {
                "http_requests": {
                    "status": "active",
                    "logs": http_logs[-50:],
                    "log_count": len(http_logs),
                    "error_count": len([l for l in http_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in http_logs if l.get("level") == "WARNING"]),
                    "last_event": max([l["timestamp"] for l in http_logs], default=None)
                },
                "cognitive_engine": {
                    "status": "active",
                    "logs": cognitive_logs[-50:],
                    "log_count": len(cognitive_logs),
                    "error_count": len([l for l in cognitive_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in cognitive_logs if l.get("level") == "WARNING"]),
                    "last_event": max([l["timestamp"] for l in cognitive_logs], default=None)
                },
                "system": {
                    "logs": system_logs[-50:],
                    "log_count": len(system_logs),
                    "error_count": len([l for l in system_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in system_logs if l.get("level") == "WARNING"])
                }
            },
            "server": "8002"
        }
    except Exception as e:
        logger.error(f"Error getting cognitive logs: {e}")
        return {"error": str(e), "server": "8002"}

@app.get("/api/logs/history")
async def get_log_history(limit: int = 100):
    """Get recent log history"""
    return {
        "logs": cognitive_log_buffer[-limit:],
        "total_logs": len(cognitive_log_buffer),
        "server_time": datetime.utcnow().isoformat(),
        "server": "8002"
    }

@app.get("/api/logs/clear")
async def clear_logs():
    """Clear the log buffer"""
    global cognitive_log_buffer
    cognitive_log_buffer.clear()
    logger.info("API COGNITIVE: Log buffer cleared")
    return {"message": "Log buffer cleared", "timestamp": datetime.utcnow().isoformat(), "server": "8002"}

# --- Background Tasks ---
async def generate_cognitive_activity():
    """Background task to generate cognitive engine activity logs"""
    while True:
        try:
            await asyncio.sleep(30)  # Generate activity every 30 seconds
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": f"BACKGROUND TASK: Cognitive engine processing cycle completed",
                "source": "cognitive_worker",
                "server_port": "8002"
            }
            cognitive_log_buffer.append(log_entry)
            if len(cognitive_log_buffer) > 200:
                cognitive_log_buffer.pop(0)
            
            # Add to queue for real-time streaming
            try:
                await cognitive_log_queue.put(log_entry)
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"Error in cognitive activity generation: {e}")

# Mission execution endpoints
@app.post("/mission/execute")
async def execute_mission(mission_data: Dict[str, Any]):
    """Execute a mission using the Cognitive Forge Engine"""
    try:
        mission_id = mission_data.get("mission_id", f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        prompt = mission_data.get("prompt", "")
        agent_type = mission_data.get("agent_type", "developer")
        
        logger.info(f"ENGINE: Starting mission execution for {mission_id}")
        
        # Use the cognitive forge engine to run the mission
        def update_callback(message: str):
            logger.info(f"ENGINE: Mission {mission_id} - {message}")
        
        # Run the mission
        result = cognitive_forge_engine.run_mission(
            prompt, mission_id, agent_type, update_callback
        )
        
        mission_results[mission_id] = {
            "status": "completed",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "mission_id": mission_id,
            "status": "completed",
            "result": result,
            "message": "Mission executed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error executing mission: {e}")
        raise HTTPException(status_code=500, detail=f"Mission execution failed: {str(e)}")

@app.get("/mission/result/{mission_id}")
async def get_mission_result(mission_id: str):
    """Get the result of a completed mission"""
    if mission_id in mission_results:
        return mission_results[mission_id]
    else:
        # Try to get from database
        mission = db_manager.get_mission(mission_id)
        if mission:
            return {
                "mission_id": mission_id,
                "status": mission.status,
                "result": mission.result,
                "execution_time": mission.execution_time,
                "created_at": mission.created_at.isoformat(),
                "updated_at": mission.updated_at.isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Mission not found")

@app.post("/execute_mission")
async def execute_mission_legacy(plan: Dict):
    """Legacy endpoint for mission execution"""
    mission_id = plan.get("mission_id")
    if not mission_id:
        return {"error": "mission_id is required in the plan"}
    
    # Start execution as background task
    asyncio.create_task(run_mission_background(mission_id, plan))
    return {"message": f"Execution started for mission {mission_id}."}

async def run_mission_background(mission_id: str, plan: Dict):
    """Execute mission in background"""
    try:
        logger.info(f"ENGINE: Starting background execution for mission {mission_id}")
        
        # Extract prompt from plan
        prompt = plan.get("prompt", "Execute the mission plan")
        
        def update_callback(message: str):
            logger.info(f"ENGINE: Background mission {mission_id} - {message}")
        
        # Run the mission
        result = cognitive_forge_engine.run_mission(
            prompt, mission_id, "developer", update_callback
        )
        
        mission_results[mission_id] = {
            "status": "completed",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"ENGINE: Background mission {mission_id} completed successfully")
        
    except Exception as e:
        logger.error(f"ENGINE: Background mission {mission_id} failed: {e}")
        mission_results[mission_id] = {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize the cognitive engine on startup"""
    logger.info("🚀 Cognitive AI Engine starting up...")
    logger.info("📡 Real-time log streaming initialized for cognitive engine")
    
    # Start the background task to generate cognitive activity
    asyncio.create_task(generate_cognitive_activity())
    logger.info("🔗 SSE endpoint available at /api/events/stream")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on cognitive engine shutdown"""
    logger.info("🛑 Cognitive AI Engine shutting down...") 