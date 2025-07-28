from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from loguru import logger
from core.database import get_db
from core.schemas import MissionSchema, MissionDispatchResponse, MissionRequest
from core.mission_planner import ExecutionPlan
import uuid
import asyncio
from config import settings
import requests
from core.mission_planner import MissionPlanner
from core.models import Mission
from datetime import datetime
from core.globals import mission_planner

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.get("/", response_model=List[MissionSchema])
def get_missions(db: Session = Depends(get_db)):
    """Get all missions."""
    try:
        missions = db.query(Mission).all()
        return [MissionSchema.model_validate(m) for m in missions]
    except Exception as e:
        logger.error(f"Failed to fetch missions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database query failed.")

@router.post("/", response_model=MissionDispatchResponse)
async def create_and_dispatch_mission(request: MissionRequest, db: Session = Depends(get_db)):
    """Create and dispatch a new mission."""
    mission_id = f"mission_{uuid.uuid4()}"
    logger.info(f"Received new mission request. Assigning ID: {mission_id}")
    try:
        if not request.prompt or len(request.prompt) < 5:
            raise ValueError("Prompt is too short.")
        plan: ExecutionPlan = await mission_planner.create_mission_plan(
            user_prompt=request.prompt,
            mission_id=mission_id
        )
        logger.info(f"Plan generated for mission {mission_id}.")
        desktop_url = f"{settings.DESKTOP_TUNNEL_URL}/execute_mission"
        response = await asyncio.to_thread(
            requests.post,
            desktop_url,
            json=plan.model_dump(),
            timeout=20
        )
        response.raise_for_status()
        execution_result = None
        result_url = f"{settings.DESKTOP_TUNNEL_URL}/mission_result/{mission_id}"
        for _ in range(10):
            try:
                poll_resp = await asyncio.to_thread(requests.get, result_url, timeout=10)
                if poll_resp.status_code == 200:
                    execution_result = poll_resp.json()
                    if execution_result and execution_result.get("status") != "pending":
                        break
            except Exception as e:
                logger.warning(f"Polling for execution result failed: {e}")
            await asyncio.sleep(2)
        now = datetime.utcnow()
        mission = Mission(
            id=mission_id,
            title=request.title or request.prompt,
            description=request.description or request.prompt,
            status="completed" if execution_result and execution_result.get("status") == "success" else "failed",
            created_at=now,
            updated_at=now,
            completed_at=now if execution_result else None,
            steps=plan.model_dump().get("steps", []),
            plan=plan.model_dump(),
            result=execution_result,
        )
        db.add(mission)
        db.commit()
        return MissionDispatchResponse(
            mission_id=mission_id,
            message="Mission planned, dispatched, and executed.",
            plan=plan,
            execution_result=execution_result
        )
    except ValueError as e:
        logger.error(f"Planning failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except requests.exceptions.RequestException as e:
        logger.error(f"Dispatch to engine failed: {e}")
        raise HTTPException(status_code=502, detail=f"Could not connect to the desktop engine: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.") 