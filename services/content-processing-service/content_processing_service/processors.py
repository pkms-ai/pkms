import logging
from typing import Dict, Any
from pydantic import ValidationError

from .models import ClassifiedContent, ContentType

logger = logging.getLogger(__name__)


class ContentProcessingError(Exception):
    """Custom exception for content processing errors."""

    pass


async def process_text(content: ClassifiedContent):
    # Implement text processing logic here
    return f"Processed text: {content}"


async def process_image(content: ClassifiedContent):
    # Implement image processing logic here
    return f"Processed image: {content}"


async def process_video(content: ClassifiedContent):
    # Implement video processing logic here
    return f"Processed video: {content}"


async def process_web_article(content: ClassifiedContent):
    # Implement web article processing logic here
    return f"Processed web article: {content}"


async def process_publication(content: ClassifiedContent):
    # Implement publication processing logic here

    return f"Processed publication: {content}"


async def process_youtube_video(content: ClassifiedContent):
    # Implement YouTube video processing logic here
    return f"Processed YouTube video: {content}"


async def process_bookmark(content: ClassifiedContent):
    # Implement bookmark processing logic here
    return f"Processed bookmark: {content}"


content_processors = {
    ContentType.WEB_ARTICLE: process_web_article,
    ContentType.PUBLICATION: process_publication,
    ContentType.YOUTUBE_VIDEO: process_youtube_video,
    ContentType.BOOKMARK: process_bookmark,
}


async def process_content(content: Dict[str, Any]) -> str:
    logger.info(f"Starting content processing: {content}")
    try:
        classified_content = ClassifiedContent.model_validate(content)
        logger.info(f"Processing publication: {content}")
        if not classified_content.url:
            raise ContentProcessingError("No content or URL provided for publication")
        logger.debug(f"Content validated as {classified_content.content_type}")

        processor = content_processors.get(classified_content.content_type)
        if processor is None:
            raise ContentProcessingError(
                f"Unknown content type: {classified_content.content_type}"
            )

        logger.debug(f"Processing content with {processor.__name__}")
        result = await processor(classified_content)
        logger.info(
            f"Content processing completed: {result[:100]}..."
        )  # Log first 100 chars of result
        return result
    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")
    except ContentProcessingError:
        raise
    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
