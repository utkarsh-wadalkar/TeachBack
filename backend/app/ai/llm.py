"""LLM adapters.

``SarvamProvider`` calls Sarvam AI's chat-completions endpoint. ``MockLLMProvider``
is a fully offline, deterministic evaluator: it reads the same structured
``EVAL_INPUT_JSON`` block the real model reads, matches the student's explanation
against the concept's expected-concept keywords, detects misconceptions, and
emits schema-valid evaluation JSON. That means the entire TeachBack loop runs —
and identifies genuine gaps — with no API keys at all.

Both adapters honour the identical contract: prompt string in, JSON string out.
The evaluation engine cannot tell them apart.
"""

from __future__ import annotations

import json
import re

import httpx

from app.ai.base import LLMProvider
from app.core.config import settings

# Delimited machine-readable payload embedded in every evaluation prompt. A real
# LLM reads it as context; the mock parses it to drive its heuristic.
_INPUT_RE = re.compile(r"<<<EVAL_INPUT_JSON\s*(.*?)\s*EVAL_INPUT_JSON>>>", re.DOTALL)


def _clamp(value: float, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, round(value)))


def heuristic_evaluate(payload: dict) -> dict:
    """Rule-based evaluation of an explanation against a concept rubric.

    ``payload`` is the structured evaluation input (see EvaluationInput). Returns
    a dict conforming to ``EvaluationResult``. Scoring is weighted keyword
    coverage: each expected concept carries a point value, ``understanding`` is
    the fraction of points earned, and the sub-scores are believable, correlated
    offsets. It is deterministic, so demos are reproducible.
    """
    response = (payload.get("response") or "").lower()
    expected = payload.get("expected_concepts", [])
    misconceptions = payload.get("misconceptions", [])

    total_weight = sum(float(ec.get("weight", 1.0)) for ec in expected) or 1.0
    matched, missing = [], []
    matched_keys: set[str] = set()
    earned = 0.0

    for ec in expected:
        keywords = [k.lower() for k in ec.get("keywords", [])]
        hit = any(kw and kw in response for kw in keywords)
        point = {"key": ec.get("key", ""), "label": ec.get("label", "")}
        if hit:
            matched.append(point)
            matched_keys.add(ec.get("key", ""))
            earned += float(ec.get("weight", 1.0))
        else:
            missing.append(point)

    coverage = earned / total_weight
    understanding = _clamp(coverage * 100)

    # Sub-scores: correlated, plausible views of the same performance. A live LLM
    # would produce these independently; the mock derives them so the headline
    # number and its breakdown stay coherent.
    conceptual_correctness = _clamp(understanding + 6)
    completeness = _clamp(understanding - 8)
    application_readiness = _clamp(understanding - 14)

    detected = []
    for m in misconceptions:
        triggers = [k.lower() for k in m.get("trigger_keywords", [])]
        triggered = any(t and t in response for t in triggers)
        resolved_key = m.get("resolved_when_key", "")
        resolved = bool(resolved_key) and resolved_key in matched_keys
        if triggered and not resolved:
            detected.append(
                {
                    "code": m.get("code", ""),
                    "title": m.get("title", ""),
                    "description": m.get("description", ""),
                    "why_it_matters": m.get("why_it_matters", ""),
                }
            )

    # Targeted explanation: teach the single most important gap. Prefer a
    # detected misconception, otherwise the highest-weight missing concept.
    targeted_explanation = ""
    top_missing_key = ""
    if detected:
        m = detected[0]
        targeted_explanation = f"{m['description']} {m['why_it_matters']}".strip()
        top_missing_key = misconceptions[0].get("resolved_when_key", "") if misconceptions else ""
    elif missing:
        top = max(
            (ec for ec in expected if ec.get("key") in {p["key"] for p in missing}),
            key=lambda ec: float(ec.get("weight", 1.0)),
            default=None,
        )
        if top:
            top_missing_key = top.get("key", "")
            targeted_explanation = top.get("description", "")

    followups = payload.get("followups", {}) or {}
    followup_question = followups.get(top_missing_key) or payload.get("default_followup", "")

    return {
        "understanding": understanding,
        "conceptual_correctness": conceptual_correctness,
        "completeness": completeness,
        "application_readiness": application_readiness,
        "got_right": matched,
        "needs_attention": missing,
        "misconceptions": detected,
        "targeted_explanation": targeted_explanation,
        "followup_question": followup_question,
    }


def _extract_payload(prompt: str) -> dict | None:
    match = _INPUT_RE.search(prompt)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


class MockLLMProvider(LLMProvider):
    """Offline, deterministic provider. Runs the heuristic over the prompt's
    embedded evaluation input."""

    name = "mock"

    def complete(self, prompt: str) -> str:
        payload = _extract_payload(prompt)
        if payload is None:
            # Not an evaluation prompt — return a minimal valid evaluation so the
            # caller's schema validation still succeeds.
            return json.dumps(
                {
                    "understanding": 0,
                    "conceptual_correctness": 0,
                    "completeness": 0,
                    "application_readiness": 0,
                    "got_right": [],
                    "needs_attention": [],
                    "misconceptions": [],
                    "targeted_explanation": "",
                    "followup_question": "",
                }
            )
        return json.dumps(heuristic_evaluate(payload))


class SarvamProvider(LLMProvider):
    """Adapter for Sarvam AI's chat-completions API.

    Endpoint/field names follow Sarvam's documented chat API; if their contract
    changes, only this adapter needs updating. Used whenever LLM_PROVIDER=sarvam
    and a key is present.
    """

    name = "sarvam"

    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.base_url = settings.llm_base_url.rstrip("/")

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is not set; cannot use the Sarvam provider.")
        resp = httpx.post(
            f"{self.base_url}/v1/chat/completions",
            headers={
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a strict examiner. Respond with a single JSON "
                            "object and nothing else."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def get_llm_provider() -> LLMProvider:
    """Factory selecting the LLM adapter from configuration."""
    provider = settings.llm_provider.lower()
    if provider == "sarvam" and settings.llm_api_key:
        return SarvamProvider()
    # Fall back to the mock when explicitly requested OR when Sarvam is selected
    # without a key, so the app never hard-fails for want of credentials.
    return MockLLMProvider()
