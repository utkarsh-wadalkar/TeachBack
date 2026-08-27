"""ORM models. Importing this package registers every table on ``Base.metadata``."""

from app.db.models.curriculum import (
    Concept,
    ExpectedConcept,
    KnowledgeChunk,
    Misconception,
    Pattern,
    Programme,
    Semester,
    Subject,
    Topic,
    Unit,
    University,
)
from app.db.models.pyq import ConceptPyq, Pyq
from app.db.models.session import DEMO_STUDENT, Attempt, Evaluation, Mastery, Session

__all__ = [
    "University",
    "Programme",
    "Pattern",
    "Semester",
    "Subject",
    "Unit",
    "Topic",
    "Concept",
    "ExpectedConcept",
    "Misconception",
    "KnowledgeChunk",
    "Pyq",
    "ConceptPyq",
    "Session",
    "Attempt",
    "Evaluation",
    "Mastery",
    "DEMO_STUDENT",
]
