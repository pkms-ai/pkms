from pydantic import BaseModel
from enum import Enum
from typing import Optional


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


class ContentClassification(BaseModel):
    content_type: ContentType
    url: Optional[str] = None


class ContentSubmission(BaseModel):
    content: str
