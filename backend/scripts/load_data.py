"""Load curriculum, concept, and PYQ seed data from ``backend/knowledge``.

    python scripts/load_data.py

Data lives as JSON, deliberately separate from the application code — adding a
new subject, concept, or PYQ is pure data entry, no code changes. Every JSON
file under ``knowledge/{curriculum,concepts,pyqs}`` is picked up automatically.

Running this performs a clean reset: it drops and recreates all tables, loads
the hierarchy, attaches concept rubrics, computes knowledge-chunk embeddings via
the configured embedding provider, and links PYQs to the concepts they test.
Student-progress tables are reset too, so demos always start from zero.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make the backend package importable when run as a bare script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.db.models  # noqa: F401,E402  (registers every table on Base.metadata)
from app.ai.embeddings import get_embedding_provider  # noqa: E402
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
from app.db.session import SessionLocal, engine  # noqa: E402

KNOWLEDGE = Path(__file__).resolve().parents[1] / "knowledge"


def _load_json_dir(subdir: str) -> list[dict]:
    directory = KNOWLEDGE / subdir
    files = sorted(directory.glob("*.json")) if directory.exists() else []
    return [json.loads(path.read_text(encoding="utf-8")) for path in files]


def _load_curriculum(
    db,
    data: dict,
    subjects_by_code: dict[str, Subject],
    concepts_by_subject: dict[str, dict[str, Concept]],
) -> None:
    university = University(code=data["university"]["code"], name=data["university"]["name"])
    programme = Programme(code=data["programme"]["code"], name=data["programme"]["name"])
    university.programmes.append(programme)
    pattern = Pattern(code=data["pattern"]["code"], name=data["pattern"]["name"])
    programme.patterns.append(pattern)
    semester = Semester(number=data["semester"]["number"], name=data["semester"]["name"])
    pattern.semesters.append(semester)

    for subject_d in data["subjects"]:
        subject = Subject(code=subject_d["code"], name=subject_d["name"])
        semester.subjects.append(subject)
        subjects_by_code[subject.code] = subject
        concepts_by_subject.setdefault(subject.code, {})
        for unit_d in subject_d["units"]:
            unit = Unit(number=unit_d["number"], name=unit_d["name"])
            subject.units.append(unit)
            for topic_d in unit_d["topics"]:
                topic = Topic(
                    code=topic_d["code"], name=topic_d["name"], order=topic_d.get("order", 0)
                )
                unit.topics.append(topic)
                for concept_d in topic_d["concepts"]:
                    concept = Concept(
                        code=concept_d["code"],
                        name=concept_d["name"],
                        order=concept_d.get("order", 0),
                        teachback_enabled=concept_d.get("teachback_enabled", False),
                    )
                    topic.concepts.append(concept)
                    concepts_by_subject[subject.code][concept.code] = concept

    db.add(university)
    db.flush()


def _load_concept_content(
    db, data: dict, concepts_by_subject: dict[str, dict[str, Concept]], embedder
) -> int:
    subject_code = data["subject"]
    concept_map = concepts_by_subject.get(subject_code, {})
    chunk_count = 0

    for code, content in data.get("concepts", {}).items():
        concept = concept_map.get(code)
        if concept is None:
            print(f"  ! skipping content for unknown concept {subject_code}/{code}")
            continue

        concept.summary = content.get("summary", "")
        concept.learning = content.get("learning", {})

        for ec in content.get("expected_concepts", []):
            concept.expected_concepts.append(
                ExpectedConcept(
                    key=ec["key"],
                    label=ec["label"],
                    description=ec.get("description", ""),
                    weight=float(ec.get("weight", 1.0)),
                    keywords=ec.get("keywords", []),
                )
            )

        for m in content.get("misconceptions", []):
            concept.misconceptions.append(
                Misconception(
                    code=m["code"],
                    title=m["title"],
                    description=m["description"],
                    why_it_matters=m.get("why_it_matters", ""),
                    trigger_keywords=m.get("trigger_keywords", []),
                    resolved_when_key=m.get("resolved_when_key", ""),
                )
            )

        chunks = content.get("knowledge_chunks", [])
        if chunks:
            # Embed title + text together so retrieval keys on both.
            vectors = embedder.embed(
                [f"{c.get('title', '')}. {c['text']}".strip() for c in chunks]
            )
            for chunk_d, vector in zip(chunks, vectors):
                concept.knowledge_chunks.append(
                    KnowledgeChunk(
                        title=chunk_d.get("title", ""),
                        text=chunk_d["text"],
                        source=chunk_d.get("source", ""),
                        embedding=vector,
                    )
                )
            chunk_count += len(chunks)

    db.flush()
    return chunk_count


def _load_pyqs(
    db,
    data: dict,
    subjects_by_code: dict[str, Subject],
    concepts_by_subject: dict[str, dict[str, Concept]],
) -> int:
    subject_code = data["subject"]
    subject = subjects_by_code.get(subject_code)
    if subject is None:
        print(f"  ! skipping PYQs for unknown subject {subject_code}")
        return 0
    concept_map = concepts_by_subject.get(subject_code, {})

    count = 0
    for pyq_d in data.get("pyqs", []):
        pyq = Pyq(
            code=pyq_d["code"],
            question=pyq_d["question"],
            marks=pyq_d.get("marks", 5),
            year=pyq_d.get("year", ""),
            source=pyq_d.get("source", {}),
        )
        subject.pyqs.append(pyq)
        db.flush()  # assign pyq.id before creating association rows
        for concept_code in pyq_d.get("concepts", []):
            concept = concept_map.get(concept_code)
            if concept is None:
                print(f"  ! PYQ {pyq.code} references unknown concept {concept_code}")
                continue
            pyq.concept_links.append(ConceptPyq(concept_id=concept.id))
        count += 1

    db.flush()
    return count


def main() -> None:
    print(f"Resetting schema at {engine.url}")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    embedder = get_embedding_provider()
    subjects_by_code: dict[str, Subject] = {}
    concepts_by_subject: dict[str, dict[str, Concept]] = {}

    db = SessionLocal()
    try:
        curriculum_files = _load_json_dir("curriculum")
        for data in curriculum_files:
            _load_curriculum(db, data, subjects_by_code, concepts_by_subject)
        concept_count = sum(len(m) for m in concepts_by_subject.values())
        print(f"Loaded {len(curriculum_files)} curriculum file(s), {concept_count} concept(s)")

        chunk_total = 0
        for data in _load_json_dir("concepts"):
            chunk_total += _load_concept_content(db, data, concepts_by_subject, embedder)
        print(f"Attached concept rubrics and {chunk_total} knowledge chunk(s)")

        pyq_total = 0
        for data in _load_json_dir("pyqs"):
            pyq_total += _load_pyqs(db, data, subjects_by_code, concepts_by_subject)
        print(f"Loaded {pyq_total} PYQ(s)")

        db.commit()
        print("Done. Seed data committed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
