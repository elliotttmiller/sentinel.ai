from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
from loguru import logger
from agent_logic import run_simple_agent_task
from db import SessionLocal, Mission
from datetime import datetime
import platform, psutil

app = FastAPI(title="Sentinel Desktop App (Local-Only)")

class AgentRequest(BaseModel):
    prompt: str

@app.get("/", response_class=FileResponse)
def serve_web_ui():
    return FileResponse("index.html")

@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    db = SessionLocal()
    mission = Mission(prompt=request.prompt, status="pending", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(mission)
    db.commit()
    db.refresh(mission)
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            run_simple_agent_task,
            request.prompt
        )
        mission.status = "completed"
        mission.result = result
        mission.updated_at = datetime.utcnow()
        db.commit()
        return {"result": result}
    except Exception as e:
        mission.status = "failed"
        mission.result = str(e)
        mission.updated_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/missions")
def list_missions():
    db = SessionLocal()
    missions = db.query(Mission).order_by(Mission.created_at.desc()).all()
    db.close()
    return [
        {
            "id": m.id,
            "prompt": m.prompt,
            "status": m.status,
            "result": m.result,
            "created_at": m.created_at,
            "updated_at": m.updated_at
        }
        for m in missions
    ]

@app.get("/system-stats")
def system_stats():
    return {
        "os": platform.system() + " " + platform.release(),
        "python": platform.python_version(),
        "cpu": platform.processor(),
        "ram": f"{round(psutil.virtual_memory().used / (1024**3), 2)}GB / {round(psutil.virtual_memory().total / (1024**3), 2)}GB",
        "llm": "Gemini 1.5 Pro",
        "status": "Online"
    } 