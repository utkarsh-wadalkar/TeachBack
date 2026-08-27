# Prompts

Versioned prompt templates, kept out of Python so they can be iterated on
independently. Rendered via `app/ai/prompt_loader.py`, which replaces
`{{TOKEN}}` placeholders (not `str.format`, so JSON braces need no escaping).

Every evaluation prompt embeds a machine-readable block:

```
<<<EVAL_INPUT_JSON
{ ...structured evaluation input... }
EVAL_INPUT_JSON>>>
```

A live LLM reads this as context. The offline `MockLLMProvider` parses the same
block to drive its deterministic heuristic — so both providers satisfy the
identical "prompt in, JSON out" contract.

## Active templates

| File | Used by | Output |
| --- | --- | --- |
| `evaluate_teachback.txt` | `evaluation_service.evaluate_explanation` | `EvaluationResult` JSON |
| `evaluate_pyq.txt` | `evaluation_service.evaluate_pyq` | `EvaluationResult` JSON |

The MVP folds the intervention and follow-up question INTO the evaluation output
(`targeted_explanation` and `followup_question`), so a single model call drives
the whole diagnostic.

## Reserved templates (post-MVP)

| File | Purpose |
| --- | --- |
| `generate_intervention.txt` | Standalone intervention when evaluation is split into multiple calls |
| `generate_followup.txt` | Standalone adaptive follow-up generation |

## Versioning

Treat prompts like code: change them in a commit with a clear message. When a
prompt's contract changes materially, copy it to `name.vN.txt` and update the
loader call, so old behaviour stays reproducible.
