import os
from typing import List
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import VectorParams, Distance

from scraper.parsers import FileParser

from scraper import config

from sentence_transformers import SentenceTransformer
import torch


model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cuda" if torch.cuda.is_available() else "cpu",
)


def convert_to_vector(text: str) -> List[float]:
    vectors = model.encode(text, show_progress_bar=False)
    return vectors


def chunk_text(text: str, max_words: int = 400) -> List[str]:
    words = text.split()
    chunks = [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
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
            payload = process_file(root, file)
            for payload in payload:
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

    process_files(client)
    print("Data inserted successfully!")
