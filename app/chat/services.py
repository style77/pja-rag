import httpx
from app.chat.retrieval import process_retrieval
from app.config import settings
from app.chat.constants import ModelEnum

from app.chat.models import Message

from openai import AsyncOpenAI, AsyncStream

openai_key = settings.OPENAI_KEY
if openai_key:
    client = AsyncOpenAI(api_key=openai_key)


class CompletionService:
    @staticmethod
    def get_messages(input_message: Message):
        latest_message = input_message.messages.pop()
        enhanced_query = process_retrieval(latest_message.content)

        messages = [
            {"role": message.role.value, "content": message.content}
            for message in input_message.messages
        ]

        messages.append(
            {"role": latest_message.role.value, "content": enhanced_query}
        )

        return messages

    @classmethod
    async def with_stream(cls, input_message: Message):
        async def stream_response():
            async with httpx.AsyncClient(timeout=300) as client:
                async with client.stream(
                    "POST",
                    f"{settings.OLLAMA_HOST}/api/chat",
                    json={"model": ModelEnum.MIXTRAL.value, "messages": cls.get_messages(input_message)},
                ) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk

        async def stream_response_openai():
            stream: AsyncStream = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=cls.get_messages(input_message),
                stream=True
            )

            async for event in stream:
                if current_response := event.choices[0].delta.content:
                    yield "data: " + current_response + "\n\n"

        return stream_response_openai if openai_key else stream_response
