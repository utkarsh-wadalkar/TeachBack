"""Curriculum hierarchy models.

These are intentionally generic entities — nothing here mentions DBMS or 3NF.
The hierarchy mirrors how Indian universities actually organise a syllabus:

    University -> Programme -> Pattern -> Semester -> Subject -> Unit -> Topic -> Concept

Each ``Concept`` carries the learning content plus the evaluation rubric that the
TeachBack engine needs: the concepts a good explanation is *expected* to cover,
the misconceptions we know students fall into, and the retrievable knowledge
chunks used for RAG. Adding a new concept/topic/subject is pure data entry.
"""

from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))

    programmes: Mapped[list["Programme"]] = relationship(
        back_populates="university", cascade="all, delete-orphan"
    )


class Programme(Base):
    __tablename__ = "programmes"

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))

    university: Mapped[University] = relationship(back_populates="programmes")
    patterns: Mapped[list["Pattern"]] = relationship(
        back_populates="programme", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("university_id", "code", name="uq_programme"),)


class Pattern(Base):
    """SPPU revises its syllabus in named "patterns" (e.g. 2019, 2024)."""

    __tablename__ = "patterns"

    id: Mapped[int] = mapped_column(primary_key=True)
    programme_id: Mapped[int] = mapped_column(ForeignKey("programmes.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))

    programme: Mapped[Programme] = relationship(back_populates="patterns")
    semesters: Mapped[list["Semester"]] = relationship(
        back_populates="pattern", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("programme_id", "code", name="uq_pattern"),)


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(primary_key=True)
    pattern_id: Mapped[int] = mapped_column(ForeignKey("patterns.id"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))

    pattern: Mapped[Pattern] = relationship(back_populates="semesters")
    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="semester", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("pattern_id", "number", name="uq_semester"),)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))

    semester: Mapped[Semester] = relationship(back_populates="subjects")
    units: Mapped[list["Unit"]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )
    pyqs: Mapped[list["Pyq"]] = relationship(  # noqa: F821
        back_populates="subject", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("semester_id", "code", name="uq_subject"),)


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))

    subject: Mapped[Subject] = relationship(back_populates="units")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan"
    )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer, default=0)

    unit: Mapped[Unit] = relationship(back_populates="topics")
    concepts: Mapped[list["Concept"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", order_by="Concept.order"
    )


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(Integer, default=0)
    # Whether the full TeachBack loop is available for this concept. In the MVP
    # only 3NF is enabled; the rest render as "coming soon" in the UI.
    teachback_enabled: Mapped[bool] = mapped_column(default=False)
    # Structured reading content: {"key_idea", "explanation", "example", "common_mistake"}
    learning: Mapped[dict] = mapped_column(JSON, default=dict)

    topic: Mapped[Topic] = relationship(back_populates="concepts")
    expected_concepts: Mapped[list["ExpectedConcept"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )
    misconceptions: Mapped[list["Misconception"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )
    knowledge_chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("topic_id", "code", name="uq_concept"),)


class ExpectedConcept(Base):
    """A sub-idea a strong explanation of the parent concept should contain.

    The ``keywords`` list is what the offline heuristic evaluator matches
    against; a real LLM reads ``label``/``description`` as rubric context.
    """

    __tablename__ = "expected_concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    key: Mapped[str] = mapped_column(String(64))
    label: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    weight: Mapped[float] = mapped_column(default=1.0)
    keywords: Mapped[list] = mapped_column(JSON, default=list)

    concept: Mapped[Concept] = relationship(back_populates="expected_concepts")


class Misconception(Base):
    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    code: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    why_it_matters: Mapped[str] = mapped_column(Text, default="")
    # Heuristic detection hints: phrases that suggest the student holds this
    # misconception, and the expected-concept key whose absence confirms it.
    trigger_keywords: Mapped[list] = mapped_column(JSON, default=list)
    resolved_when_key: Mapped[str] = mapped_column(String(64), default="")

    concept: Mapped[Concept] = relationship(back_populates="misconceptions")


class KnowledgeChunk(Base):
    """A retrievable snippet of authoritative knowledge for RAG."""

    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(255), default="")
    embedding: Mapped[list] = mapped_column(JSON, default=list)

    concept: Mapped[Concept] = relationship(back_populates="knowledge_chunks")
