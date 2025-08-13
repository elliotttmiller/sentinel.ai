from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.agents.executable_agent import PlannerAgent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


# Example agent action
def greet_user_handler(name: str):
    return f"Hello, {name}! Welcome to CopilotKit."


# Import and include CopilotKit API router for info endpoint
from src.api.copilotkit import router as copilotkit_router
app.include_router(copilotkit_router)

# Import and include GraphQL API router
from src.api.graphql import graphql_app
app.include_router(graphql_app, prefix="/api/graphql")

# WebSocket endpoint (for /ws)
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

import json
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send a valid JSON object
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": "Agent status: running"
            }))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

# Dashboard endpoint (minimal example)
@app.get("/api/dashboard")
async def dashboard():
    import datetime
    return {
        "missions": 42,
        "agents": 7,
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)