"""Create the database schema. Idempotent — safe to run repeatedly.

    python scripts/init_db.py

This only guarantees the tables exist. Seed *data* is loaded separately by
``scripts/load_data.py`` (data ingestion is kept out of the application code).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the backend package importable when run as a bare script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.db.models  # noqa: F401,E402  (registers every table on Base.metadata)
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print(f"Schema ready at {engine.url}")


if __name__ == "__main__":
    main()
