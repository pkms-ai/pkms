from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = "OPENAI_API_KEY"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Queue settings
    INPUT_QUEUE: str = "embedding_queue"
    EXCHANGE_QUEUE: str = "embedding_exchange"
    ERROR_QUEUE: str = "error_queue"

    # DB Service URL
    API_GATEWAY_HOST: str = "localhost"
    API_GATEWAY_PORT: str = "80"

    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_USER: str = "vector_user"
    VECTOR_DB_PASSWORD: str = "vector_pass"
    VECTOR_DB_PORT: int = 6024
    VECTOR_DB_NAME: str = "pkms_vector"

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS or ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

    @property
    def DB_SERVICE_URL(self) -> str:
        return f"http://{self.API_GATEWAY_HOST}:{self.API_GATEWAY_PORT}/api/db"

    @property
    def VECTOR_DB_URL(self) -> str:
        if self.VECTOR_DB_HOST != "localhost":
            return f"postgresql+psycopg://{self.VECTOR_DB_USER}:{self.VECTOR_DB_PASSWORD}@{self.VECTOR_DB_HOST}:5432/{self.VECTOR_DB_NAME}"
        return f"postgresql+psycopg://{self.VECTOR_DB_USER}:{self.VECTOR_DB_PASSWORD}@{self.VECTOR_DB_HOST}:{self.VECTOR_DB_PORT}/{self.VECTOR_DB_NAME}"

    @property
    def OUTPUT_QUEUES(self) -> List[str]:
        return []


settings = Settings()
