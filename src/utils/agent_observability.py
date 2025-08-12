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
from contextlib import contextmanager, suppress
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

# Import our advanced debug logger
from .debug_logger import debug_logger, log_function, log_websocket_event, diagnose_websockets, request_context
from .websocket_helpers import WebSocketStateEncoder

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

    @log_function
    def __init__(self, project_name: str = "cognitive-forge-v5"):
        self.project_name = project_name
        self.weave_client = None
        self.wandb_run = None
        self.active_missions: Dict[str, MissionObservability] = {}
        self.completed_missions: deque = deque(maxlen=50)
        self.live_event_stream: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._lock = threading.Lock()
        self._websockets: List[WebSocket] = []
        self._websocket_ids: Dict[int, Dict[str, Any]] = {}  # Track WebSocket metadata by ID
        self._initialize_integrations()
        
        # Start broadcast task if in an event loop
        with suppress(RuntimeError):
            asyncio.create_task(self._broadcast_events())
            debug_logger.info("WebSocket broadcast task created successfully")

    @log_function
    def add_websocket(self, websocket: WebSocket):
        """Add a new WebSocket connection to the broadcast list with detailed tracking."""
        websocket_id = id(websocket)
        
        # Create detailed metadata for this connection
        connection_info = {
            "websocket_id": websocket_id,
            "client": f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "Unknown",
            "added_at": datetime.utcnow().isoformat(),
            "state": "CONNECTED",
            "messages_sent": 0,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        with self._lock:
            if websocket not in self._websockets:
                self._websockets.append(websocket)
                self._websocket_ids[websocket_id] = connection_info
                
                # Enhanced logging
                log_websocket_event("connection_added", {
                    "connection_id": websocket_id,
                    "client": connection_info["client"],
                    "total_connections": len(self._websockets)
                })
            else:
                log_websocket_event("duplicate_connection", {
                    "connection_id": websocket_id,
                    "client": connection_info["client"]
                })

    @log_function
    def remove_websocket(self, websocket: WebSocket):
        """Remove a WebSocket connection from the broadcast list with cleanup."""
        websocket_id = id(websocket)
        
        with self._lock:
            if websocket in self._websockets:
                self._websockets.remove(websocket)
                
                # Get connection info before removing
                connection_info = self._websocket_ids.get(websocket_id, {"client": "Unknown"})
                
                # Enhanced logging
                log_websocket_event("connection_removed", {
                    "connection_id": websocket_id,
                    "client": connection_info.get("client", "Unknown"),
                    "total_connections": len(self._websockets),
                    "messages_sent": connection_info.get("messages_sent", 0),
                    "duration": connection_info.get("added_at", "Unknown")
                })
                
                # Clean up metadata
                if websocket_id in self._websocket_ids:
                    del self._websocket_ids[websocket_id]
            else:
                log_websocket_event("remove_nonexistent", {
                    "connection_id": websocket_id,
                    "total_connections": len(self._websockets)
                })

    async def _broadcast_events(self):
        """Process events from the queue and broadcast to connected WebSockets."""
        debug_logger.info("Starting WebSocket broadcast loop")
        
        while True:
            try:
                # Get next event from queue
                event = await self.live_event_stream.get()
                event_id = getattr(event, "event_id", "unknown")
                
                # Create diagnostic log with random sample ID for tracking this broadcast cycle
                broadcast_id = f"bcast_{uuid.uuid4().hex[:6]}"
                
                with request_context(broadcast_id=broadcast_id):
                    debug_logger.debug(
                        f"Broadcasting event {event_id} of type {event.event_type} to {len(self._websockets)} connections",
                        event_type=event.event_type,
                        connections=len(self._websockets)
                    )
                    
                    # Take a snapshot of connection states before broadcasting
                    if len(self._websockets) > 0:
                        diagnostics = diagnose_websockets(self._websockets)
                        # Use our WebSocketStateEncoder for safe JSON serialization
                        debug_logger.debug(f"WebSocket states before broadcast: {json.dumps(diagnostics, cls=WebSocketStateEncoder)}")
                    
                    # Make a copy of the websockets list to avoid modification during iteration
                    websockets_to_remove = []
                    serialized_event = _serialize_for_json(event)
                    
                    # Process each websocket
                    for idx, websocket in enumerate(list(self._websockets)):
                        websocket_id = id(websocket)
                        connection_info = self._websocket_ids.get(websocket_id, {})
                        
                        try:
                            # Log detailed connection state before sending
                            debug_logger.debug(
                                f"Sending to WebSocket {websocket_id} (index {idx})", 
                                connection_id=websocket_id,
                                client=connection_info.get("client", "Unknown"),
                                client_state=getattr(websocket, "client_state", None),
                                application_state=getattr(websocket, "application_state", None)
                            )
                            
                            # Verify connection is alive before sending
                            if hasattr(websocket, "client_state") and websocket.client_state.name == "CONNECTED":
                                # Send the event
                                await websocket.send_json(serialized_event)
                                
                                # Update connection metadata on success
                                if websocket_id in self._websocket_ids:
                                    self._websocket_ids[websocket_id]["messages_sent"] += 1
                                    self._websocket_ids[websocket_id]["last_activity"] = datetime.utcnow().isoformat()
                                
                                debug_logger.debug(f"Successfully sent event to WebSocket {websocket_id}")
                            else:
                                # Connection is not active, mark for removal
                                debug_logger.warning(
                                    f"WebSocket {websocket_id} found in disconnected state", 
                                    client_state=getattr(websocket, "client_state", None)
                                )
                                websockets_to_remove.append(websocket)
                                
                        except Exception as e:
                            # Log detailed error information
                            debug_logger.error(
                                f"Failed to send event to WebSocket {websocket_id}: {str(e)}",
                                connection_id=websocket_id,
                                error=str(e),
                                error_type=type(e).__name__,
                                client=connection_info.get("client", "Unknown")
                            )
                            websockets_to_remove.append(websocket)
                            
                            # Attempt to close gracefully
                            with suppress(Exception):
                                await websocket.close()
                    
                    # Remove dead websockets after iteration is complete
                    for ws in websockets_to_remove:
                        self.remove_websocket(ws)
                        
                    # Log completion of broadcast cycle
                    debug_logger.debug(
                        f"Completed broadcasting event {event_id} (removed {len(websockets_to_remove)} stale connections)",
                        event_type=event.event_type,
                        stale_connections=len(websockets_to_remove),
                        remaining_connections=len(self._websockets)
                    )
            
            except Exception as e:
                # Catch-all for any unexpected errors in the broadcast loop
                debug_logger.exception(f"Unexpected error in broadcast loop: {str(e)}")
                
                # Continue the loop - we don't want to crash the broadcast service

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
                # FIX: Updated `reinit` parameter to align with new W&B version
                self.wandb_run = wandb.init(project=self.project_name)
                logger.success("✅ W&B initialized for agent analytics.")
            except Exception as e:
                logger.warning(f"⚠️ W&B initialization failed: {e}")
                self.wandb_run = None

    @log_function
    def push_event(self, event: LiveStreamEvent):
        """Pushes a standardized event to the live stream queue with comprehensive diagnostics."""
        event_id = getattr(event, "event_id", "unknown")
        
        # Create a unique context for tracking this event through the system
        with request_context(event_id=event_id):
            try:
                # Validate WebSocket connections exist
                active_connections = len(self._websockets)
                
                debug_logger.debug(
                    f"Attempting to push event {event_id} of type {event.event_type}",
                    event_type=event.event_type,
                    active_connections=active_connections,
                    source=event.source,
                    severity=event.severity
                )
                
                # Check if we need to push based on available connections
                if not self._websockets:
                    debug_logger.info(
                        f"No active WebSocket connections, skipping event {event_id}",
                        event_type=event.event_type
                    )
                    return
                
                # Validate event type
                if not event or not isinstance(event, LiveStreamEvent):
                    debug_logger.error(
                        f"Invalid event type for event {event_id}: {type(event)}",
                        received_type=str(type(event))
                    )
                    return
                
                # Handle full queue with better error reporting
                if self.live_event_stream.full():
                    debug_logger.warning(
                        f"Event queue full when pushing event {event_id}, dropping oldest event",
                        queue_size=self.live_event_stream.qsize(),
                        max_size=self.live_event_stream.maxsize
                    )
                    try:
                        old_event = self.live_event_stream.get_nowait()
                        debug_logger.debug(
                            f"Dropped event from queue: {getattr(old_event, 'event_id', 'unknown')}",
                            event_type=getattr(old_event, "event_type", "unknown")
                        )
                    except Exception as e:
                        debug_logger.error(
                            f"Failed to remove item from full queue: {str(e)}",
                            error_type=type(e).__name__
                        )
                
                # Attempt to push to queue
                self.live_event_stream.put_nowait(event)
                
                # Log successful queue insertion with diagnostics
                debug_logger.debug(
                    f"Successfully queued event {event_id} for broadcast",
                    event_type=event.event_type,
                    queue_size=self.live_event_stream.qsize(),
                    active_connections=active_connections
                )
                
            except Exception as e:
                # Comprehensive error logging
                debug_logger.exception(
                    f"Failed to push event {event_id} to live stream: {str(e)}",
                    error=str(e),
                    error_type=type(e).__name__,
                    event_type=getattr(event, "event_type", "unknown"),
                    traceback=True
                )

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