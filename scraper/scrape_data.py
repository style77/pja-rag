import logging
import asyncio

from scraper.scraper import Scraper
from scraper import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scraper = Scraper(config)

if __name__ == "__main__":
    logger.info("Starting up the scraper service for PJA-RAG")
    logger.info(f"Using URL: {config.URL}")
    logger.info(f"Using {config.WORKERS} workers")

    asyncio.run(scraper.run())
