"""Demo calibration — locks the numbers the hackathon demo depends on.

Every other test seeds a simplified rubric from ``conftest``. This one is
different: it runs the *real* ingestion (``scripts/load_data.py`` over
``knowledge/*.json``) and the *real* evaluation path, then asserts the exact
scores from the specification:

    attempt 1 → 72%  (78 / 64 / 58) + "2NF vs 3NF" misconception detected
    attempt 2 → 86%  (+14 points)   + that misconception resolved

The two explanations below are the answers to use when recording the demo. If a
rubric keyword or weight is edited and these numbers move, this test fails —
which is the point. It is a canary for the most-watched moment of the pitch, not
a check that the evaluator is "correct" in general.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from app.db.models import Concept, Session
from app.db.session import SessionLocal
from app.services import teachback_service

# --- The demo answers -------------------------------------------------------
# Attempt 1 covers functional dependency, candidate key, 2NF/partial
# dependencies, "non-key attribute", and a worked example — but never mentions
# transitive dependencies or prime/non-prime attributes. That combination is
# what makes it a believable *partial* understanding rather than a wrong one.
ATTEMPT_1 = (
    "Third Normal Form builds on 2NF. A relation is in 3NF when it is already in "
    "second normal form, so all partial dependencies have been removed, and every "
    "non-key attribute depends on the candidate key. We use functional "
    "dependencies to check which attributes determine others. For example, in a "
    "STUDENT table, StudentID determines Name and Department."
)

# Attempt 2 adds exactly one thing: transitive dependency, with a worked
# decomposition. Prime/non-prime is still missing, so the score lands at 86 and
# not 100 — an honest improvement, not a victory lap.
ATTEMPT_2 = (
    "Third Normal Form builds on 2NF, so the relation must already be in second "
    "normal form with all partial dependencies removed. Beyond that, a relation is "
    "in 3NF only if there are no transitive dependencies: a non-key attribute must "
    "not depend on another non-key attribute, only on the candidate key. We reason "
    "about this using functional dependencies. For example, in "
    "STUDENT(StudentID, Dept, DeptHead) where StudentID determines Dept and Dept "
    "determines DeptHead, DeptHead depends transitively on the key, so it is not "
    "in 3NF and must be decomposed."
)

_BACKEND = Path(__file__).resolve().parents[1]


def _load_real_knowledge() -> None:
    """Run scripts/load_data.py against the (temporary) test database.

    ``conftest`` repoints DATABASE_URL at a throwaway SQLite file before any app
    module is imported, so the loader's engine is already the test engine — this
    ingests the shipped JSON without touching the developer's teachback.db.
    """
    spec = importlib.util.spec_from_file_location(
        "_load_data", _BACKEND / "scripts" / "load_data.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


@pytest.fixture()
def seeded_3nf():
    """The 3NF concept, loaded from the real knowledge/ JSON files."""
    _load_real_knowledge()
    session = SessionLocal()
    try:
        yield session, session.query(Concept).filter(Concept.code == "3NF").one()
    finally:
        session.close()


def test_shipped_rubric_weights_sum_to_100(seeded_3nf):
    """``understanding`` is a percentage only because the weights total 100."""
    _, concept = seeded_3nf
    assert sum(ec.weight for ec in concept.expected_concepts) == 100


def test_demo_scores_72_then_86(seeded_3nf):
    db, concept = seeded_3nf
    session = teachback_service.start_session(db, concept.id)

    first = teachback_service.submit_attempt(db, session.session_id, ATTEMPT_1, "text")
    e1 = first.evaluation
    assert (e1.understanding, e1.conceptual_correctness, e1.completeness,
            e1.application_readiness) == (72, 78, 64, 58)
    assert [m.code for m in e1.misconceptions] == ["2nf_vs_3nf"]
    missing_1 = {p.key for p in e1.needs_attention}
    assert missing_1 == {"transitive_dependency", "non_prime_attribute"}
    # The follow-up must be the one the rubric keys to the *diagnosed* gap, not a
    # generic prompt. Comparing against the JSON proves targeting exactly.
    assert e1.followup_question == concept.learning["followups"]["transitive_dependency"]

    second = teachback_service.submit_attempt(db, session.session_id, ATTEMPT_2, "text")
    e2 = second.evaluation
    assert e2.understanding == 86
    # The diagnosis is retracted once the student demonstrates the missing idea.
    assert e2.misconceptions == []
    assert "transitive_dependency" in {p.key for p in e2.got_right}
    # Still not perfect — prime/non-prime remains uncovered.
    assert "non_prime_attribute" in {p.key for p in e2.needs_attention}

    assert second.improvement is not None
    assert second.improvement.previous_understanding == 72
    assert second.improvement.current_understanding == 86
    assert second.improvement.delta == 14
    # The headline sentence judges will read on screen.
    assert "+14 points" in second.improvement.message
    assert "transitive dependency" in second.improvement.message
    assert "misconception" in second.improvement.message.lower()


def test_both_attempts_share_one_session(seeded_3nf):
    """The improvement story only holds if attempt 2 is compared to attempt 1."""
    db, concept = seeded_3nf
    started = teachback_service.start_session(db, concept.id)
    first = teachback_service.submit_attempt(db, started.session_id, ATTEMPT_1, "text")
    second = teachback_service.submit_attempt(db, started.session_id, ATTEMPT_2, "text")
    assert first.attempt_number == 1
    assert second.attempt_number == 2

    # AttemptResponse deliberately carries no session_id, so verify the linkage
    # where it actually lives — in the database.
    row = db.get(Session, started.session_id)
    assert [a.attempt_number for a in row.attempts] == [1, 2]
    assert {a.session_id for a in row.attempts} == {started.session_id}
    # Mastery reflects the better of the two, not merely the latest.
    assert second.mastery.best_score == 86
