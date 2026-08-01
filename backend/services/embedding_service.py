import logging
import hashlib
import math
from typing import List, Optional
from config.constants import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_model = None
_model_attempted = False


def _get_model():
    global _model, _model_attempted
    if not _model_attempted:
        _model_attempted = True
        import os
        if os.getenv("SKIP_HF_DOWNLOAD", "true").lower() == "true":
            logger.info("SKIP_HF_DOWNLOAD=true: Bypassing Hugging Face download for %s, using hash-based embedding fallback.", EMBEDDING_MODEL)
            _model = None
            return _model
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading BGE-M3 embedding model %s…", EMBEDDING_MODEL)
            _model = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as e:
            logger.warning("SentenceTransformer unavailable (%s). Falling back to hash-based embedding service.", e)
            _model = None
    return _model


class EmbeddingService:
    def embed(self, text: str) -> List[float]:
        model = _get_model()
        if model is not None:
            try:
                vector = model.encode(text, normalize_embeddings=True)
                return vector.tolist()
            except Exception as e:
                logger.error("Embedding generation failed: %s", e)

        # 1024-dimensional normalized vector fallback (matches BGE-M3 dimension)
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        vec = [math.sin(seed + i) for i in range(1024)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]
