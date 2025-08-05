#!/usr/bin/env python3
"""
WebSocket Health Check Utility for Sentinel

This script provides a comprehensive health check for the Sentinel WebSocket system.
It checks server status, WebSocket connection establishment, and message flow.

Usage:
    python check_websocket_health.py [--full] [--fix]
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import requests
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("websocket-health")

# Default configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001
DEFAULT_API_PREFIX = "/api"
DEFAULT_WS_PATH = "ws/mission-updates"
CHECK_TIMEOUT = 5  # seconds

class Colors:
    """Terminal colors for pretty output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colorize(text: str, color: str) -> str:
    """Add color to terminal output"""
    # Only use colors if running in a terminal
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text

async def check_server_status(host: str, port: int) -> Tuple[bool, str]:
    """Check if the HTTP server is running"""
    try:
        url = f"http://{host}:{port}/api/system/status"
        start_time = time.time()
        response = requests.get(url, timeout=CHECK_TIMEOUT)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            status_data = response.json()
            return True, f"Server is running (responded in {elapsed:.2f}s): {status_data}"
        else:
            return False, f"Server returned status code {response.status_code}"
    except requests.RequestException as e:
        return False, f"Failed to connect to server: {str(e)}"

async def check_websocket_diagnostics(host: str, port: int) -> Tuple[bool, Dict]:
    """Check WebSocket diagnostics endpoint"""
    try:
        url = f"http://{host}:{port}/api/system/diagnostics/websockets"
        response = requests.get(url, timeout=CHECK_TIMEOUT)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Diagnostics endpoint returned status code {response.status_code}"}
    except requests.RequestException as e:
        return False, {"error": f"Failed to connect to diagnostics endpoint: {str(e)}"}

