from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


class Metadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    canonical_url: Optional[str] = None


class Content(BaseModel):
    url: str
    content_id: str
    content_type: ContentType
    raw_content: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    canonical_url: Optional[str] = None
