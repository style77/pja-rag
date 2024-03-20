from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.chat.models import Message
from app.chat.services import CompletionService


router = APIRouter(tags=["Core Endpoints"])


@router.route("/v1/completion", methods=["POST", "GET"])
async def completion_create(input_message: Message) -> StreamingResponse:
    stream_response = await CompletionService.with_stream(input_message)
    return StreamingResponse(stream_response())
