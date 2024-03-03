from typing import List, Union
from pydantic import BaseModel
from app.chat.constants import ModelEnum, RoleEnum

from app.core.models import TimestampAbstractModel


class BaseMessage(BaseModel):
    role: RoleEnum
    content: str


class Message(BaseModel):
    messages: List[BaseMessage] = []


class ResponseMessage(TimestampAbstractModel):
    response: Union[str, List[str]]
