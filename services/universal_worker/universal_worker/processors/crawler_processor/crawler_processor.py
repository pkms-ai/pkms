import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content
from universal_worker.processors import Processor

from .cleaner import clean_markdown

# from .cleaner import clean_markdown
from .crawler import crawl_content

logger = logging.getLogger(__name__)


class CrawlerProcessor(Processor):
    """Processor class for handling crawling content."""

    @property
    def input_queue(self) -> str:
        return settings.CRAWL_QUEUE

    @property
    def exchange_queue(self) -> str:
        return "crawler_exchange"

    @property
    def output_queues(self) -> List[str]:
        return [settings.SUMMARY_QUEUE]

    @property
    def error_queue(self) -> str:
        return settings.ERROR_QUEUE

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
        logger.info(f"Starting content processing: {content}")
        try:
            validated_content = Content.model_validate(content)
            markdown, metadata = await crawl_content(validated_content.url)
            cleaned_markdown = await clean_markdown(markdown)

            validated_content.raw_content = cleaned_markdown
            validated_content.title = metadata.title
            validated_content.description = metadata.description
            validated_content.image_url = metadata.image_url
            validated_content.canonical_url = metadata.canonical_url

            logger.info("Content processed successfully.")
            return self.output_queues[0], validated_content.model_dump()

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