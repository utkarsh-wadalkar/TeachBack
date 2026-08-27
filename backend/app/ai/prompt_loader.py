"""Loads and renders versioned prompt templates from ``ai/prompts/``.

Prompts are plain text files, not Python string literals, so they can be edited
and version-controlled independently of code. Rendering replaces ``{{TOKEN}}``
placeholders — deliberately not ``str.format`` so JSON braces inside a template
don't need escaping.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"


@lru_cache
def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def render_prompt(name: str, **tokens: str) -> str:
    text = load_prompt(name)
    for key, value in tokens.items():
        text = text.replace("{{" + key + "}}", value)
    return text
