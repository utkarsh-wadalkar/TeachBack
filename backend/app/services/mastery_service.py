"""Mastery service — tracks the latest and best understanding per concept."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Mastery
from app.db.models.session import DEMO_STUDENT


def get_mastery_map(db: Session, student_key: str = DEMO_STUDENT) -> dict[int, int]:
    """Map of concept_id -> best mastery score, for decorating curriculum trees."""
    rows = db.query(Mastery).filter(Mastery.student_key == student_key).all()
    return {row.concept_id: row.best_score for row in rows}


def get_mastery(db: Session, concept_id: int, student_key: str = DEMO_STUDENT) -> Mastery | None:
    return (
        db.query(Mastery)
        .filter(Mastery.student_key == student_key, Mastery.concept_id == concept_id)
        .one_or_none()
    )


def update_mastery(
    db: Session, concept_id: int, understanding: int, student_key: str = DEMO_STUDENT
) -> Mastery:
    """Record a fresh understanding score. ``score`` tracks the latest attempt,
    ``best_score`` the peak. Does not commit — the caller owns the transaction."""
    row = get_mastery(db, concept_id, student_key)
    if row is None:
        row = Mastery(
            student_key=student_key,
            concept_id=concept_id,
            score=understanding,
            best_score=understanding,
            attempts_count=1,
        )
        db.add(row)
    else:
        row.score = understanding
        row.best_score = max(row.best_score, understanding)
        row.attempts_count += 1
    db.flush()
    return row
