from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from .config import settings

app = FastAPI(title="Sentinel Orchestrator Backend")

class MissionRequest(BaseModel):
    """The request model for creating a new mission."""
    prompt: str

@app.get("/health", status_code=200, tags=["System"])
def health_check():
    """Endpoint for Railway health checks."""
    return {"status": "ok", "service": "Sentinel Orchestrator Backend"}

@app.post("/missions", tags=["Missions"])
def create_mission(request: MissionRequest):
    """
    This endpoint is the main entrypoint for creating a new mission.
    It receives a raw user prompt, orchestrates the planning,
    and dispatches the final plan to the desktop engine.
    """
    print(f"Received new mission request: {request.prompt}")

    # --- Placeholder Logic (to be replaced with real orchestrator call) ---
    # In the next step, we will replace this with:
    # json_plan = generate_mission_plan(request.prompt)
    
    # For now, let's create a dummy plan to test the connection
    dummy_plan = {
        "mission_name": f"Dummy Mission for '{request.prompt}'",
        "tasks": [
            {"task_id": 1, "agent_role": "Logger", "description": "Log the received prompt."}
        ]
    }
    # ----------------------------------------------------------------------

    # Dispatch the plan to the desktop agent engine
    if settings.DESKTOP_TUNNEL_URL:
        try:
            desktop_url = f"{settings.DESKTOP_TUNNEL_URL}/execute-mission"
            print(f"Dispatching plan to desktop at: {desktop_url}")
            
            # Use a timeout to prevent the server from hanging indefinitely
            response = requests.post(desktop_url, json=dummy_plan, timeout=15)
            
            # Raise an exception if the desktop returns an error (e.g., 4xx or 5xx)
            response.raise_for_status()

            return {
                "message": "Mission plan dispatched successfully to desktop.",
                "dispatched_plan": dummy_plan
            }

        except requests.exceptions.RequestException as e:
            # This handles connection errors, timeouts, etc.
            raise HTTPException(status_code=502, detail=f"Failed to connect to desktop engine: {e}")
        except Exception as e:
            # A general catch-all for other unexpected errors
            raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")
    else:
        # If no desktop tunnel URL is configured, just return the plan
        return {
            "message": "Mission plan created successfully (desktop not configured).",
            "plan": dummy_plan
        } 