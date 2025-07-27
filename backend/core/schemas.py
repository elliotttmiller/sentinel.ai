from pydantic import BaseModel
from typing import List, Optional

class MissionRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: str

class MissionDispatchResponse(BaseModel):
    message: str
    mission_id: str
    plan: dict
    execution_result: dict = None

class MissionSchema(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    steps: Optional[List[dict]] = None
    plan: Optional[dict] = None
    result: Optional[dict] = None

    class Config:
        from_attributes = True

class AgentSchema(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    status: str
    last_active: Optional[str] = None
    missions_completed: Optional[int] = None

    class Config:
        from_attributes = True 