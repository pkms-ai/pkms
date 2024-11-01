import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content, ContentStatus
from workflow_base import BaseProcessor

from .cleaner import clean_markdown

# from .cleaner import clean_markdown
from .crawler import crawl_content

logger = logging.getLogger(__name__)


class CrawlerProcessor(BaseProcessor):
    """Processor class for handling crawling content."""

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
        logger.info(f"Starting content processing: {content}")
        try:
            input_content = Content.model_validate(content)
            markdown, metadata = await crawl_content(input_content.url)
            cleaned_markdown = await clean_markdown(markdown)

            input_content.raw_content = cleaned_markdown
            input_content.title = metadata.title
            input_content.description = metadata.description
            input_content.image_url = metadata.image_url
            input_content.canonical_url = metadata.canonical_url
            input_content.status = ContentStatus.CRAWLED

            logger.info("Content processed successfully.")
            return settings.SUMMARY_QUEUE, input_content.model_dump()

        except ValidationError as e:
            logger.error(f"Content validation failed: {e}")
            raise ContentProcessingError(f"Content validation failed: {str(e)}")

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
            logger.error(f"Error in CrawlerProcessor: {error}")
            logger.error(f"Content: {content}")

        return error_handler
