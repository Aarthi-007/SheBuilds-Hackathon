"""
PineconeService — the ONLY place that talks to Pinecone (context.md rule §15.7).
Configured for BAAI/bge-small-en-v1.5 which produces 384-dim dense vectors.
"""

from pinecone import Pinecone, ServerlessSpec
from config.settings import settings

EMBEDDING_DIMENSION = 384  # bge-small-en-v1.5


class PineconeService:
    def __init__(self):
        self._client = Pinecone(api_key=settings.PINECONE_API_KEY)

    def _index(self, index_name: str):
        return self._client.Index(index_name)

    def ensure_index(self, index_name: str, cloud: str = "aws", region: str = "us-east-1") -> None:
        """Create the index if it doesn't exist. Call once at startup per index."""
        existing = {i.name for i in self._client.list_indexes()}
        if index_name not in existing:
            self._client.create_index(
                name=index_name,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud=cloud, region=region),
            )

    async def upsert(self, index: str, namespace: str, id: str, vector: list[float], metadata: dict) -> None:
        self._index(index).upsert(
            vectors=[{"id": id, "values": vector, "metadata": metadata}],
            namespace=namespace,
        )

    async def query(self, index: str, namespace: str, vector: list[float], top_k: int = 5) -> list[dict]:
        """Returns matches as [{id, score, metadata}, ...] sorted by similarity desc."""
        result = self._index(index).query(
            vector=vector, namespace=namespace, top_k=top_k, include_metadata=True
        )
        return [{"id": m.id, "score": m.score, "metadata": m.metadata} for m in result.matches]
