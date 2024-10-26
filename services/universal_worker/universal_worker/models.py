from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    WEB_ARTICLE = "web_article"
    PUBLICATION = "publication"
    YOUTUBE_VIDEO = "youtube_video"
    BOOKMARK = "bookmark"
    UNKNOWN = "unknown"


class SubmissionContent(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        json_schema_extra={"example": "https://example.com"},
    )


# this class will be used by OpenAI to extract structure content
class ClassifiedContent(BaseModel):
    content_type: ContentType
    url: Optional[str] = None


class TranscribedContent(BaseModel):
    url: str
    raw_content: str
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_id: Optional[str] = None


class Metadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    canonical_url: Optional[str] = None
    keywords: Optional[str] = None


class Content(BaseModel):
    url: str
    content_id: str
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    canonical_url: Optional[str] = None
    keywords: Optional[list] = None
    raw_content: Optional[str] = None
    summary: Optional[str] = None
