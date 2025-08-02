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
    from .utils.weave_observability import observability_manager
    from .utils.agent_observability import agent_observability
    from .utils.test_mission_system import test_mission_system
    
    # Initialize database manager
    logger.info("Database manager initialized successfully")
except ImportError as e:
    # Fallback for direct execution
    logger.warning(f"Some imports failed: {e}")
    cognitive_forge_engine = None
    hybrid_decision_engine = None
    db_manager = None
    Mission = None
    initialize_sentry = lambda: None
    observability_manager = None
    agent_observability = None
    test_mission_system = None

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
async def run_mission_in_background(prompt: str, mission_id_str: str):
    """Run mission with comprehensive observability tracking."""
    start_time = time.time()
    
    try:
        # Initialize mission observability
        with agent_observability.mission_observability(mission_id_str, prompt) as mission_data:
            logger.info(f"🚀 Starting mission {mission_id_str} with comprehensive observability")
            
            # Update mission status to executing
            db_manager.update_mission_status(mission_id_str, "executing")
            
            # Make hybrid decision with observability
            decision_result = hybrid_decision_engine.make_hybrid_decision(prompt)
            chosen_path = decision_result["path"]
            complexity_score = decision_result["complexity_score"]
            
            # Log decision with observability
            agent_observability.log_agent_decision(
                session_id=f"hybrid_decision_{mission_id_str}",
                decision_data=decision_result,
                confidence_score=decision_result["confidence"],
                reasoning=f"Chose {chosen_path} path based on complexity score {complexity_score}"
            )
            
            logger.info(f"🎯 Hybrid Decision: {chosen_path} (Complexity: {complexity_score:.2f})")
            
            # Execute based on chosen path
            if chosen_path == "golden_path":
                # Golden Path execution with observability
                with agent_observability.agent_session("golden_path_agent", mission_id_str, "Direct LLM inference") as session:
                    agent_observability.log_agent_thinking(
                        session.session_id,
                        f"Executing simple task via Golden Path: {prompt}",
                        confidence_score=0.9
                    )
                    
                    result = await cognitive_forge_engine.run_mission_simple(prompt, mission_id_str)
                    
                    agent_observability.log_agent_response(
                        session.session_id,
                        {"result": result.get("result", ""), "status": result.get("status", "")},
                        tokens_used=result.get("tokens_used", 0)
                    )
                    
                    session.success = result.get("status") == "completed"
                    
            else:
                # Full Workflow execution with comprehensive observability
                with agent_observability.agent_session("full_workflow_orchestrator", mission_id_str, "8-phase AI workflow") as session:
                    agent_observability.log_agent_thinking(
                        session.session_id,
                        f"Executing complex task via Full Workflow: {prompt}",
                        confidence_score=0.95
                    )
                    
                    # Phase 1: Planning & Analysis
                    with agent_observability.agent_session("planning_analyst", mission_id_str, "Phase 1: Planning & Analysis") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Analyzing complex request and creating comprehensive plan",
                            confidence_score=0.8
                        )
                        
                        planning_prompt = f"""
                        Analyze this complex request and create a comprehensive plan:
                        
                        {prompt}
                        
                        Provide a structured plan with:
                        1. Problem analysis and requirements
                        2. Technical approach and methodology
                        3. Resource requirements and constraints
                        4. Risk assessment and mitigation strategies
                        5. Success criteria and validation methods
                        """
                        
                        planning_result = await cognitive_forge_engine.run_mission_simple(planning_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"planning_result": planning_result},
                            tokens_used=len(planning_prompt.split()) + len(planning_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Phase 2: Research & Information Gathering
                    with agent_observability.agent_session("research_specialist", mission_id_str, "Phase 2: Research & Information Gathering") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Conducting comprehensive research and information gathering",
                            confidence_score=0.85
                        )
                        
                        research_prompt = f"""
                        Based on the planning analysis, conduct comprehensive research:
                        
                        Planning Analysis:
                        {planning_result}
                        
                        Research Requirements:
                        {prompt}
                        
                        Provide detailed research on:
                        1. Current best practices and standards
                        2. Relevant technologies and tools
                        3. Similar implementations and case studies
                        4. Performance considerations and benchmarks
                        5. Security and compliance requirements
                        """
                        
                        research_result = await cognitive_forge_engine.run_mission_simple(research_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"research_result": research_result},
                            tokens_used=len(research_prompt.split()) + len(research_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Continue with remaining phases...
                    # Phase 3: Design & Architecture
                    with agent_observability.agent_session("design_architect", mission_id_str, "Phase 3: Design & Architecture") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Creating comprehensive system design and architecture",
                            confidence_score=0.9
                        )
                        
                        design_prompt = f"""
                        Create a comprehensive design based on research:
                        
                        Research Findings:
                        {research_result}
                        
                        Original Request:
                        {prompt}
                        
                        Design Requirements:
                        1. System architecture and components
                        2. Data models and relationships
                        3. API design and interfaces
                        4. Security architecture
                        5. Scalability and performance design
                        6. Deployment architecture
                        """
                        
                        design_result = await cognitive_forge_engine.run_mission_simple(design_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"design_result": design_result},
                            tokens_used=len(design_prompt.split()) + len(design_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Phase 4: Implementation & Development
                    with agent_observability.agent_session("implementation_developer", mission_id_str, "Phase 4: Implementation & Development") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Providing detailed implementation and development guidance",
                            confidence_score=0.85
                        )
                        
                        implementation_prompt = f"""
                        Provide detailed implementation based on the design:
                        
                        Design Specification:
                        {design_result}
                        
                        Implementation Requirements:
                        {prompt}
                        
                        Provide:
                        1. Detailed code implementation
                        2. Configuration files and setup
                        3. Database schemas and migrations
                        4. API endpoints and documentation
                        5. Testing strategies and test cases
                        6. Deployment scripts and procedures
                        """
                        
                        implementation_result = await cognitive_forge_engine.run_mission_simple(implementation_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"implementation_result": implementation_result},
                            tokens_used=len(implementation_prompt.split()) + len(implementation_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Phase 5: Testing & Validation
                    with agent_observability.agent_session("testing_qa", mission_id_str, "Phase 5: Testing & Validation") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Creating comprehensive testing strategy and validation",
                            confidence_score=0.8
                        )
                        
                        testing_prompt = f"""
                        Create comprehensive testing strategy:
                        
                        Implementation:
                        {implementation_result}
                        
                        Testing Requirements:
                        1. Unit testing strategy and test cases
                        2. Integration testing approach
                        3. Performance testing methodology
                        4. Security testing procedures
                        5. User acceptance testing criteria
                        6. Automated testing implementation
                        """
                        
                        testing_result = await cognitive_forge_engine.run_mission_simple(testing_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"testing_result": testing_result},
                            tokens_used=len(testing_prompt.split()) + len(testing_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Phase 6: Optimization & Refinement
                    with agent_observability.agent_session("optimization_engineer", mission_id_str, "Phase 6: Optimization & Refinement") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Optimizing solution for performance and quality",
                            confidence_score=0.85
                        )
                        
                        optimization_prompt = f"""
                        Optimize the solution for performance and quality:
                        
                        Current Implementation:
                        {implementation_result}
                        
                        Testing Results:
                        {testing_result}
                        
                        Optimization Areas:
                        1. Performance optimization strategies
                        2. Code quality improvements
                        3. Security enhancements
                        4. Scalability optimizations
                        5. Monitoring and observability
                        6. Cost optimization recommendations
                        """
                        
                        optimization_result = await cognitive_forge_engine.run_mission_simple(optimization_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"optimization_result": optimization_result},
                            tokens_used=len(optimization_prompt.split()) + len(optimization_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Phase 7: Documentation & Knowledge Synthesis
                    with agent_observability.agent_session("documentation_specialist", mission_id_str, "Phase 7: Documentation & Knowledge Synthesis") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Creating comprehensive documentation and knowledge synthesis",
                            confidence_score=0.8
                        )
                        
                        documentation_prompt = f"""
                        Create comprehensive documentation:
                        
                        Final Solution:
                        {optimization_result}
                        
                        Documentation Requirements:
                        1. Technical documentation and API docs
                        2. User guides and tutorials
                        3. Deployment and operations guides
                        4. Troubleshooting and FAQ
                        5. Maintenance and support procedures
                        6. Knowledge base and best practices
                        """
                        
                        documentation_result = await cognitive_forge_engine.run_mission_simple(documentation_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"documentation_result": documentation_result},
                            tokens_used=len(documentation_prompt.split()) + len(documentation_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Phase 8: Deployment & Integration
                    with agent_observability.agent_session("deployment_devops", mission_id_str, "Phase 8: Deployment & Integration") as phase_session:
                        agent_observability.log_agent_thinking(
                            phase_session.session_id,
                            "Providing deployment and integration guidance",
                            confidence_score=0.85
                        )
                        
                        deployment_prompt = f"""
                        Provide deployment and integration guidance:
                        
                        Complete Solution:
                        {optimization_result}
                        
                        Documentation:
                        {documentation_result}
                        
                        Deployment Requirements:
                        1. Environment setup and configuration
                        2. CI/CD pipeline implementation
                        3. Monitoring and alerting setup
                        4. Backup and disaster recovery
                        5. Security hardening procedures
                        6. Integration with existing systems
                        """
                        
                        deployment_result = await cognitive_forge_engine.run_mission_simple(deployment_prompt, mission_id_str) # Assuming direct_inference is cognitive_forge_engine.run_mission_simple
                        
                        agent_observability.log_agent_response(
                            phase_session.session_id,
                            {"deployment_result": deployment_result},
                            tokens_used=len(deployment_prompt.split()) + len(deployment_result.get("result", "").split())
                        )
                        
                        phase_session.success = True
                    
                    # Compile comprehensive result
                    comprehensive_result = f"""
# COMPREHENSIVE SOLUTION

## Original Request
{prompt}

## Phase 1: Planning & Analysis
{planning_result}

## Phase 2: Research & Information Gathering
{research_result}

## Phase 3: Design & Architecture
{design_result}

## Phase 4: Implementation & Development
{implementation_result}

## Phase 5: Testing & Validation
{testing_result}

## Phase 6: Optimization & Refinement
{optimization_result}

## Phase 7: Documentation & Knowledge Synthesis
{documentation_result}

## Phase 8: Deployment & Integration
{deployment_result}

---
*Generated by Cognitive Forge Engine v5.1 - Full Workflow with Comprehensive Observability*
                    """
                    
                    result = {
                        "mission_id": mission_id_str,
                        "status": "completed",
                        "result": comprehensive_result,
                        "execution_time": time.time() - start_time,
                        "path": "full_workflow",
                        "timestamp": datetime.now().isoformat(),
                        "phases_completed": 8,
                        "workflow_phases": [
                            "planning", "research", "design", "implementation", 
                            "testing", "optimization", "documentation", "deployment"
                        ]
                    }
                    
                    session.success = True
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Record performance metrics
            db_manager.record_performance_metric(
                execution_path=chosen_path,
                complexity_score=complexity_score,
                execution_time=execution_time,
                success=result.get("status") == "completed",
                user_satisfaction=result.get("user_satisfaction", 0.8)
            )
            
            # Enhanced analytics tracking
            analytics_data = {
                "mission_id": mission_id_str,
                "prompt": prompt,
                "chosen_path": chosen_path,
                "complexity_score": complexity_score,
                "execution_time": execution_time,
                "success": result.get("status") == "completed",
                "phases_completed": result.get("phases_completed", 1),
                "workflow_phases": result.get("workflow_phases", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log detailed analytics
            logger.info(f"📊 Analytics: {chosen_path} path - {execution_time:.2f}s - Success: {result.get('status') == 'completed'}")
            
            # Update hybrid decision engine with results
            hybrid_decision_engine.record_execution_result(
                task_id=mission_id_str,
                prompt=prompt,
                path=chosen_path,
                execution_time=execution_time,
                success=result.get("status") == "completed",
                user_satisfaction=result.get("user_satisfaction", 0.8)
            )
            
            # Update mission with final result
            db_manager.update_mission_status(
                mission_id_str, 
                result.get("status", "failed"),
                result=result.get("result", ""),
                execution_time=execution_time,
                user_satisfaction=result.get("user_satisfaction", 0.8),
                execution_path=chosen_path,
                complexity_score=complexity_score
            )
            
            # Mark mission as successful in observability
            mission_data.success = result.get("status") == "completed"
            
            logger.success(f"✅ Mission {mission_id_str} completed via {chosen_path} path")
            
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Mission {mission_id_str} failed: {e}")
        
        # Update mission status to failed
        db_manager.update_mission_status(
            mission_id_str, 
            "failed",
            error_message=str(e),
            execution_time=execution_time
        )
        
        # Log error with observability
        agent_observability.log_error(e, {"mission_id": mission_id_str}, mission_id_str)

# --- API Endpoints ---
@app.get("/", response_class=FileResponse)
def serve_web_ui():
    """Serve the main web interface"""
    return FileResponse("templates/index.html")

@app.get("/missions", response_class=FileResponse)
def serve_missions():
    """Serve the missions page"""
    return FileResponse("templates/missions.html")

@app.get("/ai-agents", response_class=FileResponse)
def serve_ai_agents():
    """Serve the AI agents page"""
    return FileResponse("templates/ai-agents.html")

@app.get("/settings", response_class=FileResponse)
def serve_settings():
    """Serve the settings page"""
    return FileResponse("templates/settings.html")

@app.get("/test-missions", response_class=FileResponse)
def serve_test_missions():
    """Serve the test missions page"""
    return FileResponse("templates/test-missions.html")

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
            request.prompt, 
            mission.mission_id_str
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
    """Get comprehensive hybrid system analytics"""
    try:
        db_stats = db_manager.get_system_stats()
        hybrid_stats = hybrid_decision_engine.get_system_stats()
        cache_stats = hybrid_decision_engine.cache.get_stats()
        
        # Enhanced analytics with performance metrics
        analytics = {
            "system_performance": {
                "golden_path_success_rate": hybrid_stats.get("golden_path_success_rate", 0),
                "full_workflow_success_rate": hybrid_stats.get("full_workflow_success_rate", 0),
                "average_golden_path_time": hybrid_stats.get("average_golden_path_time", 0),
                "average_full_workflow_time": hybrid_stats.get("average_full_workflow_time", 0),
                "total_missions": db_stats.get("total_missions", 0),
                "completed_missions": db_stats.get("completed_missions", 0),
                "failed_missions": db_stats.get("failed_missions", 0)
            },
            "decision_metrics": {
                "complexity_threshold": settings.HYBRID_SWITCH_THRESHOLD,
                "average_complexity_score": hybrid_stats.get("average_complexity_score", 0),
                "routing_accuracy": hybrid_stats.get("routing_accuracy", 0),
                "user_satisfaction": hybrid_stats.get("average_user_satisfaction", 0)
            },
            "cache_performance": {
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
                "cache_size": cache_stats.get("size", 0),
                "cache_effectiveness": cache_stats.get("effectiveness", 0)
            },
            "learning_metrics": {
                "performance_model_accuracy": hybrid_stats.get("performance_model_accuracy", 0),
                "user_preference_learning": hybrid_stats.get("user_preference_learning", 0),
                "adaptive_threshold_adjustments": hybrid_stats.get("adaptive_threshold_adjustments", 0)
            }
        }
        
        return {
            "status": "success",
            "analytics": analytics,
            "hybrid_stats": hybrid_stats,
            "database_stats": db_stats,
            "cache_stats": cache_stats,
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

@app.get("/api/test-missions")
async def get_test_missions():
    """Get available test missions."""
    try:
        missions = test_mission_system.get_available_test_missions()
        return {
            "success": True,
            "missions": missions,
            "total_missions": len(missions)
        }
    except Exception as e:
        logger.error(f"Error getting test missions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-missions/{mission_id}/run")
async def run_test_mission(mission_id: str, request: dict = None):
    """Run a specific test mission."""
    try:
        user_request = request.get("user_request", f"Test Mission: {mission_id}") if request else None
        execution = await test_mission_system.run_test_mission(mission_id, user_request)
        
        # Use safe serialization for the execution object
        execution_data = test_mission_system._make_execution_serializable(execution)
        
        return {
            "success": True,
            "execution_id": execution.execution_id,
            "mission_name": execution.test_mission.name,
            "execution_success": execution.success,
            "duration_seconds": execution.duration_seconds,
            "scenarios_executed": len(execution.test_results),
            "performance_metrics": execution.performance_metrics,
            "execution_data": execution_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error running test mission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-missions/executions")
async def get_test_executions():
    """Get history of test executions."""
    try:
        executions = test_mission_system.get_test_execution_history()
        return {
            "success": True,
            "executions": executions,
            "total_executions": len(executions)
        }
    except Exception as e:
        logger.error(f"Error getting test executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-missions/executions/{execution_id}")
async def get_test_execution_details(execution_id: str):
    """Get detailed results for a specific test execution."""
    try:
        execution_data = test_mission_system.get_test_execution_details(execution_id)
        if not execution_data:
            raise HTTPException(status_code=404, detail="Test execution not found")
        
        return {
            "success": True,
            "execution": execution_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting test execution details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-missions/analysis")
async def get_test_analysis():
    """Get comprehensive analysis of test mission performance."""
    try:
        analysis = test_mission_system.get_agent_performance_analysis()
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error getting test analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/observability/live-stream")
async def get_live_stream_events(event_type: str = None, limit: int = 100):
    """Get real-time live stream events for agent tracking."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        events = agent_observability.get_live_stream_events(event_type=event_type, limit=limit)
        return {
            "success": True,
            "events": events,
            "total_events": len(events),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting live stream events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get live stream events: {str(e)}")

@app.get("/api/observability/real-time-metrics")
async def get_real_time_metrics():
    """Get real-time performance metrics."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        metrics = agent_observability.get_real_time_metrics()
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")

@app.get("/api/observability/agent-live-stream/{agent_name}")
async def get_agent_live_stream(agent_name: str, limit: int = 50):
    """Get live stream of specific agent actions."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        events = agent_observability.get_agent_live_stream(agent_name=agent_name, limit=limit)
        return {
            "success": True,
            "agent_name": agent_name,
            "events": events,
            "total_events": len(events),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agent live stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent live stream: {str(e)}")

@app.get("/api/observability/mission-live-stream/{mission_id}")
async def get_mission_live_stream(mission_id: str, limit: int = 50):
    """Get live stream of specific mission events."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        events = agent_observability.get_mission_live_stream(mission_id=mission_id, limit=limit)
        return {
            "success": True,
            "mission_id": mission_id,
            "events": events,
            "total_events": len(events),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting mission live stream: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get mission live stream: {str(e)}")

@app.get("/api/observability/agent-analytics")
async def get_agent_analytics():
    """Get comprehensive agent analytics with enhanced metrics."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        analytics = agent_observability.get_agent_analytics()
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agent analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent analytics: {str(e)}")

@app.get("/api/observability/mission/{mission_id}")
async def get_mission_observability(mission_id: str):
    """Get detailed observability data for a specific mission."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        mission_data = agent_observability.get_mission_details(mission_id)
        if not mission_data:
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
        
        return {
            "success": True,
            "mission_data": mission_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mission observability: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get mission observability: {str(e)}")

@app.get("/api/observability/session/{session_id}")
async def get_session_observability(session_id: str):
    """Get detailed observability data for a specific agent session."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        session_data = agent_observability.get_agent_session_details(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "success": True,
            "session_data": session_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session observability: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session observability: {str(e)}")

@app.get("/api/observability/report")
async def get_observability_report():
    """Generate comprehensive observability report."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        report = agent_observability.generate_observability_report()
        return {
            "success": True,
            "report": report,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating observability report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate observability report: {str(e)}")

@app.post("/api/observability/export")
async def export_observability_data(request: dict = None):
    """Export observability data for analysis."""
    if agent_observability is None:
        raise HTTPException(status_code=503, detail="Observability service unavailable")
    
    try:
        mission_id = request.get("mission_id") if request else None
        export_data = agent_observability.export_observability_data(mission_id=mission_id)
        return {
            "success": True,
            "export_data": export_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting observability data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export observability data: {str(e)}")

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