async def test_websocket_connection(host: str, port: int, path: str) -> Tuple[bool, str]:
    """Test establishing a WebSocket connection"""
    uri = f"ws://{host}:{port}/{path}"
    
    try:
        start_time = time.time()
        async with websockets.connect(uri, ping_interval=None, close_timeout=CHECK_TIMEOUT) as websocket:
            elapsed = time.time() - start_time
            
            # Try to receive a message with timeout
            try:
                websocket.recv_timeout = CHECK_TIMEOUT
                await websocket.send(json.dumps({
                    "type": "health_check",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
                try:
                    # Wait for one message with a timeout
                    task = asyncio.create_task(websocket.recv())
                    message = await asyncio.wait_for(task, timeout=CHECK_TIMEOUT)
                    return True, f"Successfully connected in {elapsed:.2f}s and received initial message"
                except asyncio.TimeoutError:
                    return True, f"Successfully connected in {elapsed:.2f}s, but no initial message received"
            except Exception as e:
                return True, f"Connected in {elapsed:.2f}s, but error sending/receiving message: {str(e)}"
    except Exception as e:
        return False, f"Failed to establish WebSocket connection: {str(e)}"

async def check_mission_list(host: str, port: int) -> Tuple[bool, int]:
    """Check if missions can be retrieved"""
    try:
        url = f"http://{host}:{port}/api/missions"
        response = requests.get(url, timeout=CHECK_TIMEOUT)
        
        if response.status_code == 200:
            missions = response.json()
            return True, len(missions)
        else:
            return False, 0
    except requests.RequestException:
        return False, 0

async def check_full_diagnostic(host: str, port: int, ws_path: str) -> Dict[str, Any]:
    """Run a full diagnostic check"""
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check server status
    server_ok, server_msg = await check_server_status(host, port)
    results["checks"]["server"] = {
        "status": "ok" if server_ok else "error",
        "message": server_msg
    }
    
    # If server is not running, we can't continue with other checks
    if not server_ok:
        results["status"] = "critical"
        results["message"] = "Server is not running"
        return results
    
    # Check WebSocket diagnostics
    ws_diag_ok, ws_diag_data = await check_websocket_diagnostics(host, port)
    results["checks"]["websocket_diagnostics"] = {
        "status": "ok" if ws_diag_ok else "error",
        "data": ws_diag_data
    }
    
    # Test WebSocket connection
    ws_conn_ok, ws_conn_msg = await test_websocket_connection(host, port, ws_path)
    results["checks"]["websocket_connection"] = {
        "status": "ok" if ws_conn_ok else "error",
        "message": ws_conn_msg
    }
    
    # Check missions
    missions_ok, mission_count = await check_mission_list(host, port)
    results["checks"]["missions"] = {
        "status": "ok" if missions_ok else "error",
        "count": mission_count
    }
    
    # Determine overall status
    if not ws_conn_ok:
        results["status"] = "critical"
        results["message"] = "WebSocket connection failed"
    elif not ws_diag_ok:
        results["status"] = "warning"
        results["message"] = "WebSocket diagnostics failed but connection works"
    elif not missions_ok:
        results["status"] = "warning"
        results["message"] = "Mission list unavailable"
    else:
        results["status"] = "ok"
        results["message"] = "All systems operational"
    
    return results

def print_diagnostic_results(results: Dict[str, Any], detailed: bool = False):
    """Print diagnostic results in a human-readable format"""
    status = results["status"]
    
    if status == "ok":
        status_colored = colorize("OK", Colors.GREEN + Colors.BOLD)
    elif status == "warning":
        status_colored = colorize("WARNING", Colors.YELLOW + Colors.BOLD)
    else:
        status_colored = colorize("CRITICAL", Colors.RED + Colors.BOLD)
    
    print(f"\n===== Sentinel WebSocket Health Check Results =====")
    print(f"Status: {status_colored} - {results['message']}")
    print(f"Timestamp: {results['timestamp']}")
    print("===============================================\n")
    
    # Server check
    server_check = results["checks"]["server"]
    server_status = colorize("✓", Colors.GREEN) if server_check["status"] == "ok" else colorize("✗", Colors.RED)
    print(f"{server_status} Server: {server_check['message']}")
    
    # WebSocket diagnostics
    if "websocket_diagnostics" in results["checks"]:
        ws_diag = results["checks"]["websocket_diagnostics"]
        ws_diag_status = colorize("✓", Colors.GREEN) if ws_diag["status"] == "ok" else colorize("✗", Colors.RED)
        print(f"{ws_diag_status} WebSocket Diagnostics:")
        
        if detailed and ws_diag["status"] == "ok":
            diag_data = ws_diag["data"]
            print(f"  - Active connections: {diag_data.get('active_connections', 'N/A')}")
            print(f"  - Events broadcast: {diag_data.get('events_broadcast', 'N/A')}")
            print(f"  - Last event time: {diag_data.get('last_event_time', 'N/A')}")
            
            if "connection_info" in diag_data and diag_data["connection_info"]:
                print("  - Connection details:")
                for i, conn in enumerate(diag_data["connection_info"]):
                    print(f"    {i+1}. Client: {conn.get('client_info', 'Unknown')}")
                    print(f"       Connected: {conn.get('connected_at', 'Unknown')}")
                    print(f"       Last activity: {conn.get('last_activity', 'Unknown')}")
    
    # WebSocket connection
    if "websocket_connection" in results["checks"]:
        ws_conn = results["checks"]["websocket_connection"]
        ws_conn_status = colorize("✓", Colors.GREEN) if ws_conn["status"] == "ok" else colorize("✗", Colors.RED)
        print(f"{ws_conn_status} WebSocket Connection: {ws_conn['message']}")
    
    # Missions
    if "missions" in results["checks"]:
        missions = results["checks"]["missions"]
        missions_status = colorize("✓", Colors.GREEN) if missions["status"] == "ok" else colorize("✗", Colors.RED)
        print(f"{missions_status} Missions API: {'Available' if missions['status'] == 'ok' else 'Unavailable'}")
        if missions["status"] == "ok":
            print(f"  - Mission count: {missions['count']}")
    
    print("\n")

async def attempt_fix_common_issues(host: str, port: int, ws_path: str) -> Dict[str, Any]:
    """Attempt to fix common WebSocket issues"""
    fixes_applied = []
    fix_results = {}
    
    # First run a diagnostic to see what's wrong
    diag_results = await check_full_diagnostic(host, port, ws_path)
    
    # Check if the server is running
    if diag_results["checks"]["server"]["status"] != "ok":
        logger.info("Server is not running. Attempting to start server...")
        
        # Try to find start script
        potential_scripts = [
            "start_servers.ps1",
            "start_servers.bat",
            "scripts/start_sentinel.ps1",
            "scripts/start_sentinel.bat",
            "scripts/start_sentinel.py"
        ]
        
        script_found = False
        for script in potential_scripts:
            script_path = os.path.join(".", script)
            if os.path.exists(script_path):
                logger.info(f"Found start script: {script}")
                script_found = True
                
                # Don't actually run it automatically, just suggest it
                fixes_applied.append({
                    "issue": "server_not_running",
                    "action": "manual_required",
                    "message": f"Server needs to be started. Run '{script}'"
                })
                break
        
        if not script_found:
            fixes_applied.append({
                "issue": "server_not_running",
                "action": "manual_required",
                "message": "Server needs to be started. No start script found."
            })
        
        fix_results["server_start"] = {
            "status": "manual_required",
            "message": "Server needs to be started manually"
        }
        return {"fixes_applied": fixes_applied, "results": fix_results}
    
    # Check WebSocket diagnostics
    if "websocket_diagnostics" in diag_results["checks"] and diag_results["checks"]["websocket_diagnostics"]["status"] != "ok":
        logger.info("WebSocket diagnostics endpoint failed. This may require a server restart.")
        fixes_applied.append({
            "issue": "websocket_diagnostics_failed",
            "action": "manual_required",
            "message": "WebSocket diagnostics failed. Try restarting the server."
        })
    
    # Check WebSocket connection
    if "websocket_connection" in diag_results["checks"] and diag_results["checks"]["websocket_connection"]["status"] != "ok":
        logger.info("WebSocket connection failed. Checking for potential fixes...")
        
        # Try a simple restart request
        try:
            logger.info("Attempting to restart WebSocket system via API...")
            url = f"http://{host}:{port}/api/system/websockets/restart"
            response = requests.post(url, timeout=CHECK_TIMEOUT)
            
            if response.status_code == 200:
                logger.info("WebSocket system restart requested successfully")
                fixes_applied.append({
                    "issue": "websocket_connection_failed",
                    "action": "restart_requested",
                    "message": "Requested WebSocket system restart via API"
                })
                
                # Wait a moment for restart to complete
                logger.info("Waiting for system to restart...")
                await asyncio.sleep(2)
                
                # Check if the fix worked
                new_conn_ok, new_conn_msg = await test_websocket_connection(host, port, ws_path)
                fix_results["websocket_restart"] = {
                    "status": "success" if new_conn_ok else "failed",
                    "message": new_conn_msg
                }
            else:
                logger.error(f"Failed to restart WebSocket system: {response.status_code}")
                fixes_applied.append({
                    "issue": "websocket_connection_failed",
                    "action": "manual_required",
                    "message": "WebSocket system restart failed. Try restarting the server manually."
                })
        except requests.RequestException as e:
            logger.error(f"Failed to restart WebSocket system: {str(e)}")
            fixes_applied.append({
                "issue": "websocket_connection_failed",
                "action": "manual_required",
                "message": f"WebSocket restart request failed: {str(e)}"
            })
    
    if not fixes_applied:
        logger.info("No issues detected that require fixing")
    
    return {"fixes_applied": fixes_applied, "results": fix_results}

def print_fix_results(results: Dict[str, Any]):
    """Print fix results in a human-readable format"""
    fixes_applied = results["fixes_applied"]
    fix_results = results["results"]
    
    print("\n===== Fix Results =====")
    
    if not fixes_applied:
        print(colorize("No issues detected that required fixing", Colors.GREEN))
    else:
        for fix in fixes_applied:
            issue = fix["issue"]
            action = fix["action"]
            message = fix["message"]
            
            if action == "manual_required":
                action_colored = colorize("MANUAL ACTION REQUIRED", Colors.YELLOW)
            else:
                # Check if the fix worked
                fix_result = fix_results.get(issue.replace("_failed", "_restart"), {})
                if fix_result.get("status") == "success":
                    action_colored = colorize("FIXED", Colors.GREEN)
                else:
                    action_colored = colorize("ATTEMPTED", Colors.YELLOW)
            
            print(f"{action_colored}: {message}")
    
    print("=======================\n")

async def main():
    """Main entry point for the script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Check health of Sentinel WebSocket system')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host to connect to (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to connect to (default: {DEFAULT_PORT})')
    parser.add_argument('--path', default=DEFAULT_WS_PATH, help=f'WebSocket path (default: {DEFAULT_WS_PATH})')
    parser.add_argument('--full', action='store_true', help='Show detailed diagnostics')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix common issues')
    args = parser.parse_args()
    
    print(colorize("\n=== Sentinel WebSocket Health Check Utility ===", Colors.BLUE + Colors.BOLD))
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"WebSocket Path: {args.path}")
    print(f"Mode: {'Diagnostic' if not args.fix else 'Fix'} ({'Detailed' if args.full else 'Basic'})")
    print(colorize("=============================================\n", Colors.BLUE + Colors.BOLD))
    
    try:
        if args.fix:
            # Attempt to fix issues
            logger.info("Running in fix mode")
            fix_results = await attempt_fix_common_issues(args.host, args.port, args.path)
            print_fix_results(fix_results)
            
            # Run diagnostics again to see if fixes worked
            logger.info("Running post-fix diagnostics")
            diag_results = await check_full_diagnostic(args.host, args.port, args.path)
            print_diagnostic_results(diag_results, detailed=args.full)
        else:
            # Just run diagnostics
            logger.info("Running diagnostics")
            diag_results = await check_full_diagnostic(args.host, args.port, args.path)
            print_diagnostic_results(diag_results, detailed=args.full)
        
    except KeyboardInterrupt:
        logger.info("Health check interrupted by user")
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Set the event loop policy for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the main function
    asyncio.run(main())
