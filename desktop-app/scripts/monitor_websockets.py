#!/usr/bin/env python3
"""
WebSocket Connection Monitor for Sentinel

This script provides real-time monitoring of WebSocket connections and events
in the Sentinel system. It displays a live dashboard in the terminal.

Usage:
    python monitor_websockets.py [--host localhost] [--port 8001] [--interval 2]
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import datetime
import curses
import requests
import websockets
from typing import Dict, List, Any, Optional, Tuple

# Configure logging to a file instead of stdout (which would interfere with the UI)
LOG_FILE = "websocket_monitor.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE)]
)
logger = logging.getLogger("websocket-monitor")

# Default configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001
DEFAULT_INTERVAL = 2  # seconds
DEFAULT_API_PREFIX = "/api"
DEFAULT_WS_PATH = "ws/mission-updates"

# Global state
monitoring_active = True
event_history = []
connection_history = []
error_messages = []
last_diagnostics = {}
last_status_check = 0

class MonitorState:
    """Class to hold monitor state"""
    def __init__(self):
        self.event_history = []
        self.connection_history = []
        self.error_messages = []
        self.last_diagnostics = {}
        self.last_status_check = 0
        self.server_status = "Unknown"
        self.mission_count = 0
        self.ws_status = "Unknown"
        self.ws_connection_count = 0
        self.events_broadcast = 0
        self.last_event_time = "Never"
        self.monitor_start_time = time.time()

def fetch_websocket_diagnostics(host: str, port: int) -> Dict:
    """Fetch WebSocket diagnostics from the server"""
    try:
        url = f"http://{host}:{port}/api/system/diagnostics/websockets"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch diagnostics: {response.status_code}")
            return {}
    except requests.RequestException as e:
        logger.error(f"Error fetching diagnostics: {e}")
        return {}

def fetch_server_status(host: str, port: int) -> Dict:
    """Fetch server status"""
    try:
        url = f"http://{host}:{port}/api/system/status"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch server status: {response.status_code}")
            return {"status": "error"}
    except requests.RequestException as e:
        logger.error(f"Error fetching server status: {e}")
        return {"status": "unreachable"}

def fetch_mission_count(host: str, port: int) -> int:
    """Fetch mission count"""
    try:
        url = f"http://{host}:{port}/api/missions"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return len(response.json())
        else:
            logger.error(f"Failed to fetch missions: {response.status_code}")
            return 0
    except requests.RequestException as e:
        logger.error(f"Error fetching missions: {e}")
        return 0

async def monitor_websocket(host: str, port: int, ws_path: str, state: MonitorState):
    """Monitor a WebSocket connection"""
    uri = f"ws://{host}:{port}/{ws_path}"
    
    try:
        # Connect to WebSocket
        connection_start = time.time()
        async with websockets.connect(uri, ping_interval=20, ping_timeout=30) as websocket:
            connection_time = time.time() - connection_start
            logger.info(f"Connected to {uri} in {connection_time:.2f}s")
            state.ws_status = "Connected"
            
            # Record connection in history
            state.connection_history.append({
                "time": time.time(),
                "status": "connected",
                "uri": uri,
                "connect_time": connection_time
            })
            
            # Listen for messages
            while monitoring_active:
                try:
                    # Set a timeout for receiving messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    
                    try:
                        # Parse JSON message
                        event_data = json.loads(message)
                        event_type = event_data.get("event_type", "unknown")
                        
                        # Add to event history
                        state.event_history.append({
                            "time": time.time(),
                            "type": event_type,
                            "data": event_data
                        })
                        
                        # Trim history to keep only recent events
                        if len(state.event_history) > 100:
                            state.event_history = state.event_history[-100:]
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Received non-JSON message: {message[:100]}...")
                        
                except asyncio.TimeoutError:
                    # This is normal - no message received within timeout
                    pass
                except asyncio.CancelledError:
                    logger.info("WebSocket monitoring cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    state.error_messages.append({
                        "time": time.time(),
                        "source": "websocket",
                        "message": str(e)
                    })
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        state.ws_status = "Disconnected"
        state.error_messages.append({
            "time": time.time(),
            "source": "connection",
            "message": str(e)
        })
        
        # Record disconnection in history
        state.connection_history.append({
            "time": time.time(),
            "status": "disconnected",
            "uri": uri,
            "error": str(e)
        })

async def update_diagnostics(host: str, port: int, state: MonitorState):
    """Periodically update diagnostics information"""
    while monitoring_active:
        try:
            # Only fetch diagnostics every 5 seconds
            if time.time() - state.last_status_check > 5:
                # Fetch WebSocket diagnostics
                diagnostics = fetch_websocket_diagnostics(host, port)
                if diagnostics:
                    state.last_diagnostics = diagnostics
                    state.ws_connection_count = diagnostics.get("active_connections", 0)
                    state.events_broadcast = diagnostics.get("events_broadcast", 0)
                    state.last_event_time = diagnostics.get("last_event_time", "Never")
                
                # Fetch server status
                status = fetch_server_status(host, port)
                state.server_status = status.get("status", "Unknown")
                
                # Fetch mission count
                state.mission_count = fetch_mission_count(host, port)
                
                state.last_status_check = time.time()
        except Exception as e:
            logger.error(f"Error updating diagnostics: {e}")
            state.error_messages.append({
                "time": time.time(),
                "source": "diagnostics",
                "message": str(e)
            })
        
        # Wait before next update
        await asyncio.sleep(2)

def format_time(timestamp: float) -> str:
    """Format a timestamp as a readable string"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S")

