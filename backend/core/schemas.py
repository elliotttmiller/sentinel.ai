from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.mission_planner import ExecutionPlan

class MissionSchema(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    steps: Optional[List[dict]] = None
    plan: Optional[dict] = None
    result: Optional[dict] = None

    class Config:
        from_attributes = True

class AgentSchema(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    status: str
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    last_active: Optional[str] = None
    missions_completed: Optional[int] = None
    
    class Config:
        from_attributes = True

# --- API Request/Response Models ---

class MissionRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    description: Optional[str] = None

class MissionDispatchResponse(BaseModel):
    message: str
    mission_id: str
    plan: ExecutionPlan
    execution_result: Optional[dict] = None

class AgentExecutionRequest(BaseModel):
    agent_type: str
    prompt: str
    mission_id: Optional[str] = None

class AgentExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = {} 