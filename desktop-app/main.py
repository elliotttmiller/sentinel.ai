from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
from loguru import logger
from agent_logic import (
    run_simple_agent_task,
    run_advanced_mission,
    AgentRole,
    validate_agent_type,
    get_agent_capabilities,
)
from db import SessionLocal, Mission
from datetime import datetime
import platform
import psutil
import os
from typing import List, Optional

app = FastAPI(title="Sentinel Desktop App (Local-Only)")

# Mount static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


class AgentRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    agent_type: Optional[str] = "researcher"


class MissionResponse(BaseModel):
    id: int
    title: Optional[str]
    prompt: str
    agent_type: str
    status: str
    result: Optional[str]
    error_message: Optional[str]
    execution_time: Optional[int]
    tokens_used: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class SystemStats(BaseModel):
    os: str
    python: str
    cpu: str
    ram: str
    llm: str
    status: str
    disk_usage: Optional[str] = None
    network_status: Optional[str] = None


@app.get("/", response_class=FileResponse)
def serve_web_ui():
    """Serves the main index.html file as the user interface."""
    return FileResponse("index.html")


@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    """
    Receives a prompt from the web UI, runs the agent task, and returns the result.
    Enhanced to support mission tracking and database storage.
    """
    logger.info(f"Received request to run agent with prompt: {request.prompt}")

    db = SessionLocal()
    try:
        # Create mission record
        mission = Mission(
            title=request.title,
            prompt=request.prompt,
            agent_type=request.agent_type,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)

        logger.info(f"Created mission {mission.id}")

        # Update status to executing
        mission.status = "executing"
        mission.updated_at = datetime.utcnow()
        db.commit()

        # Run the agent task (use advanced mission system for complex tasks)
        loop = asyncio.get_running_loop()

        # Determine if this should use advanced mission system
        if len(request.prompt) > 100 or request.agent_type in ["developer", "analyst", "qa"]:
            # Use advanced mission system
            agent_result = await loop.run_in_executor(
                None, run_advanced_mission, request.prompt, str(mission.id)
            )
        else:
            # Use simple agent task
            agent_result = await loop.run_in_executor(
                None, run_simple_agent_task, request.prompt, request.agent_type
            )

        # Update mission with result
        mission.status = agent_result["status"]
        mission.result = agent_result["result"]
        mission.execution_time = agent_result["execution_time"]
        mission.agent_type = request.agent_type
        mission.updated_at = datetime.utcnow()

        if agent_result["status"] == "completed":
            mission.completed_at = datetime.utcnow()
        elif agent_result["status"] == "failed":
            mission.error_message = agent_result.get("error", "Unknown error")

        db.commit()

        logger.info(f"Mission {mission.id} completed successfully")

        return {
            "mission_id": mission.id,
            "result": agent_result["result"],
            "status": agent_result["status"],
            "execution_time": agent_result["execution_time"],
            "agent_type": request.agent_type,
        }

    except Exception as e:
        logger.error(f"An error occurred during agent execution: {e}", exc_info=True)

        # Update mission with error
        if "mission" in locals():
            mission.status = "failed"
            mission.result = str(e)
            mission.updated_at = datetime.utcnow()
            db.commit()

        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/missions", response_model=List[MissionResponse])
def list_missions():
    """Returns all missions from the database."""
    db = SessionLocal()
    try:
        missions = db.query(Mission).order_by(Mission.created_at.desc()).all()
        return [
            MissionResponse(
                id=m.id,
                title=m.title,
                prompt=m.prompt,
                agent_type=m.agent_type,
                status=m.status,
                result=m.result,
                error_message=m.error_message,
                execution_time=m.execution_time,
                tokens_used=m.tokens_used,
                created_at=m.created_at,
                updated_at=m.updated_at,
                completed_at=m.completed_at,
            )
            for m in missions
        ]
    except Exception as e:
        logger.error(f"Error fetching missions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch missions")
    finally:
        db.close()


