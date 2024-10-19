from enum import Enum

from pydantic import BaseModel


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


class ClassifiedContent(BaseModel):
    content_id: str
    content_type: ContentType
    url: str
