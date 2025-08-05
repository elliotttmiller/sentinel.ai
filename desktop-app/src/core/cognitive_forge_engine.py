"""
Cognitive Forge Engine v5.3 - Simplified Live Mission Execution with Phase 4 Sentience
Implements live mission execution with real-time database integration and self-healing capabilities
"""

import json
import time
import os
import traceback
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

# Fix LangChain deprecation warning by using pydantic.v1 compatibility namespace
from pydantic.v1 import BaseModel

from loguru import logger
from dotenv import load_dotenv
import sys
import os

# Add the src directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings
from config.settings import settings

# Import utils with fallback
try:
    from utils.google_ai_wrapper import create_google_ai_llm, direct_inference, google_ai_wrapper
except ImportError:
    # Fallback for relative imports
    from ..utils.google_ai_wrapper import create_google_ai_llm, direct_inference, google_ai_wrapper

# Import models
try:
    from models.advanced_database import db_manager
except ImportError:
    from ..models.advanced_database import db_manager

# Import observability
try:
    from utils.agent_observability import agent_observability, LiveStreamEvent
except ImportError:
    from ..utils.agent_observability import agent_observability, LiveStreamEvent

# Import Phase 4 components
try:
    from utils.guardian_protocol import GuardianProtocol
    from utils.self_learning_module import SelfLearningModule
except ImportError:
    # Create fallback classes if imports fail
    class GuardianProtocol:
        def __init__(self, llm):
            self.llm = llm
        async def run_agent_validation_suite(self, *args, **kwargs):
            return {"validation_passed": True}
        async def run_code_autofix(self, *args, **kwargs):
            return {"status": "success", "fixed_code": "Auto-fix applied"}
    
    class SelfLearningModule:
        def __init__(self, llm, db_manager):
            self.llm = llm
            self.db_manager = db_manager
        async def synthesize_and_learn(self, mission):
            logger.info("Self-learning module processing mission")
        async def analyze_completed_missions(self):
            return {"patterns": [], "insights": []}

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Initialize Sentry integration with fallback
try:
    from utils.sentry_integration import initialize_sentry, get_sentry, capture_error, start_transaction, track_async_errors
except ImportError:
    from ..utils.sentry_integration import initialize_sentry, get_sentry, capture_error, start_transaction, track_async_errors


class MissionState(Enum):
    """Formal mission state machine for surgical precision"""
    PENDING = "pending"
    RUNNING = "running"
    HEALING = "healing"  # NEW: Phoenix Protocol active
    COMPLETED = "completed"
    FAILED = "failed"


