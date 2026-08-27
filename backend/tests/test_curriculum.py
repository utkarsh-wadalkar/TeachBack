"""Curriculum contract: 3NF must sit at SPPU → AI&DS → Sem IV → DBMS → Normalization."""

from __future__ import annotations

from app.schemas.curriculum import CurriculumTree
from app.services import curriculum_service, teachback_service
from tests.conftest import seed_curriculum


def test_3nf_breadcrumb_matches_syllabus_path(db) -> None:
    nf3 = seed_curriculum(db)
    crumb = curriculum_service.get_breadcrumb(nf3)
    assert crumb.university == "Savitribai Phule Pune University"
    assert crumb.programme == "B.E. Artificial Intelligence & Data Science"
    assert "Semester IV" in crumb.semester
    assert crumb.subject == "Database Management Systems"
    assert crumb.topic == "Normalization"


def test_only_3nf_has_teachback_enabled(db) -> None:
    topic = seed_curriculum(db).topic
    enabled = [c.code for c in topic.concepts if c.teachback_enabled]
    assert enabled == ["3NF"]


def test_teachback_on_disabled_concept_is_rejected(db) -> None:
    fd = next(c for c in seed_curriculum(db).topic.concepts if c.code == "FD")
    import pytest

    from app.core.errors import ConflictError

    with pytest.raises(ConflictError):
        teachback_service.start_session(db, fd.id)


def test_curriculum_tree_is_nested_and_ordered(db) -> None:
    nf3 = seed_curriculum(db)
    tree: CurriculumTree = curriculum_service.build_tree(db)
    university = tree.universities[0]
    programme = university.programmes[0]
    semester = programme.patterns[0].semesters[0]
    subject = semester.subjects[0]
    topic = subject.units[0].topics[0]
    assert university.code == "SPPU"
    assert [c.code for c in topic.concepts] == ["FD", "1NF", "2NF", "3NF", "BCNF", "DECOMP"]
    nf3_node = topic.concepts[3]
    assert nf3_node.teachback_enabled is True
    assert nf3_node.id == nf3.id
