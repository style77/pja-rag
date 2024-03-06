from qdrant_client import QdrantClient

from app.chat.exceptions import RetrievalNoDocumentsFoundException
from app.config import settings
from app.core.logs import logger

client = QdrantClient(url=settings.QDRANT_HOST, api_key=settings.QDRANT_API_KEY)


def process_retrieval(query: str) -> str:
    """
    Create query based on the context of the message
    """
    search_result = search(query=query)
    # resulting_query: str = (
    #     "Please provide a response in the same language as the query. Based on the information retrieved from the document, provide a concise summary and explain the key points related to the query. Make sure to synthesize the information in a way that offers clear insights. \n"
    #     f"QUERY:\n{query}\n"
    #     f"CONTEXT:\n{search_result}\n"
    #     "Please, summarize the information and explain how it relates to the query, offering any necessary context or explanation for a better understanding.\n"
    # )
    resulting_query: str = (
        "Answer based only on the context, nothing else if you don't know just say \"I don't know\".\n"
        f"QUERY:\n{query}\n"
        f"CONTEXT:\n{search_result}\n"
        # "Please, summarize the information and explain how it relates to the query, offering any necessary context or explanation for a better understanding.\n"
    )
    logger.info(f"Resulting Query: {resulting_query}")
    return resulting_query


def search(query: str) -> str:
    """
    Search for the most relevant context based on the query
    """

    search_result = client.query(
        collection_name=settings.QDRANT_COLLECTION_NAME, limit=3, query_text=query
    )
    if not search_result:
        raise RetrievalNoDocumentsFoundException
    return "\n".join(result.document for result in search_result)
