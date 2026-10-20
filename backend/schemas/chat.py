from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ChatMessage(BaseModel):
    role: Literal["user", "ai"]
    content: str


class ConversationPublic(BaseModel):
    id: str
    title: str
    messages: list[ChatMessage]
    updated_at: datetime
