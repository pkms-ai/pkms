# from langchain_community.document_loaders import YoutubeLoader
#
# loader = YoutubeLoader.from_youtube_url(
#     "https://youtu.be/arKdDabcs6g?si=muHbcDDrR-Ofvl5Y", add_video_info=False
# )
#
# docs = loader.load()
#
# all_text = "\n".join([doc.page_content for doc in docs])
#
# print(docs[0])
#
#
from googleapiclient.discovery import build
from universal_worker.config import settings


def get_video_details(video_id, api_key):
    youtube = build("youtube", "v3", developerKey=api_key)

    request = youtube.videos().list(part="snippet", id=video_id)

    response = request.execute()

    print("response: ", response)
    print("=========")
    if response["items"]:
        video_info = response["items"][0]["snippet"]
        print(video_info)
        return {
            "title": video_info["title"],
            "description": video_info["description"],
            "image_url": video_info["thumbnails"]["standard"]["url"],
        }
    return None


details = get_video_details("arKdDabcs6g", settings.YOUTUBE_API_KEY)


print(details)
