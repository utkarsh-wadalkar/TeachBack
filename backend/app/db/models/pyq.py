"""Previous-year question (PYQ) models.

PYQs live at the subject level and are linked to the concepts they test via a
many-to-many association. Every PYQ carries structured ``source`` metadata so
the UI can render an authentic exam header (university, subject, marks, year).
"""

from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Pyq(Base):
    __tablename__ = "pyqs"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    question: Mapped[str] = mapped_column(Text)
    marks: Mapped[int] = mapped_column(Integer, default=5)
    year: Mapped[str] = mapped_column(String(16), default="")
    # {"university", "subject", "marks", "year", "exam"}
    source: Mapped[dict] = mapped_column(JSON, default=dict)

    subject: Mapped["Subject"] = relationship(back_populates="pyqs")  # noqa: F821
    concept_links: Mapped[list["ConceptPyq"]] = relationship(
        back_populates="pyq", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("subject_id", "code", name="uq_pyq"),)


class ConceptPyq(Base):
    """Association between a concept and a PYQ (the concepts a question tests)."""

    __tablename__ = "concept_pyqs"

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    pyq_id: Mapped[int] = mapped_column(ForeignKey("pyqs.id"), index=True)

    pyq: Mapped[Pyq] = relationship(back_populates="concept_links")

    __table_args__ = (UniqueConstraint("concept_id", "pyq_id", name="uq_concept_pyq"),)
