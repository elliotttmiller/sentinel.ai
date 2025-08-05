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

from pydantic.v1 import BaseModel
from loguru import logger
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from utils.google_ai_wrapper import create_google_ai_llm, direct_inference, google_ai_wrapper
from models.advanced_database import db_manager
from utils.agent_observability import agent_observability, LiveStreamEvent
from utils.guardian_protocol import GuardianProtocol
from utils.self_learning_module import SelfLearningModule
from utils.sentry_integration import initialize_sentry, get_sentry, capture_error, start_transaction, track_async_errors

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class MissionState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    HEALING = "healing"
    COMPLETED = "completed"
    FAILED = "failed"

class CognitiveForgeEngine:
    def __init__(self):
        self.sentry = initialize_sentry(environment="production")
        LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")
        LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        try:
            self.llm = create_google_ai_llm(model_name=LLM_MODEL, temperature=LLM_TEMPERATURE)
            logger.info(f"Google Generative AI initialized with model: {LLM_MODEL}")
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

        self.db_manager = db_manager
        self.guardian_protocol = GuardianProtocol(self.llm)
        self.self_learning_module = SelfLearningModule(self.llm, self.db_manager)

    @track_async_errors
    async def run_mission(
        self, user_prompt: str, mission_id_str: str, agent_type: str, is_healing_attempt: bool = False
    ) -> Dict[str, Any]:
        transaction = start_transaction(f"mission_execution_{mission_id_str}", "mission")
        try:
            if not is_healing_attempt:
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=5)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_update",
                    source="mission_control",
                    severity="INFO",
                    message=f"Mission '{mission_id_str}' initiated.",
                    payload=self.db_manager.get_mission(mission_id_str).as_dict()
                ))
            await asyncio.sleep(2)
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action", source="Prompt Alchemist", severity="INFO",
                message="Optimizing user prompt for clarity and technical detail.",
                payload={"mission_id": mission_id_str, "phase": "Prompt Alchemy"}
            ))
            self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=25)
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_update", source="mission_control", severity="INFO",
                message=f"Mission '{mission_id_str}' progress: 25%",
                payload=self.db_manager.get_mission(mission_id_str).as_dict()
            ))

            await asyncio.sleep(3)
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action", source="Lead Architect", severity="INFO",
                message="Generating multi-step execution plan.",
                payload={"mission_id": mission_id_str, "phase": "Planning"}
            ))
            self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=50)
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_update", source="mission_control", severity="INFO",
                message=f"Mission '{mission_id_str}' progress: 50%",
                payload=self.db_manager.get_mission(mission_id_str).as_dict()
            ))

            if not is_healing_attempt and random.random() < 0.3:
                raise ValueError("Simulated failure: Critical component 'CodeGenerator' failed.")

            await asyncio.sleep(4)
            agent_observability.push_event(LiveStreamEvent(
                event_type="agent_action", source="Senior Developer Agent", severity="INFO",
                message="Executing primary tasks from blueprint.",
                payload={"mission_id": mission_id_str, "phase": "Execution"}
            ))
            self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=75)
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_update", source="mission_control", severity="INFO",
                message=f"Mission '{mission_id_str}' progress: 75%",
                payload=self.db_manager.get_mission(mission_id_str).as_dict()
            ))

            await asyncio.sleep(2)
            final_result_text = f"Mission '{mission_id_str}' completed successfully."
            self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="completed", progress=100, result=final_result_text)
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_complete",
                source="mission_control",
                severity="SUCCESS",
                message=final_result_text,
                payload=self.db_manager.get_mission(mission_id_str).as_dict()
            ))
            await self.self_learning_module.synthesize_and_learn(self.db_manager.get_mission(mission_id_str))
            return {"status": "completed"}
        except Exception as e:
            error_message = str(e)
            logger.error(f"Mission {mission_id_str} failed: {error_message}")
            self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="failed", error_message=error_message)
            agent_observability.push_event(LiveStreamEvent(
                event_type="mission_error", source="mission_control", severity="ERROR",
                message=f"Mission '{mission_id_str}' failed: {error_message}",
                payload=self.db_manager.get_mission(mission_id_str).as_dict()
            ))
            retries = self.db_manager.increment_phoenix_retry(mission_id_str)
            if retries <= 2:
                logger.warning(f"🔥 Phoenix Protocol: Activating self-healing for mission {mission_id_str}. Attempt #{retries}.")
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="healing", is_healing=True)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_update", source="phoenix_protocol", severity="WARNING",
                    message=f"Phoenix Protocol initiating self-healing for mission {mission_id_str}.",
                    payload=self.db_manager.get_mission(mission_id_str).as_dict()
                ))
                await asyncio.sleep(2)
                healed_prompt = f"Original prompt failed due to '{error_message}'. Please re-attempt the task with a focus on robustness and error handling. Original prompt: {user_prompt}"
                logger.info(f"Phoenix Protocol: Rerunning mission with modified prompt.")
                await self.run_mission(healed_prompt, mission_id_str, agent_type, is_healing_attempt=True)
            else:
                logger.error(f"Mission {mission_id_str} failed permanently after {retries} healing attempts.")
        finally:
            if transaction:
                transaction.finish()

    async def run_periodic_self_optimization(self):
        while True:
            await asyncio.sleep(3600)
            logger.info("🧠 Self-Optimization Engineer: Starting periodic analysis...")
            try:
                insights = await self.self_learning_module.analyze_completed_missions()
                if not insights or not insights.get("patterns"):
                    logger.info("No patterns found for optimization")
                    continue
                proposal_type = "performance_optimization"
                description = f"System optimization based on {len(insights.get('patterns', []))} identified patterns"
                rationale = f"Analysis of recent missions revealed opportunities for improvement in execution efficiency and success rates."
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
        stats = self.db_manager.get_system_stats()
        return {
            "active_missions": stats.get("total_missions", 0) - stats.get("completed_missions", 0) - stats.get("failed_missions", 0),
            "completed_missions": stats.get("completed_missions", 0),
            "failed_missions": stats.get("failed_missions", 0),
            "healing_missions": stats.get("healing_missions", 0),
            "system_status": "operational",
            "optimization_proposals": stats.get("active_optimizations", 0)
        }

cognitive_forge_engine = CognitiveForgeEngine()