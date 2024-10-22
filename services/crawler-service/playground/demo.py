import asyncio
import base64
import os

import requests
from bs4 import BeautifulSoup, Tag
from crawl4ai import AsyncWebCrawler

from crawler_service.processors import extract_metadata


system_prompt = """ Clean the given context extract from a website by removing irrelevant information while preserving the main text, markdown format, and associated images. Do not translate or modify the content language.

# Steps

1. **Identify Main Text**: Carefully read the content to distinguish the main text from extraneous information.
2. **Remove Irrelevant Information**: Eliminate any unrelated or redundant information that does not contribute to the main content.
3. **Maintain Formatting**: Ensure that the original markdown formatting is kept intact to preserve text structure and styling.
4. **Preserve Images**: Retain any images related to the text, ensuring that the markdown links or tags for these images are not altered or removed.

# Output Format

The cleaned content should be presented in its original markdown format, with all main text and images retained. Make sure no translation is performed, and the language is unchanged.

# Notes

- Irrelevant information may include advertisements, pop-up notices, unrelated sidebars, or non-contextual links.
- Ensure that any headings, lists, or other markdown elements remain unaffected and correctly formatted.
"""


# def get_redirected_url(url):
#     try:
#         response = requests.head(url, allow_redirects=True)
#         return response.url  # This will return the final URL after all redirects
#     except requests.exceptions.RequestException as e:
#         return {"error": f"Failed to retrieve the URL: {e}"}
#
#
# def extract_metadata(html):
#     soup = BeautifulSoup(html, "html.parser")
#
#     def get_tag_content(tag, attrs, attr_name="content"):
#         element = soup.find(tag, attrs=attrs)
#         if isinstance(element, Tag) and element.has_attr(attr_name):
#             return element[attr_name]
#         return None
#
#     # Extract metadata with fallbacks
#     title_tag = soup.find("title")
#     title = get_tag_content("meta", {"property": "og:title"}) or (
#         title_tag.text if title_tag else "No title found"
#     )
#     description = (
#         get_tag_content("meta", {"property": "og:description"})
#         or get_tag_content("meta", {"name": "description"})
#         or "No description found"
#     )
#     image_url = (
#         get_tag_content("meta", {"property": "og:image"}) or "No image URL found"
#     )
#     twitter_image = get_tag_content("meta", {"name": "twitter:image"}) or None
#
#     return {
#         "title": title,
#         "description": description,
#         "image_url": twitter_image if twitter_image else image_url,
#         "canonical_url": get_tag_content("link", {"rel": "canonical"}, "href")
#         or "No canonical URL found",
#     }
#


async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            # url="https://vnexpress.net/chu-tich-nuoc-luong-cuong-khong-mo-lam-den-cap-nay-chuc-kia-4806802.html",
            url="https://www.cnx-software.com/2024/10/21/seeed-studio-esp32-c6-60ghz-mmwave-human-fall-detection-and-breathing-heartbeat-detection-sensor-kits/",
            screenshot=True,
            metadata=True,
            # bypass_cache=True,
            word_count_threshold=10,
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
        # Save markdown to file
        with open(os.path.join("playground", "output.md"), "w") as f:
            f.write(result.markdown)

        # Save the screenshot to a file
        with open(os.path.join("playground", "screenshot.png"), "wb") as f:
            f.write(base64.b64decode(result.screenshot))

        # soup = BeautifulSoup(result.html, "html.parser")
        # metadata = dict()
        # # Find all meta tags
        # meta_tags = soup.find_all("meta")
        # # Loop through and print metadata information
        # for meta in meta_tags:
        #     # Get the 'name' or 'property' attribute (e.g., 'description', 'keywords', etc.)
        #     meta_name = meta.get("name") or meta.get("property")
        #     # Get the 'content' attribute of the meta tag
        #     content = meta.get("content")
        #     metadata[meta_name] = content
        metadata = extract_metadata(result.html)
        print(metadata)


if __name__ == "__main__":
    asyncio.run(main())
