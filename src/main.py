    # ...existing code...

    # ...existing code...

import dotenv
dotenv.load_dotenv()
import asyncio
import json
import time
import uuid
import sys
from datetime import datetime


from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
import os
import traceback
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler

app = FastAPI()

# --- Agentic Generative UI Endpoint ---
@app.get("/api/agentic-generative-ui")
async def agentic_generative_ui():
    # Dummy agentic generative UI data
    return {
        "status": "ok",
        "message": "Agentic Generative UI endpoint is active.",
        "timestamp": datetime.utcnow().isoformat()
    }

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'cognitive_engine.log')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.session_id = getattr(record, 'session_id', 'N/A')
        record.user = getattr(record, 'user', 'system')
        return True


# --- Dashboard Endpoint ---
@app.get("/api/dashboard")
async def dashboard():
    # Dummy dashboard data
    return {
        "system_status": "ok",
        "active_users": 5,
        "missions": 2,
        "timestamp": datetime.utcnow().isoformat()
    }
    
# --- Missions Endpoint ---
@app.get("/api/missions")
async def missions():
    # Dummy missions data
    return {
        "missions": [
            {"id": "mission_1", "name": "Test Mission 1", "status": "running"},
            {"id": "mission_2", "name": "Test Mission 2", "status": "completed"}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(name)s] [session:%(session_id)s] [user:%(user)s] %(message)s'
)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

logger = logging.getLogger("sentinel")
    # Enable CORS for frontend communication



## Removed /api/ws alias. Use only /ws for WebSocket connections.


def log_exception(exc: Exception, context: str = ""):
    logger.error(f"Exception in {context}: {exc}\n{traceback.format_exc()}")


# --- Health Endpoint with Logging ---
@app.get("/health")
async def health():
    logger.debug("Health check endpoint called.")
    return {"status": "ok"}


# --- Status Endpoint with Logging ---
@app.get("/status")
async def status():
    logger.info("Status endpoint called.")
    return {"status": "ok", "message": "SentinelAI backend is running."}



# WebSocket Connection Manager (minimal fallback)
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}", extra={"user": str(websocket.client), "session_id": getattr(websocket, 'session_id', 'N/A')})

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}", extra={"user": str(websocket.client), "session_id": getattr(websocket, 'session_id', 'N/A')})

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Broadcast failed for connection: {e}", extra={"user": str(connection.client)})
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

# Dummy db_manager and User for minimal working system
class User:
    def __init__(self, id="user_1", email="user@example.com", organization_id="org_1"):
        self.id = id
        self.email = email
        self.organization_id = organization_id

def get_current_user():
    return User()

class DummyDBManager:
    def get_mission(self, mission_id):
        class Mission:
            def __init__(self):
                self.organization_id = "org_1"
                self.status = "running"
                self.result = None
            def as_dict(self):
                return {"id": mission_id, "organization_id": self.organization_id, "status": self.status, "result": self.result}
        return Mission()
    def get_mission_updates(self, mission_id):
        return []
    def update_mission_status(self, mission_id, status):
        pass
    def add_mission_update(self, mission_id, phase, message, data):
        pass
    def get_system_stats(self):
        return {"missions": 1, "users": 1}
    def get_performance_data_for_analytics(self, org_id):
        return []
    def get_pending_proposals(self):
        return []
    def update_proposal_status(self, proposal_id, status):
        class Proposal:
            def as_dict(self):
                return {"id": proposal_id, "status": status}
        return Proposal()

db_manager = DummyDBManager()
websocket_manager = ConnectionManager()


# WebSocket endpoint for real-time updates with advanced logging
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        logger.info("WebSocket connection established.", extra={"user": str(websocket.client)})
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to Sentinel mission updates",
            "timestamp": datetime.utcnow().isoformat()
        })
        while True:
            try:
                data = await websocket.receive_json()
                logger.debug(f"WebSocket received data: {data}", extra={"user": str(websocket.client)})
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected by client.", extra={"user": str(websocket.client)})
                break
            except Exception as e:
                log_exception(e, context="WebSocket message handling")
                break
    finally:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket cleanup complete.", extra={"user": str(websocket.client)})



try:
    from api.copilotkit import router as copilotkit_router
except ImportError:
    from src.api.copilotkit import router as copilotkit_router
app.include_router(copilotkit_router)
logger.info("CopilotKit router registered successfully.")

# Register CopilotKitRemoteEndpoint FastAPI app for remote agent/action support
try:
    from api.copilotkit_remote import app as copilotkit_remote_app
except ImportError:
    from src.api.copilotkit_remote import app as copilotkit_remote_app
app.mount("/copilotkit-remote", copilotkit_remote_app)
logger.info("CopilotKitRemoteEndpoint app mounted at /copilotkit-remote.")

# --- CopilotKit React Frontend Integration Example ---
# In your frontend, initialize CopilotKit with your public API key:
# <CopilotKit publicApiKey="ck_pub_011541242c359e759e3256628c64144b">
#   {/* Your App Components */}
# </CopilotKit>
# See copilotkit-references.txt for more integration details.


# --- Future-proof: Add a global exception handler for uncaught errors ---
from fastapi.requests import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_exception(exc, context=f"Global handler: {request.url}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting SentinelAI backend with advanced logging...")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)