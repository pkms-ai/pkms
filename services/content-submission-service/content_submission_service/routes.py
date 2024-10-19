import asyncio
import logging

from common_lib.models import ContentSubmission, ContentType
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .classifier import classify_content
from .config import settings
from .utils import publish_to_queue

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)


@router.post("/submit")
async def submit_content(submission: ContentSubmission):
    try:
        classified_content = classify_content(submission.content)

        if (
            classified_content is None
            or classified_content.content_type == ContentType.UNKNOWN
        ):
            return JSONResponse(
                status_code=400, content={"detail": "Failed to classify the content"}
            )

        logger.info(f"Classified content: {classified_content}")

        queue_name = f"{classified_content.content_type.value}_queue"

        for attempt in range(settings.RETRY_ATTEMPTS):
            try:
                await publish_to_queue(queue_name, classified_content.model_dump())
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
                "content_type": classified_content.content_type,
                "url": classified_content.url,
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "An unexpected error occurred"}
        )
