import logging
from typing import Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

_pc = None


class MockPineconeIndex:
    def __init__(self, name: str):
        self.name = name
        self.vectors = {}

    def upsert(self, vectors: list, namespace: str = ""):
        for v in vectors:
            key = f"{namespace}:{v['id']}"
            self.vectors[key] = v

    def query(self, vector: list, top_k: int = 10, namespace: str = "", include_metadata: bool = True):
        matches = []
        for key, item in self.vectors.items():
            if key.startswith(f"{namespace}:"):
                matches.append({"id": item["id"], "score": 0.95, "metadata": item.get("metadata", {})})
        return {"matches": matches[:top_k]}


def get_pinecone():
    global _pc
    if _pc is None:
        try:
            from pinecone import Pinecone
            if settings.pinecone_api_key:
                _pc = Pinecone(api_key=settings.pinecone_api_key)
        except Exception as e:
            logger.warning("Pinecone SDK unavailable (%s). Using in-memory fallback vector storage.", e)
    return _pc


def get_index(index_name: str):
    pc = get_pinecone()
    if pc is not None:
        try:
            return pc.Index(index_name)
        except Exception as e:
            logger.error("Failed to connect to Pinecone index %s: %s", index_name, e)
    return MockPineconeIndex(index_name)
