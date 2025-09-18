from pydantic import BaseModel
from typing import Optional, List


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str
    message_id: str


class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: str
    last_activity: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    timestamp: str
