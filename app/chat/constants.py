from enum import StrEnum


class FailureReason(StrEnum):
    NO_DOCUMENTS_FOUND: str = (
        "No documents found in context. Please try again with a different query."
    )


class RoleEnum(StrEnum):
    USER: str = "user"
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"


class ModelEnum(StrEnum):
    MISTRAL: str = "mistral"
    MIXTRAL: str = "mixtral"
