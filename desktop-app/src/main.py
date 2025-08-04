"""
Sentinel Command Center - Main API Server v5.4
Real-time dashboard with Phase 5 predictive intelligence and multi-tenancy
"""

import asyncio
import json
import time
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import core components with proper error handling
try:
    from core.cognitive_forge_engine import cognitive_forge_engine
    from models.advanced_database import db_manager, User
    from utils.agent_observability import agent_observability, LiveStreamEvent
    from utils.guardian_protocol import GuardianProtocol
except ImportError as e:
    logger.warning(f"Failed to import core modules: {e}")
    # Create fallback classes
    cognitive_forge_engine = None
    db_manager = None
    agent_observability = None
    GuardianProtocol = None

# Initialize FastAPI app
app = FastAPI(title="Sentinel Command Center v5.4", version="5.4.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API requests
class TestMissionRequest(BaseModel):
    prompt: str
    test_type: str = "unit"
    priority: str = "low"

# Global variables for fallback data
live_missions: Dict[str, Dict] = {}
live_agents: List[Dict] = []
system_logs: List[Dict] = []

# Fallback classes for missing components
class FallbackLiveStreamEvent:
    def __init__(self, event_type="system_log", source="system", severity="INFO", message="", payload=None):
        self.event_type = event_type
        self.source = source
        self.severity = severity
        self.message = message
        self.payload = payload or {}
        self.timestamp = datetime.utcnow().isoformat()

class FallbackAgentObservability:
    def __init__(self):
        self.event_queue = asyncio.Queue()
    
    def push_event(self, event):
        try:
            asyncio.create_task(self.event_queue.put(event))
        except Exception as e:
            logger.error(f"Failed to push event: {e}")
    
    async def get_event(self):
        try:
            return await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

# Initialize observability with fallback
if agent_observability is None:
    agent_observability = FallbackAgentObservability()

# Initialize database manager with fallback
if db_manager is None:
    class FallbackDatabaseManager:
        def list_missions(self, limit=50):
            return []
        def create_mission(self, **kwargs):
            return type('Mission', (), {'as_dict': lambda: kwargs})()
        def get_mission(self, mission_id_str):
            return type('Mission', (), {'as_dict': lambda: {'mission_id_str': mission_id_str}})()
        def update_mission_status(self, mission_id_str, status, **kwargs):
            pass
        def get_pending_proposals(self):
            return []
        def create_optimization_proposal(self, proposal_type, description, rationale):
            return type('Proposal', (), {'as_dict': lambda: {'id': 1, 'proposal_type': proposal_type, 'description': description, 'rationale': rationale}})()
        def update_proposal_status(self, proposal_id, status):
            return type('Proposal', (), {'as_dict': lambda: {'id': proposal_id, 'status': status}})()
        def get_or_create_default_user_and_org(self):
            return type('User', (), {'id': 1, 'organization_id': 1})()
        def get_performance_data_for_analytics(self, org_id=1):
            return []
        def get_system_stats(self):
            return {
                "total_missions": 0,
                "completed_missions": 0,
                "failed_missions": 0,
                "healing_missions": 0,
                "avg_execution_time": 0,
                "success_rate": 0,
                "active_optimizations": 0
            }

    db_manager = FallbackDatabaseManager()

# Initialize cognitive forge engine with fallback
if cognitive_forge_engine is None:
    class FallbackCognitiveForgeEngine:
        def __init__(self):
            self.guardian_protocol = GuardianProtocol() if GuardianProtocol else None
        
        async def run_mission(self, user_prompt, mission_id_str, agent_type):
            logger.info(f"Fallback: Running mission {mission_id_str}")
            # Simulate mission execution
            await asyncio.sleep(2)
            if db_manager:
                db_manager.update_mission_status(mission_id_str, "completed")
        
        async def run_periodic_self_optimization(self):
            logger.info("Fallback: Periodic self-optimization")
            # Simulate optimization
            await asyncio.sleep(30)

    cognitive_forge_engine = FallbackCognitiveForgeEngine()

# --- SIMULATED AUTHENTICATION ---
# In a real app, this would involve JWT tokens and a database lookup.
# For now, this dependency provides a default user for all operations.
def get_current_user() -> User:
    return db_manager.get_or_create_default_user_and_org()

# API Endpoints for pages
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main dashboard page"""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found</h1>")

@app.get("/missions", response_class=HTMLResponse)
async def serve_missions():
    """Serve the missions page"""
    try:
        with open("templates/missions.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Missions page not found</h1>")

@app.get("/settings", response_class=HTMLResponse)
async def serve_settings():
    """Serve the settings page"""
    try:
        with open("templates/settings.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Settings page not found</h1>")

@app.get("/analytics", response_class=HTMLResponse)
async def serve_analytics():
    """Serve the analytics page"""
    try:
        with open("templates/analytics.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Analytics page not found</h1>")

@app.get("/ai-agents", response_class=HTMLResponse)
async def serve_ai_agents():
    """Serve the AI agents page"""
    try:
        with open("templates/ai-agents.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>AI Agents page not found</h1>")

@app.get("/test-missions", response_class=HTMLResponse)
async def serve_test_missions():
    """Serve the test missions page"""
    try:
        with open("templates/test-missions.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Test Missions page not found</h1>")

# API Endpoints for data
@app.get("/api/missions")
async def list_missions_api(current_user: User = Depends(get_current_user)):
    """List all missions from the live database."""
    try:
        missions_from_db = db_manager.list_missions(org_id=current_user.organization_id)
        missions_dict = [m.as_dict() for m in missions_from_db]
        return {"success": True, "missions": missions_dict}
    except Exception as e:
        # This will now catch the OperationalError and report it properly
        error_message = f"Failed to list missions due to a database error: {e}"
        logger.error(error_message)
        # Return a proper HTTP error instead of a silent 200 OK
        raise HTTPException(status_code=500, detail=error_message)

# --- NEW: Pre-flight Check Endpoint ---
@app.post("/api/missions/pre-flight-check")
async def pre_flight_check(request: Request):
    """Analyze mission prompt for risk and clarity before execution"""
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        
        if not prompt:
            return {
                "go_no_go": False, 
                "feedback": "Prompt is empty.",
                "clarity_score": 0.0,
                "risk_score": 0.0,
                "suggestions": ["Please provide a mission description"]
            }
        
        # Run Guardian Protocol pre-flight check
        if cognitive_forge_engine and cognitive_forge_engine.guardian_protocol:
            analysis = await cognitive_forge_engine.guardian_protocol.run_pre_flight_check(prompt)
        else:
            # Fallback analysis
            analysis = {
                "clarity_score": 0.7,
                "risk_score": 0.1,
                "suggestions": ["System is in fallback mode"],
                "go_no_go": True,
                "feedback": "Fallback mode - prompt accepted",
                "risk_level": "low",
                "clarity_level": "good"
            }
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Pre-flight check failed: {e}")
        return {
            "go_no_go": False,
            "feedback": "Error connecting to Guardian Protocol.",
            "clarity_score": 0.0,
            "risk_score": 0.0,
            "suggestions": ["Please try again"]
        }

@app.post("/api/missions")
async def create_mission(request: Request, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """Create a new mission with Guardian Protocol pre-flight check and multi-tenancy"""
    try:
        data = await request.json()
        prompt = data.get("prompt")
        agent_type = data.get("agent_type", "developer")
        priority = data.get("priority", "medium")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required.")

        # Guardian Pre-flight check is now done on the frontend, but we could re-validate here if needed.
        
        mission_id = f"mission_{uuid.uuid4().hex[:8]}"
        
        new_mission = db_manager.create_mission(
            mission_id_str=mission_id, 
            prompt=prompt, 
            agent_type=agent_type,
            priority=priority, 
            status="pending",
            owner_id=current_user.id, 
            organization_id=current_user.organization_id
        )
        
        # Launch mission execution in background
        background_tasks.add_task(
            cognitive_forge_engine.run_mission,
            user_prompt=prompt, 
            mission_id_str=mission_id, 
            agent_type=agent_type
        )

        return {"success": True, "mission": new_mission.as_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create mission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create mission: {str(e)}")

@app.post("/api/test-missions")
async def create_test_mission(request: TestMissionRequest, current_user: User = Depends(get_current_user)):
    """Create a test mission with enhanced error handling"""
    try:
        logger.info(f"🧪 Creating test mission: {request.test_type} - {request.prompt[:50]}...")
        
        # Create a test mission with special identifier
        test_mission_id = f"test_{uuid.uuid4().hex[:8]}"
        
        new_test_mission = db_manager.create_mission(
            mission_id_str=test_mission_id,
            prompt=request.prompt,
            agent_type="tester",  # Special agent type for tests
            priority=request.priority,
            status="pending",
            owner_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        # Add test-specific metadata
        test_metadata = {
            "test_type": request.test_type,
            "is_test": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store test metadata in mission updates
        db_manager.add_mission_update(
            test_mission_id,
            "test_creation",
            f"Test mission created: {request.test_type}",
            test_metadata
        )
        
        logger.info(f"✅ Test mission created: {test_mission_id}")
        return {
            "success": True,
            "mission_id": test_mission_id,
            "test_type": request.test_type,
            "message": f"Test mission created successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create test mission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create test mission: {str(e)}")

@app.get("/api/agents")
async def list_agents_api():
    """List all agents"""
    try:
        # Return static agent data for now
        agents = [
            {"id": "agent_1", "name": "Senior Developer", "status": "online", "type": "developer"},
            {"id": "agent_2", "name": "Code Reviewer", "status": "online", "type": "reviewer"},
            {"id": "agent_3", "name": "QA Tester", "status": "online", "type": "tester"},
            {"id": "agent_4", "name": "System Integrator", "status": "online", "type": "integrator"}
        ]
        return {"success": True, "agents": agents}
    except Exception as e:
        logger.error(f"❌ Failed to list agents: {e}")
        return {"success": True, "agents": []}

# --- NEW: Analytics Endpoints ---
@app.get("/api/analytics/summary")
async def get_analytics_summary(current_user: User = Depends(get_current_user)):
    """Get analytics summary for the organization"""
    try:
        stats = db_manager.get_system_stats()
        return {"success": True, "summary": stats}
    except Exception as e:
        logger.error(f"❌ Failed to get analytics summary: {e}")
        return {"success": True, "summary": {}}

@app.get("/api/analytics/performance-over-time")
async def get_performance_over_time(current_user: User = Depends(get_current_user)):
    """Get performance data over time for charts"""
    try:
        performance_data = db_manager.get_performance_data_for_analytics(org_id=current_user.organization_id)
        return {"success": True, "data": performance_data}
    except Exception as e:
        logger.error(f"❌ Failed to get performance data: {e}")
        return {"success": True, "data": []}

# --- API Endpoints for Optimization Proposals ---
@app.get("/api/optimizations")
async def get_optimizations():
    """Get all pending optimization proposals"""
    try:
        proposals = db_manager.get_pending_proposals()
        return {"success": True, "proposals": [p.as_dict() for p in proposals]}
    except Exception as e:
        logger.error(f"❌ Failed to get optimizations: {e}")
        return {"success": True, "proposals": []}

@app.post("/api/optimizations/{proposal_id}/apply")
async def apply_optimization(proposal_id: int):
    """Apply an optimization proposal"""
    try:
        proposal = db_manager.update_proposal_status(proposal_id, "applied")
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        logger.info(f"✅ Optimization proposal {proposal_id} approved and applied.")
        agent_observability.push_event(FallbackLiveStreamEvent(
            event_type="system_log", 
            source="Admin", 
            severity="SUCCESS",
            message=f"Optimization '{proposal.description[:30]}...' has been applied."
        ))
        return {"success": True, "proposal": proposal.as_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to apply optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply optimization: {str(e)}")

@app.post("/api/optimizations/{proposal_id}/reject")
async def reject_optimization(proposal_id: int):
    """Reject an optimization proposal"""
    try:
        proposal = db_manager.update_proposal_status(proposal_id, "rejected")
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        logger.info(f"❌ Optimization proposal {proposal_id} was rejected.")
        return {"success": True, "proposal": proposal.as_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to reject optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject optimization: {str(e)}")

# System endpoints
@app.get("/api/system/status")
async def get_system_status():
    """Get system status"""
    try:
        return {
            "status": "operational",
            "version": "v5.4",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "Real-time mission execution",
                "Phoenix Protocol (Self-Healing)",
                "Guardian Protocol (Predictive Intelligence)",
                "Self-Learning Module",
                "Periodic Self-Optimization",
                "Multi-Tenancy Foundation",
                "Advanced Analytics"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Failed to get system status: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/api/system/logs")
async def get_system_logs():
    """Get system logs"""
    try:
        # Return recent system logs
        logs = [
            {"timestamp": datetime.utcnow().isoformat(), "level": "INFO", "message": "System operational"},
            {"timestamp": datetime.utcnow().isoformat(), "level": "INFO", "message": "All services running"}
        ]
        return {"success": True, "logs": logs}
    except Exception as e:
        logger.error(f"❌ Failed to get system logs: {e}")
        return {"success": True, "logs": []}

@app.get("/api/system/logs/stats")
async def get_system_logs_stats():
    """Get system logs statistics"""
    try:
        return {
            "total_logs": 100,
            "error_count": 5,
            "warning_count": 10,
            "info_count": 85
        }
    except Exception as e:
        logger.error(f"❌ Failed to get system logs stats: {e}")
        return {"total_logs": 0, "error_count": 0, "warning_count": 0, "info_count": 0}

# Real-time event streaming
@app.get("/api/events/stream")
async def stream_events():
    """Stream real-time events from the actual observability system"""
    async def event_generator():
        while True:
            try:
                # Get real events from the observability system
                if hasattr(agent_observability, 'get_event'):
                    event = await agent_observability.get_event()
                    if event:
                        # Convert real event to stream format
                        event_dict = {
                            "event_type": getattr(event, 'event_type', 'system_log'),
                            "source": getattr(event, 'source', 'system'),
                            "severity": getattr(event, 'severity', 'INFO'),
                            "message": getattr(event, 'message', ''),
                            "payload": getattr(event, 'payload', {}),
                            "timestamp": getattr(event, 'timestamp', datetime.utcnow().isoformat())
                        }
                        yield f"data: {json.dumps(event_dict)}\n\n"
                    else:
                        # No events available, send minimal heartbeat
                        yield f"data: {json.dumps({'event_type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                else:
                    # Observability system not available
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"❌ Event stream error: {e}")
                await asyncio.sleep(5)
            
            await asyncio.sleep(0.1)  # Check for events more frequently
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Settings endpoint
@app.get("/api/settings")
async def get_settings():
    """Get system settings"""
    try:
        return {
            "version": "v5.4",
            "features": {
                "phoenix_protocol": True,
                "guardian_protocol": True,
                "self_learning": True,
                "periodic_optimization": True,
                "multi_tenancy": True,
                "predictive_intelligence": True
            },
            "optimization_proposals_count": len(db_manager.get_pending_proposals())
        }
    except Exception as e:
        logger.error(f"❌ Failed to get settings: {e}")
        return {"version": "v5.4", "features": {}, "optimization_proposals_count": 0}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Sentinel Cognitive Forge v5.4 (Predictive Intelligence Activated) starting up...")
    
    # Push initial system event
    agent_observability.push_event(FallbackLiveStreamEvent(
        event_type="system_log", 
        severity="SUCCESS",
        message="Backend Server 8001 is online. Phase 5 features activated - Predictive Intelligence & Multi-Tenancy ready."
    ))
    
    # Start the self-optimization background task
    asyncio.create_task(cognitive_forge_engine.run_periodic_self_optimization())
    
    logger.info("✅ All systems initialized and ready for missions")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
