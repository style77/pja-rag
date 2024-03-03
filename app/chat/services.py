import httpx
from ollama import AsyncClient
from app.chat.constants import ModelEnum

from app.chat.exceptions import RetrievalNoDocumentsFoundException
from app.chat.models import Message


class CompletionService:
    @classmethod
    async def without_stream(cls, client: AsyncClient, input_message: Message) -> Message:
        try:
            return await client.chat(
                ModelEnum.MISTRAL,
                messages=[msg.model_dump() for msg in input_message.messages],
                format="json",
            )
        except RetrievalNoDocumentsFoundException:
            raise
