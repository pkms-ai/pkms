from typing import List, Dict
from pydantic_settings import BaseSettings
from common_lib.models import ContentType

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_QUEUES: Dict[ContentType, str] = {
        ContentType.WEB_ARTICLE: "web_article_queue",
        ContentType.PUBLICATION: "publication_queue",
        ContentType.YOUTUBE_VIDEO: "youtube_video_queue",
        ContentType.BOOKMARK: "bookmark_queue",
    }
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: int = 8001

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS or ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

settings = Settings()
