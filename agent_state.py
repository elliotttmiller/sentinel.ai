from pydantic import BaseModel

class AgentState(BaseModel):
    observed_steps: list[str] = []
