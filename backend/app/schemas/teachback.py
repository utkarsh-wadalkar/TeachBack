"""TeachBack schemas — sessions, attempts, improvement, and mastery."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationResult


class StartSessionRequest(BaseModel):
    concept_id: int


class StartSessionResponse(BaseModel):
    session_id: int
    concept_id: int
    concept_name: str
    prompt: str
    attempt_number: int  # next attempt number (1 for a fresh session)


class SubmitAttemptRequest(BaseModel):
    response_text: str = Field(min_length=1)
    modality: str = "text"  # "text" | "audio"


class MasteryOut(BaseModel):
    concept_id: int
    score: int
    best_score: int
    attempts_count: int


class Improvement(BaseModel):
    previous_understanding: int
    current_understanding: int
    delta: int
    message: str


class AttemptResponse(BaseModel):
    attempt_id: int
    attempt_number: int
    evaluation: EvaluationResult
    improvement: Improvement | None = None
    mastery: MasteryOut


class TranscribeResponse(BaseModel):
    text: str
