from database.pinecone_client import get_index
from utils.logger import get_logger

logger = get_logger(__name__)


class PineconeService:
    def upsert(
        self,
        index_name: str,
        namespace: str,
        vector_id: str,
        vector: list[float],
        metadata: dict,
    ) -> None:
        index = get_index(index_name)
        index.upsert(vectors=[{"id": vector_id, "values": vector, "metadata": metadata}], namespace=namespace)
        logger.debug("Upserted vector %s to index %s ns=%s", vector_id, index_name, namespace)

    def query(
        self,
        index_name: str,
        namespace: str,
        vector: list[float],
        top_k: int = 10,
    ) -> list[dict]:
        index = get_index(index_name)
        result = index.query(vector=vector, top_k=top_k, namespace=namespace, include_metadata=True)
        return [
            {"id": m["id"], "score": m["score"], "metadata": m.get("metadata", {})}
            for m in result.get("matches", [])
        ]
