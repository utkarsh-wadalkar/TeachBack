"""PYQ (previous-year question) schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationResult


class PyqOut(BaseModel):
    id: int
    code: str
    question: str
    marks: int
    year: str
    source: dict
    concepts_tested: list[str]


class PyqAttemptRequest(BaseModel):
    response_text: str = Field(min_length=1)


class PyqAttemptResponse(BaseModel):
    pyq_id: int
    evaluation: EvaluationResult
