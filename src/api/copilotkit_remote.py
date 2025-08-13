from copilotkit import CopilotKitRemoteEndpoint, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from fastapi import FastAPI
import os

def greet_user_handler(name):
    return f"Hello, {name}! Welcome to SentinelAI."

sdk = CopilotKitRemoteEndpoint(
    actions=[
        Action(
            name="greet_user",
            handler=greet_user_handler,
            description="Greet the user",
            parameters=[
                {"name": "name", "type": "string", "description": "The name of the user"}
            ]
        )
    ]
)

app = FastAPI()
add_fastapi_endpoint(app, sdk, "/copilotkit-remote")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
