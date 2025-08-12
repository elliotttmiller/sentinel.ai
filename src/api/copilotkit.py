
"""
CopilotKit FastAPI integration for self-hosted Gemini LLM backend.
Handles chat requests from CopilotKit UI and forwards them to Google Gemini API using your GOOGLE_API_KEY.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import httpx

router = APIRouter()

# Info endpoint for CopilotKit Cloud
@router.get("/api/copilotkit/info")
async def copilotkit_info():
    return {"status": "ok", "info": "SentinelAI CopilotKit Gemini integration active."}

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

@router.api_route("/api/copilotkit", methods=["POST"])
async def copilotkit_gemini(request: Request):
    """
    Handles chat requests from CopilotKit UI and forwards them to Gemini LLM.
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google Gemini API key not configured.")

    try:
        data = await request.json()
        # CopilotKit sends messages as an array of objects with a 'text' field
        messages = data.get("messages") or data.get("inputMessages")
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided.")
        # Concatenate all user and assistant messages for Gemini prompt
        prompt = "\n".join([msg.get("text", "") for msg in messages if msg.get("text")])

        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        headers = {"Content-Type": "application/json"}
        params = {"key": GOOGLE_API_KEY}
        async with httpx.AsyncClient() as client:
            resp = await client.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=60)
            if resp.status_code != 200:
                return JSONResponse(status_code=resp.status_code, content={"error": resp.text})
            gemini_data = resp.json()
        # Extract Gemini's response
        candidates = gemini_data.get("candidates", [])
        if not candidates:
            return JSONResponse(status_code=200, content={"outputMessages": [{"text": "[No response from Gemini]"}]})
        gemini_text = candidates[0]["content"]["parts"][0]["text"]
        # Return in CopilotKit-compatible format
        return JSONResponse(status_code=200, content={"outputMessages": [{"text": gemini_text}]})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# In your main.py, include this router:
# from src.api.copilotkit import router as copilotkit_router
# app.include_router(copilotkit_router)
