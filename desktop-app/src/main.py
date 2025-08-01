"""
Cognitive Forge v5.0 - Main API Server
Advanced FastAPI server with hybrid decision engine and real-time observability
"""

import uuid
import time
import asyncio
import json
import psutil
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from loguru import logger
import sys
import os

# --- Core Application Imports ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import settings

try:
    from .core.cognitive_forge_engine import cognitive_forge_engine
    from .core.hybrid_decision_engine import hybrid_decision_engine
    from .models.advanced_database import db_manager, Mission
    from .utils.sentry_integration import initialize_sentry
    
    # Initialize database manager
    logger.info("Database manager initialized successfully")
except ImportError as e:
    # Fallback for direct execution
    logger.warning(f"Some imports failed: {e}")
    cognitive_forge_engine = None
    db_manager = None
    Mission = None
    initialize_sentry = lambda: None

# --- Real-Time Logging & Streaming Setup ---
log_buffer = []
log_queue = asyncio.Queue()

class LogInterceptor:
    """Advanced log interceptor for real-time streaming"""
    
    def write(self, message: str):
        try:
            clean_message = message.strip()
            if clean_message:
                log_entry = self.parse_log(clean_message)
                if log_entry is not None:
                    log_buffer.append(log_entry)
                    if len(log_buffer) > settings.LOG_BUFFER_SIZE:
                        log_buffer.pop(0)
                    
                    # Put the new log into the async queue for live streaming
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(log_queue.put(log_entry), loop)
                    except RuntimeError:
                        # If no event loop is running, just add to buffer
                        pass
        except Exception as e:
            pass

    def parse_log(self, message: str) -> Dict:
        """Parse a raw log string into a structured dictionary"""
        timestamp = datetime.utcnow().isoformat()
        level = "INFO"
        source = "system"
        server_port = "8001"
        
        # Skip Sentry debug logs to focus on real server logs
        if "urllib3.connectionpool" in message or "sentry" in message.lower():
            return None
        
        # Heuristics to parse different log formats
        if "ERROR" in message: 
            level = "ERROR"
        elif "WARNING" in message: 
            level = "WARNING"
        elif "DEBUG" in message: 
            level = "DEBUG"
        elif "SUCCESS" in message:
            level = "SUCCESS"
        
        # Determine source and server port
        if "Uvicorn" in message: 
            source = "uvicorn"
            import re
            port_match = re.search(r':(\d+)', message)
            if port_match:
                server_port = port_match.group(1)
        elif "Cognitive Forge" in message: 
            source = "cognitive_forge"
        elif "Hybrid" in message:
            source = "hybrid_engine"
        elif "Database" in message:
            source = "database"
        
        return {
            "timestamp": timestamp,
            "level": level,
            "source": source,
            "server_port": server_port,
            "message": clean_message
        }

# Configure logging
logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL)
logger.add(settings.LOG_FILE, rotation=settings.LOG_ROTATION, level="DEBUG")
logger.add(LogInterceptor().write, level="INFO", format="{message}")

