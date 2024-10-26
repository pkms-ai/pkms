import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from aio_pika.abc import AbstractIncomingMessage

# from .models import Content
from pydantic import ValidationError

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import Content, ContentType, ContentStatus
from universal_worker.processors import Processor
from universal_worker.utils.db import check_url_exists, insert_to_db
from universal_worker.utils.url import clean_url

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
        try:
            input_content = Content.model_validate(content)
            url = input_content.url
            logger.info(f"Starting content processing: {url}")

            # only clean the url if it is not a youtube video
            if input_content.content_type != ContentType.YOUTUBE_VIDEO:
                if input_content.canonical_url:
                    url = input_content.canonical_url
                else:
                    url = clean_url(url)

            # if the url is still empty, use the original url
            if not url:
                url = input_content.url

            # check if the URL already exists in the database
            if await check_url_exists(url):
                logger.info(f"URL already exists in the database: {url}")
                raise ContentProcessingError("URL already exists in the database")

            input_content.summary = await summarize_content(input_content)
            input_content.status = ContentStatus.SUMMARIZED

            await insert_to_db(input_content)

            return settings.EMBEDDING_QUEUE, input_content.model_dump()

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
