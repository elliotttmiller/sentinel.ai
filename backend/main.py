import json
import uuid
import asyncio
import requests
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

# Import your custom components
from config import settings
from core.database import Base, engine, get_db, SessionLocal
from core import models
from core.schemas import MissionSchema, MissionRequest, AgentSchema, MissionDispatchResponse, AgentExecutionRequest, AgentExecutionResponse
from core.mission_planner import MissionPlanner, ExecutionPlan
from agents.agent_factory import AgentFactory
from api.agents import router as agents_router
from api.genai import router as genai_router
from api.system import router as system_router

# --- Application Setup ---
logger.add("logs/sentinel_backend.log", rotation="10 MB", level=settings.LOG_LEVEL)

# Global instances
llm_client = None
tool_manager = None
agent_factory = None
mission_planner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_client, tool_manager, agent_factory, mission_planner
    logger.info("Application starting up...")
    
    # Initialize components
    def get_llm_client():
        try:
            from google.oauth2 import service_account
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Try service account JSON first
            if settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
                creds_dict = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
                logger.info(f"GenAI client initialized with service account and model: {settings.DEFAULT_MODEL}")
                return ChatGoogleGenerativeAI(model=settings.DEFAULT_MODEL, credentials=credentials, temperature=0.7)
            
            # Fallback to API key
            elif settings.GOOGLE_API_KEY:
                logger.info(f"GenAI client initialized with API key and model: {settings.DEFAULT_MODEL}")
                return ChatGoogleGenerativeAI(model=settings.DEFAULT_MODEL, google_api_key=settings.GOOGLE_API_KEY, temperature=0.7)
            
            else:
                raise ValueError("Neither GOOGLE_APPLICATION_CREDENTIALS_JSON nor GOOGLE_API_KEY is configured")
                
        except Exception as e:
            logger.error(f"FATAL: Could not initialize LLM Client. Error: {e}")
            raise
    
    # --- Placeholder for ToolManager ---
    class ToolManager:
        def get_available_tools(self): return {}
    # ------------------------------------
    
    llm_client = get_llm_client()
    tool_manager = ToolManager()
    agent_factory = AgentFactory(llm_client=llm_client, tool_manager=tool_manager)
    mission_planner = MissionPlanner(llm_client=llm_client)
    
    logger.info("Verifying database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified successfully.")
        seed_agents_to_db()
    except Exception as e:
        logger.error(f"FATAL: Could not connect to database or create tables: {e}")
    
    yield
    logger.info("Application shutting down...")

def seed_agents_to_db():
    db = next(get_db())
    try:
        agent_count = db.query(models.Agent).count()
        if agent_count == 0:
            logger.info("No agents found in DB. Seeding initial agents...")
            agents_to_seed = [
                models.Agent(id="agent-1", name="Code Reviewer", type="code_reviewer", description="Reviews code for quality and security issues", capabilities=["code_analysis", "security_scanning", "best_practices"], status="available", missions_completed=5),
                models.Agent(id="agent-2", name="Debugger", type="debugger", description="Analyzes and fixes code issues", capabilities=["error_analysis", "bug_fixing", "performance_optimization"], status="available", missions_completed=3),
                models.Agent(id="agent-3", name="Mission Planner", type="planner", description="Creates and manages mission plans", capabilities=["planning", "coordination", "execution_tracking"], status="busy", missions_completed=12),
                models.Agent(id="agent-4", name="Simple Test Agent", type="simple_test", description="A basic test agent for validating the deployment system", capabilities=["text_processing", "basic_response_generation", "status_reporting", "activity_logging"], status="available", missions_completed=0),
            ]
            db.add_all(agents_to_seed)
            db.commit()
            logger.info("Initial agents have been seeded to the database.")
    finally:
        db.close()

app = FastAPI(title="Sentinel Backend Orchestrator", lifespan=lifespan)

# Include existing routers
app.include_router(agents_router)
app.include_router(genai_router)
app.include_router(system_router)

