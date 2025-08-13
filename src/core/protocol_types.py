"""CopilotKit Protocol Event and Message Types"""

from enum import Enum
from typing import Optional, TypedDict, List, Any

class RuntimeEventTypes(Enum):
    TEXT_MESSAGE_START = "TextMessageStart"
    TEXT_MESSAGE_CONTENT = "TextMessageContent"
    TEXT_MESSAGE_END = "TextMessageEnd"
    ACTION_EXECUTION_START = "ActionExecutionStart"
    ACTION_EXECUTION_ARGS = "ActionExecutionArgs"
    ACTION_EXECUTION_END = "ActionExecutionEnd"
    ACTION_EXECUTION_RESULT = "ActionExecutionResult"
    AGENT_STATE_MESSAGE = "AgentStateMessage"
    META_EVENT = "MetaEvent"
    RUN_STARTED = "RunStarted"
    RUN_FINISHED = "RunFinished"
    RUN_ERROR = "RunError"
    NODE_STARTED = "NodeStarted"
    NODE_FINISHED = "NodeFinished"

class MessageRole(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"

class Message(TypedDict):
    id: str
    createdAt: str

class TextMessage(Message):
    parentMessageId: Optional[str]
    role: MessageRole
    content: str

class ActionExecutionMessage(Message):
    parentMessageId: Optional[str]
    name: str
    arguments: dict

class ResultMessage(Message):
    actionExecutionId: str
    actionName: str
    result: str

class MetaEvent(TypedDict):
    name: str
    response: Optional[str]
