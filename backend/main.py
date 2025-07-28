import json
import uuid
import asyncio
import requests
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from loguru import logger
from contextlib import asynccontextmanager
import os

# Import your custom components
from config import settings
from core.database import Base, engine, get_db
from core import models
from core.mission_planner import MissionPlanner, ExecutionPlan
from agents.agent_factory import AgentFactory
from fastapi import FastAPI
from api.missions import router as missions_router
from api.agents import router as agents_router
from api.genai import router as genai_router
from api.system import router as system_router

# --- Application Setup (Singleton Pattern) ---
logger.add("logs/sentinel_backend.log", rotation="10 MB", level=settings.LOG_LEVEL)

# This lifespan event is the professional way to handle startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
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

# Import global instances
from core.globals import llm_client, tool_manager, agent_factory, mission_planner

app = FastAPI(title="Sentinel Backend Orchestrator", lifespan=lifespan)
app.include_router(missions_router)
app.include_router(agents_router)
app.include_router(genai_router)
app.include_router(system_router)

@app.on_event("startup")
def startup_event():
    """Initializes core components after the app starts."""
    global llm_client, tool_manager, agent_factory, mission_planner
    from core.globals import llm_client as global_llm, tool_manager as global_tool, agent_factory as global_agent, mission_planner as global_mission
    
    # --- Placeholder for ToolManager ---
    class ToolManager:
        def get_available_tools(self): return {}
    # ------------------------------------

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
            
    global_llm = get_llm_client()
    global_tool = ToolManager()
    global_agent = AgentFactory(llm_client=global_llm, tool_manager=global_tool)
    global_mission = MissionPlanner(llm_client=global_llm)
    
    # Update the global variables
    globals()['llm_client'] = global_llm
    globals()['tool_manager'] = global_tool
    globals()['agent_factory'] = global_agent
    globals()['mission_planner'] = global_mission
    
    logger.info("Core components initialized.")

# --- API Models (Pydantic) ---
from core.schemas import MissionSchema, AgentSchema, MissionDispatchResponse, MissionRequest, AgentExecutionRequest, AgentExecutionResponse

# Remove in-memory agents_db and update /agents endpoint to always use DB 