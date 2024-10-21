import logging
from typing import Any, Dict, Tuple

from pydantic import ValidationError

from .config import settings
from .models import Content
from crawl4ai import AsyncWebCrawler

logger = logging.getLogger(__name__)


class ContentProcessingError(Exception):
    pass


async def crawl_content(url: str) -> str:
    logger.info(f"Starting content crawling: {url}")

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=url,
            screenshot=False,
            # bypass_cache=True,
            # word_count_threshold=10,
            excluded_tags=[
                "form"
            ],  # Optional - Default is None, this adds more control over the content extraction for markdown
            exclude_external_links=False,  # Default is True
            exclude_social_media_links=True,  # Default is True
            exclude_external_images=False,  # Default is False
            # social_media_domains = ["facebook.com", "twitter.com", "instagram.com", ...] Here you can add more domains, default supported domains are in config.py
            html2text={
                "escape_dot": False,
                # Add more options here
                # skip_internal_links = False
                # single_line_break = False
                # mark_code = False
                # include_sup_sub = False
                # body_width = 0
                # ignore_mailto_links = True
                # ignore_links = False
                # escape_backslash = False
                # escape_dot = False
                # escape_plus = False
                # escape_dash = False
                # escape_snob = False
            },
        )

        if result.markdown is None:
            raise ContentProcessingError("Content crawling failed")

        return result.markdown


async def process_content(content: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    logger.info(f"Starting content processing: {content}")
    try:
        validated_content = Content.model_validate(content)
        validated_content.raw_content = await crawl_content(validated_content.url)

        return settings.SUMMARY_QUEUE, validated_content.model_dump()

    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")

    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