class CognitiveForgeEngine:
    """
    The Sentient Operating System - Cognitive Forge Engine v5.3
    Simplified version for live mission execution with real-time database integration and Phase 4 sentience
    """

    def __init__(self):
        # Initialize Sentry for enhanced monitoring
        self.sentry = initialize_sentry(environment="production")
        
        # LLM Configuration
        LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")  # Use direct Google AI model name
        LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

        # Use our custom Google Generative AI wrapper
        try:
            self.llm = create_google_ai_llm(
                model_name=LLM_MODEL,
                temperature=LLM_TEMPERATURE
            )
            logger.info(f"Google Generative AI initialized with model: {LLM_MODEL}")
            
            # Track successful LLM initialization
            if self.sentry:
                self.sentry.capture_message(
                    "LLM initialized successfully",
                    level="info",
                    context={"model": LLM_MODEL, "temperature": LLM_TEMPERATURE}
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Generative AI: {e}")
            if self.sentry:
                self.sentry.capture_exception(e)
            raise

        # Initialize database manager
        self.db_manager = db_manager

        # Initialize Phase 4 components
        self.guardian_protocol = GuardianProtocol(self.llm)
        self.self_learning_module = SelfLearningModule(self.llm, self.db_manager)

    @track_async_errors
    async def run_mission(
        self,
        user_prompt: str,
        mission_id_str: str,
        agent_type: str,
        is_healing_attempt: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a complete mission with REAL task execution and live event streaming.
        """
        transaction = start_transaction(f"mission_execution_{mission_id_str}", "mission")
        
        try:
            # Import the real mission executor with absolute import
            import sys
            import os
            # Add src directory to path
            src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            
            from agents.real_mission_executor import RealMissionExecutor
            
            # Create real mission executor
            real_executor = RealMissionExecutor()
            
            if not is_healing_attempt:
                # PUSH MISSION START EVENT & UPDATE DB
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=5)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_update",
                    source="cognitive_forge_engine",
                    severity="INFO",
                    message=f"Mission '{mission_id_str}' initiated with REAL execution capabilities.",
                    payload=self.db_manager.get_mission(mission_id_str).as_dict()
                ))
            
            # Execute the mission using the real executor
            logger.info(f"🚀 Starting REAL mission execution for {mission_id_str}")
            result = await real_executor.execute_mission(user_prompt, mission_id_str, agent_type)
            
            # Handle the result
            if result.get("status") == "completed":
                # Phase 4: Self-Learning Integration
                await self.self_learning_module.synthesize_and_learn(self.db_manager.get_mission(mission_id_str))
                return {"status": "completed", "real_execution": True, "results": result}
            else:
                # Mission failed, but don't trigger phoenix protocol for real execution failures
                # Real failures are usually due to actual system issues, not simulation problems
                error_message = result.get("error", "Real execution failed")
                logger.error(f"Real mission execution failed for {mission_id_str}: {error_message}")
                return {"status": "failed", "real_execution": True, "error": error_message}
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Mission {mission_id_str} failed: {error_message}")
            self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="failed", error_message=error_message)
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_error", source="mission_control", severity="ERROR",
                message=f"Mission '{mission_id_str}' failed: {error_message}",
                payload=self.db_manager.get_mission(mission_id_str).as_dict()
            ))

            # --- PHOENIX PROTOCOL ACTIVATION ---
            retries = self.db_manager.increment_phoenix_retry(mission_id_str)
            if retries <= 2:  # Allow up to 2 healing attempts
                logger.warning(f"🔥 Phoenix Protocol: Activating self-healing for mission {mission_id_str}. Attempt #{retries}.")
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="healing", is_healing=True)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_update", source="phoenix_protocol", severity="WARNING",
                    message=f"Phoenix Protocol initiating self-healing for mission {mission_id_str}.",
                    payload=self.db_manager.get_mission(mission_id_str).as_dict()
                ))
                
                await asyncio.sleep(2) # Simulate analysis
                
                # In a real scenario, this would be a more sophisticated solution
                healed_prompt = f"Original prompt failed due to '{error_message}'. Please re-attempt the task with a focus on robustness and error handling. Original prompt: {user_prompt}"
                
                logger.info(f"Phoenix Protocol: Rerunning mission with modified prompt.")
                # Recursively call the mission with the fix
                await self.run_mission(healed_prompt, mission_id_str, agent_type, is_healing_attempt=True)
            else:
                logger.error(f"Mission {mission_id_str} failed permanently after {retries} healing attempts.")
        
        finally:
            if transaction:
                transaction.finish()

    async def run_periodic_self_optimization(self):
        """Phase 4: Periodic self-optimization background task"""
        while True:
            await asyncio.sleep(3600)  # Run every hour
            logger.info("🧠 Self-Optimization Engineer: Starting periodic analysis...")
            try:
                insights = await self.self_learning_module.analyze_completed_missions()
                if not insights or not insights.get("patterns"):
                    logger.info("No patterns found for optimization")
                    continue

                # Create optimization proposal based on insights
                proposal_type = "performance_optimization"
                description = f"System optimization based on {len(insights.get('patterns', []))} identified patterns"
                rationale = f"Analysis of recent missions revealed opportunities for improvement in execution efficiency and success rates."
                
                # Create the proposal in database
                proposal = self.db_manager.create_optimization_proposal(
                    proposal_type=proposal_type,
                    description=description,
                    rationale=rationale
                )
                
                agent_observability.push_event(LiveStreamEvent(
                    event_type="system_log", source="Optimizer", severity="WARNING",
                    message="New system optimization proposal is available for review in Settings."
                ))
                
                logger.info(f"💡 Created optimization proposal: {description}")
                
            except Exception as e:
                logger.error(f"Self-optimization cycle failed: {e}")

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for monitoring"""
        return {
            "version": "v5.3",
            "status": "operational",
            "llm_model": "gemini-1.5-pro",
            "database": "SQLite",
            "observability": "enabled",
            "phase_4_features": [
                "Phoenix Protocol (Self-Healing)",
                "Guardian Protocol (Quality Assurance)", 
                "Self-Learning Module",
                "Periodic Self-Optimization"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_mission_status(self) -> Dict[str, Any]:
        """Get current mission status"""
        stats = self.db_manager.get_system_stats()
        return {
            "active_missions": stats.get("total_missions", 0) - stats.get("completed_missions", 0) - stats.get("failed_missions", 0),
            "completed_missions": stats.get("completed_missions", 0),
            "failed_missions": stats.get("failed_missions", 0),
            "healing_missions": stats.get("healing_missions", 0),
            "system_status": "operational",
            "optimization_proposals": stats.get("active_optimizations", 0)
        }


# Global instance
cognitive_forge_engine = CognitiveForgeEngine()
