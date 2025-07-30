"""
Sentinel Backend API Server
Provides core API endpoints for the Sentinel ecosystem
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime
from loguru import logger

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel Backend API",
    description="Core API server for the Sentinel ecosystem",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

class MissionRequest(BaseModel):
    prompt: str
    agent_type: str = "developer"
    title: Optional[str] = None

class MissionResponse(BaseModel):
    id: str
    status: str
    prompt: str
    agent_type: str
    created_at: str

# In-memory storage for demo
missions_db: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentinel Backend API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services={
            "api": "operational",
            "database": "connected",
            "ai_engine": "available"
        }
    )

@app.post("/missions")
async def create_mission(request: MissionRequest):
    """Create a new mission"""
    mission_id = f"mission_{len(missions_db) + 1}_{datetime.utcnow().timestamp()}"
    
    mission = {
        "id": mission_id,
        "prompt": request.prompt,
        "agent_type": request.agent_type,
        "title": request.title or f"Mission {len(missions_db) + 1}",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    missions_db[mission_id] = mission
    logger.info(f"Created mission: {mission_id}")
    
    return MissionResponse(
        id=mission_id,
        status=mission["status"],
        prompt=mission["prompt"],
        agent_type=mission["agent_type"],
        created_at=mission["created_at"]
    )

@app.get("/missions")
async def list_missions():
    """List all missions"""
    return {
        "missions": list(missions_db.values()),
        "total": len(missions_db)
    }

@app.get("/missions/{mission_id}")
async def get_mission(mission_id: str):
    """Get a specific mission"""
    if mission_id not in missions_db:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return missions_db[mission_id]

@app.put("/missions/{mission_id}")
async def update_mission(mission_id: str, status: str):
    """Update mission status"""
    if mission_id not in missions_db:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    missions_db[mission_id]["status"] = status
    missions_db[mission_id]["updated_at"] = datetime.utcnow().isoformat()
    
    logger.info(f"Updated mission {mission_id} status to {status}")
    return missions_db[mission_id]

@app.delete("/missions/{mission_id}")
async def delete_mission(mission_id: str):
    """Delete a mission"""
    if mission_id not in missions_db:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    deleted_mission = missions_db.pop(mission_id)
    logger.info(f"Deleted mission: {mission_id}")
    
    return {"message": "Mission deleted successfully", "mission": deleted_mission}

@app.get("/system/stats")
async def get_system_stats():
    """Get system statistics"""
    return {
        "total_missions": len(missions_db),
        "pending_missions": len([m for m in missions_db.values() if m["status"] == "pending"]),
        "completed_missions": len([m for m in missions_db.values() if m["status"] == "completed"]),
        "failed_missions": len([m for m in missions_db.values() if m["status"] == "failed"]),
        "uptime": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            "/health",
            "/missions",
            "/system/stats",
            "/api/status"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 