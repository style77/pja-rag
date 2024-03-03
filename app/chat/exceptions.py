from fastapi import HTTPException
from app.chat.constants import FailureReason
from starlette import status


class RetrievalNoDocumentsFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=FailureReason.NO_DOCUMENTS_FOUND,
        )
