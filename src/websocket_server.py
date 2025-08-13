from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Example: send a status update every 2 seconds
            await websocket.send_text("Agent status: running")
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
