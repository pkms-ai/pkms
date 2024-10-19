import logging

from common_lib.models import ClassifiedContent, ContentType

logger = logging.getLogger(__name__)


def process_text(data: dict):
    # Implement text processing logic here
    return f"Processed text: {data['content']}"


def process_image(data: dict):
    # Implement image processing logic here
    return f"Processed image: {data['content']}"


def process_video(data: dict):
    # Implement video processing logic here
    return f"Processed video: {data['content']}"


def process_web_article(data: dict):
    # Implement web article processing logic here
    return f"Processed web article: {data['content']}"


def process_publication(data: dict):
    # Implement publication processing logic here
    return f"Processed publication: {data['content']}"


def process_youtube_video(data: dict):
    # Implement YouTube video processing logic here
    return f"Processed YouTube video: {data['content']}"


def process_bookmark(data: dict):
    # Implement bookmark processing logic here
    return f"Processed bookmark: {data['content']}"


content_processors = {
    ContentType.WEB_ARTICLE: process_web_article,
    ContentType.PUBLICATION: process_publication,
    ContentType.YOUTUBE_VIDEO: process_youtube_video,
    ContentType.BOOKMARK: process_bookmark,
}


def process_content(content: dict):
    logger.info(f"Processing content: {content}")
    classified_content = ClassifiedContent.model_validate(content)
    processor = content_processors.get(
        classified_content.content_type, lambda x: f"Unknown content type: {x['content_type']}"
    )
    # Pass only the necessary data to the processor function
    return processor({'content': classified_content.url})
