"""Curriculum service — reads the academic hierarchy and builds display trees.

All curriculum reads go through here so route handlers stay thin and the schema
navigation lives in one place.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.db.models import Concept, University
from app.db.models.session import DEMO_STUDENT
from app.schemas.curriculum import (
    Breadcrumb,
    ConceptNode,
    CurriculumTree,
    PatternNode,
    ProgrammeNode,
    SemesterNode,
    SubjectNode,
    TopicNode,
    UniversityNode,
    UnitNode,
)
from app.services import mastery_service


def get_concept(db: Session, concept_id: int) -> Concept:
    concept = db.get(Concept, concept_id)
    if concept is None:
        raise NotFoundError(f"Concept {concept_id} not found.")
    return concept


def build_tree(db: Session, student_key: str = DEMO_STUDENT) -> CurriculumTree:
    mastery = mastery_service.get_mastery_map(db, student_key)
    universities = db.query(University).order_by(University.id).all()

    def concept_node(c: Concept) -> ConceptNode:
        return ConceptNode(
            id=c.id,
            code=c.code,
            name=c.name,
            order=c.order,
            teachback_enabled=c.teachback_enabled,
            mastery=mastery.get(c.id),
        )

    tree = CurriculumTree(
        universities=[
            UniversityNode(
                id=u.id,
                code=u.code,
                name=u.name,
                programmes=[
                    ProgrammeNode(
                        id=p.id,
                        code=p.code,
                        name=p.name,
                        patterns=[
                            PatternNode(
                                id=pat.id,
                                code=pat.code,
                                name=pat.name,
                                semesters=[
                                    SemesterNode(
                                        id=s.id,
                                        number=s.number,
                                        name=s.name,
                                        subjects=[
                                            SubjectNode(
                                                id=sub.id,
                                                code=sub.code,
                                                name=sub.name,
                                                units=[
                                                    UnitNode(
                                                        id=un.id,
                                                        number=un.number,
                                                        name=un.name,
                                                        topics=[
                                                            TopicNode(
                                                                id=t.id,
                                                                code=t.code,
                                                                name=t.name,
                                                                concepts=[
                                                                    concept_node(c)
                                                                    for c in t.concepts
                                                                ],
                                                            )
                                                            for t in un.topics
                                                        ],
                                                    )
                                                    for un in sub.units
                                                ],
                                            )
                                            for sub in s.subjects
                                        ],
                                    )
                                    for s in pat.semesters
                                ],
                            )
                            for pat in p.patterns
                        ],
                    )
                    for p in u.programmes
                ],
            )
            for u in universities
        ]
    )
    return tree


def get_breadcrumb(concept: Concept) -> Breadcrumb:
    """Walk up the hierarchy from a concept to build a display-ready path."""
    topic = concept.topic
    unit = topic.unit
    subject = unit.subject
    semester = subject.semester
    pattern = semester.pattern
    programme = pattern.programme
    university = programme.university
    return Breadcrumb(
        university=university.name,
        programme=programme.name,
        pattern=pattern.name,
        semester=semester.name,
        subject=subject.name,
        unit=unit.name,
        topic=topic.name,
    )


def get_siblings(db: Session, concept: Concept, student_key: str = DEMO_STUDENT) -> list[ConceptNode]:
    mastery = mastery_service.get_mastery_map(db, student_key)
    return [
        ConceptNode(
            id=c.id,
            code=c.code,
            name=c.name,
            order=c.order,
            teachback_enabled=c.teachback_enabled,
            mastery=mastery.get(c.id),
        )
        for c in concept.topic.concepts
    ]
