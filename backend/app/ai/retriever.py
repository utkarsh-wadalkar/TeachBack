"""Knowledge retrieval (RAG), isolated behind a single interface.

The evaluator calls ``KnowledgeRetriever.retrieve(...)`` and receives a list of
``RetrievedKnowledge``. It has no idea whether the knowledge came from local
JSON, SQL, or a vector database. For the MVP the ``LocalRetriever`` backend does
exactly what §22 of the spec asks for:

    concept (metadata filter) -> vector similarity -> top-k chunks

Adding Qdrant later means writing a new backend with the same ``search`` method.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.ai.base import EmbeddingProvider, RetrievedKnowledge
from app.ai.embeddings import cosine_similarity, get_embedding_provider
from app.core.config import settings
from app.db.models import KnowledgeChunk


class RetrieverBackend(ABC):
    @abstractmethod
    def search(self, concept_id: int, query: str, k: int = 3) -> list[RetrievedKnowledge]: ...


class LocalRetriever(RetrieverBackend):
    """Metadata-filtered vector search over KnowledgeChunk rows in the database."""

    def __init__(
        self, session_factory: Callable[[], Session], embedder: EmbeddingProvider
    ) -> None:
        self._session_factory = session_factory
        self._embedder = embedder

    def search(self, concept_id: int, query: str, k: int = 3) -> list[RetrievedKnowledge]:
        db = self._session_factory()
        try:
            # 1) Metadata filter: only chunks for this concept.
            chunks = (
                db.query(KnowledgeChunk)
                .filter(KnowledgeChunk.concept_id == concept_id)
                .all()
            )
            if not chunks:
                return []
            # 2) Semantic search over the filtered set.
            q_vec = self._embedder.embed_one(query)
            scored = [
                RetrievedKnowledge(
                    title=c.title,
                    text=c.text,
                    source=c.source,
                    score=cosine_similarity(q_vec, c.embedding or []),
                )
                for c in chunks
            ]
            scored.sort(key=lambda r: r.score, reverse=True)
            return scored[:k]
        finally:
            db.close()


class KnowledgeRetriever:
    """Facade the evaluation engine depends on."""

    def __init__(self, backend: RetrieverBackend) -> None:
        self._backend = backend

    def retrieve(self, concept_id: int, query: str, k: int = 3) -> list[RetrievedKnowledge]:
        return self._backend.search(concept_id, query, k)


def build_retriever(session_factory: Callable[[], Session]) -> KnowledgeRetriever:
    """Factory selecting the retrieval backend from configuration.

    Only the local backend is implemented in the MVP. Selecting ``qdrant`` fails
    loudly rather than silently degrading, since it needs real infrastructure.
    """
    if settings.retriever_backend.lower() == "qdrant":
        raise NotImplementedError(
            "The Qdrant retriever backend is reserved for post-MVP expansion. "
            "Set RETRIEVER_BACKEND=local for the demo."
        )
    return KnowledgeRetriever(LocalRetriever(session_factory, get_embedding_provider()))
