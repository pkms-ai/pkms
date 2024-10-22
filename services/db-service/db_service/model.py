from typing import Optional
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


# Pydantic model for updating content
class ContentUpdateModel(BaseModel):
    title: Optional[str] = None
    content_type: Optional[ContentType] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Optional[dict] = None


# Define the Pydantic model
class ContentModel(BaseModel):
    url: str
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None
    metadata: Optional[dict] = None
    content_id: Optional[UUID] = None
