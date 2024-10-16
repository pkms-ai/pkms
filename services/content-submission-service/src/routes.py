from fastapi import APIRouter, HTTPException
from models import ContentSubmission, ContentType
from utils import publish_to_queue, extract_url
from classifier import classify_content

router = APIRouter()

@router.post("/submit")
async def submit_content(submission: ContentSubmission):
    try:
        # Classify the content if not provided
        if not submission.content_type:
            submission.content_type = classify_content(submission.content)

        # Extract URL if not provided
        if not submission.url:
            submission.url = extract_url(submission.content)

        # Publish the submission to the appropriate queue
        queue_name = f"{submission.content_type}_queue"
        await publish_to_queue(queue_name, submission.dict())
        return {"message": "Content submitted successfully", "status": "pending", "content_type": submission.content_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
