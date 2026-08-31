import os
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_vercel_runtime_uses_writable_temporary_sqlite_database() -> None:
    env = {key: value for key, value in os.environ.items() if key != "DATABASE_URL"}
    env["VERCEL"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", "from app.core.config import settings; print(settings.database_url)"],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "sqlite:////tmp/teachback.db"
