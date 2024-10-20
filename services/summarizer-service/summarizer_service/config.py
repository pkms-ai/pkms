from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Configuration options
    RABBITMQ_QUEUE_NAME: str = "classified_queue"
    CONTENT_PROCESSING_TIMEOUT: int = 300  # 5 minutes in seconds

    # Queue settings
    MESSAGE_EXCHANGE: str = "message_exchange"
    ERROR_QUEUE: str = "error_queue"
    MAX_RETRIES: int = 3
    CRAWL_QUEUE: str = "crawl_queue"
    TRANSCRIBE_QUEUE: str = "transcribe_queue"

    # DB Service URL
    API_GATEWAY_HOST: str = "localhost"
    API_GATEWAY_PORT: str = "80"

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS or ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

    def db_service_url(self) -> str:
        return f"http://{self.API_GATEWAY_HOST}:{self.API_GATEWAY_PORT}/api/db"


settings = Settings()
