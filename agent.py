import asyncio
from pydantic_ai import Agent
from pydantic_ai.ag_ui import StateDeps
from ag_ui.core import StateSnapshotEvent, EventType
from agent_state import AgentState

agent = Agent('gemini:your-model', deps_type=StateDeps[AgentState])
app = agent.to_ag_ui(deps=StateDeps(AgentState()))

@agent.tool_plain
async def update_steps(steps: list[str]) -> StateSnapshotEvent:
    # Simulate long-running task with intermediate updates
    for i, step in enumerate(steps):
        await asyncio.sleep(1)  # Simulate work
        yield StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot={"observed_steps": steps[:i+1]}
        )
    # Final state snapshot
    return StateSnapshotEvent(
        type=EventType.STATE_SNAPSHOT,
        snapshot={"observed_steps": steps}
    )
