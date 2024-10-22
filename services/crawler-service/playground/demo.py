import asyncio
import base64
import os
import re
import google.generativeai as genai
from google.generativeai.types import GenerationConfigType
from crawl4ai import AsyncWebCrawler

from crawler_service.config import settings
from crawler_service.crawler import extract_metadata

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


def unwrap_first_codeblock(response_text: str) -> str:
    """
    Cleans and unwraps the first code block by removing the first occurrence of code block delimiters.
    """
    # Replace the first code block using `re.subn` which allows limiting replacements
    cleaned_text, _ = re.subn(r"```.*?```", "", response_text, count=1, flags=re.DOTALL)

    # Strip extra whitespace or newlines
    cleaned_text = cleaned_text.strip()

    return cleaned_text


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


def clean_markdown(markdown):
    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8010,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-002",
        generation_config=generation_config,
        system_instruction="You are a professional in web scraping and cleaning markdown. You excel at identifying irrelevant elements and extracting the core content cleanly.\n\nClean the provided markdown content from a website by removing irrelevant elements such as navigation and headers while maintaining the main content, language, images, and links. Ensure that the output is in markdown format only.\n\n# Steps\n\n1. **Identify Main Content**: Locate the sections of the markdown that correspond to the primary content based on context and relevance.\n2. **Remove Irrelevant Sections**: Identify and eliminate any markdown portions related to navigation, headers, footers, or any non-essential sections that do not contribute to the main content.\n3. **Preserve Language and Images**: Ensure that the main textual content remains intact, preserving the original language and all image references.\n4. **Perform Quality Check**: Review the cleaned markdown to ensure that only relevant content is maintained, and the markdown format is correctly preserved.\n\n# Output Format\n\n- The output should be pure markdown format.\n- Only relevant main content, language, and images should be included.\n- Ensure there is no extraneous or irrelevant information in the output.\n\n# Notes\n\n- Pay careful attention to sections of the markdown that are structured as navigation, headers, or footers to ensure they are removed.\n- Maintain any links or references integral to the main content.\n- Images should remain in their original markdown format with accurate alt text.\n",
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(markdown)

    return response.text


async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            # url="https://vnexpress.net/chu-tich-nuoc-luong-cuong-khong-mo-lam-den-cap-nay-chuc-kia-4806802.html",
            url="https://medium.com/@SergeyNuzhdin/how-to-build-tiny-golang-docker-images-with-gitlab-ci-166e11d5c3f7",
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

        # clean
        cleaned_markdown = clean_markdown(result.markdown)
        cleaned_markdown = unwrap_first_codeblock(cleaned_markdown)
        # Save markdown to file
        with open(os.path.join("playground", "output.md"), "w") as f:
            f.write(cleaned_markdown)

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
