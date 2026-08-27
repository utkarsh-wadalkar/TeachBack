"""Speech-to-text adapters.

``SarvamSTTProvider`` calls Sarvam's speech-to-text API (strong Indian-language
support). ``MockSTTProvider`` returns a documented sample explanation so the
audio path stays functional in an offline demo.
"""

from __future__ import annotations

import httpx

from app.ai.base import STTProvider
from app.core.config import settings

# A realistic first-attempt explanation, returned by the mock so recording an
# answer flows straight into evaluation during an offline demo.
_MOCK_TRANSCRIPT = (
    "Third normal form builds on 2NF, so a relation must already be in second "
    "normal form with all partial dependencies removed, and every non-key "
    "attribute depends only on the candidate key. We use functional dependencies "
    "to decide this. For example, in a table STUDENT with StudentID, Name and "
    "Department, StudentID determines Name and Department."
)


class MockSTTProvider(STTProvider):
    name = "mock"

    def transcribe(
        self, audio: bytes, *, content_type: str = "audio/webm", language: str | None = None
    ) -> str:
        return _MOCK_TRANSCRIPT


class SarvamSTTProvider(STTProvider):
    name = "sarvam"

    def __init__(self) -> None:
        self.api_key = settings.stt_api_key
        self.model = settings.stt_model
        self.base_url = settings.llm_base_url.rstrip("/")

    def transcribe(
        self, audio: bytes, *, content_type: str = "audio/webm", language: str | None = None
    ) -> str:
        if not self.api_key:
            raise RuntimeError("STT_API_KEY is not set; cannot use the Sarvam STT provider.")
        resp = httpx.post(
            f"{self.base_url}/speech-to-text",
            headers={"api-subscription-key": self.api_key},
            data={"model": self.model, "language_code": language or "en-IN"},
            files={"file": ("audio.webm", audio, content_type)},
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("transcript", "")


def get_stt_provider() -> STTProvider:
    provider = settings.stt_provider.lower()
    if provider == "sarvam" and settings.stt_api_key:
        return SarvamSTTProvider()
    return MockSTTProvider()
