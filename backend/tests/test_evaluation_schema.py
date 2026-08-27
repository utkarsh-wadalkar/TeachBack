"""The evaluation schema is the contract between AI output and the product.

Invalid model output must be rejected (spec §23) — never surfaced to a student
as a broken diagnostic.
"""

from __future__ import annotations

import json

import pytest

from app.schemas.evaluation import EvaluationResult

VALID = {
    "understanding": 72,
    "conceptual_correctness": 78,
    "completeness": 64,
    "application_readiness": 58,
    "got_right": [{"key": "functional_dependency", "label": "Functional dependency"}],
    "needs_attention": [],
    "misconceptions": [
        {
            "code": "2nf_vs_3nf",
            "title": "Confusing 2NF with 3NF",
            "description": "...",
            "why_it_matters": "...",
        }
    ],
    "targeted_explanation": "...",
    "followup_question": "...",
}


def test_valid_evaluation_parses() -> None:
    result = EvaluationResult.parse(json.dumps(VALID))
    assert result.understanding == 72
    assert result.got_right[0].key == "functional_dependency"
    assert result.misconceptions[0].code == "2nf_vs_3nf"


def test_markdown_fenced_json_is_accepted() -> None:
    fenced = f"```json\n{json.dumps(VALID)}\n```"
    assert EvaluationResult.parse(fenced).understanding == 72


@pytest.mark.parametrize("field", ["understanding", "conceptual_correctness", "completeness", "application_readiness"])
def test_out_of_range_scores_are_rejected(field: str) -> None:
    for bad in (-1, 101, 1000):
        payload = dict(VALID)
        payload[field] = bad
        with pytest.raises(ValueError):
            EvaluationResult.parse(json.dumps(payload))


def test_missing_required_field_is_rejected() -> None:
    payload = {k: v for k, v in VALID.items() if k != "completeness"}
    with pytest.raises(ValueError):
        EvaluationResult.parse(json.dumps(payload))


def test_non_json_output_is_rejected() -> None:
    with pytest.raises(ValueError):
        EvaluationResult.parse("I think the student did quite well overall!")
