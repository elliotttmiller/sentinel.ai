#!/usr/bin/env python3
"""
Advanced Debug Logging System for Sentinel
Provides standardized, detailed logging with context tracking and diagnostics
"""

import inspect
# import json  # Removed unused import
import os
import sys
import time
import uuid
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from functools import wraps
from loguru import logger
from .websocket_helpers import websocket_state_to_string

# Configure loguru with a more detailed format
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <yellow>{extra}</yellow> | <level>{message}</level>"

# Add production file handler with rotation
logger.remove()  # Remove default handler
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("logs/debug.log", rotation="10 MB", retention="7 days", format=LOG_FORMAT, level="DEBUG", backtrace=True, diagnose=True)

# Thread-local storage for request tracking
_request_context = threading.local()

def get_request_id() -> str:
    """Get the current request ID or generate a new one."""
    if not hasattr(_request_context, 'request_id'):
        _request_context.request_id = f"req_{uuid.uuid4().hex[:8]}"
    return _request_context.request_id

def set_request_id(request_id: str) -> None:
    """Set the request ID for the current thread."""
    _request_context.request_id = request_id

from typing import Generator

@contextmanager
def request_context(request_id: Optional[str] = None, **kwargs) -> Generator[None, None, None]:
    """Context manager to handle request context."""
    old_request_id = getattr(_request_context, 'request_id', None) if hasattr(_request_context, 'request_id') else None

    # Set new request ID
    if request_id is None:
        request_id = f"req_{uuid.uuid4().hex[:8]}"
    set_request_id(request_id)

    # Add any additional context
    old_context = {}
    for key, value in kwargs.items():
        old_context[key] = getattr(_request_context, key, None) if hasattr(_request_context, key) else None
        setattr(_request_context, key, value)

    try:
        logger.bind(request_id=request_id, **kwargs).debug(f"Starting context: {request_id}")
        yield
    finally:
        # Restore old context
        if old_request_id is not None:
            set_request_id(old_request_id)
        for key, value in old_context.items():
            if value is not None:
                setattr(_request_context, key, value)
            else:
                delattr(_request_context, key)
        logger.bind(request_id=request_id, **kwargs).debug(f"Ending context: {request_id}")

def log_function(func):
    """Decorator to log function entry and exit with timing."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        function_name = func.__qualname__
        module_name = func.__module__
        request_id = get_request_id()
        
        # Get call stack for context
        stack = inspect.stack()
        caller = stack[1].function if len(stack) > 1 else "unknown"
        
        # Create context for logging
        context = {
            "request_id": request_id,
            "function": function_name,
            "module": module_name,
            "caller": caller,
        }
        
        start_time = time.time()
        logger.bind(**context).debug(f"ENTER {function_name}")
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            logger.bind(**context, duration_ms=round(duration_ms, 2)).debug(f"EXIT {function_name}")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.bind(**context, duration_ms=round(duration_ms, 2), error=str(e), error_type=type(e).__name__).error(f"ERROR in {function_name}: {e}")
            raise
    return wrapper
def log_websocket_event(event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log WebSocket-specific events with detailed diagnostics."""
    if details is None:
        details = {}

    context = {
        "request_id": get_request_id(),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **details
    }

    # Add diagnostics information
    frame = inspect.currentframe()
    if frame is not None and frame.f_back is not None:
        frame = frame.f_back
        context["file"] = getattr(frame.f_code, "co_filename", "unknown")
        context["line"] = getattr(frame, "f_lineno", "unknown")
        context["function"] = getattr(frame.f_code, "co_name", "unknown")
    else:
        context["file"] = "unknown"
        context["line"] = "unknown"
        context["function"] = "unknown"

    logger.bind(**context).debug(f"WebSocket event: {event_type}")

# Create a diagnostic function to check the state of WebSockets
def diagnose_websockets(websockets: List) -> Dict[str, Any]:
    """Create a diagnostic snapshot of all WebSocket connections."""
    diagnostics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_connections": len(websockets),
        "connections": []
    }

    for i, ws in enumerate(websockets):
        try:
            # Use our helper function to safely convert WebSocketState to string
            client_state = getattr(ws, "client_state", None)
            client_state_name = websocket_state_to_string(client_state)

            application_state = getattr(ws, "application_state", None)
            app_state_name = websocket_state_to_string(application_state)

            connection_info = {
                "index": i,
                "id": id(ws),
                "client_state": client_state_name,
                "client_info": str(getattr(ws, "client", "unknown")),
                "application_state": app_state_name,
            }
            diagnostics["connections"].append(connection_info)
        except Exception as e:
            diagnostics["connections"].append({
                "index": i,
                "id": id(ws),
                "error": str(e)
            })

    # Add call site information
    context = {
        "request_id": get_request_id(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    frame = inspect.currentframe()
    if frame is not None and frame.f_back is not None:
        frame = frame.f_back
        context["file"] = os.path.basename(getattr(frame.f_code, "co_filename", "unknown"))
        context["line"] = getattr(frame, "f_lineno", "unknown")
        context["function"] = getattr(frame.f_code, "co_name", "unknown")
    else:
        context["file"] = "unknown"
        context["line"] = "unknown"
        context["function"] = "unknown"

    logger.bind(**context).debug("WebSocket diagnostics generated")
    return diagnostics
