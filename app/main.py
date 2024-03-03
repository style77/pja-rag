from fastapi import FastAPI
from contextlib import asynccontextmanager

from ollama import AsyncClient

from app.core.api import router as core_router
from app.chat.api import router as chat_router
from app.core.logs import logger
from app.config import settings


def init_client():
    return AsyncClient(host=settings.OLLAMA_HOST)


@asynccontextmanager
async def lifespan(app: str):
    logger.info("Starting up the server")
    app.state.client = init_client()
    yield
    logger.info("Shutting down the server")


app = FastAPI(lifespan=lifespan)

app.include_router(core_router)
app.include_router(chat_router)
