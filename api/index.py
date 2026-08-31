"""Vercel ASGI entrypoint for TeachBack's same-origin demo API."""

from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

__all__ = ["app"]
