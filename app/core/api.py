from fastapi import APIRouter

from starlette import status
from starlette.requests import Request


router = APIRouter(tags=["Core"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(request: Request):
    return {"status": "ok", "version": request.app.version}
