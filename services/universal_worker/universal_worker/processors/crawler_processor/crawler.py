import logging
from typing import Tuple

import httpx

from universal_worker.config import settings
from universal_worker.exceptions import ContentProcessingError
from universal_worker.models import CrawlResponse, Metadata

logger = logging.getLogger(__name__)


async def crawl_content(url: str) -> Tuple[str, Metadata]:
    logger.info(f"Starting content crawling: {url}")

    timeout = httpx.Timeout(
        connect=10.0,  # Time to establish a connection
        read=60.0,  # Time to wait for a response
        write=10.0,  # Time to write request data
        pool=60.0,  # Maximum time to wait for a connection from the pool
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                f"{settings.CRAWL4AI_URL}/crawl", json={"url": url}
            )

            # Handle error responses with more detail
            if response.status_code >= 400:
                error_detail = "Unknown error"
                try:
                    error_body = response.json()
                    error_detail = error_body.get("detail", str(error_body))
                except Exception:
                    error_detail = response.text or str(response.status_code)

                logger.error(
                    f"Crawl service error: {error_detail} (Status: {response.status_code})"
                )
                raise ContentProcessingError(
                    f"Crawl service failed: {error_detail} (Status: {response.status_code})"
                )

            crawl_response = CrawlResponse.model_validate(response.json())

        except httpx.RequestError as e:
            # Handle network/connection errors
            logger.error(f"Network error while crawling content: {str(e)}")
            raise ContentProcessingError(
                f"Network error while crawling content: {str(e)}"
            )

        except ValueError as e:
            # Handle JSON parsing or validation errors
            logger.error(f"Invalid response format: {str(e)}")
            raise ContentProcessingError(
                f"Invalid response format from crawl service: {str(e)}"
            )

        return crawl_response.content, crawl_response.metadata
