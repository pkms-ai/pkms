import logging
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError
from workflow_base import BaseProcessor

from universal_worker.config import settings
from universal_worker.exceptions import (
    ContentAlreadyExistsError,
    ContentProcessingError,
)
from universal_worker.models import (
    Content,
    ContentType,
    NotificationMessage,
    NotificationType,
    SubmittedContent,
)
from universal_worker.utils.db import check_url_exists
from universal_worker.utils.notifier import notify

from .classifier import classify_content

logger = logging.getLogger(__name__)


async def process_web_article(content: Content) -> Tuple[str, Dict[str, Any]]:
    return settings.CRAWL_QUEUE, content.model_dump()


async def process_publication(content: Content) -> Tuple[str, Dict[str, Any]]:
    return settings.CRAWL_QUEUE, content.model_dump()


async def process_youtube_video(
    content: Content,
) -> Tuple[str, Dict[str, Any]]:
    return settings.TRANSCRIBE_QUEUE, content.model_dump()


async def process_bookmark(content: Content) -> Tuple[str, Dict[str, Any]]:
    return settings.CRAWL_QUEUE, content.model_dump()


content_forwarders = {
    ContentType.WEB_ARTICLE: process_web_article,
    ContentType.PUBLICATION: process_publication,
    ContentType.YOUTUBE_VIDEO: process_youtube_video,
    ContentType.BOOKMARK: process_bookmark,
}


class ClassifierProcessor(BaseProcessor):
    """Processor class for handling crawling content."""

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
        logger.info(f"Starting content processing: {content}")
        try:
            submission_content = SubmittedContent.model_validate(content)
            classified_content = classify_content(submission_content.content)
            classified_content.source = submission_content.source

            logger.info(f"Got contennt from: {classified_content.source}")

            logger.info(f"Classified content from openai: {classified_content}")

            # Check if the URL already exists in the database
            if await check_url_exists(classified_content.url):
                await notify(
                    NotificationMessage(
                        url=classified_content.url,
                        status=classified_content.status,
                        notification_type=NotificationType.INFO,
                        source=classified_content.source,
                        message="URL already exists in the database.",
                    )
                )
                raise ContentAlreadyExistsError(
                    f"Content with URL {classified_content.url} already exists in the database"
                )

            logger.debug(f"Content validated as {classified_content.content_type}")

            processor = content_forwarders.get(classified_content.content_type)
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

    @property
    def handle_error(
        self,
    ) -> Optional[
        Callable[
            [Exception, Optional[Dict[str, Any]], AbstractIncomingMessage],
            Coroutine[Any, Any, None],
        ]
    ]:
        async def error_handler(
            error: Exception,
            content: Optional[Dict[str, Any]],
            message: AbstractIncomingMessage,
        ) -> None:
            if isinstance(error, ContentAlreadyExistsError):
                logger.info(f"Content already exists: {str(error)}")
                await message.ack()
            else:
                # Re-raise the exception to let the default handler manage it
                raise error

        return error_handler
