"""PYQ service — lists previous-year questions and grades answers to them."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.db.models import Concept, Pyq
from app.schemas.pyq import PyqAttemptResponse, PyqOut
from app.services import evaluation_service


def _concepts_tested(db: Session, pyq: Pyq) -> list[Concept]:
    concept_ids = [link.concept_id for link in pyq.concept_links]
    if not concept_ids:
        return []
    concepts = db.query(Concept).filter(Concept.id.in_(concept_ids)).all()
    # Present in curriculum order (FD before 3NF …) rather than arbitrary PK order.
    return sorted(concepts, key=lambda c: c.order)


def _gradable_concept(concepts: list[Concept]) -> Concept:
    """Pick the concept whose rubric the answer should be graded against.

    A PYQ may be tagged with several concepts for display, but only some carry an
    evaluation rubric (expected concepts). Prefer a TeachBack-enabled concept with
    a rubric, then any concept with a rubric, then the first tagged concept.
    """
    for concept in concepts:
        if concept.teachback_enabled and concept.expected_concepts:
            return concept
    for concept in concepts:
        if concept.expected_concepts:
            return concept
    return concepts[0]


def list_for_concept(db: Session, concept_id: int) -> list[PyqOut]:
    concept = db.get(Concept, concept_id)
    if concept is None:
        raise NotFoundError(f"Concept {concept_id} not found.")
    pyqs = (
        db.query(Pyq)
        .join(Pyq.concept_links)
        .filter_by(concept_id=concept_id)
        .order_by(Pyq.id)
        .all()
    )
    out: list[PyqOut] = []
    for pyq in pyqs:
        out.append(
            PyqOut(
                id=pyq.id,
                code=pyq.code,
                question=pyq.question,
                marks=pyq.marks,
                year=pyq.year,
                source=pyq.source,
                concepts_tested=[c.name for c in _concepts_tested(db, pyq)],
            )
        )
    return out


def get_pyq(db: Session, pyq_id: int) -> Pyq:
    pyq = db.get(Pyq, pyq_id)
    if pyq is None:
        raise NotFoundError(f"PYQ {pyq_id} not found.")
    return pyq


def get_pyq_out(db: Session, pyq_id: int) -> PyqOut:
    """A single PYQ, display-ready — used by the exam page for deep links."""
    pyq = get_pyq(db, pyq_id)
    return PyqOut(
        id=pyq.id,
        code=pyq.code,
        question=pyq.question,
        marks=pyq.marks,
        year=pyq.year,
        source=pyq.source,
        concepts_tested=[c.name for c in _concepts_tested(db, pyq)],
    )


def evaluate(db: Session, pyq_id: int, response_text: str) -> PyqAttemptResponse:
    pyq = get_pyq(db, pyq_id)
    concepts = _concepts_tested(db, pyq)
    if not concepts:
        raise NotFoundError(f"PYQ {pyq_id} has no linked concept to evaluate against.")
    # Grade against the concept that actually carries a rubric.
    concept = _gradable_concept(concepts)
    result = evaluation_service.evaluate_pyq(db, pyq, concept, response_text)
    return PyqAttemptResponse(pyq_id=pyq.id, evaluation=result)
