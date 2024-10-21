import logging
from typing import Any, Dict, Tuple

from openai import OpenAI
from pydantic import ValidationError

from .config import settings
from .models import Content

logger = logging.getLogger(__name__)


class ContentProcessingError(Exception):
    pass


async def summary_content(content: Content) -> str:
    logger.info(f"Summarizing content: {content.url}")
    try:
        client = OpenAI()

        system_prompt = """
Summarize the content of a web page.\n\n# Steps\n\n1. Identify the main topic of the web page content.\n2. Extract key points and supporting details from the text.\n3. Determine the purpose and any conclusions or calls to action presented on the page.\n4. Compile the identified information into a concise summary, ensuring all essential points are covered.\n\n# Output Format\n\nThe summary should be a short paragraph that captures the key information from the web page, approximately 3-5 sentences in length. \n\n# Notes\n\n- Ensure the summary is clear and informative without extraneous details.\n- Maintain the original intentions and significant points of the content.\n- Focus on key facts and ideas rather than specific figures or data unless crucial to the topic.
            """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": content.raw_content,
                        }
                    ],
                },
            ],
            temperature=1,
            max_tokens=1048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={"type": "text"},
        )

        logger.info(f"Content summarized: {response.choices[0].message}")
        return response.choices[0].message.content
    except Exception as e:
        logger.exception(f"Error summarizing content: {e}")
        raise ContentProcessingError(f"Error summarizing content: {str(e)}")


async def process_content(content: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    url = content.get("url")
    logger.info(f"Starting content processing: {url}")
    try:
        validated_content = Content.model_validate(content)
        validated_content.summary = await summary_content(validated_content)

        return settings.EMBEDDING_QUEUE, validated_content.model_dump()

    except ValidationError as e:
        logger.error(f"Content validation failed: {e}")
        raise ContentProcessingError(f"Content validation failed: {str(e)}")

    except Exception as e:
        logger.exception(f"Error processing content: {e}")
        raise ContentProcessingError(f"Error processing content: {str(e)}")
