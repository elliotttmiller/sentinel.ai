"""
Main entry point for Project Sentinel Agent Engine.

Initializes the agent engine and provides the local API server
for communication with the cloud backend.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add dotenv loading and Gemini import
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Add the agent-engine directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.mission_planner import MissionPlanner
from core.crew_manager import CrewManager
from core.memory_manager import MemoryManager
from agents.agent_factory import AgentFactory
from config import config


class AgentEngine:
    """
    Main agent engine for Project Sentinel.
    
    Coordinates the entire agent system including:
    - Mission planning and execution
    - Agent crew management
    - Memory and learning
    - API communication with cloud backend
    """
    
    def __init__(self):
        self.logger = logger.bind(component="agent_engine")
        self.mission_planner: Optional[MissionPlanner] = None
        self.crew_manager: Optional[CrewManager] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.agent_factory: Optional[AgentFactory] = None
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Project Sentinel Agent Engine",
            description="Local agent engine for executing AI missions",
            version="0.1.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        self.logger.info("Agent Engine initialized")
    
    def _setup_routes(self):
        """Setup FastAPI routes for the agent engine."""
        
        @self.app.get("/")
        async def root():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "service": "Project Sentinel Agent Engine",
                "version": "0.1.0",
                "model": config.default_model
            }
        
        @self.app.post("/mission/create")
        async def create_mission(user_prompt: str, mission_id: str):
            """Create a new mission from user prompt."""
            try:
                if not self.mission_planner:
                    raise HTTPException(status_code=500, detail="Mission planner not initialized")
                
                # Create mission plan
                execution_plan = await self.mission_planner.create_mission_plan(user_prompt, mission_id)
                
                return {
                    "mission_id": mission_id,
                    "status": "planned",
                    "execution_plan": execution_plan.dict(),
                    "message": "Mission plan created successfully"
                }
            except Exception as e:
                self.logger.error(f"Error creating mission: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mission/execute")
        async def execute_mission(mission_id: str, execution_plan: dict):
            """Execute a mission using the crew manager."""
            try:
                if not self.crew_manager:
                    raise HTTPException(status_code=500, detail="Crew manager not initialized")
                
                # Assemble crew
                crew_id = await self.crew_manager.assemble_crew(execution_plan, Path.cwd())
                
                # Execute mission
                result = await self.crew_manager.execute_mission(crew_id, execution_plan, "User prompt")
                
                return {
                    "mission_id": mission_id,
                    "crew_id": crew_id,
                    "status": "completed" if result.success else "failed",
                    "result": result.dict(),
                    "message": "Mission executed successfully" if result.success else "Mission failed"
                }
            except Exception as e:
                self.logger.error(f"Error executing mission: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/crew/status/{crew_id}")
        async def get_crew_status(crew_id: str):
            """Get status of a specific crew."""
            try:
                if not self.crew_manager:
                    raise HTTPException(status_code=500, detail="Crew manager not initialized")
                
                status = self.crew_manager.get_crew_status(crew_id)
                if not status:
                    raise HTTPException(status_code=404, detail="Crew not found")
                
                return status
            except Exception as e:
                self.logger.error(f"Error getting crew status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/memory/stats")
        async def get_memory_stats():
            """Get memory statistics."""
            try:
                if not self.memory_manager:
                    raise HTTPException(status_code=500, detail="Memory manager not initialized")
                
                return self.memory_manager.get_memory_stats()
            except Exception as e:
                self.logger.error(f"Error getting memory stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents/available")
        async def get_available_agents():
            """Get list of available agent roles."""
            try:
                if not self.agent_factory:
                    raise HTTPException(status_code=500, detail="Agent factory not initialized")
                
                return {
                    "available_roles": [role.value for role in self.agent_factory.get_available_roles()]
                }
            except Exception as e:
                self.logger.error(f"Error getting available agents: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def initialize(self):
        """Initialize all components of the agent engine."""
        self.logger.info("Initializing Agent Engine components")
        
        try:
            # Load environment variables
            load_dotenv()
            # Initialize LLM client with Gemini, using environment variable for credentials
            llm_client = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
            
            # Initialize tool manager (placeholder for now)
            tool_manager = None  # TODO: Initialize actual tool manager
            
            # Initialize memory manager
            self.memory_manager = MemoryManager()
            self.logger.info("Memory manager initialized")
            
            # Initialize agent factory
            self.agent_factory = AgentFactory(llm_client, tool_manager)
            self.logger.info("Agent factory initialized")
            
            # Initialize mission planner
            self.mission_planner = MissionPlanner(llm_client)
            self.logger.info("Mission planner initialized")
            
            # Initialize crew manager
            self.crew_manager = CrewManager(self.agent_factory, tool_manager)
            self.logger.info("Crew manager initialized")
            
            self.logger.info("All Agent Engine components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Agent Engine: {e}")
            raise
    
    async def start(self, host: str = None, port: int = None):
        """Start the agent engine API server."""
        # Use config values if not provided
        host = host or config.host
        port = port or config.port
        
        self.logger.info(f"Starting Agent Engine on {host}:{port}")
        
        # Initialize components
        await self.initialize()
        
        # Start the server
        config_obj = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config_obj)
        await server.serve()
    
    async def shutdown(self):
        """Shutdown the agent engine gracefully."""
        self.logger.info("Shutting down Agent Engine")
        
        # Cleanup resources
        if self.crew_manager:
            active_crews = self.crew_manager.get_active_crews()
            for crew_id in active_crews:
                self.crew_manager.disband_crew(crew_id)
        
        self.logger.info("Agent Engine shutdown complete")


async def main():
    """Main entry point for the agent engine."""
    # Configure logging
    logger.add(
        config.log_file,
        rotation="1 day",
        retention="7 days",
        level=config.log_level
    )
    
    # Create and start agent engine
    engine = AgentEngine()
    
    try:
        await engine.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Agent Engine error: {e}")
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    # Run the agent engine
    asyncio.run(main()) 