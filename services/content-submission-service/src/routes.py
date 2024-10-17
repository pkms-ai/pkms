from fastapi import APIRouter, HTTPException
from models import ContentSubmission
from utils import publish_to_queue
from classifier import classify_content

router = APIRouter()


@router.post("/submit")
async def submit_content(submission: ContentSubmission):
    try:
        # Classify the content if not provided
        classified_content = classify_content(submission.content)

        print(classified_content)

        # Publish the submission to the appropriate queue
        queue_name = f"{classified_content.content_type}_queue"
        await publish_to_queue(queue_name, submission.dict())
        return {
            "message": "Content submitted successfully",
            "status": "pending",
            "content_type": classified_content.content_type,
            "url": classified_content.url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
