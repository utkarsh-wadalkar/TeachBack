"""Mastery contract: a valid evaluation updates the student's mastery row,
keeping the running score, the best score, and the attempt count."""

from __future__ import annotations

from app.db.models import Mastery
from app.services import teachback_service
from tests.conftest import seed_curriculum

WEAK = (
    "3NF builds on 2NF. Once second normal form removes partial dependencies and "
    "every non-key attribute depends on the candidate key, we use functional "
    "dependencies. For example StudentID determines Name in a student table."
)
STRONG = (
    "3NF builds on 2NF: partial dependencies are gone, and there must be no "
    "transitive dependencies either — a non-key attribute may not depend on "
    "another non-key attribute, only on the candidate key. Functional dependencies "
    "show this: for example, if StudentID -> Dept and Dept -> DeptHead then "
    "DeptHead depends transitively on StudentID."
)


def test_first_evaluation_creates_a_single_mastery_row(db) -> None:
    nf3 = seed_curriculum(db)
    session = teachback_service.start_session(db, nf3.id)
    a1 = teachback_service.submit_attempt(db, session.session_id, WEAK)

    rows = db.query(Mastery).filter_by(concept_id=nf3.id).all()
    assert len(rows) == 1
    assert rows[0].score == a1.evaluation.understanding
    assert rows[0].best_score == a1.evaluation.understanding
    assert rows[0].attempts_count == 1


def test_second_evaluation_updates_the_same_row(db) -> None:
    nf3 = seed_curriculum(db)
    s1 = teachback_service.start_session(db, nf3.id)
    teachback_service.submit_attempt(db, s1.session_id, WEAK)

    # Mastery persists across sessions for the same student+concept.
    s2 = teachback_service.start_session(db, nf3.id)
    a2 = teachback_service.submit_attempt(db, s2.session_id, STRONG)

    rows = db.query(Mastery).filter_by(concept_id=nf3.id).all()
    assert len(rows) == 1
    m = rows[0]
    assert m.score == a2.evaluation.understanding  # latest
    assert m.best_score >= a2.evaluation.understanding  # peak kept
    assert m.attempts_count == 2  # counted across sessions


def test_weak_then_strong_improvement_is_reported(db) -> None:
    nf3 = seed_curriculum(db)
    session = teachback_service.start_session(db, nf3.id)
    a1 = teachback_service.submit_attempt(db, session.session_id, WEAK)
    assert a1.improvement is None  # nothing to diff against on attempt one

    a2 = teachback_service.submit_attempt(db, session.session_id, STRONG)
    assert a1.evaluation.misconceptions, "weak answer should flag the misconception"
    assert not a2.evaluation.misconceptions, "strong answer resolves it"
    delta = a2.improvement.delta
    assert delta == a2.evaluation.understanding - a1.evaluation.understanding
    assert delta > 0
