"""PYQ contract: previous-year questions carry authentic exam metadata, are
linked to the concepts they test, and are graded against a rubric-bearing
concept — not just whichever concept happens to sort first."""

from __future__ import annotations

from app.schemas.pyq import PyqAttemptRequest
from app.services import pyq_service, teachback_service
from tests.conftest import seed_curriculum

STRONG_3NF_ANSWER = (
    "3NF builds on 2NF: partial dependencies are gone, and there must be no "
    "transitive dependencies either. For example, if StudentID -> Dept and "
    "Dept -> DeptHead, DeptHead depends transitively on the candidate key."
)


def test_pyq_has_valid_source_metadata(db) -> None:
    nf3 = seed_curriculum(db)
    pyqs = pyq_service.list_for_concept(db, nf3.id)
    assert len(pyqs) == 1

    source = pyqs[0].source
    for key in ("university", "subject", "marks", "year", "exam"):
        assert key in source and source[key], f"source.{key} must be present"
    assert source["university"] == "SPPU"
    assert pyqs[0].marks == 5
    assert "3NF" in pyqs[0].question


def test_concepts_tested_lists_linked_concepts(db) -> None:
    nf3 = seed_curriculum(db)
    pyqs = pyq_service.list_for_concept(db, nf3.id)
    assert set(pyqs[0].concepts_tested) == {"Functional Dependency", "Third Normal Form"}


def test_evaluation_targets_the_rubric_bearing_concept(db) -> None:
    """The PYQ is linked to FD (no rubric) AND 3NF (rubric). Grading must use 3NF.

    The strong answer covers transitive dependency — a 3NF-only point — so a
    non-zero understanding proves the right rubric was applied.
    """
    nf3 = seed_curriculum(db)
    pyqs = pyq_service.list_for_concept(db, nf3.id)

    body = PyqAttemptRequest(response_text=STRONG_3NF_ANSWER)
    result = pyq_service.evaluate(db, pyqs[0].id, body.response_text)

    assert result.pyq_id == pyqs[0].id
    assert result.evaluation.understanding > 50
    keys = {p.key for p in result.evaluation.got_right}
    assert "transitive_dependency" in keys


def test_attempting_a_rubric_less_answer_scores_low(db) -> None:
    nf3 = seed_curriculum(db)
    pyqs = pyq_service.list_for_concept(db, nf3.id)

    result = pyq_service.evaluate(
        db, pyqs[0].id, "Third normal form is a database thing about tables."
    )
    assert result.evaluation.understanding <= 20


def test_unknown_pyq_is_not_found(db) -> None:
    import pytest

    from app.core.errors import NotFoundError

    seed_curriculum(db)
    with pytest.raises(NotFoundError):
        pyq_service.evaluate(db, 99999, "anything")
