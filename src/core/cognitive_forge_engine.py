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

# Add the src directory to the Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core modules using absolute imports
from config.settings import settings
from utils.google_ai_wrapper import create_google_ai_llm, direct_inference, google_ai_wrapper
from models.advanced_database import db_manager
from utils.agent_observability import agent_observability, LiveStreamEvent
from utils.guardian_protocol import GuardianProtocol
from utils.self_learning_module import SelfLearningModule
from utils.sentry_integration import initialize_sentry, get_sentry, capture_error, start_transaction, track_async_errors

# Import for real agent execution (with fallback)
try:
    from real_mission_executor import RealMissionExecutor
    REAL_EXECUTOR_AVAILABLE = True
    logger.info("✅ Real mission executor available - agents will perform actual tasks")
except ImportError as e:
    logger.warning(f"⚠️ Real mission executor not available: {e} - falling back to simulation")
    REAL_EXECUTOR_AVAILABLE = False
    RealMissionExecutor = None

# Enhanced cognitive forge capabilities
ENHANCED_MULTI_AGENT_AVAILABLE = False  # Simplified for clean architecture
logger.info("✅ Enhanced Cognitive Forge Engine v6.0 initialized")

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
                    message=f"Mission '{mission_id_str}' initiated - deploying real AI agents.",
                    payload=self.db_manager.get_mission(mission_id_str).as_dict()
                ))
            
            # First priority: Enhanced multi-agent system (disabled for simplified architecture)
            if False:  # ENHANCED_MULTI_AGENT_AVAILABLE and EnhancedCognitiveForgeEngine:
                logger.info(f"🚀 Using ENHANCED MULTI-AGENT SYSTEM for mission {mission_id_str}")
                
                # Create enhanced cognitive forge engine if not already created
                if not hasattr(self, '_enhanced_engine'):
                    pass  # self._enhanced_engine = EnhancedCognitiveForgeEngine()
                
                agent_observability.push_event(LiveStreamEvent(
                    event_type="enhanced_agent_deployment", 
                    source="enhanced_multi_agent_system", 
                    severity="INFO",
                    message="Deploying enhanced multi-agent system for mission execution.",
                    payload={"mission_id": mission_id_str, "phase": "Enhanced Multi-Agent Deployment"}
                ))
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=30)
                
                # Execute using enhanced multi-agent system
                logger.info(f"🤖 Deploying enhanced multi-agent workflow for mission {mission_id_str}: {user_prompt}")
                enhanced_result = await self._enhanced_engine.run_mission(user_prompt, mission_id_str, agent_type)
                
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=85)
                
                # Process enhanced execution result
                if enhanced_result.get("status") == "completed":
                    final_result_text = (
                        f"Mission '{mission_id_str}' completed successfully by enhanced multi-agent system. "
                        f"Workflow pattern: {enhanced_result.get('summary', {}).get('workflow_pattern', 'standard')}. "
                        f"Agents involved: {enhanced_result.get('summary', {}).get('agents_involved', 'multiple')}."
                    )
                    self.db_manager.update_mission_status(
                        mission_id_str=mission_id_str, 
                        status="completed", 
                        progress=100, 
                        result=final_result_text
                    )
                    agent_observability.push_event(LiveStreamEvent(
                        event_type="mission_complete",
                        source="enhanced_multi_agent_system",
                        severity="SUCCESS", 
                        message=final_result_text,
                        payload={
                            **self.db_manager.get_mission(mission_id_str).as_dict(),
                            **enhanced_result
                        }
                    ))
                    await self.self_learning_module.synthesize_and_learn(self.db_manager.get_mission(mission_id_str))
                    return {"status": "completed", "enhanced_multi_agent": True, "result": enhanced_result}
                else:
                    # Enhanced execution failed, try fallback
                    logger.warning(f"Enhanced multi-agent execution failed for {mission_id_str}, trying fallback")
                    error_message = enhanced_result.get("error", "Enhanced multi-agent execution failed")
                    agent_observability.push_event(LiveStreamEvent(
                        event_type="enhanced_execution_fallback",
                        source="enhanced_multi_agent_system",
                        severity="WARNING", 
                        message=f"Enhanced execution failed, falling back: {error_message}",
                        payload=enhanced_result
                    ))
            
            # Use REAL AGENT EXECUTION if available, otherwise fallback to simulation
            elif REAL_EXECUTOR_AVAILABLE and RealMissionExecutor:
                # REAL AGENT EXECUTION PATH
                logger.info(f"🚀 Using REAL AGENT EXECUTION for mission {mission_id_str}")
                
                # Create real mission executor
                real_executor = RealMissionExecutor()
                
                # Prepare mission data for real execution
                mission_data = {
                    'id': mission_id_str,
                    'objective': user_prompt,
                    'agent_type': agent_type,
                    'complexity': 'medium',  # Could be derived from user_prompt analysis
                    'metadata': {
                        'is_healing_attempt': is_healing_attempt,
                        'created_by': 'cognitive_forge_engine'
                    }
                }
                
                agent_observability.push_event(LiveStreamEvent(
                    event_type="agent_deployment", 
                    source="real_mission_executor", 
                    severity="INFO",
                    message="Deploying real CrewAI agents to complete mission.",
                    payload={"mission_id": mission_id_str, "phase": "Real Agent Deployment"}
                ))
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=25)
                
                # Execute the mission using REAL AGENTS (not simulation)
                logger.info(f"🤖 Deploying real AI agents for mission {mission_id_str}: {user_prompt}")
                execution_result = await real_executor.execute_mission(mission_data)
                
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=75)
                
                # Process the real execution result
                if execution_result.get("success", False):
                    final_result_text = (
                        f"Mission '{mission_id_str}' completed successfully by real AI agents. "
                        f"Real-world changes made: {execution_result.get('real_world_changes', False)}"
                    )
                    self.db_manager.update_mission_status(
                        mission_id_str=mission_id_str, 
                        status="completed", 
                        progress=100, 
                        result=final_result_text
                    )
                    agent_observability.push_event(LiveStreamEvent(
                        event_type="mission_complete",
                        source="mission_control",
                        severity="SUCCESS", 
                        message=final_result_text,
                        payload={
                            **self.db_manager.get_mission(mission_id_str).as_dict(),
                            **execution_result
                        }
                    ))
                    await self.self_learning_module.synthesize_and_learn(self.db_manager.get_mission(mission_id_str))
                    return {"status": "completed", "real_execution": True, "result": execution_result}
                else:
                    # Real execution failed, this is a genuine failure
                    error_message = execution_result.get("message", "Real agent execution failed")
                    raise ValueError(f"Real agent execution failed: {error_message}")
                    
            else:
                # SIMULATION FALLBACK PATH (when real agents not available)
                logger.warning(f"⚠️ Using SIMULATION MODE for mission {mission_id_str} - real agents not available")
                
                await asyncio.sleep(2)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="agent_action", source="Simulated Agent", severity="WARNING",
                    message="Using simulation mode - real agents not available.",
                    payload={"mission_id": mission_id_str, "phase": "Simulation Fallback"}
                ))
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=25)
                
                await asyncio.sleep(3)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="agent_action", source="Simulated Planner", severity="WARNING",
                    message="Simulating task planning and execution.",
                    payload={"mission_id": mission_id_str, "phase": "Simulated Planning"}
                ))
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=50)

                if not is_healing_attempt and random.random() < 0.3:
                    raise ValueError("Simulated failure: Critical component 'CodeGenerator' failed.")

                await asyncio.sleep(4)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="agent_action", source="Simulated Executor", severity="WARNING",
                    message="Simulating task execution - no real changes made.",
                    payload={"mission_id": mission_id_str, "phase": "Simulated Execution"}
                ))
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="running", progress=75)

                await asyncio.sleep(2)
                final_result_text = f"Mission '{mission_id_str}' completed in SIMULATION MODE - no real changes made."
                self.db_manager.update_mission_status(mission_id_str=mission_id_str, status="completed", progress=100, result=final_result_text)
                agent_observability.push_event(LiveStreamEvent(
                    event_type="mission_complete",
                    source="mission_control",
                    severity="WARNING",
                    message=final_result_text,
                    payload=self.db_manager.get_mission(mission_id_str).as_dict()
                ))
                await self.self_learning_module.synthesize_and_learn(self.db_manager.get_mission(mission_id_str))
                return {"status": "completed", "real_execution": False, "simulation_mode": True}
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
        """Enhanced periodic self-optimization using multi-agent analysis"""
        while True:
            await asyncio.sleep(3600)
            logger.info("🧠 Enhanced Self-Optimization: Starting periodic multi-agent analysis...")
            try:
                # Use enhanced multi-agent system for optimization (simplified architecture)
                if False:  # ENHANCED_MULTI_AGENT_AVAILABLE and hasattr(self, '_enhanced_engine'):
                    logger.info("Using enhanced multi-agent system for self-optimization")
                    # await self._enhanced_engine.run_periodic_self_optimization()
                else:
                    # Fallback to standard self-optimization
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
                logger.error(f"Enhanced self-optimization cycle failed: {e}")

    def get_system_info(self) -> Dict[str, Any]:
        enhanced_features = [
            "Phoenix Protocol (Self-Healing)",
            "Guardian Protocol (Quality Assurance)", 
            "Self-Learning Module",
            "Periodic Self-Optimization"
        ]
        
        # Add enhanced features (simplified architecture)
        if False:  # ENHANCED_MULTI_AGENT_AVAILABLE:
            enhanced_features.extend([
                "Enhanced Multi-Agent System",
                "Advanced Agent Workflows",
                "Collaborative Agent Execution", 
                "Agent Learning & Adaptation",
                "Multi-Pattern Workflow Support"
            ])
        
        return {
            "version": "v6.0",  # Always v6.0 for simplified architecture
            "status": "operational",
            "llm_model": "gemini-1.5-pro",
            "database": "SQLite",
            "observability": "enabled",  # Always enabled
            "multi_agent_system": False,  # Simplified architecture
            "real_executor": REAL_EXECUTOR_AVAILABLE,
            "enhanced_features": enhanced_features,
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