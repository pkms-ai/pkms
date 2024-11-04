import logging
from typing import Optional

import httpx
from pydantic import BaseModel

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content, ContentType

logger = logging.getLogger(__name__)


# use to insert new content to database
class InsertContent(BaseModel):
    url: str
    content_type: ContentType
    title: Optional[str] = None
    raw_content: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None
    metadata: Optional[dict] = None
    content_id: Optional[str] = None


async def check_url_exists(url: str) -> bool:
    """
    Check if the URL exists by calling the db-manager API.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.DB_MANAGER_URL}/contents/check_url", json={"url": url}
            )
            response.raise_for_status()
            return response.json().get("exists", False)
        except httpx.HTTPError as e:
            logger.error(f"Error checking URL existence: {e}")
            raise ContentProcessingError(f"Error checking URL existence: {str(e)}")


async def insert_to_db(content: Content) -> dict:
    """
    Inserts content into the database service and returns the response as a dictionary.

    Raises:
        ContentProcessingError: If there is an issue during the HTTP request.
    """
    try:
        # Create the InsertContent object with the converted data
        insert_content = InsertContent(
            url=content.url,
            content_type=content.content_type,
            title=content.title,
            description=content.description,
            raw_content=content.raw_content,
            summary=content.summary,
            image_url=content.image_url,
            content_id=content.content_id if content.content_id else None,
            metadata={
                "canonical_url": content.canonical_url
                if content.canonical_url
                else None,
                "keywords": content.keywords if content.keywords else None,
            },
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.DB_SERVICE_URL}/contents",
                json=insert_content.model_dump(),  # Ensure correct method based on Pydantic version
            )
            response.raise_for_status()  # Raise exception for 4xx and 5xx responses
            return response.json()  # Returning JSON response from DB service
    except httpx.HTTPError as e:
        logger.error(f"Error inserting content to DB: {e}")
        raise ContentProcessingError(f"Error inserting content to DB: {str(e)}")
    except Exception as e:  # General exception handling (optional)
        logger.error(f"Unexpected error inserting content to DB: {e}")
        raise ContentProcessingError(
            f"Unexpected error inserting content to DB: {str(e)}"
        )
