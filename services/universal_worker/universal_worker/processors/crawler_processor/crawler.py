import logging
from typing import Tuple

import httpx

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import CrawlResponse, Metadata

logger = logging.getLogger(__name__)


async def crawl_content(url: str) -> Tuple[str, Metadata]:
    logger.info(f"Starting content crawling: {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.CRAWL4AI_URL}/crawl", json={"url": url}
            )
            response.raise_for_status()

            crawl_response = CrawlResponse.model_validate(response.json())

        except httpx.HTTPError as e:
            logger.error(f"Error checking URL existence: {e}")
            raise ContentProcessingError(f"Error checking URL existence: {str(e)}")

        return crawl_response.content, crawl_response.metadata
