"""
Cognitive Forge Desktop App - Main API Server
Advanced FastAPI server with full async capabilities and real-time observability
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger
from sqlalchemy.orm import Session

from .core.cognitive_forge_engine import cognitive_forge_engine
from .models.advanced_database import db_manager, Mission

# Configure logging
logger.add("logs/cognitive_forge.log", rotation="10 MB", retention="7 days")

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel Cognitive Forge",
    description="Advanced AI Agent Engine with Memory and Learning",
    version="3.0.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory store for real-time mission status
mission_status_db: Dict[str, Any] = {}


# Pydantic Models
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


# Background Task Functions
def run_mission_in_background(mission_id_str: str, prompt: str, agent_type: str):
    """
    Background task to run a complete mission with real-time updates
    """
    logger.info(f"BACKGROUND TASK: Starting mission {mission_id_str}")

    def update_callback(update_message: str):
        """Callback function for real-time mission updates"""
        if mission_id_str in mission_status_db:
            mission_status_db[mission_id_str]["updates"].append(
                {"timestamp": datetime.utcnow().isoformat(), "message": update_message}
            )
            mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()

            # Also log to database
            db_manager.add_mission_update(mission_id_str, update_message, "info")

    # Initialize mission status
    mission_status_db[mission_id_str] = {
        "status": "PLANNING",
        "updates": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "message": "🚀 Mission accepted. Initializing Cognitive Forge Engine...",
            }
        ],
        "result": None,
        "last_update": datetime.utcnow().isoformat(),
    }

    try:
        # Run the mission using the Cognitive Forge Engine
        final_result = cognitive_forge_engine.run_mission(
            prompt, mission_id_str, agent_type, update_callback
        )

        # Update final status
        mission_status_db[mission_id_str]["status"] = final_result.get(
            "status", "completed"
        ).upper()
        mission_status_db[mission_id_str]["result"] = final_result
        mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()

        logger.info(f"BACKGROUND TASK: Mission {mission_id_str} completed successfully")

    except Exception as e:
        logger.error(f"BACKGROUND TASK: Mission {mission_id_str} failed. Error: {e}", exc_info=True)
        mission_status_db[mission_id_str]["status"] = "FAILED"
        mission_status_db[mission_id_str]["result"] = {"error": str(e)}
        mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()


# API Endpoints
@app.get("/", response_class=FileResponse)
def serve_web_ui():
    """Serve the main web interface"""
    return FileResponse("../templates/index.html")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": "3.0.0"}


@app.post("/advanced-mission")
async def create_advanced_mission(request: MissionRequest, background_tasks: BackgroundTasks):
    """
    Create and start a new advanced mission using the Cognitive Forge Engine
    """
    mission_id_str = f"mission_{uuid.uuid4().hex[:8]}"

    # Create mission record in database
    try:
        mission = db_manager.create_mission(
            mission_id_str=mission_id_str,
            title=request.title or request.prompt[:50],
            prompt=request.prompt,
            agent_type=request.agent_type,
        )

        # Add background task
        background_tasks.add_task(
            run_mission_in_background, mission_id_str, request.prompt, request.agent_type
        )

        logger.info(f"Created new mission: {mission_id_str}")

        return {
            "mission_id": mission_id_str,
            "message": "🚀 Advanced mission accepted and planning has begun.",
            "status": "accepted",
        }

    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create mission: {str(e)}")


@app.get("/mission/{mission_id}")
def get_mission_status(mission_id: str):
    """
    Get real-time status and updates for a mission
    """
    # First check live status
    live_status = mission_status_db.get(mission_id)
    if live_status:
        return live_status

    # Fallback to database
    mission = db_manager.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    # Get recent updates from database
    updates = db_manager.get_mission_updates(mission_id, limit=50)

    return {
        "status": mission.status.upper(),
        "result": mission.result,
        "updates": [
            {"timestamp": update.timestamp.isoformat(), "message": update.update_message}
            for update in updates
        ],
        "last_update": mission.updated_at.isoformat(),
    }


@app.get("/missions", response_model=List[MissionResponse])
def list_missions(limit: int = 50, include_archived: bool = False):
    """
    List recent missions with pagination
    """
    missions = db_manager.list_missions(limit=limit, include_archived=include_archived)
    return missions


@app.get("/system-stats", response_model=SystemStatsResponse)
def get_system_stats():
    """
    Get comprehensive system statistics and health information
    """
    try:
        stats = cognitive_forge_engine.get_system_info()
        return SystemStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system stats")


@app.get("/api/status")
def api_status():
    """
    Detailed API status and capabilities
    """
    return {
        "api_version": "3.0.0",
        "engine": "Cognitive Forge",
        "status": "operational",
        "capabilities": [
            "Advanced Mission Planning",
            "Multi-Agent Execution",
            "Real-time Observability",
            "Long-term Memory",
            "Learning & Adaptation",
        ],
        "agents": [
            "Lead AI Architect",
            "Plan Validator",
            "Senior Developer",
            "QA Tester",
            "Code Analyzer",
            "System Integrator",
            "Memory Synthesizer",
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.delete("/mission/{mission_id}")
def delete_mission(mission_id: str):
    """
    Archive a mission (soft delete)
    """
    try:
        # Update mission as archived
        success = db_manager.update_mission_status(
            mission_id, "archived", metadata={"archived_at": datetime.utcnow().isoformat()}
        )

        if success:
            return {"message": f"Mission {mission_id} archived successfully"}
        else:
            raise HTTPException(status_code=404, detail="Mission not found")

    except Exception as e:
        logger.error(f"Error archiving mission: {e}")
        raise HTTPException(status_code=500, detail="Failed to archive mission")


@app.get("/memory/search")
def search_memory(query: str, limit: int = 5):
    """
    Search mission memory for relevant past experiences
    """
    try:
        memories = db_manager.search_memory(query, limit=limit)
        return {"query": query, "results": memories, "count": len(memories)}
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to search memory")


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Cognitive Forge Desktop App starting up...")

    # Log system startup
    db_manager.log_system_event(
        "INFO",
        "Cognitive Forge Desktop App started successfully",
        "main",
        {"version": "3.0.0", "startup_time": datetime.utcnow().isoformat()},
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Cognitive Forge Desktop App shutting down...")

    # Log system shutdown
    db_manager.log_system_event(
        "INFO",
        "Cognitive Forge Desktop App shutting down",
        "main",
        {"shutdown_time": datetime.utcnow().isoformat()},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
