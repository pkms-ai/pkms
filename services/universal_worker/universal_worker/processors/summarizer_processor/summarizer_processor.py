import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content
from universal_worker.processors import Processor
from universal_worker.utils.db import insert_to_db

from .summarizer import summarize_content

logger = logging.getLogger(__name__)


class SummarizerProcessor(Processor):
    """Processor class for handling crawling content."""

    @property
    def input_queue(self) -> str:
        return settings.SUMMARY_QUEUE

    @property
    def exchange_queue(self) -> str:
        return "summarizer_exchange"

    @property
    def output_queues(self) -> List[str]:
        return [settings.EMBEDDING_QUEUE]

    @property
    def error_queue(self) -> str:
        return settings.ERROR_QUEUE

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
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

    @property
    def handle_error(
        self,
    ) -> Optional[
        Callable[
            [Exception, Optional[Dict[str, Any]], AbstractIncomingMessage],
            Coroutine[Any, Any, None],
        ]
    ]:
        return None
