import logging
from typing import Dict, Any, Tuple
from pydantic import ValidationError
import httpx
import json

from .models import ClassifiedContent, ContentType
from .config import settings

logger = logging.getLogger(__name__)


class ContentProcessingError(Exception):
    """Custom exception for content processing errors."""

    pass


class ContentAlreadyExistsError(Exception):
    """Custom exception for content that already exists in the database."""
    pass


async def check_url_exists(url: str) -> bool:
    """
    Check if the URL exists by calling the db-service API.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.DB_SERVICE_URL}/check_url", params={"url": url})
            response.raise_for_status()
            return response.json().get("exists", False)
        except httpx.HTTPError as e:
            logger.error(f"Error checking URL existence: {e}")
            raise ContentProcessingError(f"Error checking URL existence: {str(e)}")


async def process_text(content: ClassifiedContent):
    # Implement text processing logic here
    return f"Processed text: {content}"


async def process_image(content: ClassifiedContent):
    # Implement image processing logic here
    return f"Processed image: {content}"


async def process_video(content: ClassifiedContent):
    # Implement video processing logic here
    return f"Processed video: {content}"


async def process_web_article(content: ClassifiedContent) -> Tuple[str, Dict[str, Any]]:
    return settings.CRAWL_QUEUE, content.model_dump()


async def process_publication(content: ClassifiedContent) -> Tuple[str, Dict[str, Any]]:
    return settings.CRAWL_QUEUE, content.model_dump()


async def process_youtube_video(content: ClassifiedContent) -> Tuple[str, Dict[str, Any]]:
    return settings.TRANSCRIBE_QUEUE, content.model_dump()


async def process_bookmark(content: ClassifiedContent) -> Tuple[str, Dict[str, Any]]:
    return settings.CRAWL_QUEUE, content.model_dump()


content_processors = {
    ContentType.WEB_ARTICLE: process_web_article,
    ContentType.PUBLICATION: process_publication,
    ContentType.YOUTUBE_VIDEO: process_youtube_video,
    ContentType.BOOKMARK: process_bookmark,
}


async def process_content(content: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    logger.info(f"Starting content processing: {content}")
    try:
        classified_content = ClassifiedContent.model_validate(content)
        logger.info(f"Processing content: {classified_content}")
        if not classified_content.url:
            raise ContentProcessingError("No content or URL provided")
        
        # Check if the URL already exists in the database
        if await check_url_exists(classified_content.url):
            raise ContentAlreadyExistsError(f"Content with URL {classified_content.url} already exists in the database")
        
        logger.debug(f"Content validated as {classified_content.content_type}")

        processor = content_processors.get(classified_content.content_type)
        if processor is None:
            raise ContentProcessingError(
                f"Unknown content type: {classified_content.content_type}"
            )

        logger.debug(f"Processing content with {processor.__name__}")
        queue_name, processed_content = await processor(classified_content)
        logger.info(f"Content processing completed. Queued for: {queue_name}")
        return queue_name, processed_content
    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")
    except ContentAlreadyExistsError:
        raise
    except ContentProcessingError:
        raise
    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
