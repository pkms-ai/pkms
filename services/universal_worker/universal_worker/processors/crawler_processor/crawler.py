import logging
from typing import Optional, Tuple

from bs4 import BeautifulSoup, Tag
from crawl4ai import AsyncWebCrawler

from universal_worker.models import Metadata
from universal_worker.exceptions import ContentProcessingError

logger = logging.getLogger(__name__)


def extract_metadata(html) -> Metadata:
    logger.info("Extracting metadata from HTML content")
    soup = BeautifulSoup(html, "html.parser")

    def get_tag_content(
        tag: str, attrs: dict, attr_name: str = "content"
    ) -> Optional[str]:
        """
        Find the first tag matching the given attributes and return the first non-empty content.
        """
        elements = soup.find_all(tag, attrs=attrs)  # Find all matching tags
        for element in elements:
            if isinstance(element, Tag) and element.has_attr(attr_name):
                content = element[attr_name]
                if isinstance(content, str):
                    content = content.strip()
                    if content:
                        return content
        return None  # Return None if no non-empty content found

    # Extract metadata with fallbacks
    title_tag = soup.find("title")
    title = (
        get_tag_content("meta", {"property": "og:title"})
        or get_tag_content("meta", {"property": "twitter:title"})
        or (title_tag.text if title_tag else "No title found")
    )

    description = (
        get_tag_content("meta", {"property": "og:description"})
        or get_tag_content("meta", {"name": "description"})
        or get_tag_content("meta", {"name": "Description"})
        or get_tag_content("meta", {"name": "twitter:description"})
        or "No description found"
    )
    image_url = (
        get_tag_content("meta", {"property": "og:image"})
        or get_tag_content("meta", {"name": "twitter:image"})
        or None
    )

    canonical_url = get_tag_content("link", {"rel": "canonical"}, "href")
    # keywords = get_tag_content("meta", {"name": "keywords"})

    return Metadata(
        title=title,
        description=description,
        image_url=image_url,
        canonical_url=canonical_url,
        # keywords=keywords,
    )


async def crawl_content(url: str) -> Tuple[str, Metadata]:
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
            remove_overlay_elements=True,  # Default is False
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
        metadata = extract_metadata(result.html)
        logger.info(f"Content crawling completed: {url}")
        return result.markdown, metadata
