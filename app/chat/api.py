from fastapi import APIRouter, Request
from huggingface_hub import InferenceClient

from app.chat.models import Message, ResponseMessage
from app.chat.services import CompletionService


router = APIRouter(tags=["Core Endpoints"])


@router.post("/v1/completion")
async def completion_create(request: Request, input_message: Message) -> ResponseMessage:
    client: InferenceClient = request.app.state.client

    res = await CompletionService.without_stream(client, input_message)
    print(res)
    return res
