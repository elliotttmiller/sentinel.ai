#!/usr/bin/env python3
"""
Comprehensive Agent Observability System v1.0
Provides detailed tracking, monitoring, and visualization of AI agent activities.
Integrates with Weave for tracing and W&B for analytics.
"""

import uuid
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
import psutil

try:
    import weave
    WEAVE_AVAILABLE = True
except ImportError:
    weave = None
    WEAVE_AVAILABLE = False

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    wandb = None
    WANDB_AVAILABLE = False

from loguru import logger

# --- Data Models for Structured Observability ---

@dataclass
class AgentAction:
    """Detailed tracking of an individual, atomic agent action."""
    action_id: str = field(default_factory=lambda: f"action_{uuid.uuid4().hex[:8]}")
    action_type: str = "unknown"  # 'thinking', 'tool_call', 'decision', 'response', 'error'
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    tokens_used: int = 0
    cost_estimate: float = 0.0
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None

@dataclass
class AgentSession:
    """A container for all actions taken by a single agent for a specific task."""
    session_id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex[:8]}")
    agent_name: str = "unknown_agent"
    mission_id: str = "unknown_mission"
    session_description: str = "No description"
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    actions: List[AgentAction] = field(default_factory=list)
    success: bool = False
    total_tokens: int = 0
    total_cost: float = 0.0
    error_count: int = 0

@dataclass
class MissionObservability:
    """The top-level container for all observability data for a single mission."""
    mission_id: str
    user_request: str
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    agent_sessions: Dict[str, AgentSession] = field(default_factory=dict)
    success: bool = False
    total_cost: float = 0.0
    total_tokens: int = 0
    execution_path: Optional[str] = None
    complexity_score: Optional[float] = None


