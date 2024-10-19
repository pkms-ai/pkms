import logging

from common_lib.models import ContentClassification, ContentType
from openai import OpenAI

from .config import settings


def classify_content(input_text: str) -> ContentClassification:
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
            response_format=ContentClassification,
        )

        classified_content = completion.choices[0].message.parsed
        if classified_content is None:
            return ContentClassification(content_type=ContentType.UNKNOWN)
        return classified_content
    except Exception as e:
        logging.error(f"Error classifying content: {e}")
        return ContentClassification(content_type=ContentType.UNKNOWN)
