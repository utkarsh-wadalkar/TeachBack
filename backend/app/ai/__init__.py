"""AI adapters and the evaluation-support layer.

Public factories:
    get_llm_provider()        -> LLMProvider
    get_stt_provider()        -> STTProvider
    get_embedding_provider()  -> EmbeddingProvider
    build_retriever(factory)  -> KnowledgeRetriever
"""

from app.ai.base import EmbeddingProvider, LLMProvider, RetrievedKnowledge, STTProvider
from app.ai.embeddings import get_embedding_provider
from app.ai.llm import get_llm_provider, heuristic_evaluate
from app.ai.retriever import KnowledgeRetriever, build_retriever
from app.ai.stt import get_stt_provider

__all__ = [
    "LLMProvider",
    "STTProvider",
    "EmbeddingProvider",
    "RetrievedKnowledge",
    "get_llm_provider",
    "get_stt_provider",
    "get_embedding_provider",
    "build_retriever",
    "KnowledgeRetriever",
    "heuristic_evaluate",
]
