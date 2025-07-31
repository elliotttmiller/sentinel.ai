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
    import os
    # Get the absolute path to the templates directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    template_path = os.path.join(project_root, "templates", "index.html")
    
    # Check if file exists
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template file not found")
    
    return FileResponse(template_path)


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
        
        # Ensure all required fields are present
        if "engine_status" not in stats:
            stats["engine_status"] = "error"
        if "database_stats" not in stats:
            stats["database_stats"] = {"error": "Database stats unavailable"}
        if "system_info" not in stats:
            stats["system_info"] = "System info unavailable"
        if "model" not in stats:
            stats["model"] = "unknown"
        if "last_updated" not in stats:
            stats["last_updated"] = datetime.utcnow().isoformat()
            
        return SystemStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        # Return a minimal valid response
        return SystemStatsResponse(
            engine_status="error",
            database_stats={"error": str(e)},
            system_info="System information unavailable",
            model="unknown",
            last_updated=datetime.utcnow().isoformat()
        )


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


@app.post("/api/missions")
async def create_mission_api(request: MissionRequest, background_tasks: BackgroundTasks):
    """
    Create a new mission via the /api/missions endpoint
    This is the standard REST API endpoint for mission creation
    """
    try:
        # Generate unique mission ID
        mission_id_str = f"mission_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Create mission in database
        mission = Mission(
            mission_id_str=mission_id_str,
            title=request.title or f"Mission: {request.prompt[:50]}...",
            prompt=request.prompt,
            agent_type=request.agent_type,
            status="pending"
        )
        
        # Save to database using the create_mission method
        mission = db_manager.create_mission(
            mission_id_str=mission_id_str,
            title=request.title or f"Mission: {request.prompt[:50]}...",
            prompt=request.prompt,
            agent_type=request.agent_type
        )
        
        # Initialize status tracking
        mission_status_db[mission_id_str] = {
            "status": "pending",
            "progress": 0,
            "messages": [],
            "start_time": time.time(),
            "last_update": time.time()
        }
        
        # Add background task for mission execution
        background_tasks.add_task(run_mission_in_background, mission_id_str, request.prompt, request.agent_type)
        
        logger.info(f"API MISSION CREATED: {mission_id_str} - {request.prompt[:50]}...")
        
        return {
            "mission_id": mission_id_str,
            "status": "pending",
            "message": "Mission created and queued for execution",
            "created_at": mission.created_at.isoformat(),
            "estimated_duration": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to create mission via API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create mission: {str(e)}")


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


@app.get("/observability/data", response_model=ObservabilityData)
def get_observability_data():
    """
    Get real-time observability data from Weave
    """
    try:
        # Import Weave observability manager
        from .utils.weave_observability import observability_manager
        
        # Get real observability data
        performance_analytics = observability_manager.get_performance_analytics()
        
        # Get active missions count
        active_missions = len([m for m in mission_status_db.values() if m.get("status") in ["PLANNING", "EXECUTING"]])
        
        # Get agent performance data
        agent_performance = {}
        for agent_name, metrics in observability_manager.performance_baselines.items():
            agent_performance[agent_name] = AgentMetricsResponse(
                agent_name=agent_name,
                total_executions=metrics.get("total_executions", 0),
                avg_execution_time=metrics.get("avg_execution_time", 0.0),
                success_rate=metrics.get("success_rate", 0.0),
                total_tokens=0,  # Would need to track this separately
                memory_usage=0.0,  # Would need to track this separately
                cpu_usage=0.0,  # Would need to track this separately
                cost_estimate=0.0,  # Would need to track this separately
                recent_errors=[]
            )
        
        # Get system metrics
        import psutil
        system_metrics = {
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent(),
            "disk_usage": psutil.disk_usage('/').percent
        }
        
        # Get recent traces (simulated for now)
        recent_traces = [
            {
                "trace_id": "trace_001",
                "trace_name": "Mission Planning",
                "duration": 1.5,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        # Performance grades based on success rates
        performance_grades = {}
        for agent_name, metrics in agent_performance.items():
            success_rate = metrics.success_rate
            if success_rate >= 0.95:
                performance_grades[agent_name] = "A+"
            elif success_rate >= 0.90:
                performance_grades[agent_name] = "A"
            elif success_rate >= 0.80:
                performance_grades[agent_name] = "B"
            elif success_rate >= 0.70:
                performance_grades[agent_name] = "C"
            else:
                performance_grades[agent_name] = "D"
        
        return ObservabilityData(
            active_missions=active_missions,
            total_missions=len(mission_status_db),
            agent_performance=agent_performance,
            system_metrics=system_metrics,
            recent_traces=recent_traces,
            performance_grades=performance_grades,
            weave_status="online" if observability_manager.weave_client else "offline",
            wandb_runs=[{"run_id": "current", "project": "cognitive-forge-v5", "status": "running", "start_time": datetime.utcnow().isoformat()}]
        )
        
    except Exception as e:
        logger.error(f"Error fetching observability data: {e}")
        # Return fallback data
        return ObservabilityData(
            active_missions=0,
            total_missions=0,
            agent_performance={},
            system_metrics={"memory_usage": 0, "cpu_usage": 0, "disk_usage": 0},
            recent_traces=[],
            performance_grades={},
            weave_status="offline",
            wandb_runs=[]
        )


@app.get("/observability/agents/{agent_name}", response_model=AgentMetricsResponse)
def get_agent_metrics(agent_name: str):
    """
    Get detailed metrics for a specific agent
    """
    try:
        from .utils.weave_observability import observability_manager
        
        if agent_name not in observability_manager.performance_baselines:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        metrics = observability_manager.performance_baselines[agent_name]
        
        return AgentMetricsResponse(
            agent_name=agent_name,
            total_executions=metrics.get("total_executions", 0),
            avg_execution_time=metrics.get("avg_execution_time", 0.0),
            success_rate=metrics.get("success_rate", 0.0),
            total_tokens=0,  # Would need to track this separately
            memory_usage=0.0,  # Would need to track this separately
            cpu_usage=0.0,  # Would need to track this separately
            cost_estimate=0.0,  # Would need to track this separately
            recent_errors=[]
        )
        
    except Exception as e:
        logger.error(f"Error fetching agent metrics for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent metrics")


@app.get("/observability/traces")
def get_recent_traces(limit: int = 10):
    """
    Get recent mission traces
    """
    try:
        # This would fetch from Weave API in a real implementation
        # For now, return simulated data
        traces = []
        for i in range(min(limit, 5)):
            traces.append({
                "trace_id": f"trace_{i:03d}",
                "mission_id": f"mission_{i:03d}",
                "trace_name": f"Mission {i} Execution",
                "duration": round(1.0 + i * 0.5, 2),
                "status": "success" if i % 2 == 0 else "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "agent_name": "Lead AI Architect" if i % 2 == 0 else "Plan Validator"
            })
        
        return {"traces": traces}
        
    except Exception as e:
        logger.error(f"Error fetching recent traces: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch traces")


@app.get("/service-status")
async def get_service_status():
    """Get comprehensive service status including Railway connection"""
    try:
        import requests
        import psutil
        import os
        from datetime import datetime
        
        # Check local services
        services = {
            "cognitive_engine": {
                "url": "http://localhost:8002/health", 
                "name": "Cognitive Engine",
                "port": 8002
            }
        }
        
        # Check Railway deployment if available
        railway_status = {
            "available": False,
            "url": None,
            "status": "unknown"
        }
        
        # Try to get Railway URL from environment
        railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_url:
            try:
                response = requests.get(f"https://{railway_url}/health", timeout=5)
                railway_status = {
                    "available": True,
                    "url": f"https://{railway_url}",
                    "status": "online" if response.status_code == 200 else "offline"
                }
            except:
                railway_status = {
                    "available": True,
                    "url": f"https://{railway_url}",
                    "status": "offline"
                }
        
        # Check local services
        service_status = {}
        for service_id, service in services.items():
            try:
                response = requests.get(service["url"], timeout=5)
                service_status[service_id] = {
                    "name": service["name"],
                    "status": "online" if response.status_code == 200 else "offline",
                    "port": service["port"],
                    "response_time": response.elapsed.total_seconds(),
                    "last_check": datetime.now().isoformat()
                }
            except Exception as e:
                service_status[service_id] = {
                    "name": service["name"],
                    "status": "offline",
                    "port": service["port"],
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
        
        # Add Desktop App status (always online since we're running from it)
        service_status["desktop_app"] = {
            "name": "Desktop App",
            "status": "online",
            "port": 8001,
            "response_time": 0.001,
            "last_check": datetime.now().isoformat()
        }
        
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "services": service_status,
            "railway": railway_status,
            "system": {
                "memory_usage": memory.percent,
                "cpu_usage": cpu,
                "disk_usage": disk.percent,
                "memory_available": memory.available / 1024 / 1024,  # MB
                "disk_free": disk.free / 1024 / 1024 / 1024  # GB
            },
            "overall_status": "healthy" if all(s["status"] == "online" for s in service_status.values()) else "degraded"
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "overall_status": "error"
        }


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