# --- FastAPI App ---
app = FastAPI(
    title="Sentinel Cognitive Forge v5.0",
    description="Advanced AI-powered mission execution system with hybrid decision engine",
    version="5.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
from pydantic import BaseModel

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
    execution_time: Optional[float]
    created_at: datetime
    execution_path: Optional[str]
    complexity_score: Optional[float]

    class Config:
        from_attributes = True

class SystemStatsResponse(BaseModel):
    engine_status: str
    database_stats: Dict[str, Any]
    system_info: str
    model: str
    last_updated: str

class HybridAnalysisRequest(BaseModel):
    prompt: str
    title: Optional[str] = None

class HybridAnalysisResponse(BaseModel):
    status: str
    task_analysis: Dict[str, Any]
    performance_prediction: Dict[str, Any]
    recommendation: Dict[str, Any]
    timestamp: str

# --- Background Tasks ---
def run_mission_in_background(mission_id_str: str, prompt: str, agent_type: str, title: str):
    """Enhanced background task with hybrid decision engine"""
    logger.info(f"🚀 BACKGROUND: Starting mission {mission_id_str}")
    db_manager.update_mission_status(mission_id_str, "executing")
    
    start_time = time.time()
    
    try:
        # Use hybrid decision engine to determine execution path
        decision = hybrid_decision_engine.make_hybrid_decision(prompt)
        chosen_path = decision["path"]
        complexity_score = decision["complexity_score"]
        
        logger.info(f"🧠 Hybrid Engine chose path: '{chosen_path}' for mission {mission_id_str}")
        logger.info(f"📊 Complexity score: {complexity_score:.3f}")
        
        # Update mission with decision metadata
        db_manager.update_mission_status(
            mission_id_str, 
            "executing",
            execution_path=chosen_path,
            complexity_score=complexity_score
        )
        
        # Execute based on chosen path
        if chosen_path == "golden_path":
            result = asyncio.run(cognitive_forge_engine.run_mission_simple(prompt, mission_id_str))
        else:
            result = asyncio.run(cognitive_forge_engine.run_mission_full(prompt, mission_id_str))
        
        execution_time = time.time() - start_time
        
        # Record performance metric for learning
        db_manager.record_performance_metric(
            execution_path=chosen_path,
            complexity_score=complexity_score,
            execution_time=execution_time,
            success=result.get("status") == "completed",
            user_satisfaction=result.get("user_satisfaction", 0.8)
        )
        
        # Update mission with final result
        db_manager.update_mission_status(
            mission_id_str, 
            result.get("status", "failed"), 
            result=json.dumps(result),
            execution_time=execution_time
        )
        
        logger.info(f"✅ Mission {mission_id_str} completed in {execution_time:.2f}s via {chosen_path}")
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ BACKGROUND: Mission {mission_id_str} failed: {e}", exc_info=True)
        db_manager.update_mission_status(
            mission_id_str, 
            "failed", 
            error_message=str(e),
            execution_time=execution_time
        )

# --- API Endpoints ---
@app.get("/", response_class=FileResponse)
def serve_web_ui():
    """Serve the main web interface"""
    return FileResponse("static/index.html")

@app.get("/static/{path:path}")
def serve_static(path: str):
    """Serve static files"""
    return FileResponse(f"static/{path}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "5.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "hybrid_engine": "active" if hybrid_decision_engine else "inactive",
        "cognitive_engine": "active" if cognitive_forge_engine else "inactive"
    }

@app.get("/api/events/stream")
async def stream_events() -> StreamingResponse:
    """Real-time event streaming via Server-Sent Events"""
    
    async def event_generator():
        # Send the last 50 buffered logs immediately on connection
        for log_entry in log_buffer[-50:]:
            yield f"data: {json.dumps(log_entry)}\n\n"
        
        # Continue streaming new logs
        while True:
            try:
                log_entry = await asyncio.wait_for(log_queue.get(), timeout=settings.SSE_KEEPALIVE_INTERVAL)
                yield f"data: {json.dumps(log_entry)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
    
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.get("/api/logs/live")
async def get_live_logs():
    """Get current log buffer"""
    return {
        "logs": log_buffer[-100:],  # Last 100 logs
        "buffer_size": len(log_buffer),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/missions")
async def create_mission_api(request: MissionRequest, background_tasks: BackgroundTasks):
    """Create a new mission with hybrid routing"""
    mission_id_str = f"mission_{uuid.uuid4().hex[:8]}"
    
    try:
        mission = db_manager.create_mission(
            mission_id_str=mission_id_str,
            title=request.title or request.prompt[:70],
            prompt=request.prompt,
            agent_type=request.agent_type,
            description=request.prompt
        )
        
        # Add background task for mission execution
        background_tasks.add_task(
            run_mission_in_background, 
            mission.mission_id_str, 
            request.prompt, 
            request.agent_type, 
            request.title
        )
        
        logger.info(f"📝 Created mission {mission_id_str}: {request.prompt[:50]}...")
        
        return {
            "mission_id": mission.mission_id_str,
            "status": "pending",
            "message": "Mission created and queued for execution"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/missions/{mission_id}/updates")
async def get_mission_updates(mission_id: str, limit: int = 50):
    """Get real-time updates for a mission"""
    try:
        updates = db_manager.get_mission_updates(mission_id, limit)
        return {
            "mission_id": mission_id,
            "updates": [
                {
                    "phase": update.phase,
                    "message": update.message,
                    "data": update.data,
                    "timestamp": update.timestamp.isoformat()
                }
                for update in updates
            ]
        }
    except Exception as e:
        logger.error(f"❌ Failed to get mission updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/missions")
def list_missions(limit: int = 50):
    """List all missions with enhanced metadata"""
    try:
        missions = db_manager.list_missions(limit)
        return [
            {
                "id": mission.id,
                "mission_id_str": mission.mission_id_str,
                "title": mission.title,
                "prompt": mission.prompt,
                "agent_type": mission.agent_type,
                "status": mission.status,
                "execution_time": mission.execution_time,
                "execution_path": mission.execution_path,
                "complexity_score": mission.complexity_score,
                "created_at": mission.created_at.isoformat(),
                "updated_at": mission.updated_at.isoformat()
            }
            for mission in missions
        ]
    except Exception as e:
        logger.error(f"❌ Failed to list missions: {e}")
        return []

@app.get("/api/hybrid/status")
async def get_hybrid_status():
    """Get comprehensive hybrid system status"""
    try:
        stats = hybrid_decision_engine.get_system_stats()
        return {
            "status": "active",
            "hybrid_mode": settings.ENABLE_HYBRID_MODE,
            "auto_switching": settings.AUTO_SWITCHING,
            "threshold": settings.HYBRID_SWITCH_THRESHOLD,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get hybrid status: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/hybrid/analyze")
async def analyze_task_complexity(request: HybridAnalysisRequest):
    """Analyze task complexity and get routing recommendation"""
    try:
        # Analyze task complexity
        complexity = hybrid_decision_engine.analyze_task_complexity(request.prompt)
        
        # Predict performance
        performance = hybrid_decision_engine.predict_performance(request.prompt, complexity.overall_score)
        
        # Make decision
        decision = hybrid_decision_engine.make_hybrid_decision(request.prompt)
        
        return HybridAnalysisResponse(
            status="success",
            task_analysis={
                "overall_score": complexity.overall_score,
                "length_score": complexity.length_score,
                "keyword_score": complexity.keyword_score,
                "context_score": complexity.context_score,
                "confidence": complexity.confidence
            },
            performance_prediction={
                "golden_path_time": performance.golden_path_time,
                "full_workflow_time": performance.full_workflow_time,
                "golden_path_success_rate": performance.golden_path_success_rate,
                "full_workflow_success_rate": performance.full_workflow_success_rate,
                "confidence": performance.confidence
            },
            recommendation={
                "path": decision["path"],
                "reason": decision["reason"],
                "confidence": decision["confidence"],
                "complexity_score": decision["complexity_score"],
                "predicted_time": decision["predicted_time"]
            },
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hybrid/analytics")
async def get_hybrid_analytics():
    """Get advanced analytics and performance metrics"""
    try:
        db_stats = db_manager.get_system_stats()
        hybrid_stats = hybrid_decision_engine.get_system_stats()
        
        return {
            "database_stats": db_stats,
            "hybrid_stats": hybrid_stats,
            "cache_stats": hybrid_decision_engine.cache.get_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        db_stats = db_manager.get_system_stats()
        
        return SystemStatsResponse(
            engine_status="active" if cognitive_forge_engine else "inactive",
            database_stats=db_stats,
            system_info=f"Sentinel Cognitive Forge v5.0 on {settings.HOST}:{settings.PORT}",
            model=settings.LLM_MODEL,
            last_updated=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"❌ Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("🚀 Sentinel Cognitive Forge v5.0 starting up...")
    logger.info("📡 Real-time log streaming initialized")
    logger.info("🔗 SSE endpoint available at /api/events/stream")
    logger.info("🧠 Hybrid Decision Engine active")
    logger.info("💾 Database system ready")
    
    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        initialize_sentry()
        logger.success("✅ Sentry integration initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Sentinel Cognitive Forge v5.0")
    logger.info("💾 Saving final state...")
    logger.info("✅ Shutdown complete")

# --- Middleware for Request Logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"🌐 {request.method} {request.url.path} | Client: {request.client.host if request.client else 'unknown'}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"📊 Response {response.status_code} for {request.method} {request.url.path} | Time: {process_time:.3f}s")
    
    return response
