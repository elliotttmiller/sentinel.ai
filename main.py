from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit.sdk import CopilotKitRemoteEndpoint
from agent import update_steps
import json

app = FastAPI()
sdk = CopilotKitRemoteEndpoint(app=app)  # Or your CopilotKit app instance

add_fastapi_endpoint(app, sdk, prefix="api")

# Optionally, add CORS middleware for frontend-backend communication
try:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except ImportError:
    pass

# Streaming endpoint for agent state updates (SSE)
@app.get("/stream-agent-state")
async def stream_agent_state(request: Request):
    steps = request.query_params.get("steps", "step1,step2,step3").split(",")
    async def event_generator():
        async for event in update_steps(steps):
            data = json.dumps(event.snapshot)
            yield f"data: {data}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
