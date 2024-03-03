from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

from app.core.constants import Environment


class Settings(BaseSettings):
    APP_NAME: str = "PJA-RAG"
    ENVIRONMENT: str = Field(default=Environment.LOCAL.value)
    OLLAMA_HOST: str = "http://ollama:11434"

    QDRANT_HOST: str = "http://qdrant:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "documents"

    DATA_DIRECTORY: str = "data/"

    @property
    def is_local(self):
        return self.ENVIRONMENT == Environment.LOCAL.value

    class Config:
        env_file = ".env"


settings = Settings()