def format_duration(seconds: float) -> str:
    """Format a duration in seconds as a readable string"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def draw_dashboard(stdscr, state: MonitorState):
    """Draw the dashboard UI"""
    # Get terminal size
    max_y, max_x = stdscr.getmaxlines(), stdscr.getmaxyx()[1]
    
    # Clear the screen
    stdscr.clear()
    
    # Set up colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # Green for good status
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Yellow for warnings
    curses.init_pair(3, curses.COLOR_RED, -1)  # Red for errors
    curses.init_pair(4, curses.COLOR_CYAN, -1)  # Cyan for info
    curses.init_pair(5, curses.COLOR_WHITE, -1)  # White for normal text
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)  # White bg for headers
    
    # Draw header
    header = " Sentinel WebSocket Monitor "
    stdscr.attron(curses.color_pair(6))
    stdscr.addstr(0, 0, header.ljust(max_x))
    stdscr.attroff(curses.color_pair(6))
    
    # Draw uptime
    uptime = time.time() - state.monitor_start_time
    uptime_str = f"Monitor uptime: {format_duration(uptime)}"
    stdscr.addstr(0, max_x - len(uptime_str) - 1, uptime_str)
    
    # Draw server status section
    stdscr.addstr(2, 2, "Server Status:", curses.color_pair(4))
    
    if state.server_status == "running":
        status_color = curses.color_pair(1)
        status_text = "RUNNING"
    elif state.server_status == "error":
        status_color = curses.color_pair(3)
        status_text = "ERROR"
    else:
        status_color = curses.color_pair(2)
        status_text = state.server_status.upper()
    
    stdscr.addstr(2, 17, status_text, status_color)
    stdscr.addstr(3, 2, f"Missions: {state.mission_count}")
    
    # Draw WebSocket status section
    stdscr.addstr(2, 40, "WebSocket Status:", curses.color_pair(4))
    
    if state.ws_status == "Connected":
        ws_color = curses.color_pair(1)
    else:
        ws_color = curses.color_pair(3)
    
    stdscr.addstr(2, 57, state.ws_status, ws_color)
    stdscr.addstr(3, 40, f"Active Connections: {state.ws_connection_count}")
    stdscr.addstr(4, 40, f"Events Broadcast: {state.events_broadcast}")
    stdscr.addstr(5, 40, f"Last Event: {state.last_event_time}")
    
    # Draw event history section
    stdscr.addstr(7, 2, "Recent Events:", curses.color_pair(4))
    stdscr.addstr(8, 2, "Time".ljust(10) + "Type".ljust(20) + "Details")
    stdscr.hline(9, 2, '-', max_x - 4)
    
    event_y = 10
    for event in reversed(state.event_history[-10:]):
        if event_y >= max_y - 5:  # Leave room for error section
            break
            
        event_time = format_time(event["time"])
        event_type = event["type"]
        
        # Determine event color based on type
        if event_type in ["error", "exception"]:
            event_color = curses.color_pair(3)
        elif event_type in ["warning"]:
            event_color = curses.color_pair(2)
        else:
            event_color = curses.color_pair(5)
        
        # Add event to display
        stdscr.addstr(event_y, 2, event_time.ljust(10), event_color)
        stdscr.addstr(event_y, 12, event_type.ljust(20), event_color)
        
        # Add event details
        details = str(event["data"].get("mission_id", ""))
        if not details and "message" in event["data"]:
            details = event["data"]["message"][:40]
        stdscr.addstr(event_y, 32, details[:max_x - 34], event_color)
        
        event_y += 1
    
    # Draw error section
    error_start_y = max_y - 5
    stdscr.addstr(error_start_y, 2, "Recent Errors:", curses.color_pair(3))
    stdscr.hline(error_start_y + 1, 2, '-', max_x - 4)
    
    error_y = error_start_y + 2
    for error in reversed(state.error_messages[-3:]):
        if error_y >= max_y - 1:
            break
            
        error_time = format_time(error["time"])
        error_source = error["source"]
        error_message = error["message"]
        
        # Add error to display
        stdscr.addstr(error_y, 2, f"{error_time} [{error_source}]: {error_message[:max_x - 20]}", curses.color_pair(3))
        error_y += 1
    
    # Draw footer
    footer = " Press 'q' to quit | 'r' to reconnect "
    stdscr.attron(curses.color_pair(6))
    stdscr.addstr(max_y - 1, 0, footer.ljust(max_x))
    stdscr.attroff(curses.color_pair(6))
    
    # Refresh the screen
    stdscr.refresh()

async def handle_input(stdscr, state: MonitorState, host: str, port: int, ws_path: str):
    """Handle user input"""
    global monitoring_active
    
    stdscr.nodelay(True)  # Don't block on getch()
    
    while monitoring_active:
        try:
            # Check for user input
            key = stdscr.getch()
            
            if key == ord('q'):
                # Quit
                monitoring_active = False
            elif key == ord('r'):
                # Reconnect WebSocket
                logger.info("User requested WebSocket reconnection")
                state.error_messages.append({
                    "time": time.time(),
                    "source": "user",
                    "message": "Reconnection requested"
                })
                
                # Start a new WebSocket monitoring task
                # (We don't cancel the existing one as it will exit when it detects the error)
                asyncio.create_task(monitor_websocket(host, port, ws_path, state))
        except Exception as e:
            logger.error(f"Error handling input: {e}")
        
        # Sleep a bit to avoid hogging CPU
        await asyncio.sleep(0.1)

async def main_async(stdscr, host: str, port: int, ws_path: str, interval: int):
    """Main async function for the monitor"""
    global monitoring_active
    
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    # Initialize state
    state = MonitorState()
    
    # Start monitoring tasks
    ws_task = asyncio.create_task(monitor_websocket(host, port, ws_path, state))
    diag_task = asyncio.create_task(update_diagnostics(host, port, state))
    input_task = asyncio.create_task(handle_input(stdscr, state, host, port, ws_path))
    
    # Main loop - update display
    try:
        while monitoring_active:
            draw_dashboard(stdscr, state)
            await asyncio.sleep(interval)
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        monitoring_active = False
        
        # Cancel tasks
        for task in [ws_task, diag_task, input_task]:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

def main():
    """Main entry point for the script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Monitor WebSocket connections in Sentinel')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host to connect to (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to connect to (default: {DEFAULT_PORT})')
    parser.add_argument('--path', default=DEFAULT_WS_PATH, help=f'WebSocket path (default: {DEFAULT_WS_PATH})')
    parser.add_argument('--interval', type=float, default=DEFAULT_INTERVAL, 
                        help=f'Update interval in seconds (default: {DEFAULT_INTERVAL})')
    args = parser.parse_args()
    
    # Run the curses interface
    try:
        curses.wrapper(lambda stdscr: asyncio.run(main_async(stdscr, args.host, args.port, args.path, args.interval)))
    except KeyboardInterrupt:
        logger.info("Monitor interrupted by user")
    except Exception as e:
        logger.error(f"Error running monitor: {e}", exc_info=True)
        print(f"Error running monitor: {e}")
        print(f"See {LOG_FILE} for details")

if __name__ == "__main__":
    # Set the event loop policy for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the main function
    main()
