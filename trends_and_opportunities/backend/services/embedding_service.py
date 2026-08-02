"""
EmbeddingService — wraps BAAI/bge-small-en-v1.5.
Produces 384-dim dense vectors used for similarity search against brand/campaign Pinecone indices.
"""

from FlagEmbedding import FlagModel


class EmbeddingService:
    def __init__(self):
        self._model = FlagModel(
            "BAAI/bge-small-en-v1.5",
            query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
            use_fp16=True,
        )

    def embed(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()
