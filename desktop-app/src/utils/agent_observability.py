#!/usr/bin/env python3
"""
Unified Agent Observability & Real-Time Event Bus v1.5
Provides detailed tracking and a central, unified live stream for all system events.
"""

import os
# Disable problematic auto-patching before importing weave
os.environ["WEAVE_PATCH_ALL"] = "false"

import uuid
import time
import threading
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from collections import deque

try:
    import weave
    from weave.monitoring import span, log as weave_log
    WEAVE_AVAILABLE = True
except ImportError:
    weave, span, weave_log = None, contextmanager(lambda name: (yield)), lambda data: None
    WEAVE_AVAILABLE = False

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    wandb = None
    WANDB_AVAILABLE = False

from loguru import logger

# --- Unified Data Models ---

@dataclass
class LiveStreamEvent:
    """A standardized model for any real-time event pushed to the frontend."""
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: str = "generic"
    source: str = "system"
    server_port: str = "8001"
    severity: str = "INFO"
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

# Your other dataclasses for internal structure
@dataclass
class AgentAction:
    action_id: str = field(default_factory=lambda: f"action_{uuid.uuid4().hex[:8]}")
    # ... other fields as needed

@dataclass
class AgentSession:
    session_id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex[:8]}")
    # ... other fields as needed

@dataclass
class MissionObservability:
    mission_id: str
    user_request: str
    agent_sessions: Dict[str, AgentSession] = field(default_factory=dict)
    # ... other fields as needed

def _serialize_for_json(data: Any) -> Any:
    """Robustly and recursively converts objects to JSON-serializable formats."""
    if isinstance(data, (datetime,)):
        return data.isoformat()
    if isinstance(data, deque):
        return list(data)
    if isinstance(data, dict):
        return {k: _serialize_for_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_serialize_for_json(item) for item in data]
    if hasattr(data, '__dataclass_fields__'):
        return _serialize_for_json(asdict(data))
    return data

from fastapi import WebSocket

class CuttingEdgeAgentObservabilityManager:
    """Acts as the central Event Bus for all real-time data."""

    def __init__(self, project_name: str = "cognitive-forge-v5"):
        self.project_name = project_name
        self.weave_client = None
        self.wandb_run = None
        self.active_missions: Dict[str, MissionObservability] = {}
        self.completed_missions: deque = deque(maxlen=50)
        self.live_event_stream: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._lock = threading.Lock()
        self._websockets: List[WebSocket] = []
        self._initialize_integrations()
        try:
            asyncio.create_task(self._broadcast_events())
        except RuntimeError:
            # If not in an event loop, skip for now (will need to be started in app startup)
            pass

    def add_websocket(self, websocket: WebSocket):
        if websocket not in self._websockets:
            self._websockets.append(websocket)

    def remove_websocket(self, websocket: WebSocket):
        if websocket in self._websockets:
            self._websockets.remove(websocket)

    async def _broadcast_events(self):
        while True:
            event = await self.live_event_stream.get()
            for websocket in list(self._websockets):
                try:
                    await websocket.send_json(_serialize_for_json(event))
                except Exception as e:
                    logger.error(f"Failed to send event to websocket: {e}")
                    try:
                        await websocket.close()
                    except Exception:
                        pass
                    self.remove_websocket(websocket)

    def _initialize_integrations(self):
        if WEAVE_AVAILABLE:
            try:
                self.weave_client = weave.init(project_name=self.project_name)
                logger.success("✅ Weave observability initialized.")
            except Exception as e:
                logger.warning(f"⚠️ Weave initialization failed: {e}")
                self.weave_client = None
        if WANDB_AVAILABLE:
            try:
                self.wandb_run = wandb.init(project=self.project_name, reinit=True)
                logger.success("✅ W&B initialized for agent analytics.")
            except Exception as e:
                logger.warning(f"⚠️ W&B initialization failed: {e}")
                self.wandb_run = None

    def push_event(self, event: LiveStreamEvent):
        """Pushes a standardized event to the live stream queue."""
        try:
            if self.live_event_stream.full():
                self.live_event_stream.get_nowait()
            self.live_event_stream.put_nowait(event)
        except Exception:
            pass

    def log_error(self, error: Exception, context: Dict, mission_id: Optional[str] = None):
        """Log an error and push it to the event stream."""
        self.push_event(LiveStreamEvent(
            event_type="system_log",
            severity="ERROR",
            message=f"Error in {context.get('component', 'system')}: {str(error)}",
            payload={"error_type": type(error).__name__, "context": context, "mission_id": mission_id}
        ))
        logger.error(f"Error in mission {mission_id or 'N/A'}: {error} | Context: {context}")

    # You can add more specific logging methods here that call push_event
    # For example:
    def log_agent_action(self, agent_name: str, action_type: str, message: str, payload: dict):
        self.push_event(LiveStreamEvent(
                    event_type="agent_action",
            source=agent_name,
            severity="INFO",
            message=message,
            payload=payload
        ))

    async def get_event(self) -> Optional[LiveStreamEvent]:
        """Get the next event from the live stream queue."""
        try:
            return await asyncio.wait_for(self.live_event_stream.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error getting event from queue: {e}")
            return None

# Global instance
agent_observability = CuttingEdgeAgentObservabilityManager() 