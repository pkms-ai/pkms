from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@message-queue:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Default value
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else self.CORS_ORIGINS.split(",")

settings = Settings()
