"""Learning service — assembles the reading content for a concept."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.session import DEMO_STUDENT
from app.schemas.curriculum import LearningContent
from app.services import curriculum_service, mastery_service


def get_learning_content(
    db: Session, concept_id: int, student_key: str = DEMO_STUDENT
) -> LearningContent:
    concept = curriculum_service.get_concept(db, concept_id)
    learning = concept.learning or {}
    breadcrumb = curriculum_service.get_breadcrumb(concept)
    mastery = mastery_service.get_mastery(db, concept_id, student_key)
    siblings = curriculum_service.get_siblings(db, concept, student_key)

    return LearningContent(
        concept_id=concept.id,
        code=concept.code,
        name=concept.name,
        summary=concept.summary,
        key_idea=learning.get("key_idea", ""),
        explanation=learning.get("explanation", ""),
        example=learning.get("example", ""),
        common_mistake=learning.get("common_mistake", ""),
        teachback_enabled=concept.teachback_enabled,
        breadcrumb=breadcrumb,
        mastery=mastery.best_score if mastery else None,
        siblings=siblings,
    )
