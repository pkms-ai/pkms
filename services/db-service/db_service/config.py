import json
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "content_db"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5  # seconds
    PORT: int = 8003

    def parse_cors_origins(self, v: str | List[str]) -> List[str]:
        """Custom parser for CORS_ORIGINS."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]  # Return the string itself as a single origin if not JSON
        return v  # If it's already a list, return it as is

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS if it's a string
        self.CORS_ORIGINS = self.parse_cors_origins(self.CORS_ORIGINS)

    # Use Pydantic v2's model_config instead of Config
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}

    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS or ["http://localhost:3000"]  # Ensure a default value

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
