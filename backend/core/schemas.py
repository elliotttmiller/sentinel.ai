from pydantic import BaseModel
from typing import List, Optional, Dict

class MissionRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: str

class MissionDispatchResponse(BaseModel):
    message: str
    mission_id: str
    plan: dict
    execution_result: dict = None

class Mission(BaseModel):
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
        orm_mode = True

class Agent(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    status: str
    last_active: Optional[str] = None
    missions_completed: Optional[int] = None

class AgentExecutionRequest(BaseModel):
    agent_type: str
    prompt: str
    mission_id: Optional[str] = None

class AgentExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict = {} 