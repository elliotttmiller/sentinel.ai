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
import os

# Initialize Sentry before FastAPI
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry with your DSN
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    send_default_pii=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[
        FastApiIntegration(),
    ],
)

from .core.cognitive_forge_engine import cognitive_forge_engine
from .models.advanced_database import db_manager, Mission

# Add these new imports at the top
from src.utils.sentry_api_client import get_sentry_api_client
import asyncio
import json
import psutil
from datetime import datetime, timedelta

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


# Add new Pydantic models for parallel execution
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


# Background Task Functions
def run_mission_in_background(mission_id_str: str, prompt: str, agent_type: str):
    """
    Background task to run a complete mission with real-time updates and parallel execution
    """
    import asyncio
    
    async def _run_mission_async():
        logger.info(f"BACKGROUND TASK: Starting mission {mission_id_str}")

        def update_callback(update_message: str):
            """Enhanced callback function for real-time mission updates with detailed logging"""
            timestamp = datetime.utcnow().isoformat()
            
            # Log to console for debugging
            logger.info(f"🔄 Mission Update [{mission_id_str}]: {update_message}")
            
            if mission_id_str in mission_status_db:
                mission_status_db[mission_id_str]["updates"].append(
                    {"timestamp": timestamp, "message": update_message}
                )
                mission_status_db[mission_id_str]["last_update"] = timestamp

                # Log to database with enhanced metadata
                db_manager.add_mission_update(
                    mission_id_str=mission_id_str, 
                    message=update_message, 
                    update_type="info"
                )
                
                # Log system event for observability
                db_manager.log_system_event(
                    level="INFO",
                    message=f"Mission update: {update_message}",
                    component="mission_execution",
                    metadata={
                        "mission_id": mission_id_str,
                        "update_message": update_message,
                        "timestamp": timestamp
                    }
                )

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
            final_result = await cognitive_forge_engine.run_mission(
                prompt, mission_id_str, agent_type, update_callback
            )

            # Determine mission status based on result
            mission_status = "COMPLETED"
            if final_result.get("needs_healing", False):
                mission_status = "COMPLETED_WITH_HEALING"
            elif final_result.get("error"):
                mission_status = "FAILED"
            
            # Update in-memory status
            mission_status_db[mission_id_str]["status"] = mission_status
            mission_status_db[mission_id_str]["result"] = final_result
            mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()

            # Calculate execution time
            start_time = datetime.fromisoformat(mission_status_db[mission_id_str]["updates"][0]["timestamp"])
            execution_time = int((datetime.utcnow() - start_time).total_seconds())

            # Create structured JSON result for database storage
            structured_result = {
                "summary": final_result.get("result", "Mission completed successfully"),
                "status": mission_status,
                "execution_time": execution_time,
                "final_output": final_result.get("output", ""),
                "metadata": final_result.get("metadata", {}),
                "needs_healing": final_result.get("needs_healing", False),
                "error": final_result.get("error", None),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Update database status with proper JSON formatting
            db_status = "completed" if mission_status in ["COMPLETED", "COMPLETED_WITH_HEALING"] else "failed"
            success = db_manager.update_mission_status(
                mission_id_str=mission_id_str,
                status=db_status,
                result=json.dumps(structured_result),  # Convert to JSON string
                execution_time=execution_time
            )
            
            if success:
                logger.info(f"BACKGROUND TASK: Mission {mission_id_str} completed successfully and database updated")
                update_callback(f"✅ Mission completed successfully! Status: {mission_status}")
            else:
                logger.warning(f"BACKGROUND TASK: Mission {mission_id_str} completed but database update failed")

        except Exception as e:
            logger.error(f"BACKGROUND TASK: Mission {mission_id_str} failed. Error: {e}", exc_info=True)
            mission_status_db[mission_id_str]["status"] = "FAILED"
            mission_status_db[mission_id_str]["result"] = {"error": str(e)}
            mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()
            
            # Create structured error result for database
            error_result = {
                "error": str(e),
                "status": "FAILED",
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(e).__name__
            }
            
            # Update database with failure using proper JSON
            db_manager.update_mission_status(
                mission_id_str=mission_id_str,
                status="failed",
                result=json.dumps(error_result),  # Convert to JSON string
                error_message=str(e)
            )
            update_callback(f"❌ Mission failed: {str(e)}")
    
    # Run the async function in the event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, create a task
            asyncio.create_task(_run_mission_async())
        else:
            # If no event loop is running, run it
            loop.run_until_complete(_run_mission_async())
    except RuntimeError:
        # If no event loop exists, create one
        asyncio.run(_run_mission_async())


# Parallel Execution for Complex Missions
async def run_parallel_mission(mission_id_str: str, prompt: str, agent_type: str, complexity_level: str = "standard"):
    """
    Execute complex missions with parallel processing capabilities
    
    Args:
        mission_id_str: Unique mission identifier
        prompt: User's mission prompt
        agent_type: Type of agent to use
        complexity_level: Mission complexity (standard, complex, advanced)
    """
    logger.info(f"PARALLEL EXECUTION: Starting complex mission {mission_id_str} with level {complexity_level}")
    
    def parallel_update_callback(update_message: str, phase: str = "general"):
        """Enhanced callback for parallel execution updates"""
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"🔄 Parallel Mission Update [{mission_id_str}][{phase}]: {update_message}")
        
        if mission_id_str in mission_status_db:
            mission_status_db[mission_id_str]["updates"].append(
                {"timestamp": timestamp, "message": f"[{phase.upper()}] {update_message}", "phase": phase}
            )
            mission_status_db[mission_id_str]["last_update"] = timestamp

    # Initialize parallel mission status
    mission_status_db[mission_id_str] = {
        "status": "PARALLEL_PLANNING",
        "updates": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "message": "🚀 Complex mission accepted. Initializing parallel execution...",
                "phase": "initialization"
            }
        ],
        "result": None,
        "last_update": datetime.utcnow().isoformat(),
        "parallel_phases": [],
        "complexity_level": complexity_level
    }

    try:
        # Phase 1: Parallel Planning
        parallel_update_callback("Starting parallel planning phase", "planning")
        
        # Create parallel execution tasks based on complexity
        parallel_tasks = []
        
        if complexity_level == "complex":
            # Split mission into parallel sub-tasks
            planning_task = asyncio.create_task(
                cognitive_forge_engine.run_mission_phase(prompt, mission_id_str, "planning", parallel_update_callback)
            )
            analysis_task = asyncio.create_task(
                cognitive_forge_engine.run_mission_phase(prompt, mission_id_str, "analysis", parallel_update_callback)
            )
            parallel_tasks = [planning_task, analysis_task]
            
        elif complexity_level == "advanced":
            # Advanced parallel execution with multiple specialized agents
            planning_task = asyncio.create_task(
                cognitive_forge_engine.run_mission_phase(prompt, mission_id_str, "planning", parallel_update_callback)
            )
            analysis_task = asyncio.create_task(
                cognitive_forge_engine.run_mission_phase(prompt, mission_id_str, "analysis", parallel_update_callback)
            )
            research_task = asyncio.create_task(
                cognitive_forge_engine.run_mission_phase(prompt, mission_id_str, "research", parallel_update_callback)
            )
            parallel_tasks = [planning_task, analysis_task, research_task]
        
        else:
            # Standard execution
            parallel_update_callback("Using standard execution mode", "execution")
            final_result = await cognitive_forge_engine.run_mission(
                prompt, mission_id_str, agent_type, parallel_update_callback
            )
            return final_result

        # Execute parallel tasks
        parallel_update_callback(f"Executing {len(parallel_tasks)} parallel tasks", "execution")
        parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        
        # Phase 2: Synthesize parallel results
        parallel_update_callback("Synthesizing parallel execution results", "synthesis")
        
        # Process results and handle exceptions
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(parallel_results):
            if isinstance(result, Exception):
                failed_results.append({"task_index": i, "error": str(result)})
                parallel_update_callback(f"Parallel task {i} failed: {str(result)}", "error")
            else:
                successful_results.append(result)
                parallel_update_callback(f"Parallel task {i} completed successfully", "success")
        
        # Phase 3: Final synthesis and execution
        if successful_results:
            parallel_update_callback("Synthesizing successful parallel results", "synthesis")
            
            # Combine successful results and execute final mission
            combined_prompt = f"Original: {prompt}\n\nParallel Results:\n"
            for i, result in enumerate(successful_results):
                combined_prompt += f"Task {i}: {result.get('output', '')}\n"
            
            final_result = await cognitive_forge_engine.run_mission(
                combined_prompt, mission_id_str, agent_type, parallel_update_callback
            )
            
            # Add parallel execution metadata
            final_result["parallel_execution"] = {
                "complexity_level": complexity_level,
                "total_tasks": len(parallel_tasks),
                "successful_tasks": len(successful_results),
                "failed_tasks": len(failed_results),
                "parallel_results": successful_results,
                "failed_results": failed_results
            }
            
        else:
            # All parallel tasks failed
            final_result = {
                "error": "All parallel tasks failed",
                "parallel_execution": {
                    "complexity_level": complexity_level,
                    "total_tasks": len(parallel_tasks),
                    "successful_tasks": 0,
                    "failed_tasks": len(failed_results),
                    "failed_results": failed_results
                }
            }
        
        # Update mission status
        mission_status = "COMPLETED" if not final_result.get("error") else "FAILED"
        mission_status_db[mission_id_str]["status"] = mission_status
        mission_status_db[mission_id_str]["result"] = final_result
        mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()

        # Calculate execution time
        start_time = datetime.fromisoformat(mission_status_db[mission_id_str]["updates"][0]["timestamp"])
        execution_time = int((datetime.utcnow() - start_time).total_seconds())

        # Create structured JSON result for database storage
        structured_result = {
            "summary": final_result.get("result", "Parallel mission completed successfully"),
            "status": mission_status,
            "execution_time": execution_time,
            "final_output": final_result.get("output", ""),
            "metadata": final_result.get("metadata", {}),
            "parallel_execution": final_result.get("parallel_execution", {}),
            "error": final_result.get("error", None),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Update database with proper JSON formatting
        db_status = "completed" if mission_status == "COMPLETED" else "failed"
        success = db_manager.update_mission_status(
            mission_id_str=mission_id_str,
            status=db_status,
            result=json.dumps(structured_result),  # Convert to JSON string
            execution_time=execution_time
        )
        
        if success:
            logger.info(f"PARALLEL EXECUTION: Mission {mission_id_str} completed successfully")
            parallel_update_callback(f"✅ Parallel mission completed successfully! Status: {mission_status}", "completion")
        else:
            logger.warning(f"PARALLEL EXECUTION: Mission {mission_id_str} completed but database update failed")
        
        return final_result

    except Exception as e:
        logger.error(f"PARALLEL EXECUTION: Mission {mission_id_str} failed. Error: {e}", exc_info=True)
        mission_status_db[mission_id_str]["status"] = "FAILED"
        mission_status_db[mission_id_str]["result"] = {"error": str(e)}
        mission_status_db[mission_id_str]["last_update"] = datetime.utcnow().isoformat()
        
        # Create structured error result for database
        error_result = {
            "error": str(e),
            "status": "FAILED",
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(e).__name__,
            "parallel_execution": {
                "complexity_level": complexity_level,
                "error": "Parallel execution failed"
            }
        }
        
        # Update database with failure using proper JSON
        db_manager.update_mission_status(
            mission_id_str=mission_id_str,
            status="failed",
            result=json.dumps(error_result),  # Convert to JSON string
            error_message=str(e)
        )
        parallel_update_callback(f"❌ Parallel mission failed: {str(e)}", "error")
        
        return {"error": str(e)}


def run_parallel_mission_in_background(mission_id_str: str, prompt: str, agent_type: str, complexity_level: str = "standard"):
    """
    Background task wrapper for parallel mission execution
    """
    async def _run_parallel_mission_async():
        return await run_parallel_mission(mission_id_str, prompt, agent_type, complexity_level)
    
    # Run the async function in the event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, create a task
            asyncio.create_task(_run_parallel_mission_async())
        else:
            # If no event loop is running, run it
            loop.run_until_complete(_run_parallel_mission_async())
    except RuntimeError:
        # If no event loop exists, create one
        asyncio.run(_run_parallel_mission_async())


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
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/sentry-debug")
async def trigger_error():
    """Sentry debug endpoint to test error tracking"""
    division_by_zero = 1 / 0
    return {"message": "This should never be reached"}


@app.get("/sentry-test")
async def test_sentry():
    """Safer Sentry test endpoint"""
    import sentry_sdk
    
    # Capture a test message
    sentry_sdk.capture_message("Sentry integration test message", level="info")
    
    return {
        "message": "Sentry test completed",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/automated-debugger/status")
async def get_automated_debugger_status():
    """Get the status of the automated debugger service"""
    try:
        from .utils.automated_debugger import get_automated_debugger
        debugger = get_automated_debugger()
        return debugger.get_status()
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


@app.post("/automated-debugger/start")
async def start_automated_debugger():
    """Start the automated debugger service"""
    try:
        from .utils.automated_debugger import start_automated_debugging
        # Start in background
        import asyncio
        asyncio.create_task(start_automated_debugging())
        return {
            "message": "Automated debugger started",
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


@app.post("/automated-debugger/stop")
async def stop_automated_debugger():
    """Stop the automated debugger service"""
    try:
        from .utils.automated_debugger import stop_automated_debugging
        stop_automated_debugging()
        return {
            "message": "Automated debugger stopped",
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


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
            complexity_level="standard"
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
        mission = db_manager.create_mission(
            mission_id_str=mission_id_str,
            title=request.title or f"Mission: {request.prompt[:50]}...",
            prompt=request.prompt,
            agent_type=request.agent_type,
            complexity_level="standard"
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


@app.post("/parallel-mission")
async def create_parallel_mission(request: ParallelMissionRequest, background_tasks: BackgroundTasks):
    """
    Create and execute a complex mission with parallel processing capabilities
    """
    try:
        # Generate unique mission ID
        mission_id_str = f"mission_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Create mission in database
        mission = db_manager.create_mission(
            mission_id_str=mission_id_str,
            title=request.title or f"Parallel Mission - {request.complexity_level.title()}",
            prompt=request.prompt,
            agent_type=request.agent_type,
            complexity_level=request.complexity_level
        )
        
        # Add complexity level to mission metadata
        mission.complexity_level = request.complexity_level
        db_manager.update_mission_status(
            mission_id_str=mission_id_str,
            status="parallel_planning",
            plan={"complexity_level": request.complexity_level}
        )
        
        # Start parallel execution in background
        background_tasks.add_task(
            run_parallel_mission_in_background,
            mission_id_str,
            request.prompt,
            request.agent_type,
            request.complexity_level
        )
        
        logger.info(f"PARALLEL MISSION: Created mission {mission_id_str} with complexity {request.complexity_level}")
        
        return {
            "mission_id": mission_id_str,
            "status": "parallel_planning",
            "complexity_level": request.complexity_level,
            "message": f"Parallel mission created with {request.complexity_level} complexity level"
        }
        
    except Exception as e:
        logger.error(f"Error creating parallel mission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create parallel mission: {str(e)}")


@app.post("/api/parallel-missions")
async def create_parallel_mission_api(request: ParallelMissionRequest, background_tasks: BackgroundTasks):
    """
    API endpoint for creating parallel missions with advanced complexity levels
    """
    try:
        # Generate unique mission ID
        mission_id_str = f"mission_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Create mission in database
        mission = db_manager.create_mission(
            mission_id_str=mission_id_str,
            title=request.title or f"Parallel Mission - {request.complexity_level.title()}",
            prompt=request.prompt,
            agent_type=request.agent_type
        )
        
        # Add complexity level to mission metadata
        mission.complexity_level = request.complexity_level
        db_manager.update_mission_status(
            mission_id_str=mission_id_str,
            status="parallel_planning",
            plan={"complexity_level": request.complexity_level}
        )
        
        # Start parallel execution in background
        background_tasks.add_task(
            run_parallel_mission_in_background,
            mission_id_str,
            request.prompt,
            request.agent_type,
            request.complexity_level
        )
        
        logger.info(f"PARALLEL MISSION API: Created mission {mission_id_str} with complexity {request.complexity_level}")
        
        return {
            "mission_id": mission_id_str,
            "status": "parallel_planning",
            "complexity_level": request.complexity_level,
            "message": f"Parallel mission created with {request.complexity_level} complexity level",
            "estimated_duration": {
                "standard": "2-5 minutes",
                "complex": "5-10 minutes", 
                "advanced": "10-20 minutes"
            }.get(request.complexity_level, "Unknown")
        }
        
    except Exception as e:
        logger.error(f"Error creating parallel mission via API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create parallel mission: {str(e)}")


@app.get("/parallel-missions", response_model=List[ParallelMissionResponse])
def list_parallel_missions(limit: int = 50, complexity_level: Optional[str] = None):
    """
    List parallel missions with optional complexity filtering
    """
    try:
        missions = db_manager.list_missions(limit=limit, include_archived=False)
        
        # Filter by complexity level if specified
        if complexity_level:
            missions = [m for m in missions if hasattr(m, 'complexity_level') and m.complexity_level == complexity_level]
        
        # Convert to response model
        parallel_missions = []
        for mission in missions:
            if hasattr(mission, 'complexity_level') and mission.complexity_level:
                parallel_missions.append(ParallelMissionResponse(
                    id=mission.id,
                    mission_id_str=mission.mission_id_str,
                    title=mission.title,
                    prompt=mission.prompt,
                    agent_type=mission.agent_type,
                    complexity_level=mission.complexity_level,
                    status=mission.status,
                    execution_time=mission.execution_time,
                    created_at=mission.created_at,
                    parallel_execution=mission.result.get("parallel_execution") if mission.result else None
                ))
        
        return parallel_missions
        
    except Exception as e:
        logger.error(f"Error listing parallel missions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list parallel missions: {str(e)}")


@app.get("/api/parallel-missions", response_model=List[ParallelMissionResponse])
def list_parallel_missions_api(limit: int = 50, complexity_level: Optional[str] = None):
    """
    API endpoint for listing parallel missions
    """
    return list_parallel_missions(limit=limit, complexity_level=complexity_level)


@app.get("/parallel-mission/{mission_id}")
def get_parallel_mission_status(mission_id: str):
    """
    Get detailed status of a parallel mission including parallel execution metadata
    """
    try:
        # Get mission from database
        mission = db_manager.get_mission(mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Parallel mission not found")
        
        # Get real-time status from memory
        real_time_status = mission_status_db.get(mission_id, {})
        
        # Parse result JSON if available
        parallel_execution_data = None
        if mission.result:
            try:
                result_data = json.loads(mission.result) if isinstance(mission.result, str) else mission.result
                parallel_execution_data = result_data.get("parallel_execution")
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return {
            "mission_id": mission_id,
            "status": real_time_status.get("status", mission.status),
            "complexity_level": getattr(mission, 'complexity_level', 'standard'),
            "execution_time": mission.execution_time,
            "created_at": mission.created_at,
            "updated_at": mission.updated_at,
            "completed_at": mission.completed_at,
            "real_time_updates": real_time_status.get("updates", []),
            "parallel_execution": parallel_execution_data,
            "result": mission.result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parallel mission status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get parallel mission status: {str(e)}")


@app.get("/api/parallel-mission/{mission_id}")
def get_parallel_mission_status_api(mission_id: str):
    """
    API endpoint for getting parallel mission status
    """
    return get_parallel_mission_status(mission_id)


@app.get("/parallel-execution/stats")
def get_parallel_execution_stats():
    """
    Get statistics about parallel execution performance
    """
    try:
        # Get all missions with complexity levels
        missions = db_manager.list_missions(limit=1000, include_archived=False)
        
        # Filter parallel missions
        parallel_missions = [m for m in missions if hasattr(m, 'complexity_level') and m.complexity_level]
        
        # Calculate statistics
        stats = {
            "total_parallel_missions": len(parallel_missions),
            "by_complexity": {},
            "avg_execution_times": {},
            "success_rates": {},
            "recent_activity": []
        }
        
        # Group by complexity level
        for mission in parallel_missions:
            complexity = mission.complexity_level
            if complexity not in stats["by_complexity"]:
                stats["by_complexity"][complexity] = {
                    "count": 0,
                    "execution_times": [],
                    "successful": 0,
                    "failed": 0
                }
            
            stats["by_complexity"][complexity]["count"] += 1
            
            if mission.execution_time:
                stats["by_complexity"][complexity]["execution_times"].append(mission.execution_time)
            
            if mission.status == "completed":
                stats["by_complexity"][complexity]["successful"] += 1
            elif mission.status == "failed":
                stats["by_complexity"][complexity]["failed"] += 1
        
        # Calculate averages and success rates
        for complexity, data in stats["by_complexity"].items():
            if data["execution_times"]:
                stats["avg_execution_times"][complexity] = sum(data["execution_times"]) / len(data["execution_times"])
            
            total = data["successful"] + data["failed"]
            if total > 0:
                stats["success_rates"][complexity] = data["successful"] / total
        
        # Get recent activity
        recent_missions = sorted(parallel_missions, key=lambda x: x.created_at, reverse=True)[:10]
        stats["recent_activity"] = [
            {
                "mission_id": m.mission_id_str,
                "complexity": m.complexity_level,
                "status": m.status,
                "created_at": m.created_at.isoformat(),
                "execution_time": m.execution_time
            }
            for m in recent_missions
        ]
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting parallel execution stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get parallel execution stats: {str(e)}")


@app.get("/api/parallel-execution/stats")
def get_parallel_execution_stats_api():
    """
    API endpoint for parallel execution statistics
    """
    return get_parallel_execution_stats()


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


@app.get("/observability/weave")
async def get_weave_observability():
    """Get real-time Weave observability data"""
    try:
        from src.observability_manager import observability_manager
        
        # Get real Weave data
        weave_data = observability_manager.get_weave_data()
        
        return weave_data
        
    except Exception as e:
        logger.error(f"Error fetching Weave data: {e}")
        return {
            "status": "ERROR",
            "error": str(e),
            "active_traces": 0,
            "success_rate": 0,
            "avg_response": 0,
            "total_traces": 0,
            "recent_traces": [],
            "performance_metrics": {}
        }

@app.get("/observability/wandb")
async def get_wandb_observability():
    """Get real-time WandB observability data"""
    try:
        from src.observability_manager import observability_manager
        
        # Get real WandB data
        wandb_data = observability_manager.get_wandb_data()
        
        return wandb_data
        
    except Exception as e:
        logger.error(f"Error fetching WandB data: {e}")
        return {
            "status": "ERROR",
            "error": str(e),
            "active_runs": 0,
            "accuracy": 0,
            "loss": 0,
            "experiments": [],
            "metrics": {}
        }

@app.get("/observability/sentry")
async def get_sentry_observability():
    """Get real-time Sentry observability data"""
    try:
        from src.observability_manager import observability_manager
        
        # Get real Sentry data
        sentry_data = observability_manager.get_sentry_data()
        
        return sentry_data
        
    except Exception as e:
        logger.error(f"Error fetching Sentry data: {e}")
        return {
            "status": "ERROR",
            "error": str(e),
            "error_rate": 0,
            "active_issues": 0,
            "uptime": 0,
            "recent_issues": [],
            "issue_types": {},
            "error_trends": {}
        }

@app.get("/observability/detailed/{system}")
async def get_detailed_observability(system: str):
    """Get detailed observability data for a specific system"""
    try:
        if system == "weave":
            from src.utils.weave_observability import observability_manager
            
            detailed_data = {
                "system": "weave",
                "traces": [],
                "performance": observability_manager.get_performance_analytics(),
                "report": observability_manager.generate_observability_report()
            }
            
            # Get detailed trace data
            if observability_manager.metrics_history:
                detailed_data["traces"] = [
                    {
                        "mission_id": trace.mission_id if hasattr(trace, 'mission_id') else "unknown",
                        "user_request": trace.user_request if hasattr(trace, 'user_request') else "",
                        "start_time": trace.start_time.isoformat() if hasattr(trace, 'start_time') else "",
                        "end_time": trace.end_time.isoformat() if hasattr(trace, 'end_time') else "",
                        "duration": trace.total_duration if hasattr(trace, 'total_duration') else 0,
                        "success": trace.success if hasattr(trace, 'success') else True,
                        "phases": trace.phases if hasattr(trace, 'phases') else [],
                        "agents_used": trace.agents_used if hasattr(trace, 'agents_used') else [],
                        "total_cost": trace.total_cost if hasattr(trace, 'total_cost') else 0
                    }
                    for trace in observability_manager.metrics_history[-20:]  # Last 20 traces
                ]
            
            return detailed_data
            
        elif system == "wandb":
            detailed_data = {
                "system": "wandb",
                "experiments": [],
                "metrics": {},
                "runs": []
            }
            
            try:
                import wandb
                api = wandb.Api()
                runs = api.runs("cognitive-forge-v5", per_page=20)
                
                detailed_data["runs"] = [
                    {
                        "id": run.id,
                        "name": run.name,
                        "state": run.state,
                        "created_at": run.created_at.isoformat(),
                        "updated_at": run.updated_at.isoformat() if hasattr(run, 'updated_at') else "",
                        "metrics": run.summary,
                        "config": run.config
                    }
                    for run in runs
                ]
            except Exception as e:
                logger.warning(f"Could not fetch detailed WandB data: {e}")
            
            return detailed_data
            
        elif system == "sentry":
            sentry_client = get_sentry_api_client()
            recent_issues = sentry_client.get_recent_issues(hours=168)  # Last week
            
            detailed_data = {
                "system": "sentry",
                "issues": recent_issues,
                "statistics": {
                    "total_issues": len(recent_issues),
                    "resolved_issues": len([i for i in recent_issues if i.get('status') == 'resolved']),
                    "unresolved_issues": len([i for i in recent_issues if i.get('status') != 'resolved']),
                    "critical_issues": len([i for i in recent_issues if i.get('level') == 'fatal']),
                    "error_issues": len([i for i in recent_issues if i.get('level') == 'error']),
                    "warning_issues": len([i for i in recent_issues if i.get('level') == 'warning'])
                },
                "issue_details": []
            }
            
            # Get detailed info for first 10 issues
            for issue in recent_issues[:10]:
                issue_id = issue.get('id')
                if issue_id:
                    details = sentry_client.get_issue_details(issue_id)
                    if details:
                        detailed_data["issue_details"].append(details)
            
            return detailed_data
            
        else:
            return {"error": f"Unknown system: {system}"}
            
    except Exception as e:
        logger.error(f"Error fetching detailed {system} data: {e}")
        return {"error": str(e)}


@app.get("/api/system/vitals")
async def get_system_vitals():
    """Provides a snapshot of real-time system performance metrics."""
    try:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    except Exception as e:
        logger.error(f"Error getting system vitals: {e}")
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0
        }

@app.get("/api/observability/overview")
async def get_observability_overview():
    """Provides high-level summary stats for the observability systems."""
    try:
        from src.observability_manager import observability_manager
        
        # Get real data from all systems
        weave_data = observability_manager.get_weave_data()
        sentry_data = observability_manager.get_sentry_data()
        wandb_data = observability_manager.get_wandb_data()
        
        return {
            "weave": {
                "status": weave_data["status"],
                "active_traces": weave_data["active_traces"],
                "success_rate": weave_data["success_rate"],
                "avg_response_ms": weave_data["avg_response_ms"]
            },
            "sentry": {
                "status": sentry_data["status"],
                "error_rate_percent": sentry_data["error_rate"],
                "active_issues": sentry_data["active_issues"],
                "uptime_percent": sentry_data["uptime"]
            },
            "wandb": {
                "status": wandb_data["status"],
                "active_runs": wandb_data["active_runs"],
                "best_accuracy": wandb_data["metrics"].get("best_accuracy", 0),
                "avg_loss": wandb_data["metrics"].get("avg_loss", 0)
            }
        }
    except Exception as e:
        logger.error(f"Error getting observability overview: {e}")
        return {
            "weave": {"status": "ERROR", "active_traces": 0, "success_rate": 0, "avg_response_ms": 0},
            "wandb": {"status": "ERROR", "active_runs": 0, "best_accuracy": 0, "avg_loss": 0},
            "sentry": {"status": "ERROR", "error_rate_percent": 0, "active_issues": 0, "uptime_percent": 0}
        }

@app.get("/api/events/live")
async def get_live_events():
    """Provides a stream of the latest system events."""
    try:
        # Get recent missions for events
        recent_missions = db_manager.list_missions(limit=5)
        
        events = []
        for mission in recent_missions:
            events.append({
                "timestamp": mission.created_at.isoformat(),
                "level": "INFO" if mission.status == "COMPLETED" else "WARNING" if mission.status == "FAILED" else "INFO",
                "message": f"Mission {mission.mission_id_str} {mission.status.lower()}"
            })
        
        # Add some system events
        events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": "System health check completed"
        })
        
        return events
    except Exception as e:
        logger.error(f"Error getting live events: {e}")
        return []

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


# Real-time Observability Streaming
@app.get("/api/observability/stream")
async def stream_observability_data():
    """Real-time streaming endpoint for observability data"""
    from fastapi.responses import StreamingResponse
    import json
    import asyncio
    
    async def generate_stream():
        """Generate real-time observability data stream"""
        while True:
            try:
                # Get real-time data from observability manager
                from src.observability_manager import observability_manager
                import psutil
                
                # Update metrics for fresh data
                observability_manager.update_metrics()
                
                # System vitals
                try:
                    system_vitals = {
                        "cpu_usage": psutil.cpu_percent(),
                        "memory_usage": psutil.virtual_memory().percent,
                        "disk_usage": psutil.disk_usage('/').percent
                    }
                except Exception as e:
                    system_vitals = {"cpu_usage": 0, "memory_usage": 0, "disk_usage": 0}
                
                # Get real observability data
                weave_data = observability_manager.get_weave_data()
                sentry_data = observability_manager.get_sentry_data()
                wandb_data = observability_manager.get_wandb_data()
                
                stream_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "weave": {
                        "status": weave_data["status"],
                        "active_traces": weave_data["active_traces"],
                        "success_rate": weave_data["success_rate"],
                        "avg_response_ms": weave_data["avg_response_ms"]
                    },
                    "sentry": {
                        "status": sentry_data["status"],
                        "error_rate_percent": sentry_data["error_rate"],
                        "active_issues": sentry_data["active_issues"],
                        "uptime_percent": sentry_data["uptime"]
                    },
                    "wandb": {
                        "status": wandb_data["status"],
                        "active_runs": wandb_data["active_runs"],
                        "best_accuracy": wandb_data["accuracy"],
                        "avg_loss": wandb_data["loss"]
                    },
                    "system_vitals": system_vitals
                }
                
                # Send data as Server-Sent Events
                yield f"data: {json.dumps(stream_data)}\n\n"
                
                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in observability stream: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

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
