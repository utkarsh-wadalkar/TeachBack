"""Session contract: every attempt of a TeachBack belongs to the same session,
numbered sequentially, and each attempt carries exactly one evaluation."""

from __future__ import annotations

from app.db.models import Attempt
from app.services import teachback_service
from tests.conftest import seed_curriculum


def test_second_attempt_belongs_to_same_session(db) -> None:
    nf3 = seed_curriculum(db)
    session = teachback_service.start_session(db, nf3.id)

    a1 = teachback_service.submit_attempt(
        db, session.session_id, "3NF is about functional dependencies.", "text"
    )
    a2 = teachback_service.submit_attempt(
        db, session.session_id, "3NF adds transitive dependency removal to 2NF.", "text"
    )

    assert a1.attempt_number == 1
    assert a2.attempt_number == 2

    attempts = (
        db.query(Attempt)
        .filter(Attempt.session_id == session.session_id)
        .order_by(Attempt.attempt_number)
        .all()
    )
    assert [a.id for a in attempts] == [a1.attempt_id, a2.attempt_id]


def test_attempt_number_cannot_be_duplicated(db) -> None:
    """The unique (session_id, attempt_number) constraint guards the sequence."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    nf3 = seed_curriculum(db)
    session = teachback_service.start_session(db, nf3.id)
    db.add(Attempt(session_id=session.session_id, attempt_number=1, response_text="x"))
    db.commit()
    db.add(Attempt(session_id=session.session_id, attempt_number=1, response_text="y"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_unknown_session_is_not_found(db) -> None:
    import pytest

    from app.core.errors import NotFoundError

    seed_curriculum(db)
    with pytest.raises(NotFoundError):
        teachback_service.submit_attempt(db, 99999, "anything", "text")


def test_start_session_returns_the_teachback_prompt(db) -> None:
    nf3 = seed_curriculum(db)
    nf3.learning["teachback_prompt"] = "Explain 3NF to a classmate who knows 2NF."
    db.commit()

    session = teachback_service.start_session(db, nf3.id)
    assert session.concept_name == "Third Normal Form"
    assert session.concept_id == nf3.id
    assert "classmate" in session.prompt
