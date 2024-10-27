from typing import Optional
from pydantic import BaseModel


class TelegramSource(BaseModel):
    message_id: str
    chat_id: str


class ContentSource(BaseModel):
    telegram: Optional[TelegramSource] = None


class ContentSubmission(BaseModel):
    content: str
    source: Optional[ContentSource] = None
