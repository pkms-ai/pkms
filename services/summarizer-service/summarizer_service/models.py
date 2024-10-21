from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


class Content(BaseModel):
    content_id: str
    content_type: ContentType
    url: str
    raw_content: str
    summary: Optional[str] = None
