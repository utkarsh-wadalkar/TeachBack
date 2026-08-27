"""Embedding adapters.

``MockEmbeddingProvider`` produces deterministic bag-of-words vectors with no
external dependencies — enough for genuine cosine-similarity retrieval over the
small MVP corpus. A real multilingual embedding adapter can be dropped in later
without changing the retriever.
"""

from __future__ import annotations

import hashlib
import math
import re

from app.ai.base import EmbeddingProvider
from app.core.config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class MockEmbeddingProvider(EmbeddingProvider):
    """Hashed bag-of-words embeddings. Deterministic and dependency-free."""

    name = "mock"

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed_text(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _TOKEN_RE.findall(text.lower()):
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm:
            vec = [v / norm for v in vec]
        return vec

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(t) for t in texts]


def get_embedding_provider() -> EmbeddingProvider:
    # Only the mock is implemented in the MVP; the factory exists so a real
    # multilingual provider can be selected via EMBEDDING_PROVIDER later.
    _ = settings.embedding_provider
    return MockEmbeddingProvider()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)
