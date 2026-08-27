"""Learning-session models: the record of a student proving understanding.

    Session (one concept, one sitting)
      └── Attempt (attempt_number 1, 2, ...)
            └── Evaluation (the diagnostic report for that attempt)

    Mastery (latest score per student+concept, updated after each evaluation)

There is no ``students`` table in the MVP; a single demo learner is represented
by the ``student_key`` string ("demo"), which makes multi-user trivial to add
later without a migration to existing rows.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utcnow

DEMO_STUDENT = "demo"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_key: Mapped[str] = mapped_column(String(64), default=DEMO_STUDENT, index=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    concept: Mapped["Concept"] = relationship()  # noqa: F821
    attempts: Mapped[list["Attempt"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Attempt.attempt_number",
    )


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    attempt_number: Mapped[int] = mapped_column(Integer)
    modality: Mapped[str] = mapped_column(String(16), default="text")  # "text" | "audio"
    response_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    session: Mapped[Session] = relationship(back_populates="attempts")
    evaluation: Mapped["Evaluation"] = relationship(
        back_populates="attempt", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("session_id", "attempt_number", name="uq_attempt_number"),
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("attempts.id"), index=True)

    understanding: Mapped[int] = mapped_column(Integer)
    conceptual_correctness: Mapped[int] = mapped_column(Integer)
    completeness: Mapped[int] = mapped_column(Integer)
    application_readiness: Mapped[int] = mapped_column(Integer)

    got_right: Mapped[list] = mapped_column(JSON, default=list)
    needs_attention: Mapped[list] = mapped_column(JSON, default=list)
    misconceptions: Mapped[list] = mapped_column(JSON, default=list)
    targeted_explanation: Mapped[str] = mapped_column(Text, default="")
    followup_question: Mapped[str] = mapped_column(Text, default="")

    provider: Mapped[str] = mapped_column(String(32), default="")
    raw: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    attempt: Mapped[Attempt] = relationship(back_populates="evaluation")


class Mastery(Base):
    __tablename__ = "mastery"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_key: Mapped[str] = mapped_column(String(64), default=DEMO_STUDENT, index=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    best_score: Mapped[int] = mapped_column(Integer, default=0)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("student_key", "concept_id", name="uq_mastery"),
    )
