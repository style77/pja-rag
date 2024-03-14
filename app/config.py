from typing import Optional
import typing
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

    OPENAI_KEY: typing.Optional[str] = None

    ALLOWED_HOSTS: list[str] = ["*"]

    @property
    def is_local(self):
        return self.ENVIRONMENT == Environment.LOCAL.value

    class Config:
        env_file = ".env"


settings = Settings()
