import logging
from typing import Any, Dict, Tuple

import httpx
from pydantic import ValidationError

from .config import settings
from .models import Content, InsertContent
from .exceptions import ContentProcessingError
from .summarizer import summarize_content

logger = logging.getLogger(__name__)


async def check_url_exists(url: str) -> bool:
    """
    Check if the URL exists by calling the db-service API.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.DB_SERVICE_URL}/check_url", params={"url": url}
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
                f"{settings.DB_SERVICE_URL}/content",
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


async def process_content(content: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    url = content.get("url")
    logger.info(f"Starting content processing: {url}")
    try:
        validated_content = Content.model_validate(content)
        validated_content.summary = await summarize_content(validated_content)

        await insert_to_db(validated_content)

        return settings.EMBEDDING_QUEUE, validated_content.model_dump()

    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")

    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
