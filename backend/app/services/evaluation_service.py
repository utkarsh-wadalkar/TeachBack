"""Evaluation service — the TeachBack diagnostic engine.

Responsibilities:
  1. Assemble the structured evaluation input (curriculum context, concept
     definition, expected concepts, misconceptions, retrieved knowledge, student
     response).
  2. Render the versioned prompt.
  3. Call the configured LLM provider.
  4. Validate the output against the strict ``EvaluationResult`` schema.

It depends only on the AI abstractions and never on a concrete provider, so the
same code path serves the live Sarvam model and the offline mock.
"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.ai import KnowledgeRetriever, build_retriever, get_llm_provider
from app.ai.base import LLMProvider
from app.ai.prompt_loader import render_prompt
from app.db.models import Concept, Pyq
from app.db.session import SessionLocal
from app.schemas.evaluation import EvaluationResult
from app.services import curriculum_service


def _concept_payload(concept: Concept) -> dict:
    learning = concept.learning or {}
    return {
        "code": concept.code,
        "name": concept.name,
        "definition": concept.summary or learning.get("key_idea", ""),
    }


def _expected_payload(concept: Concept) -> list[dict]:
    return [
        {
            "key": ec.key,
            "label": ec.label,
            "description": ec.description,
            "weight": ec.weight,
            "keywords": ec.keywords,
        }
        for ec in concept.expected_concepts
    ]


def _misconceptions_payload(concept: Concept) -> list[dict]:
    return [
        {
            "code": m.code,
            "title": m.title,
            "description": m.description,
            "why_it_matters": m.why_it_matters,
            "trigger_keywords": m.trigger_keywords,
            "resolved_when_key": m.resolved_when_key,
        }
        for m in concept.misconceptions
    ]


def _build_payload(
    concept: Concept, response_text: str, retriever: KnowledgeRetriever, *, question: str = ""
) -> dict:
    breadcrumb = curriculum_service.get_breadcrumb(concept)
    retrieved = retriever.retrieve(concept.id, question or response_text, k=3)
    learning = concept.learning or {}
    payload: dict = {
        "curriculum": {
            "university": breadcrumb.university,
            "subject": breadcrumb.subject,
            "topic": breadcrumb.topic,
        },
        "concept": _concept_payload(concept),
        "expected_concepts": _expected_payload(concept),
        "misconceptions": _misconceptions_payload(concept),
        "retrieved_knowledge": [
            {"title": r.title, "text": r.text, "source": r.source} for r in retrieved
        ],
        "response": response_text,
        "followups": learning.get("followups", {}),
        "default_followup": learning.get("default_followup", ""),
    }
    if question:
        payload["question"] = question
    return payload


def _run(prompt_name: str, payload: dict, llm: LLMProvider) -> EvaluationResult:
    prompt = render_prompt(
        prompt_name, EVAL_INPUT_JSON=json.dumps(payload, ensure_ascii=False, indent=2)
    )
    raw = llm.complete(prompt)
    # ``parse`` raises ValueError on malformed/invalid output; that surfaces as a
    # 500 rather than showing a student a broken diagnostic.
    return EvaluationResult.parse(raw)


def evaluate_explanation(
    db: Session,
    concept: Concept,
    response_text: str,
    *,
    llm: LLMProvider | None = None,
    retriever: KnowledgeRetriever | None = None,
) -> EvaluationResult:
    llm = llm or get_llm_provider()
    retriever = retriever or build_retriever(SessionLocal)
    payload = _build_payload(concept, response_text, retriever)
    return _run("evaluate_teachback.txt", payload, llm)


def evaluate_pyq(
    db: Session,
    pyq: Pyq,
    concept: Concept,
    response_text: str,
    *,
    llm: LLMProvider | None = None,
    retriever: KnowledgeRetriever | None = None,
) -> EvaluationResult:
    llm = llm or get_llm_provider()
    retriever = retriever or build_retriever(SessionLocal)
    payload = _build_payload(concept, response_text, retriever, question=pyq.question)
    return _run("evaluate_pyq.txt", payload, llm)
