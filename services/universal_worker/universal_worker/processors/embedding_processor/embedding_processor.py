import logging
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import (
    Content,
    ContentStatus,
    NotificationMessage,
    NotificationType,
)
from workflow_base import BaseProcessor
from universal_worker.utils.notifier import notify

from .embedder import embedding_content

logger = logging.getLogger(__name__)


class EmbeddingProcessor(BaseProcessor):
    """Processor class for handling crawling content."""

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
        url = content.get("url")
        logger.info(f"Starting content processing: {url}")
        try:
            input_content = Content.model_validate(content)
            await embedding_content(input_content)
            input_content.status = ContentStatus.EMBEDDED

            logger.info("Content embeddings completely.")

            await notify(
                NotificationMessage(
                    url=input_content.url,
                    status=input_content.status,
                    notification_type=NotificationType.INFO,
                    source=input_content.source,
                    message="Content has been processed successfully.",
                )
            )

            return "", input_content.model_dump()

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
