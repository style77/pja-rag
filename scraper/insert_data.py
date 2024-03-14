import os
import logging
from typing import List, Union
import uuid
from openai import OpenAI
from qdrant_client import QdrantClient

from scraper.parsers import FileParser

from scraper import config

from sentence_transformers import SentenceTransformer
import torch


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cuda" if torch.cuda.is_available() else "cpu",
)


def get_embedding(text: str, model: str = "text-embedding-3-small"):
    text = text.replace("\n", " ")
    openai_client = OpenAI(
        config.OPENAI_KEY
    )  # todo, obj should not be created every time
    return openai_client.embeddings.create(input=[text], model=model).data[0].embedding


def convert_to_vector(text: str) -> List[float]:
    if config.OPENAI_KEY:
        vectors = get_embedding(text)
    else:
        vectors = model.encode([text])[0].tolist()
    return vectors


def chunk_text(text: str, max_words: int = 400) -> List[str]:
    words = text.split()
    chunks = [
        " ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)
    ]
    return chunks


def process_file(root, file):
    filepath = os.path.join(root, file)
    try:
        parser = FileParser(filepath)
        data = parser.parse()
    except Exception as e:
        print(f"Failed to parse file: {file}, error: {e}")
        return

    chunks = chunk_text(data.content)
    for chunk in chunks:
        id_ = uuid.uuid4().hex

        yield {
            "id": id_,
            "content": chunk,
            "metadata": {
                "filename": data.filename,
                "path": data.path,
                "metadata": data.metadata,
            },
        }


def process_files(qdrant_client: QdrantClient):
    directory = os.walk(config.DATA_DIRECTORY)
    points = []

    for root, _, files in directory:
        for file in files:
            logger.info(f"Processing file: {file}")
            payloads = process_file(root, file)
            for i, payload in enumerate(payloads):
                logger.info(f"| Processing payload: {i} for file: {file}")
                points.append(payload)

    qdrant_client.add(
        collection_name=config.QDRANT_COLLECTION_NAME,
        ids=[point["id"] for point in points],
        documents=[point["content"] for point in points],
        metadata=[point["metadata"] for point in points],
    )


if __name__ == "__main__":
    client = QdrantClient(
        url=config.QDRANT_HOST, api_key=config.QDRANT_API_KEY, timeout=300
    )

    client.delete_collection(collection_name=config.QDRANT_COLLECTION_NAME)

    logger.info("Processing files")
    process_files(client)
    logger.info("Data inserted successfully!")
