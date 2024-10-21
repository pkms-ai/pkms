from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = "OPENAI_API_KEY"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Configuration options
    CONTENT_PROCESSING_TIMEOUT: int = 300  # 5 minutes in seconds
    MAX_RETRIES: int = 3

    # Queue settings
    INPUT_QUEUE: str = "summary_queue"
    MAIN_EXCHANGE: str = "summary_exchange"
    ERROR_QUEUE: str = "error_queue"
    EMBEDDING_QUEUE: str = "embedding_queue"

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
