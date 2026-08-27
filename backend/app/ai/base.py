"""AI provider interfaces.

Everything the evaluation engine needs from the outside world — text generation,
speech-to-text, embeddings — is expressed as a small abstract interface here.
Concrete adapters (Sarvam for the hackathon, deterministic mocks for offline
demos) live alongside this file. Swapping infrastructure later means writing a
new adapter, not touching the evaluation engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RetrievedKnowledge:
    """A single authoritative snippet returned by the retriever.

    The evaluator receives a list of these and never learns whether they came
    from local JSON, Postgres, or a vector database.
    """

    title: str
    text: str
    source: str
    score: float = 0.0


class LLMProvider(ABC):
    """Generates a completion from a fully-rendered prompt.

    The contract is intentionally minimal: a prompt string in, a response string
    out (expected to be JSON for evaluation prompts). This keeps every caller
    provider-agnostic.
    """

    name: str = "base"

    @abstractmethod
    def complete(self, prompt: str) -> str: ...


class STTProvider(ABC):
    name: str = "base"

    @abstractmethod
    def transcribe(
        self, audio: bytes, *, content_type: str = "audio/webm", language: str | None = None
    ) -> str: ...


class EmbeddingProvider(ABC):
    name: str = "base"
    dim: int = 256

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]
