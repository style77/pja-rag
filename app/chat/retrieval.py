from typing import List
from qdrant_client import QdrantClient
from qdrant_client.fastembed_common import QueryResponse

from app.chat.exceptions import RetrievalNoDocumentsFoundException
from app.config import settings
from app.core.logs import logger

client = QdrantClient(url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY)


def process_retrieval(query: str) -> str:
    """
    Create query based on the context of the message
    """
    search_result = search(query=query)
    search_content = "\n".join(result.document for result in search_result)
    source = ", ".join(result.metadata.get("path") for result in search_result)

    resulting_query: str = (
        "Answer based only on the context, nothing else if you don't know just say \"I don't know\". Add source at the end of the message\n"
        f"QUERY:\n{query}\n"
        f"CONTEXT:\n{search_content}\n"
        f"SOURCE: {source}"
        # "Please, summarize the information and explain how it relates to the query, offering any necessary context or explanation for a better understanding.\n"
    )
    logger.info(f"Resulting Query: {resulting_query}")
    return resulting_query


def search(query: str) -> List[QueryResponse]:
    """
    Search for the most relevant context based on the query
    """

    search_result = client.query(
        collection_name=settings.QDRANT_COLLECTION_NAME, limit=3, query_text=query
    )
    if not search_result:
        raise RetrievalNoDocumentsFoundException
    return search_result
