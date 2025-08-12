"""
Advanced FastAPI integration for CopilotKit endpoint.
Handles chat, actions, and agent orchestration for CopilotKit clients.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import httpx

router = APIRouter()

COPILOT_API_KEY = os.getenv("COPILOT_API_KEY")
COPILOTKIT_CLOUD_URL = "https://api.copilotkit.ai/v1"  # CopilotKit Cloud base URL (do not change unless instructed)

@router.api_route("/api/copilotkit", methods=["POST", "GET"])
async def copilotkit_proxy(request: Request):
    """
    Proxy CopilotKit requests to the CopilotKit cloud API, including authentication.
    Supports both GET (status/ping) and POST (chat, actions, etc) requests.
    """
    if not COPILOT_API_KEY:
        raise HTTPException(status_code=500, detail="CopilotKit API key not configured.")

    # Forward the request to CopilotKit cloud
    async with httpx.AsyncClient() as client:
        if request.method == "GET":
            # Health check or status
            copilotkit_url = f"{COPILOTKIT_CLOUD_URL}/status"
            headers = {"Authorization": f"Bearer {COPILOT_API_KEY}"}
            resp = await client.get(copilotkit_url, headers=headers)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        elif request.method == "POST":
            # Proxy chat/action requests
            body = await request.body()
            copilotkit_url = f"{COPILOTKIT_CLOUD_URL}/chat"
            headers = {
                "Authorization": f"Bearer {COPILOT_API_KEY}",
                "Content-Type": request.headers.get("content-type", "application/json"),
            }
            resp = await client.post(copilotkit_url, headers=headers, content=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
        else:
            raise HTTPException(status_code=405, detail="Method not allowed.")

# In your main.py, include this router:
# from src.api.copilotkit import router as copilotkit_router
# app.include_router(copilotkit_router)
