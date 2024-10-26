import uuid

from openai import OpenAI

from universal_worker.config import settings
from universal_worker.models import Content, ClassifiedContent, ContentStatus
from universal_worker.exceptions import ContentProcessingError


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

        if (
            classified_content is None
            or classified_content.url is None
            or classified_content.content_type is None
            or classified_content.url == ""
        ):
            raise ContentProcessingError("Failed to classify content with openai")

        content = Content(
            content_id=str(uuid.uuid4()),
            content_type=classified_content.content_type,
            url=classified_content.url,
            status=ContentStatus.CLASSIFIED,
        )
        return content
    except Exception as e:
        raise ContentProcessingError(f"Error classifying content with openai: {str(e)}")
