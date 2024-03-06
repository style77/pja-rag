from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.core.api import router as core_router
from app.chat.api import router as chat_router
from app.core.logs import logger
from app.config import settings


@asynccontextmanager
async def lifespan(app: str):
    logger.info("Starting up the server")
    yield
    logger.info("Shutting down the server")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_router)
app.include_router(chat_router)
