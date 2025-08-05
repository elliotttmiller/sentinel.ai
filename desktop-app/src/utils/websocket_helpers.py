"""WebSocket helper utilities for Sentinel

This module provides helper functions for WebSocket handling,
particularly for JSON serialization of WebSocketState objects.
"""

import json
from typing import Any
from enum import Enum


class WebSocketStateEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles WebSocketState objects."""
    
    def default(self, obj: Any) -> Any:
        # Handle WebSocketState enum objects
        if hasattr(obj, 'name') and hasattr(obj, 'value'):
            # This is likely an enum, return its name as a string
            return obj.name
        
        # Handle other enum-like objects
        if hasattr(obj, '__class__') and 'State' in obj.__class__.__name__:
            # Try to get a string representation
            if hasattr(obj, 'name'):
                return obj.name
            elif hasattr(obj, 'value'):
                return str(obj.value)
            else:
                return str(obj)
        
        # Let the base class handle other objects
        return super().default(obj)


def safe_serialize_websocket_data(data: dict) -> str:
    """Safely serialize WebSocket data that may contain WebSocketState objects."""
    try:
        return json.dumps(data, cls=WebSocketStateEncoder)
    except Exception as e:
        # Fallback: convert problematic objects to strings
        safe_data = {}
        for key, value in data.items():
            try:
                json.dumps(value)
                safe_data[key] = value
            except:
                safe_data[key] = str(value)
        return json.dumps(safe_data)


def websocket_state_to_string(state) -> str:
    """Convert a WebSocketState object to a readable string."""
    if state is None:
        return "UNKNOWN"
    
    if hasattr(state, 'name'):
        return state.name
    elif hasattr(state, 'value'):
        return str(state.value)
    else:
        return str(state)
