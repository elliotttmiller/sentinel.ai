# Sentinel WebSocket Diagnostic Tools

This collection of tools helps diagnose and troubleshoot WebSocket connection issues in the Sentinel Dashboard application.

## Available Tools

### 1. WebSocket Test Client (`test_websocket.py`)

A standalone WebSocket client that connects to the server and reports on connection status.

**Usage:**
```
python scripts/test_websocket.py [--host localhost] [--port 8001]
```

**Options:**
- `--host`: The hostname to connect to (default: localhost)
- `--port`: The port to connect to (default: 8001)
- `--path`: The WebSocket path (default: ws/mission-updates)
- `--verbose`: Enable verbose logging

### 2. WebSocket Health Check (`check_websocket_health.py`)

Performs comprehensive health checks on the WebSocket system, checking server status, diagnostics endpoints, and connection establishment.

**Usage:**
```
python scripts/check_websocket_health.py [--full] [--fix]
```

**Options:**
- `--host`: The hostname to check (default: localhost)
- `--port`: The port to check (default: 8001)
- `--path`: The WebSocket path (default: ws/mission-updates)
- `--full`: Show detailed diagnostics
- `--fix`: Attempt to fix common issues

### 3. WebSocket Monitor (`monitor_websockets.py`)

A real-time terminal-based dashboard that monitors WebSocket connections and events.

**Usage:**
```
python scripts/monitor_websockets.py [--host localhost] [--port 8001] [--interval 2]
```

**Options:**
- `--host`: The hostname to monitor (default: localhost)
- `--port`: The port to monitor (default: 8001)
- `--path`: The WebSocket path (default: ws/mission-updates)
- `--interval`: Update interval in seconds (default: 2)

### Launcher Scripts

For convenience, you can use one of the launcher scripts to access all tools through a menu:

- **Windows Command Prompt**: `websocket_tools.bat`
- **PowerShell**: `websocket_tools.ps1`

## Troubleshooting Common WebSocket Issues

### WebSocket 403 Forbidden Errors

This typically occurs due to:
1. Authentication issues
2. CORS configuration problems
3. Invalid WebSocket path

**Solution:**
- Verify that any required authentication is correctly set up
- Check CORS headers in the server configuration
- Confirm that the WebSocket path is correct

### WebSocket Connections Closing When Navigating Between Pages

This can happen due to:
1. Browser page navigation destroying WebSocket connections
2. Missing reconnection logic in the frontend
3. Server closing idle connections

**Solution:**
- Implement robust reconnection logic in the frontend
- Store connection state in a service that survives page navigation
- Use the `monitor_websockets.py` tool to track connection lifecycle

### Failed to Send Event to WebSocket

This occurs when:
1. The WebSocket connection is closed unexpectedly
2. The server has stale connections in its connection manager
3. The client attempts to send on a closed connection

**Solution:**
- Use `check_websocket_health.py --fix` to attempt automatic fixes
- Check server logs for connection closure reasons
- Implement better connection state validation

## Advanced Debugging Tips

1. **Monitor connections in real-time**:
   ```
   python scripts/monitor_websockets.py
   ```

2. **Check WebSocket system health**:
   ```
   python scripts/check_websocket_health.py --full
   ```

3. **Test connections from outside the application**:
   ```
   python scripts/test_websocket.py
   ```

4. **Check diagnostic endpoints**:
   ```
   curl http://localhost:8001/api/system/diagnostics/websockets
   ```

5. **Use browser developer tools**:
   - Open the Network tab
   - Filter for WS/WSS connections
   - Inspect messages and connection state

## Integration with Sentinel System

These tools are designed to work with the Sentinel Dashboard's WebSocket system. They expect:

1. A WebSocket endpoint at `ws://host:port/ws/mission-updates`
2. An API status endpoint at `http://host:port/api/system/status`
3. A diagnostic endpoint at `http://host:port/api/system/diagnostics/websockets`

If your endpoints differ, use the appropriate command-line options to specify the correct paths.
