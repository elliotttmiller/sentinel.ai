from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
import time
import logging
import sys
from typing import Dict, Any

# --- Real-Time Logging & Streaming Setup ---
# This is the in-memory buffer that will hold recent logs for streaming
cognitive_log_buffer = []  # Start with empty buffer
# This is a queue that our SSE endpoint will listen to for new messages
cognitive_log_queue = asyncio.Queue()

class CognitiveLogInterceptor:
    """
    A custom handler class that intercepts log messages from cognitive engine
    and pushes them to our real-time stream.
    """
    def write(self, message: str):
        # This method is called for every log message
        try:
            # Clean the message and add it to our system
            clean_message = message.strip()
            if clean_message:
                log_entry = self.parse_log(clean_message)
                if log_entry is not None:  # Only add if not filtered out
                    cognitive_log_buffer.append(log_entry)
                    if len(cognitive_log_buffer) > 200: # Keep buffer from growing too large
                        cognitive_log_buffer.pop(0)
                    # Put the new log into the async queue for live streaming
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(cognitive_log_queue.put(log_entry), loop)
                    except RuntimeError:
                        # If no event loop is running, just add to buffer
                        pass
        except Exception as e:
            # If parsing fails, just pass the raw message
            pass

    def parse_log(self, message: str) -> Dict:
        """Parses a raw log string into a structured dictionary."""
        timestamp = datetime.utcnow().isoformat()
        level = "INFO"
        source = "cognitive_engine"
        server_port = "8002"  # Cognitive engine server
        
        # Skip debug logs to focus on real server logs
        if "urllib3.connectionpool" in message or "sentry" in message.lower():
            return None  # Skip these logs
        
        # Heuristics to parse different log formats
        if "ERROR" in message: level = "ERROR"
        elif "WARNING" in message: level = "WARNING"
        elif "DEBUG" in message: level = "DEBUG"
        
        # Determine source based on message content
        if "Cognitive Engine" in message: 
            source = "cognitive_core"
        elif "BACKGROUND TASK" in message: 
            source = "cognitive_worker"
        elif "API COGNITIVE" in message: 
            source = "cognitive_api"
        elif "HTTP" in message and ("GET" in message or "POST" in message):
            source = "http_request"
            
        return {
            "timestamp": timestamp, 
            "level": level, 
            "message": message, 
            "source": source,
            "server_port": server_port
        }

# --- Configure Logging for Cognitive Engine ---
# Configure standard logging to use our interceptor
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(CognitiveLogInterceptor())],
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# --- End of Logging Setup ---

app = FastAPI(title="Cognitive Engine Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def capture_cognitive_requests(request: Request, call_next):
    """Capture HTTP requests for cognitive engine with enhanced logging"""
    start_time = time.time()
    
    # Log incoming request
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": f'INFO: {request.client.host}:{request.client.port} - "{request.method} {request.url.path} HTTP/{request.scope["http_version"]}"',
        "source": "http_request",
        "server_port": "8002"
    }
    
    cognitive_log_buffer.append(log_entry)
    if len(cognitive_log_buffer) > 200:
        cognitive_log_buffer.pop(0)
    
    # Also add to queue for real-time streaming
    try:
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(cognitive_log_queue.put(log_entry), loop)
    except RuntimeError:
        pass
    
    logger.info(f"Cognitive Engine: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": f'INFO: {request.client.host}:{request.client.port} - "{request.method} {request.url.path} HTTP/{request.scope["http_version"]}" {response.status_code} OK',
        "source": "http_request",
        "server_port": "8002"
    }
    
    cognitive_log_buffer.append(log_entry)
    if len(cognitive_log_buffer) > 200:
        cognitive_log_buffer.pop(0)
    
    # Also add to queue for real-time streaming
    try:
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(cognitive_log_queue.put(log_entry), loop)
    except RuntimeError:
        pass
    
    return response

@app.get("/")
async def root():
    """Cognitive Engine root endpoint"""
    logger.info("API COGNITIVE: Root endpoint accessed")
    return {"message": "Cognitive Engine Server", "port": "8002", "status": "active"}

@app.get("/health")
async def health_check():
    """Health check for cognitive engine"""
    logger.info("API COGNITIVE: Health check requested")
    return {"status": "healthy", "server": "cognitive_engine", "port": "8002"}

@app.get("/api/cognitive/status")
async def cognitive_status():
    """Cognitive engine status"""
    logger.info("API COGNITIVE: Status check requested")
    return {
        "status": "active",
        "model": "gemini-1.5-pro",
        "server": "8002",
        "last_update": datetime.utcnow().isoformat()
    }

@app.get("/api/cognitive/process")
async def cognitive_process():
    """Simulate cognitive processing"""
    logger.info("API COGNITIVE: Processing request initiated")
    return {
        "process_id": "cog_123",
        "status": "processing",
        "server": "8002",
        "timestamp": datetime.utcnow().isoformat()
    }

