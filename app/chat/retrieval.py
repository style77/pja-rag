from qdrant_client import QdrantClient

from app.chat.exceptions import RetrievalNoDocumentsFoundException
from app.chat.models import BaseMessage
from app.config import settings
from app.core.logs import logger

client = QdrantClient(url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY)


def process_retrieval(message: BaseMessage) -> BaseMessage:
    search_result = search(query=message.message)
    resulting_query: str = (
        f"Answer based only on the context, nothing else. \n"
        f"QUERY:\n{message.message}\n"
        f"CONTEXT:\n{search_result}"
    )
    logger.info(f"Resulting Query: {resulting_query}")
    return BaseMessage(message=resulting_query, model=message.model)


def search(query: str) -> str:
    search_result = client.query(
        collection_name=settings.QDRANT_COLLECTION_NAME, limit=3, query_text=query
    )
    if not search_result:
        raise RetrievalNoDocumentsFoundException
    return "\n".join(result.payload["page_content"] for result in search_result)