@app.get("/mission/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int):
    """Returns a specific mission by ID."""
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        return MissionResponse(
            id=mission.id,
            title=mission.title,
            prompt=mission.prompt,
            agent_type=mission.agent_type,
            status=mission.status,
            result=mission.result,
            error_message=mission.error_message,
            execution_time=mission.execution_time,
            tokens_used=mission.tokens_used,
            created_at=mission.created_at,
            updated_at=mission.updated_at,
            completed_at=mission.completed_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mission {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mission")
    finally:
        db.close()


@app.get("/system-stats", response_model=SystemStats)
def system_stats():
    """Returns comprehensive system statistics."""
    try:
        # Get system information
        os_info = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()
        cpu_info = platform.processor()

        # Get memory usage
        memory = psutil.virtual_memory()
        ram_usage = f"{round(memory.used / (1024**3), 2)}GB / {round(memory.total / (1024**3), 2)}GB ({memory.percent}%)"

        # Get disk usage
        disk = psutil.disk_usage("/")
        disk_usage = f"{round(disk.used / (1024**3), 2)}GB / {round(disk.total / (1024**3), 2)}GB ({round(disk.percent, 1)}%)"

        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_info = f"{cpu_info} ({cpu_percent}%)"

        # Check network connectivity
        try:
            import socket

            socket.create_connection(("8.8.8.8", 53), timeout=3)
            network_status = "Connected"
        except OSError:
            network_status = "Disconnected"

        return SystemStats(
            os=os_info,
            python=python_version,
            cpu=cpu_info,
            ram=ram_usage,
            llm="Gemini 1.5 Pro",
            status="Online",
            disk_usage=disk_usage,
            network_status=network_status,
        )
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {"database": "connected", "llm": "available", "system": "operational"},
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/api/status")
def api_status():
    """Returns API status and version information."""
    return {
        "name": "Sentinel Desktop API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/",
            "/run-agent",
            "/missions",
            "/mission/{id}",
            "/system-stats",
            "/health",
            "/api/status",
            "/agents/capabilities",
            "/agents/validate",
            "/advanced-mission",
        ],
    }


@app.get("/agents/capabilities")
def get_agent_capabilities_endpoint():
    """Returns capabilities of all available agent types."""
    return {
        "available_agents": {
            "researcher": get_agent_capabilities("researcher"),
            "developer": get_agent_capabilities("developer"),
            "analyst": get_agent_capabilities("analyst"),
            "qa": get_agent_capabilities("qa"),
            "debugger": get_agent_capabilities("debugger"),
            "documentation": get_agent_capabilities("documentation"),
        }
    }


@app.post("/agents/validate")
def validate_agent_type_endpoint(request: dict):
    """Validate if an agent type is supported."""
    agent_type = request.get("agent_type", "")
    is_valid = validate_agent_type(agent_type)
    return {
        "agent_type": agent_type,
        "valid": is_valid,
        "capabilities": get_agent_capabilities(agent_type) if is_valid else None,
    }


@app.post("/advanced-mission")
async def run_advanced_mission_endpoint(request: AgentRequest):
    """Run an advanced mission with full planning and execution."""
    logger.info(f"Received advanced mission request: {request.prompt}")

    db = SessionLocal()
    try:
        # Create mission record
        mission = Mission(
            title=request.title,
            prompt=request.prompt,
            agent_type=request.agent_type,
            status="planning",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)

        logger.info(f"Created advanced mission {mission.id}")

        # Update status to executing
        mission.status = "executing"
        mission.updated_at = datetime.utcnow()
        db.commit()

        # Run the advanced mission
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, run_advanced_mission, request.prompt, str(mission.id)
        )

        # Update mission with result
        mission.status = "completed" if result["status"] == "completed" else "failed"
        mission.result = str(result["result"])
        mission.execution_time = result["execution_time"]
        mission.updated_at = datetime.utcnow()

        if result["status"] == "completed":
            mission.completed_at = datetime.utcnow()
        elif result["status"] == "failed":
            mission.error_message = result.get("error", "Unknown error")

        db.commit()

        logger.info(f"Advanced mission {mission.id} completed")

        return {
            "mission_id": mission.id,
            "result": result["result"],
            "status": result["status"],
            "execution_time": result["execution_time"],
        }

    except Exception as e:
        logger.error(f"Advanced mission failed: {e}")

        # Update mission with error
        if "mission" in locals():
            mission.status = "failed"
            mission.error_message = str(e)
            mission.updated_at = datetime.utcnow()
            db.commit()

        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.delete("/mission/{mission_id}")
def delete_mission(mission_id: int):
    """Deletes a mission by ID."""
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        db.delete(mission)
        db.commit()

        logger.info(f"Deleted mission {mission_id}")
        return {"message": f"Mission {mission_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting mission {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete mission")
    finally:
        db.close()


@app.put("/mission/{mission_id}")
def update_mission(mission_id: int, request: AgentRequest):
    """Updates a mission's prompt and re-runs it."""
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")

        # Update mission
        mission.prompt = request.prompt
        mission.status = "pending"
        mission.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Updated mission {mission_id}")

        # Re-run the mission
        return run_agent(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating mission {mission_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update mission")
    finally:
        db.close()


# Startup event


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("Sentinel Desktop App starting up...")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info("Application startup complete.")


# Shutdown event


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Sentinel Desktop App shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
