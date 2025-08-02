#!/usr/bin/env python3
"""
Cutting-Edge Agent Observability & Real-Time Tracking System v3.1
Provides ultra-detailed tracking, monitoring, and visualization of AI agent activities.
Integrates with Weave for tracing and W&B for analytics with enhanced robustness.
"""

import os
# Disable problematic auto-patching before importing weave
os.environ["WEAVE_PATCH_ALL"] = "false"

import uuid
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from collections import deque
import psutil

try:
    import weave
    # <<< FIX #2: Import specific functions for robustness
    from weave.monitoring import span, log as weave_log
    WEAVE_AVAILABLE = True
except ImportError:
    weave = None
    span = contextmanager(lambda name: (yield))  # Dummy context manager
    weave_log = lambda data: None  # Dummy function
    WEAVE_AVAILABLE = False

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    wandb = None
    WANDB_AVAILABLE = False

from loguru import logger

# --- Ultra-Detailed Data Models for Cutting-Edge Observability ---

@dataclass
class AgentAction:
    """Ultra-detailed tracking of an individual, atomic agent action with real-time streaming."""
    action_id: str = field(default_factory=lambda: f"action_{uuid.uuid4().hex[:8]}")
    action_type: str = "unknown"  # 'thinking', 'tool_call', 'decision', 'response', 'error', 'test_execution', 'planning', 'analysis', 'optimization', 'validation'
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    tokens_used: int = 0
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None
    
    # Enhanced real-time tracking fields
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_calls: int = 0
    api_calls: int = 0
    tool_calls: int = 0
    test_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    # Cutting-edge tracking fields
    thought_process: Optional[str] = None
    decision_tree: Optional[Dict[str, Any]] = None
    context_window: Optional[Dict[str, Any]] = None
    attention_weights: Optional[List[float]] = None
    reasoning_chain: Optional[List[str]] = None
    confidence_breakdown: Optional[Dict[str, float]] = None
    uncertainty_metrics: Optional[Dict[str, float]] = None
    learning_progress: Optional[Dict[str, Any]] = None
    adaptation_metrics: Optional[Dict[str, Any]] = None
    collaboration_data: Optional[Dict[str, Any]] = None
    real_time_feedback: Optional[Dict[str, Any]] = None

