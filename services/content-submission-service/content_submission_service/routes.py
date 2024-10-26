import asyncio
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import re
from .config import settings
from .models import ContentSubmission
from .utils import publish_to_queue

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)


def contains_url(text: str) -> bool:
    # Regular expression pattern for URLs
    url_pattern = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
    # Search for the pattern in the text

    return bool(url_pattern.search(text))


@router.post("/submit")
async def submit_content(submission: ContentSubmission):
    try:
        # classified_content = classify_content(submission.content)
        #
        # if (
        #     classified_content is None
        #     or classified_content.content_type == ContentType.UNKNOWN
        # ):
        #     return JSONResponse(
        #         status_code=400, content={"detail": "Failed to classify the content"}
        #     )
        #
        # logger.info(f"Classified content: {classified_content}")

        # NOTE: for now just simply forward to classifier
        # in future, we can add more AI logic here to see if this is a command
        # or if we need to do something else with the content
        if not contains_url(submission.content):
            return JSONResponse(
                status_code=400, content={"detail": "Content does not contain a URL"}
            )

        queue_name = "classify_queue"

        for attempt in range(settings.RETRY_ATTEMPTS):
            try:
                await publish_to_queue(queue_name, submission.model_dump())
                logger.info(f"Content submitted to queue: {queue_name}")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == settings.RETRY_ATTEMPTS - 1:
                    return JSONResponse(
                        status_code=503,
                        content={
                            "detail": f"Queue service unavailable after {settings.RETRY_ATTEMPTS} attempts. Please try again later."
                        },
                    )
                await asyncio.sleep(settings.RETRY_DELAY)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Content submitted successfully",
                "status": "pending",
                "content": submission.model_dump_json(),
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "An unexpected error occurred"}
        )
