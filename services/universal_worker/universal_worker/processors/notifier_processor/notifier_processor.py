import logging
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import NotificationMessage
from workflow_base import BaseProcessor

from .notifier import notify

logger = logging.getLogger(__name__)


class NotifierProcessor(BaseProcessor):
    """Processor class for handling crawling content."""

    async def process_content(
        self, content: Dict[str, Any]
    ) -> Tuple[str, Dict[str, str | list[str]]]:
        try:
            notification_message = NotificationMessage.model_validate(content)
            url = notification_message.url
            logger.info(f"Starting content processing: {url}")
            await notify(notification_message)

            logger.info("Content notified completely.")

            return "", notification_message.model_dump()

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
        # async def error_handler(
        #     error: Exception,
        #     content: Optional[Dict[str, Any]],
        #     message: AbstractIncomingMessage,
        # ) -> None:
        #     # notification is an edge service, we don't wnat to throw error to put in queue
        #     # simply output the error to the logs, and forget about the message
        #     logger.info(f"Error processing content: {content} with {error})")
        #     await message.ack()
        #
        # return error_handler
        return None
