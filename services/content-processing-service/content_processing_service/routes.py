from fastapi import APIRouter
from .processors import process_content

router = APIRouter()

@router.post("/process")
async def process_content_route(content: dict):
    result = process_content(content)
    return {"status": "processed", "result": result}
