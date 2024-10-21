from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Queue settings
    INPUT_QUEUE: str = "classified_queue"
    EXCHANGE_QUEUE: str = "content_processing_exchange"
    ERROR_QUEUE: str = "error_queue"
    CRAWL_QUEUE: str = "crawl_queue"
    TRANSCRIBE_QUEUE: str = "transcribe_queue"

    # DB Service URL
    API_GATEWAY_HOST: str = "localhost"
    API_GATEWAY_PORT: str = "80"

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS or ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

    @property
    def DB_SERVICE_URL(self) -> str:
        return f"http://{self.API_GATEWAY_HOST}:{self.API_GATEWAY_PORT}/api/db"

    @property
    def OUTPUT_QUEUES(self) -> List[str]:
        return [self.CRAWL_QUEUE, self.TRANSCRIBE_QUEUE]


settings = Settings()