@dataclass
class AgentSession:
    """A container for all actions taken by a single agent with real-time streaming."""
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
    error_count: int = 0
    
    # Enhanced tracking fields
    peak_memory_usage_mb: float = 0.0
    avg_cpu_usage_percent: float = 0.0
    total_network_calls: int = 0
    total_api_calls: int = 0
    total_tool_calls: int = 0
    test_suite_results: Optional[Dict[str, Any]] = None
    performance_baseline: Optional[Dict[str, Any]] = None
    
    # Real-time streaming fields
    live_action_stream: deque = field(default_factory=lambda: deque(maxlen=1000))
    real_time_metrics: Dict[str, Any] = field(default_factory=dict)
    adaptive_behavior: Dict[str, Any] = field(default_factory=dict)
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class MissionObservability:
    """The top-level container for all observability data with real-time streaming."""
    mission_id: str
    user_request: str
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    agent_sessions: Dict[str, AgentSession] = field(default_factory=dict)
    success: bool = False
    total_tokens: int = 0
    execution_path: Optional[str] = None
    complexity_score: Optional[float] = None
    
    # Enhanced mission tracking
    test_mode: bool = False
    test_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    agent_performance_comparison: Optional[Dict[str, Any]] = None
    
    # Real-time streaming fields
    live_mission_stream: deque = field(default_factory=lambda: deque(maxlen=2000))
    real_time_collaboration: Dict[str, Any] = field(default_factory=dict)
    adaptive_workflow: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentTestSuite:
    """Comprehensive test suite for agent validation with real-time tracking."""
    test_suite_id: str = field(default_factory=lambda: f"test_{uuid.uuid4().hex[:8]}")
    agent_name: str = "unknown_agent"
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    success_rate: float = 0.0
    performance_metrics: Optional[Dict[str, Any]] = None
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Real-time test tracking
    live_test_stream: deque = field(default_factory=lambda: deque(maxlen=500))
    real_time_performance: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LiveStreamEvent:
    """Real-time streaming event for live agent tracking."""
    event_id: str = field(default_factory=lambda: f"event_{uuid.uuid4().hex[:8]}")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "agent_action"  # 'agent_action', 'mission_update', 'system_event', 'collaboration', 'performance_alert'
    agent_name: Optional[str] = None
    mission_id: Optional[str] = None
    session_id: Optional[str] = None
    action_id: Optional[str] = None
    event_data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # 'debug', 'info', 'warning', 'error', 'critical'
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CuttingEdgeAgentObservabilityManager:
    """Cutting-Edge Agent Observability & Real-Time Tracking System v3.0"""

    def __init__(self, project_name: str = "cognitive-forge-v5"):
        self.project_name = project_name
        self.weave_client = None
        self.wandb_run = None
        self.active_missions: Dict[str, MissionObservability] = {}
        self.completed_missions: List[MissionObservability] = []
        self.live_stream_queue = deque(maxlen=1000)
        self.live_stream_subscribers: Set[str] = set()
        self.stream_events: List[Dict[str, Any]] = []
        self.real_time_metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._initialize_integrations()

    def _initialize_integrations(self):
        """Initialize Weave and W&B if available with enhanced error handling."""
        if WEAVE_AVAILABLE:
            try:
                self.weave_client = weave.init(project_name=self.project_name)
                logger.success("✅ Weave observability initialized for agent tracking.")
            except Exception as e:
                logger.error(f"Failed to initialize Weave: {e}")
                self.weave_client = None
        if WANDB_AVAILABLE:
            try:
                self.wandb_run = wandb.init(project=self.project_name, config={"system_version": "v5.1"}, reinit=True)
                logger.success("✅ W&B initialized for agent analytics.")
            except Exception as e:
                logger.error(f"Failed to initialize W&B: {e}")
                self.wandb_run = None

    def _start_system_monitoring(self):
        """Start real-time system monitoring with enhanced metrics."""
        def monitor_system():
            while True:
                try:
                    # Enhanced system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    network = psutil.net_io_counters()
                    
                    system_metrics = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_available_gb": memory.available / (1024**3),
                        "disk_percent": disk.percent,
                        "network_bytes_sent": network.bytes_sent,
                        "network_bytes_recv": network.bytes_recv,
                        "active_processes": len(psutil.pids())
                    }
                    
                    # Log to W&B for real-time monitoring
                    if WANDB_AVAILABLE:
                        wandb.log({"system_metrics": system_metrics})
                    
                    # Update real-time metrics
                    with self._lock:
                        self.real_time_metrics["system"] = system_metrics
                    
                    time.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                    time.sleep(10)
        
        self._system_monitor = threading.Thread(target=monitor_system, daemon=True)
        self._system_monitor.start()

    def _start_live_stream_processor(self):
        """Start real-time stream processing for live agent tracking."""
        def process_live_stream():
            while True:
                try:
                    # Process live stream events
                    while not self.live_stream_queue.empty():
                        event = self.live_stream_queue.popleft() # Changed from get_nowait to popleft
                        self._process_stream_event(event)
                    
                    # Update real-time metrics
                    self._update_real_time_metrics()
                    
                    time.sleep(0.1)  # Process every 100ms for real-time responsiveness
                    
                except Exception as e:
                    logger.error(f"Live stream processing error: {e}")
                    time.sleep(1)
        
        self._stream_processor = threading.Thread(target=process_live_stream, daemon=True)
        self._stream_processor.start()

    def _process_stream_event(self, event: LiveStreamEvent):
        """Process a live stream event with ultra-detailed tracking."""
        # Add to stream history
        self.stream_events.append(asdict(event)) # Changed from append to append
        
        # Update real-time metrics
        with self._lock:
            if event.event_type not in self.real_time_metrics:
                self.real_time_metrics[event.event_type] = []
            self.real_time_metrics[event.event_type].append(asdict(event))
            
            # Keep only last 1000 events per type
            if len(self.real_time_metrics[event.event_type]) > 1000:
                self.real_time_metrics[event.event_type] = self.real_time_metrics[event.event_type][-1000:]
        
        # Log to Weave for real-time tracing
        if WEAVE_AVAILABLE:
            try:
                weave_log({f"live_stream_{event.event_type}": asdict(event)})
            except Exception as e:
                logger.warning(f"Weave logging failed: {e}")
        
        # Log to W&B for analytics
        if WANDB_AVAILABLE:
            try:
                wandb.log({
                    f"live_stream_{event.event_type}": asdict(event),
                    "stream_event_count": len(self.stream_events)
                })
            except Exception as e:
                logger.warning(f"W&B logging failed: {e}")

    def _update_real_time_metrics(self):
        """Update real-time performance metrics."""
        with self._lock:
            # Calculate real-time agent performance
            active_agents = set()
            total_actions = 0
            success_rate = 0.0
            
            for mission in self.active_missions.values():
                for session in mission.agent_sessions.values():
                    active_agents.add(session.agent_name)
                    total_actions += len(session.actions)
                    if session.actions:
                        success_rate += sum(1 for a in session.actions if a.success) / len(session.actions)
            
            if active_agents:
                success_rate /= len(active_agents)
            
            self.real_time_metrics["performance"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "active_agents": len(active_agents),
                "total_actions": total_actions,
                "success_rate": success_rate,
                "active_missions": len(self.active_missions),
                "stream_events": len(self.stream_events)
            }

    def _create_live_stream_event(self, event_type: str, agent_name: str = None, 
                                 mission_id: str = None, session_id: str = None, 
                                 action_id: str = None, event_data: Dict[str, Any] = None,
                                 severity: str = "info", tags: List[str] = None) -> LiveStreamEvent:
        """Create a live stream event with detailed tracking."""
        event = LiveStreamEvent(
            event_type=event_type,
            agent_name=agent_name,
            mission_id=mission_id,
            session_id=session_id,
            action_id=action_id,
            event_data=event_data or {},
            severity=severity,
            tags=tags or []
        )
        
        # Add to live stream queue
        try:
            self.live_stream_queue.append(event) # Changed from put_nowait to append
        except queue.Full:
            # Remove oldest event if queue is full
            try:
                self.live_stream_queue.popleft() # Changed from get_nowait to popleft
                self.live_stream_queue.append(event)
            except:
                pass
        
        return event 

    @contextmanager
    def mission_observability(self, mission_id: str, user_request: str, test_mode: bool = False):
        """Context manager for complete mission observability with ultra-detailed tracking."""
        mission_data = MissionObservability(mission_id=mission_id, user_request=user_request)
        
        # Create live stream event for mission start
        start_event = self._create_live_stream_event(
            event_type="mission_start",
            agent_name="system",
            mission_id=mission_id,
            event_data={
                "user_request": user_request,
                "test_mode": test_mode,
                "timestamp": datetime.utcnow().isoformat()
            },
            severity="info"
        )
        self._process_stream_event(start_event)
        
        with self._lock:
            self.active_missions[mission_id] = mission_data
        
        try:
            # <<< FIX #2: Use the imported `span` directly
            with span(name=f"mission_{mission_id}") as s:
                if WEAVE_AVAILABLE:
                    s.set_input({"user_request": user_request, "test_mode": test_mode})
                yield mission_data
        except Exception as e:
            mission_data.success = False
            self.log_error(e, {"context": "mission_execution"}, mission_id)
            raise
        finally:
            mission_data.end_time = datetime.utcnow()
            mission_data.total_duration_ms = (mission_data.end_time - mission_data.start_time).total_seconds() * 1000
            mission_data.total_tokens = sum(s.total_tokens for s in mission_data.agent_sessions.values())
            
            # Create live stream event for mission completion
            end_event = self._create_live_stream_event(
                event_type="mission_complete",
                agent_name="system",
                mission_id=mission_id,
                event_data={
                    "success": mission_data.success,
                    "duration_ms": mission_data.total_duration_ms,
                    "total_tokens": mission_data.total_tokens,
                    "agent_count": len(mission_data.agent_sessions)
                },
                severity="info" if mission_data.success else "error"
            )
            self._process_stream_event(end_event)
            
            with self._lock:
                if mission_id in self.active_missions:
                    del self.active_missions[mission_id]
                self.completed_missions.append(mission_data)
                if len(self.completed_missions) > 100:
                    self.completed_missions.pop(0)
            
            if WANDB_AVAILABLE and self.wandb_run:
                try:
                    # Ensure mission_data is JSON serializable before logging to W&B
                    # Convert AgentAction objects to dictionaries
                    mission_dict = asdict(mission_data)
                    # Convert any remaining AgentAction objects in agent_sessions
                    for session_id, session in mission_dict.get('agent_sessions', {}).items():
                        if hasattr(session, 'actions'):
                            session['actions'] = [asdict(action) for action in session.actions]
                    
                    serializable_mission_data = self._serialize_for_json(mission_dict)
                    wandb.log({"mission_summary": serializable_mission_data})
                except Exception as e:
                    logger.warning(f"W&B logging failed: {e}")

    @contextmanager
    def agent_session(self, agent_name: str, mission_id: str, session_description: str = ""):
        """Context manager for agent session observability with ultra-detailed tracking."""
        session = AgentSession(
            agent_name=agent_name,
            mission_id=mission_id,
            session_description=session_description
        )
        
        # Create live stream event for session start
        start_event = self._create_live_stream_event(
            event_type="agent_session_start",
            agent_name=agent_name,
            mission_id=mission_id,
            event_data={
                "session_description": session_description,
                "timestamp": datetime.utcnow().isoformat()
            },
            severity="info"
        )
        self._process_stream_event(start_event)
        
        try:
            # <<< FIX #2: Use the imported `span` directly
            with span(name=f"agent_session_{session.session_id}") as s:
                if WEAVE_AVAILABLE:
                    s.set_input({
                        "agent_name": agent_name,
                        "mission_id": mission_id,
                        "session_description": session_description
                    })
                yield session
        except Exception as e:
            session.success = False
            session.error_count += 1
            self.log_error(e, {"context": "agent_session"}, session.session_id)
            raise
        finally:
            session.end_time = datetime.utcnow()
            session.total_duration_ms = (session.end_time - session.start_time).total_seconds() * 1000
            
            # Create live stream event for session completion
            end_event = self._create_live_stream_event(
                event_type="agent_session_complete",
                agent_name=agent_name,
                mission_id=mission_id,
                event_data={
                    "session_id": session.session_id,
                    "success": session.success,
                    "duration_ms": session.total_duration_ms,
                    "total_tokens": session.total_tokens,
                    "error_count": session.error_count
                },
                severity="info" if session.success else "error"
            )
            self._process_stream_event(end_event)

    def _log_action(self, mission_id: str, session_id: str, action: AgentAction):
        """Internal helper to log an action with ultra-detailed tracking and real-time streaming."""
        # Get current system metrics
        try:
            process = psutil.Process()
            action.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
            action.cpu_usage_percent = process.cpu_percent()
        except Exception as e:
            logger.warning(f"Could not get system metrics: {e}")

        with self._lock:
            if mission_id in self.active_missions and session_id in self.active_missions[mission_id].agent_sessions:
                session = self.active_missions[mission_id].agent_sessions[session_id]
                session.actions.append(action)
                
                # Add to live action stream
                session.live_action_stream.append(action)
                
                # Ensure action data is serializable before logging
                log_data = self._serialize_for_json(asdict(action))

                # Log to Weave and W&B
                if WEAVE_AVAILABLE:
                    try:
                        weave_log({f"agent_action_{action.action_type}": log_data})
                    except Exception as e:
                        logger.warning(f"Weave logging not available: {e}, using basic logging")
                if WANDB_AVAILABLE:
                    wandb.log({f"agent_{session.agent_name}_{action.action_type}": log_data})

                # Create live stream event for action
                self._create_live_stream_event(
                    event_type="agent_action",
                    agent_name=session.agent_name,
                    mission_id=mission_id,
                    session_id=session_id,
                    action_id=action.action_id,
                    event_data={
                        "action_type": action.action_type,
                        "duration_ms": action.duration_ms,
                        "success": action.success,
                        "tokens_used": action.tokens_used,
                        "confidence_score": action.confidence_score,
                        "memory_usage_mb": action.memory_usage_mb,
                        "cpu_usage_percent": action.cpu_usage_percent,
                        "input_data": action.input_data,
                        "output_data": action.output_data,
                        "reasoning": action.reasoning,
                        "thought_process": action.thought_process,
                        "decision_tree": action.decision_tree,
                        "attention_weights": action.attention_weights,
                        "reasoning_chain": action.reasoning_chain,
                        "confidence_breakdown": action.confidence_breakdown,
                        "uncertainty_metrics": action.uncertainty_metrics,
                        "learning_progress": action.learning_progress,
                        "adaptation_metrics": action.adaptation_metrics,
                        "collaboration_data": action.collaboration_data,
                        "real_time_feedback": action.real_time_feedback
                    },
                    severity="info" if action.success else "warning",
                    tags=["action", action.action_type, session.agent_name]
                )

                logger.trace(f"Logged action '{action.action_type}' for agent '{session.agent_name}'.")

    # --- Ultra-Detailed Action Logging Methods ---

    def log_agent_thinking(self, session_id: str, thought: str, confidence_score: float, 
                          reasoning_chain: List[str] = None, attention_weights: List[float] = None,
                          uncertainty_metrics: Dict[str, float] = None):
        """Log an agent's internal thought process with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="thinking",
            output_data={"thought": thought},
            reasoning=thought,
            confidence_score=confidence_score,
            reasoning_chain=reasoning_chain,
            attention_weights=attention_weights,
            uncertainty_metrics=uncertainty_metrics,
            thought_process=thought
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_decision(self, session_id: str, decision_data: Dict, confidence_score: float, 
                          reasoning: str, decision_tree: Dict[str, Any] = None,
                          confidence_breakdown: Dict[str, float] = None):
        """Log a decision made by an agent with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="decision",
            input_data=decision_data,
            output_data={"decision": decision_data.get("path", "unknown")},
            confidence_score=confidence_score,
            reasoning=reasoning,
            decision_tree=decision_tree,
            confidence_breakdown=confidence_breakdown
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_response(self, session_id: str, response: Dict, tokens_used: int,
                          context_window: Dict[str, Any] = None, learning_progress: Dict[str, Any] = None):
        """Log an agent response with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        # Ensure response is JSON serializable
        serialized_response = self._serialize_for_json(response)
        
        action = AgentAction(
            action_type="response",
            output_data=serialized_response,
            tokens_used=tokens_used,
            context_window=context_window,
            learning_progress=learning_progress
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_tool_call(self, session_id: str, tool_name: str, tool_input: Dict, 
                           tool_output: Dict, duration_ms: float, adaptation_metrics: Dict[str, Any] = None):
        """Log a tool call made by an agent with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="tool_call",
            input_data={"tool_name": tool_name, "tool_input": tool_input},
            output_data={"tool_output": tool_output},
            duration_ms=duration_ms,
            tool_calls=1,
            adaptation_metrics=adaptation_metrics
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_api_call(self, session_id: str, api_endpoint: str, request_data: Dict, 
                          response_data: Dict, duration_ms: float, collaboration_data: Dict[str, Any] = None):
        """Log an API call made by an agent with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="api_call",
            input_data={"api_endpoint": api_endpoint, "request_data": request_data},
            output_data={"response_data": response_data},
            duration_ms=duration_ms,
            api_calls=1,
            collaboration_data=collaboration_data
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_test_execution(self, session_id: str, test_name: str, test_input: Dict, 
                                test_output: Dict, test_success: bool, real_time_feedback: Dict[str, Any] = None):
        """Log a test execution by an agent with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="test_execution",
            input_data={"test_name": test_name, "test_input": test_input},
            output_data={"test_output": test_output},
            success=test_success,
            test_results={"test_name": test_name, "success": test_success, "output": test_output},
            real_time_feedback=real_time_feedback
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_planning(self, session_id: str, plan: str, confidence_score: float,
                          planning_steps: List[str] = None, resource_requirements: Dict[str, Any] = None):
        """Log agent planning activities with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="planning",
            output_data={"plan": plan},
            confidence_score=confidence_score,
            reasoning=plan,
            thought_process=plan,
            reasoning_chain=planning_steps,
            context_window={"resource_requirements": resource_requirements}
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_analysis(self, session_id: str, analysis_data: Dict, analysis_type: str,
                          insights: List[str] = None, patterns_detected: List[str] = None):
        """Log agent analysis activities with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="analysis",
            input_data={"analysis_type": analysis_type},
            output_data=analysis_data,
            reasoning=f"Analysis of type: {analysis_type}",
            thought_process=f"Analyzing {analysis_type}",
            reasoning_chain=insights,
            context_window={"patterns_detected": patterns_detected}
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_optimization(self, session_id: str, optimization_data: Dict, 
                              before_metrics: Dict[str, Any] = None, after_metrics: Dict[str, Any] = None,
                              improvement_score: float = None):
        """Log agent optimization activities with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="optimization",
            input_data={"before_metrics": before_metrics},
            output_data=optimization_data,
            reasoning=f"Optimization with improvement score: {improvement_score}",
            thought_process="Performing optimization",
            performance_metrics={"before": before_metrics, "after": after_metrics, "improvement_score": improvement_score}
        )
        self._log_action(mission_id, session_id, action)

    def log_agent_validation(self, session_id: str, validation_data: Dict, validation_type: str,
                            validation_results: Dict[str, Any] = None, quality_score: float = None):
        """Log agent validation activities with ultra-detailed tracking."""
        mission_id = self._find_mission_for_session(session_id)
        if not mission_id: return
        
        action = AgentAction(
            action_type="validation",
            input_data={"validation_type": validation_type},
            output_data=validation_data,
            reasoning=f"Validation of type: {validation_type}",
            thought_process=f"Validating {validation_type}",
            test_results=validation_results,
            performance_metrics={"quality_score": quality_score}
        )
        self._log_action(mission_id, session_id, action)

    def log_error(self, error: Exception, context: Dict, mission_id: str):
        """Log an error that occurred during a mission with enhanced tracking."""
        logger.error(f"Error in mission {mission_id}: {error} | Context: {context}")
        
        # Create live stream event for error
        self._create_live_stream_event(
            event_type="system_error",
            mission_id=mission_id,
            event_data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            },
            severity="error",
            tags=["error", "system"]
        )
        
        # Log to W&B for error tracking
        if WANDB_AVAILABLE:
            wandb.log({
                "system_error": {
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "context": context,
                    "mission_id": mission_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })

    def _find_mission_for_session(self, session_id: str) -> Optional[str]:
        """Find the mission ID for a given active session ID."""
        with self._lock:
            for mission_id, mission_data in self.active_missions.items():
                if session_id in mission_data.agent_sessions:
                    return mission_id
        logger.warning(f"Could not find active mission for session_id: {session_id}")
        return None

    # --- Real-Time Streaming Methods ---

    def get_live_stream_events(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get live stream events for real-time monitoring."""
        with self._lock:
            events = list(self.stream_events)
            if event_type:
                events = [e for e in events if e["event_type"] == event_type] # Changed from asdict to direct access
            return events[-limit:]

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics."""
        with self._lock:
            return self.real_time_metrics.copy()

    def get_agent_live_stream(self, agent_name: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get live stream of agent actions."""
        with self._lock:
            events = list(self.stream_events)
            if agent_name:
                events = [e for e in events if e["agent_name"] == agent_name] # Changed from asdict to direct access
            return events[-limit:]

    def get_mission_live_stream(self, mission_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get live stream of mission events."""
        with self._lock:
            events = list(self.stream_events)
            if mission_id:
                events = [e for e in events if e["mission_id"] == mission_id] # Changed from asdict to direct access
            return events[-limit:]

    # --- Enhanced Analytics & Reporting Methods ---

    def _calculate_mission_performance(self, mission_data: MissionObservability) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics for a mission."""
        if not mission_data.agent_sessions:
            return {}
        
        sessions = list(mission_data.agent_sessions.values())
        
        return {
            "total_agents": len(sessions),
            "avg_session_duration_ms": sum(s.total_duration_ms for s in sessions) / len(sessions),
            "total_tokens": sum(s.total_tokens for s in sessions),
            "success_rate": sum(1 for s in sessions if s.success) / len(sessions),
            "peak_memory_usage_mb": max(s.peak_memory_usage_mb for s in sessions),
            "avg_cpu_usage_percent": sum(s.avg_cpu_usage_percent for s in sessions) / len(sessions),
            "total_network_calls": sum(s.total_network_calls for s in sessions),
            "total_api_calls": sum(s.total_api_calls for s in sessions),
            "total_tool_calls": sum(s.total_tool_calls for s in sessions)
        }

    def _compare_agent_performance(self, mission_data: MissionObservability) -> Dict[str, Any]:
        """Compare performance across different agents in the mission."""
        if not mission_data.agent_sessions:
            return {}
        
        agent_comparison = {}
        for session in mission_data.agent_sessions.values():
            agent_name = session.agent_name
            if agent_name not in agent_comparison:
                agent_comparison[agent_name] = {
                    "sessions": 0,
                    "total_duration_ms": 0,
                    "total_tokens": 0,
                    "success_count": 0,
                    "error_count": 0
                }
            
            agent_comparison[agent_name]["sessions"] += 1
            agent_comparison[agent_name]["total_duration_ms"] += session.total_duration_ms
            agent_comparison[agent_name]["total_tokens"] += session.total_tokens
            agent_comparison[agent_name]["success_count"] += 1 if session.success else 0
            agent_comparison[agent_name]["error_count"] += session.error_count
        
        # Calculate averages
        for agent_name, data in agent_comparison.items():
            data["avg_duration_ms"] = data["total_duration_ms"] / data["sessions"]
            data["avg_tokens"] = data["total_tokens"] / data["sessions"]
            data["success_rate"] = data["success_count"] / data["sessions"]
        
        return agent_comparison

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
            analytics = {"summary": {}, "by_agent": {}, "performance_trends": {}}

            analytics["summary"] = {
                "total_missions": len(self.completed_missions),
                "successful_missions": sum(1 for m in self.completed_missions if m.success),
                "avg_mission_duration_ms": sum(m.total_duration_ms for m in self.completed_missions) / len(self.completed_missions),
                "total_tokens": sum(m.total_tokens for m in self.completed_missions),
                "test_missions": sum(1 for m in self.completed_missions if m.test_mode)
            }

            for name in agent_names:
                agent_sessions = [s for s in all_sessions if s.agent_name == name]
                if not agent_sessions: continue
                analytics["by_agent"][name] = {
                    "session_count": len(agent_sessions),
                    "avg_duration_ms": sum(s.total_duration_ms for s in agent_sessions) / len(agent_sessions),
                    "success_rate": sum(1 for s in agent_sessions if s.success) / len(agent_sessions),
                    "avg_tokens": sum(s.total_tokens for s in agent_sessions) / len(agent_sessions),
                    "avg_memory_usage_mb": sum(s.peak_memory_usage_mb for s in agent_sessions) / len(agent_sessions),
                    "avg_cpu_usage_percent": sum(s.avg_cpu_usage_percent for s in agent_sessions) / len(agent_sessions),
                    "total_network_calls": sum(s.total_network_calls for s in agent_sessions),
                    "total_api_calls": sum(s.total_api_calls for s in agent_sessions),
                    "total_tool_calls": sum(s.total_tool_calls for s in agent_sessions)
                }
        
        return analytics

    def generate_observability_report(self) -> Dict:
        """Generate a user-friendly summary report with enhanced metrics."""
        analytics = self.get_agent_analytics()
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "system_status": "Operational",
            "weave_status": "Available" if WEAVE_AVAILABLE else "Unavailable",
            "wandb_status": "Available" if WANDB_AVAILABLE else "Unavailable",
            "active_missions": len(self.active_missions),
            "completed_missions_in_memory": len(self.completed_missions),
            "active_test_suites": len(self.active_test_suites),
            "completed_test_suites": len(self.completed_test_suites),
            "stream_events_count": len(self.stream_events),
            "real_time_metrics": self.real_time_metrics,
            "analytics_summary": analytics
        }

    # --- Testing & Validation Methods ---

    async def run_agent_test_suite(self, agent_name: str, test_cases: List[Dict[str, Any]]) -> AgentTestSuite:
        """Run a comprehensive test suite for an agent."""
        test_suite = AgentTestSuite(
            agent_name=agent_name,
            test_cases=test_cases,
            total_tests=len(test_cases)
        )
        
        with self._lock:
            self.active_test_suites[test_suite.test_suite_id] = test_suite
        
        try:
            for test_case in test_cases:
                test_result = await self._execute_test_case(agent_name, test_case)
                test_suite.test_results.append(test_result)
                
                if test_result["success"]:
                    test_suite.passed_tests += 1
                else:
                    test_suite.failed_tests += 1
            
            test_suite.success_rate = test_suite.passed_tests / test_suite.total_tests
            test_suite.performance_metrics = self._calculate_test_performance(test_suite)
            
        finally:
            test_suite.end_time = datetime.utcnow()
            with self._lock:
                if test_suite.test_suite_id in self.active_test_suites:
                    del self.active_test_suites[test_suite.test_suite_id]
                self.completed_test_suites.append(test_suite)
        
        return test_suite

    async def _execute_test_case(self, agent_name: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test case for an agent."""
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            # Simulate agent execution for testing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Mock test execution
            success = test_case.get("expected_success", True)
            result = {
                "test_id": test_id,
                "test_name": test_case.get("name", "Unknown Test"),
                "success": success,
                "duration_ms": (time.time() - start_time) * 1000,
                "input": test_case.get("input", {}),
                "output": test_case.get("expected_output", {}),
                "error_message": None if success else test_case.get("expected_error", "Test failed")
            }
            
            return result
            
        except Exception as e:
            return {
                "test_id": test_id,
                "test_name": test_case.get("name", "Unknown Test"),
                "success": False,
                "duration_ms": (time.time() - start_time) * 1000,
                "input": test_case.get("input", {}),
                "output": {},
                "error_message": str(e)
            }

    def _calculate_test_performance(self, test_suite: AgentTestSuite) -> Dict[str, Any]:
        """Calculate performance metrics for a test suite."""
        if not test_suite.test_results:
            return {}
        
        return {
            "avg_test_duration_ms": sum(r["duration_ms"] for r in test_suite.test_results) / len(test_suite.test_results),
            "total_duration_ms": sum(r["duration_ms"] for r in test_suite.test_results),
            "success_rate": test_suite.success_rate,
            "fastest_test_ms": min(r["duration_ms"] for r in test_suite.test_results),
            "slowest_test_ms": max(r["duration_ms"] for r in test_suite.test_results)
        }

    def get_test_suite_results(self, test_suite_id: str) -> Optional[Dict]:
        """Get detailed results for a specific test suite."""
        with self._lock:
            test_suite = next((ts for ts in self.completed_test_suites if ts.test_suite_id == test_suite_id), None)
            if test_suite:
                return asdict(test_suite)
        return None

    def get_agent_test_history(self, agent_name: str) -> List[Dict]:
        """Get test history for a specific agent."""
        with self._lock:
            agent_tests = [ts for ts in self.completed_test_suites if ts.agent_name == agent_name]
            return [asdict(ts) for ts in agent_tests]

    def export_observability_data(self, mission_id: Optional[str] = None) -> Dict[str, Any]:
        """Export observability data for analysis."""
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "system_info": {
                "weave_available": WEAVE_AVAILABLE,
                "wandb_available": WANDB_AVAILABLE,
                "active_missions": len(self.active_missions),
                "completed_missions": len(self.completed_missions),
                "completed_test_suites": len(self.completed_test_suites),
                "stream_events_count": len(self.stream_events)
            }
        }
        
        if mission_id:
            mission_data = self.get_mission_details(mission_id)
            if mission_data:
                export_data["mission_data"] = mission_data
        else:
            export_data["recent_missions"] = [asdict(m) for m in self.completed_missions[-10:]]
            export_data["recent_test_suites"] = [asdict(ts) for ts in self.completed_test_suites[-5:]]
            export_data["recent_stream_events"] = [asdict(e) for e in list(self.stream_events)[-100:]]
        
        return export_data

    def _serialize_for_json(self, obj):
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, deque):
            return list(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        else:
            return obj


# Global instance for the application to use
agent_observability = CuttingEdgeAgentObservabilityManager() 