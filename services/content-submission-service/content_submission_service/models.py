from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ContentSubmission(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        json_schema_extra={"example": "https://example.com"},
    )
    source: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata dictionary for the content source",
        json_schema_extra={
            "example": {
                "telegram": {
                    "messagge_id": "123456",
                    "chat_id": "123456",
                }
            }
        },
    )
