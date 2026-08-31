import os
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEMO_DB = BACKEND_DIR / "tests" / "vercel-demo.db"


def test_vercel_runtime_seeds_the_bundled_curriculum() -> None:
    DEMO_DB.unlink(missing_ok=True)
    env = {key: value for key, value in os.environ.items() if key != "DATABASE_URL"}
    env.update({"VERCEL": "1", "DATABASE_URL": "sqlite:///./tests/vercel-demo.db"})
    script = """
from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    response = client.get('/api/curriculum')
    print(response.status_code)
    print(len(response.json()['universities']))
"""

    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=BACKEND_DIR,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        DEMO_DB.unlink(missing_ok=True)

    assert result.stdout.strip().endswith("200\n1")
