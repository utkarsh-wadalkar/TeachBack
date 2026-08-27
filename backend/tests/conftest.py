"""Shared test fixtures.

The database URL is pointed at a throwaway SQLite file BEFORE any app module is
imported, so the whole stack (services, retriever, mock AI providers) runs
against one hermetic engine with no network access and no API keys.
"""

from __future__ import annotations

import os
import tempfile

# Must happen before importing anything under app.* — the engine is created at
# import time from settings.
_TEST_DIR = tempfile.mkdtemp(prefix="teachback-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DIR}/test.db"
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("STT_PROVIDER", "mock")
os.environ.setdefault("EMBEDDING_PROVIDER", "mock")

import pytest  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.models import (  # noqa: E402
    Concept,
    ConceptPyq,
    ExpectedConcept,
    KnowledgeChunk,
    Misconception,
    Pattern,
    Programme,
    Pyq,
    Semester,
    Subject,
    Topic,
    Unit,
    University,
)
from app.ai.embeddings import get_embedding_provider  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402


@pytest.fixture()
def db():
    """A fresh schema per test; yields a session and always closes it."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def seed_curriculum(db) -> Concept:
    """Seed the SPPU → AI&DS → Sem IV → DBMS → Normalization hierarchy.

    Mirrors the production shape of ``knowledge/`` data: six concepts under the
    Normalization topic, only 3NF TeachBack-enabled and carrying the full rubric,
    plus one PYQ linked to FD + 3NF. Returns the 3NF concept.
    """
    university = University(code="SPPU", name="Savitribai Phule Pune University")
    programme = Programme(code="BE-AIDS", name="B.E. Artificial Intelligence & Data Science")
    university.programmes.append(programme)
    pattern = Pattern(code="2019", name="2019 Pattern")
    programme.patterns.append(pattern)
    semester = Semester(number=4, name="Semester IV")
    pattern.semesters.append(semester)
    subject = Subject(code="DBMS", name="Database Management Systems")
    semester.subjects.append(subject)
    unit = Unit(number=3, name="Relational Database Design")
    subject.units.append(unit)
    topic = Topic(code="NORM", name="Normalization", order=1)
    unit.topics.append(topic)

    concepts: dict[str, Concept] = {}
    for i, code in enumerate(["FD", "1NF", "2NF", "3NF", "BCNF", "DECOMP"], start=1):
        concept = Concept(
            code=code,
            name={
                "FD": "Functional Dependency",
                "1NF": "First Normal Form",
                "2NF": "Second Normal Form",
                "3NF": "Third Normal Form",
                "BCNF": "Boyce–Codd Normal Form",
                "DECOMP": "Decomposition",
            }[code],
            order=i,
            teachback_enabled=(code == "3NF"),
        )
        topic.concepts.append(concept)
        concepts[code] = concept

    nf3 = concepts["3NF"]
    nf3.summary = (
        "A relation is in 3NF when it is in 2NF and no non-prime attribute is "
        "transitively dependent on any candidate key."
    )
    nf3.learning = {"key_idea": "No transitive dependencies."}
    for ec_d in [
        {
            "key": "functional_dependency",
            "label": "Functional dependency",
            "weight": 16,
            "description": "3NF is defined via functional dependencies.",
            "keywords": ["functional dependenc", "determines", "depends on"],
        },
        {
            "key": "candidate_key",
            "label": "Candidate key",
            "weight": 14,
            "description": "Judged relative to candidate keys.",
            "keywords": ["candidate key", "primary key"],
        },
        {
            "key": "builds_on_2nf",
            "label": "Builds on 2NF",
            "weight": 14,
            "description": "Must already be in 2NF.",
            "keywords": ["2nf", "second normal form"],
        },
        {
            "key": "definition_core",
            "label": "Non-key attributes depend on the key",
            "weight": 14,
            "description": "Non-key attributes determined by the key itself.",
            "keywords": ["non-key attribute"],
        },
        {
            "key": "transitive_dependency",
            "label": "No transitive dependencies",
            "weight": 14,
            "description": "No non-key -> non-key dependency chains.",
            "keywords": ["transitive"],
        },
        {
            "key": "non_prime_attribute",
            "label": "Prime vs non-prime attributes",
            "weight": 14,
            "description": "Formal definition uses prime/non-prime attributes.",
            "keywords": ["non-prime"],
        },
        {
            "key": "example_application",
            "label": "Concrete worked example",
            "weight": 14,
            "description": "Grounded in a concrete relation.",
            "keywords": ["for example"],
        },
    ]:
        nf3.expected_concepts.append(ExpectedConcept(**ec_d))

    nf3.misconceptions.append(
        Misconception(
            code="2nf_vs_3nf",
            title="Confusing 2NF with 3NF",
            description="Stops at partial-dependency removal (that is 2NF).",
            why_it_matters="3NF also forbids transitive dependencies.",
            trigger_keywords=["partial dependenc"],
            resolved_when_key="transitive_dependency",
        )
    )

    embedder = get_embedding_provider()
    chunk_texts = [
        ("Definition of 3NF", "R is in 3NF if for every non-trivial FD X -> A, X is a superkey or A is prime."),
        ("Transitive dependency", "A transitive dependency is a non-prime attribute depending on another non-prime attribute."),
    ]
    vectors = embedder.embed([f"{t}. {x}" for t, x in chunk_texts])
    for (title, text), vec in zip(chunk_texts, vectors):
        nf3.knowledge_chunks.append(
            KnowledgeChunk(title=title, text=text, source="Test source", embedding=vec)
        )

    pyq = Pyq(
        code="DBMS-NORM-2023-Q4",
        question="Explain Third Normal Form (3NF) with a suitable example.",
        marks=5,
        year="2023",
        source={
            "university": "SPPU",
            "subject": "Database Management Systems",
            "marks": 5,
            "year": "2023",
            "exam": "End Semester Examination",
        },
    )
    subject.pyqs.append(pyq)
    db.add(university)  # persisting the root cascades through the whole graph
    db.flush()  # assign ids before linking
    for code in ["FD", "3NF"]:
        pyq.concept_links.append(ConceptPyq(concept_id=concepts[code].id))

    db.commit()
    return concepts["3NF"]