# --- Background Task ---
async def run_mission_planning_and_dispatch(mission_id: str, prompt: str, title: str = None, description: str = None):
    """This is the long-running task that will execute in the background."""
    db = SessionLocal()  # Create a new session for this background task
    try:
        logger.info(f"BACKGROUND TASK: Starting AI planning for mission {mission_id}.")
        
        # 1. Run the AI planning
        plan: ExecutionPlan = await mission_planner.create_mission_plan(user_prompt=prompt, mission_id=mission_id)
        logger.info(f"BACKGROUND TASK: AI planning complete for {mission_id}.")
        
        # 2. Update mission in DB with the plan
        mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
        if mission:
            mission.status = "planned"
            mission.plan = plan.model_dump()
            mission.steps = plan.model_dump().get("steps", [])
            db.commit()

        # 3. Dispatch to engine
        desktop_url = f"{settings.DESKTOP_TUNNEL_URL}/execute_mission"
        response = await asyncio.to_thread(
            requests.post,
            desktop_url,
            json=plan.model_dump(),
            timeout=20
        )
        response.raise_for_status()
        logger.info(f"BACKGROUND TASK: Mission {mission_id} dispatched to engine.")

        # 4. Poll for execution result
        execution_result = None
        result_url = f"{settings.DESKTOP_TUNNEL_URL}/mission_result/{mission_id}"
        for _ in range(10):
            try:
                poll_resp = await asyncio.to_thread(requests.get, result_url, timeout=10)
                if poll_resp.status_code == 200:
                    execution_result = poll_resp.json()
                    if execution_result and execution_result.get("status") != "pending":
                        break
            except Exception as e:
                logger.warning(f"Polling for execution result failed: {e}")
            await asyncio.sleep(2)

        # 5. Update mission with final status
        now = datetime.utcnow()
        mission.status = "completed" if execution_result and execution_result.get("status") == "success" else "failed"
        mission.completed_at = now
        mission.result = execution_result
        db.commit()
        
        logger.info(f"BACKGROUND TASK: Mission {mission_id} completed with status: {mission.status}")
        
    except Exception as e:
        logger.error(f"BACKGROUND TASK: Failed for mission {mission_id}. Error: {e}", exc_info=True)
        mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
        if mission:
            mission.status = "planning_failed"
            db.commit()
    finally:
        db.close()  # CRITICAL: Always close the session in a background task

# --- API Endpoints ---
@app.get("/health", status_code=200)
def health_check():
    logger.info("Healthcheck endpoint hit")
    return {"status": "ok", "service": "Sentinel Orchestrator Backend"}

@app.get("/missions", response_model=List[MissionSchema])
def get_missions(db: Session = Depends(get_db)):
    """Fetches all missions from the database."""
    try:
        missions = db.query(models.Mission).order_by(models.Mission.created_at.desc()).all()
        return [MissionSchema.model_validate(m) for m in missions]
    except Exception as e:
        logger.error(f"Failed to fetch missions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database query failed.")

@app.post("/missions", status_code=202)  # Use 202 Accepted status code
async def create_mission(
    request: MissionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receives a prompt, responds IMMEDIATELY, and starts the AI planning
    and dispatch process in the background.
    """
    mission_id = f"mission_{uuid.uuid4()}"
    logger.info(f"API: Received mission request for '{request.prompt}'. Assigning ID: {mission_id}.")

    # Validate prompt
    if not request.prompt or len(request.prompt) < 5:
        raise HTTPException(status_code=400, detail="Prompt is too short.")

    # 1. Immediately create and save a record in the database
    now = datetime.utcnow()
    new_mission = models.Mission(
        id=mission_id,
        title=request.title or request.prompt[:120],
        description=request.description or request.prompt,
        status="planning",
        created_at=now,
        updated_at=now
    )
    db.add(new_mission)
    db.commit()
    db.refresh(new_mission)

    # 2. Add the long-running job to the background tasks
    background_tasks.add_task(
        run_mission_planning_and_dispatch,
        mission_id=mission_id,
        prompt=request.prompt,
        title=request.title,
        description=request.description
    )

    # 3. Return an immediate "Accepted" response to the mobile app
    return {
        "message": "Mission accepted and planning has begun in the background.",
        "mission_id": mission_id,
        "status": "planning"
    } 