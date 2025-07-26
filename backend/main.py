from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "Sentinel Orchestrator Backend"}

@app.post("/plan")
def create_plan(user_prompt: str):
    # Placeholder for planning logic
    return {"plan": f"Plan for: {user_prompt}"} 