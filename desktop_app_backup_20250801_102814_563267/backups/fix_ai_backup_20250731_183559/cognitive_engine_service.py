"""
Unified Cognitive Engine Service for Desktop App
Combines the best features from both engine implementations
"""

import asyncio
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
import sys
from loguru import logger
from starlette.responses import Response

# Import our AI components
from .core.cognitive_forge_engine import cognitive_forge_engine
from .models.advanced_database import db_manager

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
    req_body = await request.body()
    logger.info(f"ENGINE: {request.method} {request.url} | Body: {safe_log_body(req_body)}")
    try:
        response = await call_next(request)
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        logger.info(f"ENGINE: Response {response.status_code} for {request.method} {request.url}")
        return Response(content=resp_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
    except Exception as e:
        logger.error(f"ENGINE: Exception during request: {request.method} {request.url} - {e}", exc_info=True)
        raise

# Core endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cognitive_engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Sentinel Cognitive AI Engine",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/health",
            "/ai/generate",
            "/ai/analyze-code",
            "/ai/chat",
            "/ai/models",
            "/ai/status",
            "/mission/execute",
            "/mission/result/{mission_id}"
        ]
    }

# AI Service endpoints
@app.post("/ai/generate")
async def generate_ai_response(request: AIRequest):
    """Generate AI response using the Cognitive Forge Engine"""
    try:
        # Use the cognitive forge engine for real AI generation
        response = cognitive_forge_engine.llm.invoke(request.prompt)
        
        return AIResponse(
            response=response.content,
            model=request.model,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.post("/ai/analyze-code")
async def analyze_code_endpoint(request: CodeAnalysisRequest):
    """Analyze code using AI"""
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
    """Chat with AI using the Cognitive Forge Engine"""
    try:
        response = cognitive_forge_engine.llm.invoke(request.prompt)
        
        return AIResponse(
            response=response.content,
            model=request.model,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

@app.get("/ai/models")
async def list_available_models():
    """List available AI models"""
    return {
        "models": [
            {
                "id": "gemini-1.5-pro-latest",
                "name": "Google Gemini 1.5 Pro",
                "description": "Latest Gemini model for advanced reasoning",
                "capabilities": ["text-generation", "code-analysis", "reasoning"]
            }
        ],
        "default_model": "gemini-1.5-pro-latest"
    }

@app.get("/ai/status")
async def ai_status():
    """Get AI service status"""
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
            "output": result.get("result", "Mission completed"),
            "details": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"ENGINE: Background mission {mission_id} failed: {e}")
        mission_results[mission_id] = {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the cognitive engine on startup"""
    logger.info("🚀 Cognitive AI Engine starting up...")
    
    # Log system startup
    db_manager.log_system_event(
        "INFO",
        "Cognitive AI Engine started successfully",
        "cognitive_engine",
        {"version": "2.0.0", "startup_time": datetime.utcnow().isoformat()},
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Cognitive AI Engine shutting down...")
    
    # Log system shutdown
    db_manager.log_system_event(
        "INFO",
        "Cognitive AI Engine shutting down",
        "cognitive_engine",
        {"shutdown_time": datetime.utcnow().isoformat()},
    ) 