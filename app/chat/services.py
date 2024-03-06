import httpx
from app.chat.retrieval import process_retrieval
from app.config import settings
from app.chat.constants import ModelEnum

from app.chat.models import Message


class CompletionService:
    @classmethod
    async def with_stream(cls, input_message: Message):
        async def stream_response():
            async with httpx.AsyncClient(timeout=300) as client:
                latest_message = input_message.messages.pop()
                enhanced_query = process_retrieval(latest_message.content)

                messages = [
                    {"role": message.role.value, "content": message.content}
                    for message in input_message.messages
                ]

                messages.append(
                    {"role": latest_message.role.value, "content": enhanced_query}
                )

                async with client.stream(
                    "POST",
                    f"{settings.OLLAMA_HOST}/api/chat",
                    json={"model": ModelEnum.MIXTRAL.value, "messages": messages},
                ) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk

        return stream_response
