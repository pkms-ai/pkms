import os
import asyncio
import base64
from crawl4ai import AsyncWebCrawler


async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url="https://vnexpress.net",
            screenshot=True,
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
        # Save markdown to file
        with open(os.path.join("playground", "output.md"), "w") as f:
            f.write(result.markdown)

        print(result.markdown)
        # Save the screenshot to a file
        with open(os.path.join("playground", "screenshot.png"), "wb") as f:
            f.write(base64.b64decode(result.screenshot))


if __name__ == "__main__":
    asyncio.run(main())
