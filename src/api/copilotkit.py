
"""
CopilotKit FastAPI integration for self-hosted Gemini LLM backend.
Handles chat requests from CopilotKit UI and forwards them to Google Gemini API using your GOOGLE_API_KEY.
"""

import dotenv
dotenv.load_dotenv()
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import os
import httpx
from copilotkit import CopilotKitRemoteEndpoint, Action

router = APIRouter()

# Info endpoint for CopilotKit Cloud
@router.get("/api/copilotkit/info")
async def copilotkit_info():
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "info": "SentinelAI CopilotKit Gemini integration active."},
        headers={"Access-Control-Allow-Origin": "*"}
    )


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"

@router.api_route("/api/copilotkit", methods=["POST"])
async def copilotkit_gemini(request: Request):
    """
    Handles chat requests from CopilotKit UI and forwards them to Gemini LLM using google-generativeai.
    """
    from src.utils.debug_logger import logger
    if not GOOGLE_API_KEY:
        logger.error("Google Gemini API key not configured.")
        raise HTTPException(status_code=500, detail="Google Gemini API key not configured.")


    try:
        data = await request.json()
        messages = data.get("messages") or data.get("inputMessages")
        if not messages:
            logger.error("No messages provided in request body.")
            raise HTTPException(status_code=400, detail="No messages provided.")
        prompt = "\n".join([msg.get("text", "") for msg in messages if msg.get("text")])

        # Streaming support
        if data.get("stream", False):
            async def event_generator():
                payload = {
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
                }
                headers = {"Content-Type": "application/json"}
                params = {"key": GOOGLE_API_KEY}
                async with httpx.AsyncClient() as client:
                    async with client.stream("POST", GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=60) as resp:
                        if resp.status_code != 200:
                            logger.error(f"Gemini API error: {resp.status_code} {resp.text}")
                            yield f"data: [ERROR] {resp.text}\n\n"
                            return
                        async for chunk in resp.aiter_text():
                            yield f"data: {chunk}\n\n"
            return StreamingResponse(event_generator(), media_type="text/event-stream")

        # Standard response
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
                logger.error(f"Gemini API error: {resp.status_code} {resp.text}")
                return JSONResponse(status_code=resp.status_code, content={"error": resp.text}, headers={"Access-Control-Allow-Origin": "*"})
            gemini_data = resp.json()
        candidates = gemini_data.get("candidates", [])
        if not candidates:
            logger.error("No candidates returned from Gemini API.")
            return JSONResponse(status_code=200, content={"outputMessages": [{"text": "[No response from Gemini]"}]}, headers={"Access-Control-Allow-Origin": "*"})
        gemini_text = candidates[0]["content"]["parts"][0]["text"]
        output_message = {
            "text": gemini_text,
            "isResultMessage": True,
            "isAgentStateMessage": False
        }
        return JSONResponse(status_code=200, content={"outputMessages": [output_message]}, headers={"Access-Control-Allow-Origin": "*"})
    except HTTPException as he:
        import traceback
        logger.error(f"HTTPException in CopilotKit handler: {he}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=he.status_code, content={"error": str(he.detail)}, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        import traceback
        logger.error(f"Unhandled error in CopilotKit handler: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)}, headers={"Access-Control-Allow-Origin": "*"})

# --- Agent Actions Example ---
# You can add a separate endpoint for agent actions, or integrate with CopilotKitRemoteEndpoint
def greet_user(name):
    return f"Hello, {name}!"

agent_sdk = CopilotKitRemoteEndpoint(
    actions=[
        Action(
            name="greet_user",
            handler=greet_user,
            description="Greet the user",
            parameters=[{"name": "name", "type": "string", "description": "The name of the user"}]
        )
    ]
)

# In your main.py, include this router:
# from src.api.copilotkit import router as copilotkit_router
# app.include_router(copilotkit_router)
