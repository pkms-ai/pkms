import openai
from models import ContentType
from config import settings

openai.api_key = settings.OPENAI_API_KEY

def classify_content(content: str) -> ContentType:
    # prompt = f"""
    # Classify the following content into one of these categories: WEB_ARTICLE, YOUTUBE_VIDEO, or BOOKMARK.
    # If it's a URL, determine if it's a web article, YouTube video, or a general bookmark.
    # If it's text content, classify it as WEB_ARTICLE.

    # Content: {content}

    # Classification:
    # """

    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=prompt,
    #     max_tokens=1,
    #     n=1,
    #     stop=None,
    #     temperature=0.5,
    # )

    # classification = response.choices[0].text.strip()

    classification = "WEB_ARTICLE"
    
    if classification == "WEB_ARTICLE":
        return ContentType.WEB_ARTICLE
    elif classification == "YOUTUBE_VIDEO":
        return ContentType.YOUTUBE_VIDEO
    else:
        return ContentType.BOOKMARK
