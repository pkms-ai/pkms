from pydantic import BaseModel, HttpUrl
from enum import Enum
from typing import Optional

class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"

class ContentSubmission(BaseModel):
    content: str
    user_id: str
    content_type: Optional[ContentType] = None
    url: Optional[HttpUrl] = None
