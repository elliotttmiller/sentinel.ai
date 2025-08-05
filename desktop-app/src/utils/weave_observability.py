#!/usr/bin/env python3
"""
Weave Observability Integration for Cognitive Forge System
Provides comprehensive monitoring, tracing, and analytics for multi-agent operations.
"""

import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import weave

    WEAVE_AVAILABLE = True
except ImportError:
    WEAVE_AVAILABLE = False
    print("Warning: Weave not available. Running without observability.")

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

from loguru import logger


@dataclass
class AgentMetrics:
    """Comprehensive metrics for agent performance tracking."""

    agent_name: str
    mission_id: str
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    api_calls: int = 0
    cost_estimate: float = 0.0


@dataclass
class MissionTrace:
    """Complete mission execution trace with all phases."""

    mission_id: str
    user_request: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    phases: List[Dict[str, Any]] = None
    agents_used: List[str] = None
    success: bool = False
    error_phase: Optional[str] = None
    rollback_count: int = 0
    surgical_fixes_applied: int = 0
    total_cost: float = 0.0


class WeaveObservabilityManager:
    """Comprehensive observability manager for the Cognitive Forge system."""

    def __init__(self, project_name: str = "cognitive-forge-v5"):
        self.project_name = project_name
        self.weave_client = None
        self.wandb_run = None
        self.active_traces = {}
        self.metrics_history = []
        self.performance_baselines = {}

        if WEAVE_AVAILABLE:
            self._initialize_weave()

        if WANDB_AVAILABLE:
            self._initialize_wandb()

    def _initialize_weave(self):
        """Initialize Weave client and configuration."""
        try:
            self.weave_client = weave.init(project_name=self.project_name)
            logger.info("✅ Weave observability initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Weave: {e}")
            self.weave_client = None

    def _initialize_wandb(self):
        """Initialize Weights & Biases for experiment tracking."""
        try:
            wandb.init(
                project=self.project_name,
                config={
                    "system_version": "v5.0",
                    "observability_enabled": True,
                    "weave_integration": True,
                },
            )
            self.wandb_run = wandb.run
            logger.info("✅ Weights & Biases initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize W&B: {e}")
            self.wandb_run = None

    @contextmanager
    def mission_trace(self, mission_id: str, user_request: str):
        """Context manager for comprehensive mission tracing."""
        trace_data = MissionTrace(
            mission_id=mission_id,
            user_request=user_request,
            start_time=datetime.now(),
            phases=[],
            agents_used=[],
        )

        try:
            if self.weave_client:
                with self.weave_client.trace(f"mission_{mission_id}") as trace:
                    trace.log("user_request", user_request)
                    trace.log("start_time", trace_data.start_time.isoformat())
                    self.active_traces[mission_id] = trace
                    yield trace_data
            else:
                yield trace_data

        except Exception as e:
            trace_data.error_phase = "trace_initialization"
            logger.error(f"Mission trace failed: {e}")
            yield trace_data
        finally:
            if mission_id in self.active_traces:
                del self.active_traces[mission_id]

    @contextmanager
    def agent_trace(self, agent_name: str, mission_id: str, task_description: str):
        """Context manager for agent-level tracing."""
        start_time = time.time()
        metrics = AgentMetrics(
            agent_name=agent_name,
            mission_id=mission_id,
            execution_time=0.0,
            success=False,
        )

        try:
            if self.weave_client and mission_id in self.active_traces:
                with self.active_traces[mission_id].span(f"agent_{agent_name}") as span:
                    span.log("task_description", task_description)
                    span.log("agent_name", agent_name)
                    yield metrics
            else:
                yield metrics

        except Exception as e:
            metrics.error_message = str(e)
            logger.error(f"Agent trace failed for {agent_name}: {e}")
            yield metrics
        finally:
            metrics.execution_time = time.time() - start_time
            self._record_agent_metrics(metrics)

    @contextmanager
    def phase_trace(self, phase_name: str, mission_id: str):
        """Context manager for phase-level tracing."""
        start_time = time.time()
        phase_data = {
            "phase_name": phase_name,
            "start_time": datetime.now(),
            "duration": 0.0,
            "success": False,
            "error": None,
        }

        try:
            if self.weave_client and mission_id in self.active_traces:
                with self.active_traces[mission_id].span(f"phase_{phase_name}") as span:
                    span.log("phase_name", phase_name)
                    yield phase_data
            else:
                yield phase_data

        except Exception as e:
            phase_data["error"] = str(e)
            logger.error(f"Phase trace failed for {phase_name}: {e}")
            yield phase_data
        finally:
            phase_data["duration"] = time.time() - start_time
            self._record_phase_metrics(phase_data)

    def _record_agent_metrics(self, metrics: AgentMetrics):
        """Record agent performance metrics."""
        self.metrics_history.append(asdict(metrics))

        # Update performance baselines
        if metrics.agent_name not in self.performance_baselines:
            self.performance_baselines[metrics.agent_name] = {
                "avg_execution_time": metrics.execution_time,
                "success_rate": 1.0 if metrics.success else 0.0,
                "total_executions": 1,
            }
        else:
            baseline = self.performance_baselines[metrics.agent_name]
            baseline["avg_execution_time"] = (
                baseline["avg_execution_time"] * baseline["total_executions"]
                + metrics.execution_time
            ) / (baseline["total_executions"] + 1)
            baseline["success_rate"] = (
                baseline["success_rate"] * baseline["total_executions"]
                + (1.0 if metrics.success else 0.0)
            ) / (baseline["total_executions"] + 1)
            baseline["total_executions"] += 1

        # Log to W&B if available
        if self.wandb_run:
            wandb.log(
                {
                    f"agent_{metrics.agent_name}_execution_time": metrics.execution_time,
                    f"agent_{metrics.agent_name}_success": (
                        1.0 if metrics.success else 0.0
                    ),
                    f"agent_{metrics.agent_name}_tokens": metrics.input_tokens
                    + metrics.output_tokens,
                    f"agent_{metrics.agent_name}_tool_calls": metrics.tool_calls,
                    f"agent_{metrics.agent_name}_memory_usage": metrics.memory_usage,
                    f"agent_{metrics.agent_name}_cpu_usage": metrics.cpu_usage,
                    f"agent_{metrics.agent_name}_cost": metrics.cost_estimate,
                }
            )

    def _record_phase_metrics(self, phase_data: Dict[str, Any]):
        """Record phase execution metrics."""
        if self.wandb_run:
            wandb.log(
                {
                    f"phase_{phase_data['phase_name']}_duration": phase_data[
                        "duration"
                    ],
                    f"phase_{phase_data['phase_name']}_success": (
                        1.0 if phase_data["success"] else 0.0
                    ),
                }
            )

    def log_system_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        mission_id: Optional[str] = None,
    ):
        """Log system-wide events for monitoring."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_data": event_data,
            "mission_id": mission_id,
        }

        if self.weave_client and mission_id and mission_id in self.active_traces:
            self.active_traces[mission_id].log(event_type, event_data)

        if self.wandb_run:
            wandb.log({f"system_{event_type}": event_data})

        logger.info(f"System event: {event_type} - {event_data}")

    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        mission_id: Optional[str] = None,
    ):
        """Log errors with full context for debugging."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }

        if self.weave_client and mission_id and mission_id in self.active_traces:
            self.active_traces[mission_id].log("error", error_data)

        if self.wandb_run:
            wandb.log({"system_error": error_data})

        logger.error(f"System error: {error_data}")

    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics."""
        if not self.metrics_history:
            return {"message": "No metrics available"}

        analytics = {
            "total_missions": len(set(m["mission_id"] for m in self.metrics_history)),
            "total_agent_executions": len(self.metrics_history),
            "agent_performance": {},
            "system_health": {
                "avg_execution_time": sum(
                    m["execution_time"] for m in self.metrics_history
                )
                / len(self.metrics_history),
                "success_rate": sum(1 for m in self.metrics_history if m["success"])
                / len(self.metrics_history),
                "total_cost": sum(m["cost_estimate"] for m in self.metrics_history),
            },
        }

        # Agent-specific analytics
        for agent_name in set(m["agent_name"] for m in self.metrics_history):
            agent_metrics = [
                m for m in self.metrics_history if m["agent_name"] == agent_name
            ]
            analytics["agent_performance"][agent_name] = {
                "total_executions": len(agent_metrics),
                "avg_execution_time": sum(m["execution_time"] for m in agent_metrics)
                / len(agent_metrics),
                "success_rate": sum(1 for m in agent_metrics if m["success"])
                / len(agent_metrics),
                "total_cost": sum(m["cost_estimate"] for m in agent_metrics),
            }

        return analytics

    def generate_observability_report(self) -> Dict[str, Any]:
        """Generate comprehensive observability report."""
        analytics = self.get_performance_analytics()

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": (
                "operational"
                if analytics["system_health"]["success_rate"] > 0.8
                else "degraded"
            ),
            "analytics": analytics,
            "performance_baselines": self.performance_baselines,
            "weave_available": WEAVE_AVAILABLE,
            "wandb_available": WANDB_AVAILABLE,
        }

        return report

    def cleanup(self):
        """Cleanup observability resources."""
        if self.wandb_run:
            wandb.finish()

        logger.info("Observability manager cleanup completed")


class WeaveEnhancedAgent:
    """Enhanced agent wrapper with Weave observability."""

    def __init__(
        self,
        agent_name: str,
        original_agent,
        observability_manager: WeaveObservabilityManager,
    ):
        self.agent_name = agent_name
        self.original_agent = original_agent
        self.observability = observability_manager

    async def execute(self, task, context: Dict[str, Any], mission_id: str):
        """Execute agent with full observability."""
        with self.observability.agent_trace(
            self.agent_name, mission_id, str(task)
        ) as metrics:
            try:
                # Execute the original agent
                result = await self.original_agent.execute(task, context)

                # Update metrics
                metrics.success = True
                metrics.input_tokens = getattr(result, "input_tokens", 0)
                metrics.output_tokens = getattr(result, "output_tokens", 0)
                metrics.tool_calls = getattr(result, "tool_calls", 0)

                return result

            except Exception as e:
                metrics.success = False
                metrics.error_message = str(e)
                self.observability.log_error(
                    e, {"agent": self.agent_name, "task": str(task)}, mission_id
                )
                raise


class WeaveEnhancedEngine:
    """Enhanced cognitive forge engine with Weave observability."""

    def __init__(
        self, original_engine, observability_manager: WeaveObservabilityManager
    ):
        self.original_engine = original_engine
        self.observability = observability_manager

    async def run_mission_with_observability(self, user_request: str) -> Dict[str, Any]:
        """Run mission with comprehensive observability."""
        mission_id = f"mission_{int(time.time())}"

        with self.observability.mission_trace(mission_id, user_request) as trace_data:
            try:
                # Phase 1: Prompt Optimization
                with self.observability.phase_trace(
                    "prompt_optimization", mission_id
                ) as phase_data:
                    optimized_result = (
                        await self.original_engine._execute_prompt_alchemy(user_request)
                    )
                    phase_data["success"] = True
                    trace_data.phases.append(phase_data)

                # Phase 2: Planning Specialist
                with self.observability.phase_trace(
                    "planning_specialist", mission_id
                ) as phase_data:
                    execution_blueprint = (
                        await self.original_engine._execute_planning_specialist(
                            optimized_result["optimized_prompt"],
                            optimized_result["technical_context"],
                        )
                    )
                    phase_data["success"] = True
                    trace_data.phases.append(phase_data)

                # Phase 3: Blueprint Validation
                with self.observability.phase_trace(
                    "blueprint_validation", mission_id
                ) as phase_data:
                    validation_result = (
                        await self.original_engine._validate_execution_blueprint(
                            execution_blueprint
                        )
                    )
                    phase_data["success"] = True
                    trace_data.phases.append(phase_data)

                # Phase 4: Mission Execution
                with self.observability.phase_trace(
                    "mission_execution", mission_id
                ) as phase_data:
                    execution_result = (
                        await self.original_engine._execute_mission_from_blueprint(
                            execution_blueprint, mission_id
                        )
                    )
                    phase_data["success"] = True
                    trace_data.phases.append(phase_data)

                # Mission completed successfully
                trace_data.end_time = datetime.now()
                trace_data.total_duration = (
                    trace_data.end_time - trace_data.start_time
                ).total_seconds()
                trace_data.success = True

                self.observability.log_system_event(
                    "mission_completed",
                    {
                        "duration": trace_data.total_duration,
                        "phases": len(trace_data.phases),
                    },
                    mission_id,
                )

                return execution_result

            except Exception as e:
                trace_data.end_time = datetime.now()
                trace_data.total_duration = (
                    trace_data.end_time - trace_data.start_time
                ).total_seconds()
                trace_data.success = False
                trace_data.error_phase = "mission_execution"

                self.observability.log_error(e, {"mission_id": mission_id}, mission_id)
                raise


# Global observability manager instance
observability_manager = WeaveObservabilityManager()
