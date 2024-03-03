import os
import random
from typing import List
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

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


def process_files(qdrant_client: QdrantClient):
    directory = os.walk(config.DATA_DIRECTORY)
    points = []

    for root, _, files in directory:
        for file in files:
            filepath = os.path.join(root, file)
            try:
                parser = FileParser(filepath)
                content = parser.parse()
            except Exception as e:
                print(f"Failed to parse file: {file}, error: {e}")
                continue

            id_ = uuid.uuid4().hex
            vector = convert_to_vector(content)
            vector_payload = {"fast-bge-small-en": vector.tolist()}
            payload = PointStruct(id=id_, vector=vector_payload, payload={"text": content})
            points.append(payload)

    qdrant_client.upsert(collection_name=config.QDRANT_COLLECTION_NAME, points=points, wait=True)


if __name__ == "__main__":
    client = QdrantClient(url=config.QDRANT_HOST, api_key=config.QDRANT_API_KEY, timeout=300)

    process_files(client)
    print("Data inserted successfully!")
