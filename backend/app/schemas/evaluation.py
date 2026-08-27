"""Evaluation schemas — the strict contract for TeachBack diagnostics.

``EvaluationResult`` is the shape every attempt evaluation must conform to,
whether it came from a live LLM or the offline heuristic provider. It is
deliberately strict: understanding scores are clamped to 0-100 and the required
fields must be present, so malformed AI output is *rejected* rather than shown
to a student (see ``EvaluationResult.parse``).
"""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, ValidationError


class ConceptPoint(BaseModel):
    """One rubric concept the student did / didn't convey."""

    key: str = ""
    label: str


class MisconceptionOut(BaseModel):
    code: str = ""
    title: str
    description: str
    why_it_matters: str = ""


class EvaluationResult(BaseModel):
    """The diagnostic report for a single explanation."""

    understanding: int = Field(ge=0, le=100)
    conceptual_correctness: int = Field(ge=0, le=100)
    completeness: int = Field(ge=0, le=100)
    application_readiness: int = Field(ge=0, le=100)

    got_right: list[ConceptPoint] = Field(default_factory=list)
    needs_attention: list[ConceptPoint] = Field(default_factory=list)
    misconceptions: list[MisconceptionOut] = Field(default_factory=list)

    targeted_explanation: str = ""
    followup_question: str = ""

    # Unknown extra keys from an LLM are ignored rather than fatal.
    model_config = {"extra": "ignore"}

    @classmethod
    def parse(cls, raw: str | dict) -> "EvaluationResult":
        """Parse + validate raw provider output. Raises ``ValueError`` if invalid.

        Accepts either a JSON string (optionally wrapped in a ```json fence) or a
        dict. This is the single choke point that guarantees no malformed
        evaluation ever reaches a student.
        """
        if isinstance(raw, str):
            text = raw.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:]
                text = text.strip()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # Robust fallback for LLMs that include surrounding prose or backticks
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(0))
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"Evaluation output was not valid JSON: {exc}") from exc
                else:
                    raise ValueError(f"Evaluation output was not valid JSON: {text[:100]}") from None
        else:
            data = raw

        try:
            return cls.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Evaluation output failed schema validation: {exc}") from exc