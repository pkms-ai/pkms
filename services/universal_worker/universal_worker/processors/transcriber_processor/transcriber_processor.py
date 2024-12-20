import logging
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

from pydantic import ValidationError

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content, ContentStatus
from workflow_base import BaseProcessor

from .transcriber import transcribe_content

logger = logging.getLogger(__name__)


class TranscriberProcessor(BaseProcessor):
    """Processor class for handling crawling content."""

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
        url = content.get("url")
        logger.info(f"Starting content processing: {url}")
        try:
            input_content = Content.model_validate(content)
            transcribed_content = await transcribe_content(input_content.url)

            input_content.url = transcribed_content.url
            input_content.raw_content = transcribed_content.raw_content
            input_content.content_type = transcribed_content.content_type
            input_content.title = transcribed_content.title
            input_content.description = transcribed_content.description
            input_content.image_url = transcribed_content.image_url
            input_content.status = ContentStatus.TRANSCRIBED

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
        return None