class AgentObservabilityManager:
    """Comprehensive agent observability manager with real-time monitoring."""

    def __init__(self, project_name: str = "cognitive-forge-v5.1"):
        self.project_name = project_name
        self.active_missions: Dict[str, MissionObservability] = {}
        self.completed_missions: List[MissionObservability] = []
        self._lock = threading.Lock()

        self._initialize_integrations()

    def _initialize_integrations(self):
        """Initialize Weave and W&B if available."""
        if WEAVE_AVAILABLE:
            try:
                # Use the same project name as W&B to avoid mismatch
                weave.init(project_name="cognitive-forge-v5")
                logger.success("✅ Weave observability initialized for agent tracking.")
            except Exception as e:
                logger.error(f"Failed to initialize Weave: {e}")
        if WANDB_AVAILABLE:
            try:
                wandb.init(project="cognitive-forge-v5", config={"system_version": "v5.1"})
                logger.success("✅ W&B initialized for agent analytics.")
            except Exception as e:
                logger.error(f"Failed to initialize W&B: {e}")

    @contextmanager
    def mission_observability(self, mission_id: str, user_request: str):
        """Context manager for complete mission observability."""
        mission_data = MissionObservability(mission_id=mission_id, user_request=user_request)
        with self._lock:
            self.active_missions[mission_id] = mission_data

        try:
            # Weave tracing for the entire mission
            if WEAVE_AVAILABLE:
                try:
                    # Use weave.ops.trace() for mission tracing
                    with weave.ops.trace(f"mission_{mission_id}") as trace:
                        trace.log("user_request", user_request)
                        yield mission_data
                except Exception as e:
                    # Fallback if weave tracing is not available
                    logger.warning(f"Weave tracing not available: {e}, using basic logging")
                    yield mission_data
            else:
                yield mission_data
        except Exception as e:
            mission_data.success = False
            self.log_error(e, {"context": "mission_execution"}, mission_id)
            raise
        finally:
            mission_data.end_time = datetime.utcnow()
            mission_data.total_duration_ms = (mission_data.end_time - mission_data.start_time).total_seconds() * 1000
            mission_data.total_cost = sum(s.total_cost for s in mission_data.agent_sessions.values())
            mission_data.total_tokens = sum(s.total_tokens for s in mission_data.agent_sessions.values())

            with self._lock:
                if mission_id in self.active_missions:
                    del self.active_missions[mission_id]
                self.completed_missions.append(mission_data)
                # Keep last 100 completed missions
                if len(self.completed_missions) > 100:
                    self.completed_missions.pop(0)

            # Log summary to W&B
            if WANDB_AVAILABLE:
                wandb.log({
                    "mission_summary": {
                        "mission_id": mission_id,
                        "duration_ms": mission_data.total_duration_ms,
                        "success": mission_data.success,
                        "total_cost": mission_data.total_cost,
                        "total_tokens": mission_data.total_tokens,
                        "agent_count": len(mission_data.agent_sessions),
                        "path": mission_data.execution_path,
                    }
                })

    @contextmanager
    def agent_session(self, agent_name: str, mission_id: str, session_description: str):
        """Context manager for a single agent's session."""
        session_data = AgentSession(
            agent_name=agent_name,
            mission_id=mission_id,
            session_description=session_description
        )
        with self._lock:
            if mission_id in self.active_missions:
                self.active_missions[mission_id].agent_sessions[session_data.session_id] = session_data

        try:
             # Weave tracing for the agent session
            if WEAVE_AVAILABLE:
                try:
                    # Use weave.ops.trace() for agent session tracing
                    with weave.ops.trace(f"agent_session_{agent_name}") as trace:
                        trace.log("description", session_description)
                        yield session_data
                except Exception as e:
                    # Fallback if weave tracing is not available
                    logger.warning(f"Weave tracing not available: {e}, using basic logging")
                    yield session_data
            else:
                yield session_data
        finally:
            session_data.end_time = datetime.utcnow()
            session_data.total_duration_ms = (session_data.end_time - session_data.start_time).total_seconds() * 1000
            session_data.total_tokens = sum(a.tokens_used for a in session_data.actions)
            session_data.total_cost = sum(a.cost_estimate for a in session_data.actions)
            session_data.error_count = sum(1 for a in session_data.actions if not a.success)

    def _log_action(self, mission_id: str, session_id: str, action: AgentAction):
        """Internal helper to log an action to its session."""
        with self._lock:
            if mission_id in self.active_missions and session_id in self.active_missions[mission_id].agent_sessions:
                session = self.active_missions[mission_id].agent_sessions[session_id]
                session.actions.append(action)
                log_data = asdict(action)

                # Log to Weave and W&B
                if WEAVE_AVAILABLE:
                    try:
                        # Use weave.ops.log() for action logging
                        weave.ops.log({f"agent_action_{action.action_type}": log_data})
                    except Exception as e:
                        logger.warning(f"Weave logging not available: {e}, using basic logging")
                if WANDB_AVAILABLE:
                    wandb.log({f"agent_{session.agent_name}_{action.action_type}": log_data})

                logger.trace(f"Logged action '{action.action_type}' for agent '{session.agent_name}'.")

    def log_agent_thinking(self, session_id: str, thought: str, confidence_score: float):
        """Log an agent's internal thought process."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        action = AgentAction(
            action_type="thinking",
            output_data={"thought": thought},
            reasoning=thought,
            confidence_score=confidence_score,
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_decision(self, session_id: str, decision_data: Dict, confidence_score: float, reasoning: str):
        """Log a decision made by an agent."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        action = AgentAction(
            action_type="decision",
            input_data=decision_data,
            output_data={"decision": decision_data.get("path", "unknown")},
            confidence_score=confidence_score,
            reasoning=reasoning,
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_response(self, session_id: str, response: Dict, tokens_used: int, cost_estimate: float):
        """Log the final response from an agent."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        action = AgentAction(
            action_type="response",
            output_data=response,
            tokens_used=tokens_used,
            cost_estimate=cost_estimate,
        )
        self._log_action(mission_id, session_id, action)

    def log_error(self, error: Exception, context: Dict, mission_id: str):
        """Log an error that occurred during a mission."""
        # This can be called outside a session context
        logger.error(f"Error in mission {mission_id}: {error} | Context: {context}")
        # In a real scenario, you might want to associate this with a session if possible
        # or log it at the mission level.

    def _find_mission_for_session(self, session_id: str) -> Optional[str]:
        """Find the mission ID for a given active session ID."""
        with self._lock:
            for mission_id, mission_data in self.active_missions.items():
                if session_id in mission_data.agent_sessions:
                    return mission_id
        logger.warning(f"Could not find active mission for session_id: {session_id}")
        return None

    # --- Analytics & Reporting Methods ---

    def get_mission_details(self, mission_id: str) -> Optional[Dict]:
        """Get detailed observability data for a specific mission."""
        with self._lock:
            mission = next((m for m in self.completed_missions if m.mission_id == mission_id), None)
            if mission:
                return asdict(mission)
        return None

    def get_agent_session_details(self, session_id: str) -> Optional[Dict]:
        """Get detailed data for a specific agent session."""
        with self._lock:
            for mission in self.completed_missions:
                if session_id in mission.agent_sessions:
                    return asdict(mission.agent_sessions[session_id])
        return None

    def get_agent_analytics(self) -> Dict:
        """Get comprehensive, aggregated analytics across all completed missions."""
        with self._lock:
            if not self.completed_missions:
                return {"message": "No completed missions to analyze."}

            all_sessions = [s for m in self.completed_missions for s in m.agent_sessions.values()]
            agent_names = set(s.agent_name for s in all_sessions)
            analytics = {"summary": {}, "by_agent": {}}

            analytics["summary"] = {
                "total_missions": len(self.completed_missions),
                "successful_missions": sum(1 for m in self.completed_missions if m.success),
                "avg_mission_duration_ms": sum(m.total_duration_ms for m in self.completed_missions) / len(self.completed_missions),
                "total_cost": sum(m.total_cost for m in self.completed_missions),
            }

            for name in agent_names:
                agent_sessions = [s for s in all_sessions if s.agent_name == name]
                if not agent_sessions: continue
                analytics["by_agent"][name] = {
                    "session_count": len(agent_sessions),
                    "avg_duration_ms": sum(s.total_duration_ms for s in agent_sessions) / len(agent_sessions),
                    "success_rate": sum(1 for s in agent_sessions if s.success) / len(agent_sessions),
                    "avg_tokens": sum(s.total_tokens for s in agent_sessions) / len(agent_sessions),
                    "total_cost": sum(s.total_cost for s in agent_sessions),
                }
        return analytics

    def generate_observability_report(self) -> Dict:
        """Generate a user-friendly summary report."""
        analytics = self.get_agent_analytics()
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "system_status": "Operational",
            "weave_status": "Available" if WEAVE_AVAILABLE else "Unavailable",
            "wandb_status": "Available" if WANDB_AVAILABLE else "Unavailable",
            "active_missions": len(self.active_missions),
            "completed_missions_in_memory": len(self.completed_missions),
            "analytics_summary": analytics
        }


# Global instance for the application to use
agent_observability = AgentObservabilityManager() 