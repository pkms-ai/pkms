import logging
from typing import Any, Dict, Tuple

from pydantic import ValidationError

from .cleaner import clean_markdown
from .config import settings
from .crawler import crawl_content
from .exceptions import ContentProcessingError
from .models import Content

logger = logging.getLogger(__name__)


async def process_content(
    content: Dict[str, Any],
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

        # logger.info(f"Content processed: {validated_content}")

        return settings.SUMMARY_QUEUE, validated_content.model_dump()

    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")

    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
