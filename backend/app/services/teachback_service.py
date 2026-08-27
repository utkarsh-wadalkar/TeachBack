"""TeachBack service — orchestrates the core learning loop.

    start_session -> submit_attempt (evaluate + persist + update mastery + diff
    against the previous attempt) -> repeat

This is where a Session, its Attempts, their Evaluations, and Mastery are tied
together. It owns the database transaction for a submission.
"""

from __future__ import annotations

from sqlalchemy.orm import Session as OrmSession

from app.ai import get_llm_provider, get_stt_provider
from app.core.errors import ConflictError, NotFoundError
from app.db.models import Attempt, Evaluation, Mastery, Session
from app.db.models.session import DEMO_STUDENT
from app.schemas.evaluation import EvaluationResult
from app.schemas.teachback import (
    AttemptResponse,
    Improvement,
    MasteryOut,
    StartSessionResponse,
)
from app.services import curriculum_service, evaluation_service, mastery_service


def _lower_first(label: str) -> str:
    """Lower-case a rubric label so it reads as prose mid-sentence.

    Labels are written for display in lists ("Transitive dependency"), but the
    improvement message splices them into a sentence. Acronym-initial labels
    ("2NF foundation", "BCNF …") are left alone.
    """
    head = label.split(" ", 1)[0]
    letters = [ch for ch in head if ch.isalpha()]
    if len(letters) > 1 and all(ch.isupper() for ch in letters):
        return label
    return label[:1].lower() + label[1:]


def _join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} and {items[-1]}"


def start_session(
    db: OrmSession, concept_id: int, student_key: str = DEMO_STUDENT
) -> StartSessionResponse:
    concept = curriculum_service.get_concept(db, concept_id)
    if not concept.teachback_enabled:
        raise ConflictError(f"TeachBack is not enabled for {concept.name} yet.")

    session = Session(concept_id=concept.id, student_key=student_key)
    db.add(session)
    db.commit()
    db.refresh(session)

    prompt = (concept.learning or {}).get("teachback_prompt") or (
        f"Explain {concept.name} in your own words, as if you were teaching it to a classmate."
    )
    return StartSessionResponse(
        session_id=session.id,
        concept_id=concept.id,
        concept_name=concept.name,
        prompt=prompt,
        attempt_number=1,
    )


def _compute_improvement(
    prev_eval: Evaluation | None, result: EvaluationResult
) -> Improvement | None:
    if prev_eval is None:
        return None

    delta = result.understanding - prev_eval.understanding
    prev_right_keys = {p.get("key") for p in (prev_eval.got_right or [])}
    newly_covered = [p.label for p in result.got_right if p.key not in prev_right_keys]
    prev_misc = {m.get("code") for m in (prev_eval.misconceptions or [])}
    cur_misc = {m.code for m in result.misconceptions}
    resolved = prev_misc - cur_misc

    parts: list[str] = []
    if delta > 0:
        parts.append(f"+{delta} points from your previous attempt.")
    elif delta < 0:
        parts.append(f"{delta} points from your previous attempt.")
    else:
        parts.append("Same score as your previous attempt.")

    if newly_covered:
        prose = _join([_lower_first(label) for label in newly_covered])
        parts.append(f"Your explanation now correctly covers {prose}.")
    if resolved:
        parts.append("You've cleared up the misconception from your last attempt.")
    if delta <= 0 and not newly_covered:
        parts.append("Focus on the areas still marked for attention.")

    return Improvement(
        previous_understanding=prev_eval.understanding,
        current_understanding=result.understanding,
        delta=delta,
        message=" ".join(parts),
    )


def submit_attempt(
    db: OrmSession, session_id: int, response_text: str, modality: str = "text"
) -> AttemptResponse:
    session = db.get(Session, session_id)
    if session is None:
        raise NotFoundError(f"Session {session_id} not found.")
    concept = session.concept

    # Capture the previous attempt's evaluation BEFORE adding the new one, so we
    # can diff against it for the improvement message.
    prior_attempts = list(session.attempts)
    prev_eval = prior_attempts[-1].evaluation if prior_attempts else None
    attempt_number = len(prior_attempts) + 1

    result = evaluation_service.evaluate_explanation(db, concept, response_text)

    attempt = Attempt(
        session_id=session.id,
        attempt_number=attempt_number,
        modality=modality,
        response_text=response_text,
    )
    db.add(attempt)
    db.flush()

    evaluation = Evaluation(
        attempt_id=attempt.id,
        understanding=result.understanding,
        conceptual_correctness=result.conceptual_correctness,
        completeness=result.completeness,
        application_readiness=result.application_readiness,
        got_right=[p.model_dump() for p in result.got_right],
        needs_attention=[p.model_dump() for p in result.needs_attention],
        misconceptions=[m.model_dump() for m in result.misconceptions],
        targeted_explanation=result.targeted_explanation,
        followup_question=result.followup_question,
        provider=get_llm_provider().name,
        raw=result.model_dump(),
    )
    db.add(evaluation)

    mastery: Mastery = mastery_service.update_mastery(
        db, concept.id, result.understanding, session.student_key
    )
    improvement = _compute_improvement(prev_eval, result)

    db.commit()

    return AttemptResponse(
        attempt_id=attempt.id,
        attempt_number=attempt_number,
        evaluation=result,
        improvement=improvement,
        mastery=MasteryOut(
            concept_id=concept.id,
            score=mastery.score,
            best_score=mastery.best_score,
            attempts_count=mastery.attempts_count,
        ),
    )


def transcribe_audio(
    audio: bytes, content_type: str = "audio/webm", language: str | None = None
) -> str:
    return get_stt_provider().transcribe(audio, content_type=content_type, language=language)
