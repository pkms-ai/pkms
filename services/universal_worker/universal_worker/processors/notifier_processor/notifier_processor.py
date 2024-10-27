import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import NotificationMessage
from universal_worker.processors import Processor

from .notifier import notify

logger = logging.getLogger(__name__)


class NotifierProcessor(Processor):
    """Processor class for handling crawling content."""

    @property
    def input_queue(self) -> str:
        return settings.NOTIFY_QUEUE

    @property
    def exchange_queue(self) -> str:
        return "notify_exchange"

    @property
    def output_queues(self) -> List[str]:
        return []

    @property
    def error_queue(self) -> str:
        return settings.ERROR_QUEUE

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
