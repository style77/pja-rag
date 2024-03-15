from typing import List
from qdrant_client import QdrantClient
from qdrant_client.fastembed_common import QueryResponse

from app.chat.exceptions import RetrievalNoDocumentsFoundException
from app.config import settings
from app.core.logs import logger

client = QdrantClient(url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY)


def process_retrieval(query: str) -> str:
    """
    Create a query based on the context of the message, clearly linking each piece of context to its source URL or identifier.
    """
    search_results = search(query=query)

    search_contents_with_sources = []
    for i, result in enumerate(search_results, start=1):
        document = result.document.strip()
        source = result.metadata.get("path", "Unknown source").strip()
        search_contents_with_sources.append(f"CONTEXT {i}:\n{document}\nSOURCE {i}: {source}\n")

    search_contents_with_sources_str = "\n".join(search_contents_with_sources)

    resulting_query: str = (
        "Answer based only on the context and your general knowledge"
        f"QUERY:\n{query}\n\n"
        f"{search_contents_with_sources_str}"
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