# --- Enhanced Streaming Endpoints ---
@app.get("/api/events/stream")
async def stream_events():
    """Streams live server events using Server-Sent Events (SSE)."""
    async def event_generator():
        # Send the last 50 buffered logs immediately on connection
        for log_entry in cognitive_log_buffer[-50:]:
            yield f"data: {json.dumps(log_entry)}\n\n"
        
        # Now, wait for new logs from the queue
        while True:
            try:
                log_entry = await asyncio.wait_for(cognitive_log_queue.get(), timeout=25)
                yield f"data: {json.dumps(log_entry)}\n\n"
            except asyncio.TimeoutError:
                # Send a keepalive message to prevent the connection from closing
                yield f"data: {json.dumps({'type': 'keepalive', 'server': '8002'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@app.get("/api/cognitive/logs")
async def get_cognitive_logs():
    """Get cognitive engine logs with enhanced structure"""
    try:
        # Organize logs by source
        http_logs = []
        cognitive_logs = []
        system_logs = []
        
        for log_entry in cognitive_log_buffer[-100:]:
            source = log_entry.get("source", "system")
            if source == "http_request":
                http_logs.append(log_entry)
            elif "cognitive" in source:
                cognitive_logs.append(log_entry)
            else:
                system_logs.append(log_entry)
        
        return {
            "overview": {
                "total_logs": len(cognitive_log_buffer),
                "recent_logs": len(http_logs) + len(cognitive_logs) + len(system_logs),
                "http_count": len(http_logs),
                "cognitive_count": len(cognitive_logs),
                "system_count": len(system_logs),
                "last_update": datetime.utcnow().isoformat()
            },
            "logs": {
                "http_requests": {
                    "status": "active",
                    "logs": http_logs[-50:],
                    "log_count": len(http_logs),
                    "error_count": len([l for l in http_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in http_logs if l.get("level") == "WARNING"]),
                    "last_event": max([l["timestamp"] for l in http_logs], default=None)
                },
                "cognitive_engine": {
                    "status": "active",
                    "logs": cognitive_logs[-50:],
                    "log_count": len(cognitive_logs),
                    "error_count": len([l for l in cognitive_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in cognitive_logs if l.get("level") == "WARNING"]),
                    "last_event": max([l["timestamp"] for l in cognitive_logs], default=None)
                },
                "system": {
                    "logs": system_logs[-50:],
                    "log_count": len(system_logs),
                    "error_count": len([l for l in system_logs if l.get("level") == "ERROR"]),
                    "warning_count": len([l for l in system_logs if l.get("level") == "WARNING"])
                }
            },
            "server": "8002"
        }
    except Exception as e:
        logger.error(f"Error getting cognitive logs: {e}")
        return {"error": str(e), "server": "8002"}

@app.get("/api/cognitive/stream")
async def stream_cognitive_events():
    """Stream cognitive engine events - alias for main stream"""
    return await stream_events()

@app.get("/api/logs/live")
async def get_live_logs():
    """Get recent logs for the live log streaming container"""
    return await get_cognitive_logs()

@app.get("/api/logs/history")
async def get_log_history(limit: int = 100):
    """Get recent log history"""
    return {
        "logs": cognitive_log_buffer[-limit:],
        "total_logs": len(cognitive_log_buffer),
        "server_time": datetime.utcnow().isoformat(),
        "server": "8002"
    }

@app.get("/api/logs/clear")
async def clear_logs():
    """Clear the log buffer"""
    global cognitive_log_buffer
    cognitive_log_buffer.clear()
    logger.info("API COGNITIVE: Log buffer cleared")
    return {"message": "Log buffer cleared", "timestamp": datetime.utcnow().isoformat(), "server": "8002"}

# --- Background Tasks ---
async def generate_cognitive_activity():
    """Background task to generate cognitive engine activity logs"""
    while True:
        try:
            await asyncio.sleep(30)  # Generate activity every 30 seconds
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": f"BACKGROUND TASK: Cognitive engine processing cycle completed",
                "source": "cognitive_worker",
                "server_port": "8002"
            }
            cognitive_log_buffer.append(log_entry)
            if len(cognitive_log_buffer) > 200:
                cognitive_log_buffer.pop(0)
            
            # Add to queue for real-time streaming
            try:
                await cognitive_log_queue.put(log_entry)
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"Error in cognitive activity generation: {e}")

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize the cognitive engine on startup"""
    logger.info("🚀 Cognitive Engine Server starting up on port 8002...")
    logger.info("📡 Real-time log streaming initialized for cognitive engine")
    
    # Start the background task to generate cognitive activity
    asyncio.create_task(generate_cognitive_activity())
    logger.info("🔗 SSE endpoint available at /api/events/stream")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on cognitive engine shutdown"""
    logger.info("🛑 Cognitive Engine Server shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 