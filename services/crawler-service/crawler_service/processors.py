import logging
from typing import Any, Dict, Tuple

import httpx
from pydantic import ValidationError

from .config import settings
from .models import Content, ContentType

logger = logging.getLogger(__name__)


async def process_content(content: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    logger.info(f"Starting content processing: {content}")
    try:
        content = Content.model_validate(content)
        content.raw_content = "This is a raw content in markdown format"

        return settings.SUMMARY_QUEUE, content.model_dump()
        
    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")
    
    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
