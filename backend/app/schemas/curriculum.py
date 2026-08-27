"""Curriculum schemas — the academic hierarchy and per-concept learning content."""

from __future__ import annotations

from pydantic import BaseModel


class ConceptNode(BaseModel):
    id: int
    code: str
    name: str
    order: int
    teachback_enabled: bool
    mastery: int | None = None


class TopicNode(BaseModel):
    id: int
    code: str
    name: str
    concepts: list[ConceptNode]


class UnitNode(BaseModel):
    id: int
    number: int
    name: str
    topics: list[TopicNode]


class SubjectNode(BaseModel):
    id: int
    code: str
    name: str
    units: list[UnitNode]


class SemesterNode(BaseModel):
    id: int
    number: int
    name: str
    subjects: list[SubjectNode]


class PatternNode(BaseModel):
    id: int
    code: str
    name: str
    semesters: list[SemesterNode]


class ProgrammeNode(BaseModel):
    id: int
    code: str
    name: str
    patterns: list[PatternNode]


class UniversityNode(BaseModel):
    id: int
    code: str
    name: str
    programmes: list[ProgrammeNode]


class CurriculumTree(BaseModel):
    universities: list[UniversityNode]


class Breadcrumb(BaseModel):
    """Flat, display-ready path from university down to topic."""

    university: str
    programme: str
    pattern: str
    semester: str
    subject: str
    unit: str
    topic: str


class LearningContent(BaseModel):
    concept_id: int
    code: str
    name: str
    summary: str
    key_idea: str
    explanation: str
    example: str
    common_mistake: str
    teachback_enabled: bool
    breadcrumb: Breadcrumb
    mastery: int | None = None
    # Sibling concepts within the same topic, for the curriculum rail.
    siblings: list[ConceptNode] = []
