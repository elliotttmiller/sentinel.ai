# File: sentinel/engine/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import os
from datetime import datetime

app = FastAPI(title="Sentinel Desktop Engine")

class ExecutionPlan(BaseModel):
    """A simple model to receive the plan from the backend."""
    mission_id: str
    steps: list
    metadata: Dict[str, Any]

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Sentinel Engine", "timestamp": datetime.now().isoformat()}

@app.post("/execute_mission")
def execute_mission(plan: ExecutionPlan):
    """Receives an execution plan and prints it to the console."""
    print("--- MISSION PLAN RECEIVED ---")
    print(f"Mission ID: {plan.mission_id}")
    print(f"Number of Steps: {len(plan.steps)}")
    print(f"Metadata: {plan.metadata}")
    print("Steps:")
    for i, step in enumerate(plan.steps, 1):
        print(f"  {i}. {step}")
    print("--- END OF PLAN ---")
    
    # --- ACTION LOGIC ---
    try:
        # Create a file named after the mission ID to prove it worked
        file_name = f"{plan.mission_id}.txt"
        with open(file_name, "w") as f:
            f.write("Mission plan executed successfully!\n\n")
            f.write(f"Mission ID: {plan.mission_id}\n")
            f.write(f"Number of steps: {len(plan.steps)}\n")
            f.write(f"Executed at: {datetime.now().isoformat()}\n\n")
            f.write("Steps:\n")
            for i, step in enumerate(plan.steps, 1):
                f.write(f"{i}. {step}\n")
        print(f"SUCCESS: Created proof-of-execution file: {file_name}")
        return {"status": "success", "message": f"Plan executed. File '{file_name}' created."}
    except Exception as e:
        print(f"ERROR: Failed to perform action. Error: {e}")
        return {"status": "error", "message": f"Failed to execute plan on engine: {str(e)}"}
    # --------------------

@app.get("/")
def root():
    return {"message": "Sentinel Desktop Engine is running", "endpoints": ["/health", "/execute_mission"]} 