import logging

from googleapiclient.discovery import build
from langchain_community.document_loaders import YoutubeLoader

from universal_worker.config import settings
from universal_worker.models import ContentType, TranscribedContent
from universal_worker.exceptions import ContentProcessingError

logger = logging.getLogger(__name__)


def get_video_details(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)

    request = youtube.videos().list(part="snippet", id=video_id)

    response = request.execute()

    if response["items"]:
        video_info = response["items"][0]["snippet"]
        return {
            "title": video_info["title"],
            "description": video_info["description"],
            "image_url": video_info.get("thumbnails", {})
            .get("standard", {})
            .get("url", "No Image Available"),
        }
    return None


async def transcribe_content(url: str) -> TranscribedContent:
    try:
        logger.info(f"Transcribing: {url}")
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)

        docs = loader.load()

        transcript = "\n".join([doc.page_content for doc in docs])

        id = docs[0].metadata["source"]

        if id is None or id == "":
            raise Exception("Failed to get youtube id")

        new_url = f"https://www.youtube.com/watch?v={id}"

        logger.info(f"Fetching video details for youtube id: {id}")
        details = get_video_details(id, settings.YOUTUBE_API_KEY)
        if not details:
            raise Exception("Failed to fetch video details")

        content = TranscribedContent(
            url=new_url,
            raw_content=transcript,
            content_type=ContentType.YOUTUBE_VIDEO,
            title=details["title"],
            description=details["description"],
            image_url=details["image_url"],
            video_id=id,
        )

        logger.info(f"Transcribing Completed for: {url}")
        return content
    except Exception as e:
        logger.error(f"Error transcribing content using api: {e}")
        raise ContentProcessingError(f"Error transcribing content: {str(e)}")
