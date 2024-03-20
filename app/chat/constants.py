from enum import Enum


class FailureReason(Enum):
    NO_DOCUMENTS_FOUND: str = (
        "No documents found in context. Please try again with a different query."
    )


class RoleEnum(Enum):
    USER: str = "user"
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"


class ModelEnum(Enum):
    MISTRAL: str = "mistral"
    MIXTRAL: str = "mixtral"
