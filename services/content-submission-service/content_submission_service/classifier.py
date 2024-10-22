import logging
import uuid

from openai import OpenAI

from .config import settings
from .models import Content, ClassifiedContent, ContentType


def classify_content(input_text: str) -> Content:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = """
    Classify the given content as WEB_ARTICLE, PUBLICATION, YOUTUBE_VIDEO, BOOKMARK, UNKNOWN based on its type.

- Determine whether the content is text or a URL.
- If it's a URL, identify if it links to a web article, a YouTube video, scientific publicaton or consider it a general bookmark if it doesn't fit the other categories.
- If the URL is unclear whether it's a web article or a general website bookmark, default to BOOKMARK unless clear evidence suggests otherwise.
- If the content is text which doesn't contain a URL, classify it as UNKNOWN.
"""

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": input_text},
            ],
            response_format=ClassifiedContent,
        )

        classified_content = completion.choices[0].message.parsed
        if classified_content is None:
            return Content(content_type=ContentType.UNKNOWN)
        content = Content(
            content_id=str(uuid.uuid4()),
            content_type=classified_content.content_type,
            url=classified_content.url,
        )
        return content
    except Exception as e:
        logging.error(f"Error classifying content: {e}")
        return Content(content_type=ContentType.UNKNOWN)
