"""
Synapse Logging System - Unified Consciousness & Pattern Recognition
Provides structured logging and pattern analysis across all system components
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from pathlib import Path


class SynapseLoggingSystem:
    """
    The Synapse Logging System - Unified Consciousness & Pattern Recognition
    Provides structured logging and pattern analysis across all system components
    """

    def __init__(self):
        self.log_file = Path("logs/synapse_system.log")
        self.patterns_file = Path("logs/pattern_analysis.json")
        self.metrics_file = Path("logs/system_metrics.json")
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Initialize pattern recognition
        self.patterns = {}
        self.metrics = {}
        self.system_events = []
        
        logger.info("Synapse Logging System initialized - Unified consciousness active")

    def log_mission_start(self, mission_id: str, user_prompt: str) -> None:
        """
        Log mission start with comprehensive context
        
        Args:
            mission_id: The mission identifier
            user_prompt: The original user prompt
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "mission_start",
            "mission_id": mission_id,
            "user_prompt": user_prompt,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("mission_start", event)

    def log_mission_completion(self, mission_id: str, result: Dict[str, Any]) -> None:
        """
        Log mission completion with results
        
        Args:
            mission_id: The mission identifier
            result: The mission result data
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "mission_completion",
            "mission_id": mission_id,
            "execution_time": result.get("execution_time", 0),
            "phases_completed": result.get("phases_completed", 0),
            "success": result.get("status") == "completed",
            "optimization_metrics": result.get("optimization_metrics", {}),
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("mission_completion", event)

    def log_mission_failure(self, mission_id: str, error: str, failed_phase: str) -> None:
        """
        Log mission failure with error details
        
        Args:
            mission_id: The mission identifier
            error: The error message
            failed_phase: The phase where failure occurred
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "mission_failure",
            "mission_id": mission_id,
            "error": error,
            "failed_phase": failed_phase,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("mission_failure", event)

    def log_phoenix_protocol_activation(self, mission_id: str, error_context: Dict[str, Any]) -> None:
        """
        Log Phoenix Protocol activation
        
        Args:
            mission_id: The mission identifier
            error_context: The error context that triggered Phoenix Protocol
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "phoenix_protocol_activation",
            "mission_id": mission_id,
            "error_context": error_context,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("phoenix_protocol_activation", event)

    def log_guardian_protocol_activation(self, mission_id: str, validation_type: str, result: Dict[str, Any]) -> None:
        """
        Log Guardian Protocol activation
        
        Args:
            mission_id: The mission identifier
            validation_type: Type of validation performed
            result: Validation results
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "guardian_protocol_activation",
            "mission_id": mission_id,
            "validation_type": validation_type,
            "validation_result": result,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("guardian_protocol_activation", event)

    def log_agent_performance(self, agent_role: str, performance_metrics: Dict[str, Any]) -> None:
        """
        Log agent performance metrics
        
        Args:
            agent_role: The agent role
            performance_metrics: Performance metrics for the agent
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "agent_performance",
            "agent_role": agent_role,
            "performance_metrics": performance_metrics,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("agent_performance", event)

    def log_optimization_event(self, optimization_type: str, metrics: Dict[str, Any]) -> None:
        """
        Log optimization events
        
        Args:
            optimization_type: Type of optimization performed
            metrics: Optimization metrics
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "optimization_event",
            "optimization_type": optimization_type,
            "metrics": metrics,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("optimization_event", event)

    def log_system_health(self, health_metrics: Dict[str, Any]) -> None:
        """
        Log system health metrics
        
        Args:
            health_metrics: System health metrics
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "system_health",
            "health_metrics": health_metrics,
            "system_state": self._capture_system_state()
        }
        
        self._log_event(event)
        self._update_patterns("system_health", event)

    def _log_event(self, event: Dict[str, Any]) -> None:
        """
        Log an event to the synapse log file
        
        Args:
            event: The event to log
        """
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to log event: {e}")

    def _capture_system_state(self) -> Dict[str, Any]:
        """
        Capture current system state
        
        Returns:
            System state information
        """
        try:
            import psutil
            
            return {
                "memory_usage": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "cpu_usage": psutil.cpu_percent(interval=1),
                "disk_usage": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "active_processes": len(psutil.pids()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except ImportError:
            return {
                "error": "psutil not available",
                "timestamp": datetime.utcnow().isoformat()
            }

    def _update_patterns(self, event_type: str, event: Dict[str, Any]) -> None:
        """
        Update pattern recognition data
        
        Args:
            event_type: Type of event
            event: Event data
        """
        if event_type not in self.patterns:
            self.patterns[event_type] = {
                "count": 0,
                "first_seen": event["timestamp"],
                "last_seen": event["timestamp"],
                "frequency": 0,
                "common_attributes": {}
            }
        
        pattern = self.patterns[event_type]
        pattern["count"] += 1
        pattern["last_seen"] = event["timestamp"]
        
        # Calculate frequency (events per hour)
        first_seen = datetime.fromisoformat(pattern["first_seen"])
        last_seen = datetime.fromisoformat(pattern["last_seen"])
        hours_elapsed = (last_seen - first_seen).total_seconds() / 3600
        pattern["frequency"] = pattern["count"] / max(hours_elapsed, 1)
        
        # Track common attributes
        for key, value in event.items():
            if key not in ["timestamp", "event_type"]:
                if key not in pattern["common_attributes"]:
                    pattern["common_attributes"][key] = {}
                
                if isinstance(value, (str, int, float, bool)):
                    if value not in pattern["common_attributes"][key]:
                        pattern["common_attributes"][key][value] = 0
                    pattern["common_attributes"][key][value] += 1

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in system events
        
        Returns:
            Pattern analysis results
        """
        analysis = {
            "total_events": sum(pattern["count"] for pattern in self.patterns.values()),
            "event_types": len(self.patterns),
            "patterns": self.patterns,
            "insights": [],
            "recommendations": []
        }
        
        # Generate insights
        for event_type, pattern in self.patterns.items():
            if pattern["frequency"] > 10:  # High frequency events
                analysis["insights"].append(f"High frequency {event_type} events detected")
            
            if pattern["count"] > 100:  # High volume events
                analysis["insights"].append(f"High volume {event_type} events detected")
        
        # Generate recommendations
        if analysis["total_events"] > 1000:
            analysis["recommendations"].append("Consider implementing event aggregation for high-volume logging")
        
        for event_type, pattern in self.patterns.items():
            if pattern["frequency"] > 50:
                analysis["recommendations"].append(f"Optimize {event_type} processing for high frequency")
        
        return analysis

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics
        
        Returns:
            System metrics
        """
        try:
            import psutil
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_health": {
                    "memory_usage_percent": psutil.virtual_memory().percent,
                    "cpu_usage_percent": psutil.cpu_percent(interval=1),
                    "disk_usage_percent": psutil.disk_usage('/').percent,
                    "active_processes": len(psutil.pids())
                },
                "logging_metrics": {
                    "total_events_logged": sum(pattern["count"] for pattern in self.patterns.values()),
                    "event_types_tracked": len(self.patterns),
                    "log_file_size_mb": self.log_file.stat().st_size / (1024 * 1024) if self.log_file.exists() else 0
                },
                "pattern_analysis": self.analyze_patterns()
            }
        except ImportError:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": "psutil not available for system metrics"
            }

    def save_patterns(self) -> None:
        """Save pattern analysis to file"""
        try:
            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(self.patterns, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def load_patterns(self) -> None:
        """Load pattern analysis from file"""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, "r", encoding="utf-8") as f:
                    self.patterns = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")

    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get Synapse Logging System statistics and status"""
        return {
            "protocol_name": "Synapse Logging System",
            "version": "1.0.0",
            "status": "active",
            "capabilities": [
                "Structured event logging",
                "Pattern recognition",
                "System health monitoring",
                "Performance metrics tracking",
                "Unified consciousness",
                "Real-time analysis"
            ],
            "event_types": [
                "mission_start",
                "mission_completion",
                "mission_failure",
                "phoenix_protocol_activation",
                "guardian_protocol_activation",
                "agent_performance",
                "optimization_event",
                "system_health"
            ],
            "log_file": str(self.log_file),
            "patterns_file": str(self.patterns_file),
            "total_events": sum(pattern["count"] for pattern in self.patterns.values()),
            "event_types_tracked": len(self.patterns)
        } 