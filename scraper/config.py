from typing import Optional
from pydantic_settings import BaseSettings


class ScraperSettings(BaseSettings):
    URL: str = "https://pja.mykhi.org/"  # Default URL to scrape data from
    WORKERS: int = 5  # Number of workers to use for scraping
    HEADLESS: bool = True  # Use headless mode for the browser

    QDRANT_HOST: str = "http://qdrant:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "documents"

    DATA_DIRECTORY: str = "data/"

    OLLAMA_HOST: str = "http://ollama:8000"  # Pydantic is dumb, and raises ValidationError

    LLAMA_PARSE_API_KEY: str

    class Config:
        env_file = ".env"
