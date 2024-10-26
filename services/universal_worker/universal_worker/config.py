from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROCESSOR_NAME: str = "sample_processor"
    GEMINI_API_KEY: str = "gemini_1234567890"
    OPENAI_API_KEY: str = "openai_1234567890"
    YOUTUBE_API_KEY: str = "youtube_1234567890"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Queue settings
    CLASSIFY_QUEUE: str = "classify_queue"
    TRANSCRIBE_QUEUE: str = "transcribe_queue"
    CRAWL_QUEUE: str = "crawl_queue"
    SUMMARY_QUEUE: str = "summary_queue"
    ERROR_QUEUE: str = "error_queue"
    EMBEDDING_QUEUE: str = "embedding_queue"

    # DB Service URL
    API_GATEWAY_HOST: str = "localhost"
    API_GATEWAY_PORT: str = "10000"

    # PGVector DB
    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_USER: str = "vector_user"
    VECTOR_DB_PASSWORD: str = "vector_pass"
    VECTOR_DB_PORT: int = 6024
    VECTOR_DB_NAME: str = "pkms_vector"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

    @property
    def DB_SERVICE_URL(self) -> str:
        return f"http://{self.API_GATEWAY_HOST}:{self.API_GATEWAY_PORT}/api/db"

    @property
    def VECTOR_DB_URL(self) -> str:
        if self.VECTOR_DB_HOST != "localhost":
            return f"postgresql+psycopg://{self.VECTOR_DB_USER}:{self.VECTOR_DB_PASSWORD}@{self.VECTOR_DB_HOST}:5432/{self.VECTOR_DB_NAME}"
        return f"postgresql+psycopg://{self.VECTOR_DB_USER}:{self.VECTOR_DB_PASSWORD}@{self.VECTOR_DB_HOST}:{self.VECTOR_DB_PORT}/{self.VECTOR_DB_NAME}"


settings = Settings()
