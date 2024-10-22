from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


class ClassifiedContent(BaseModel):
    content_type: ContentType
    url: Optional[str] = None


class Content(BaseModel):
    content_id: Optional[str] = None
    content_type: ContentType
    url: Optional[str] = None


class ContentSubmission(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        json_schema_extra={"example": "https://example.com"},
    )
