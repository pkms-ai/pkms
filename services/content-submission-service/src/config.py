from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@message-queue:5672/"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Default value
    OPENAI_API_KEY: str

    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_parsers": {
            "CORS_ORIGINS": parse_cors_origins
        }
    }

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS

settings = Settings()
