import asyncio
from crawl4ai import AsyncWebCrawler

url = "https://www.marktechpost.com/2024/10/11/40-cool-ai-tools-you-should-check-out-december-2023/"
# url = "https://www.anthropic.com/news/github-copilot"
url = (
    "https://online.stanford.edu/programs/artificial-intelligence-graduate-certificate"
)


async def main():
    async with AsyncWebCrawler(
        browser_type="chromium",
        verbose=True,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        java_script_enabled=True,
        viewport={"width": 1920, "height": 1080},
    ) as crawler:
        result = await crawler.arun(
            url=url,
            screenshot=False,
            magic=True,
            simulate_user=True,
            page_timeout=60000,
            # bypass_cache=True,
            word_count_threshold=10,
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

        print(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
