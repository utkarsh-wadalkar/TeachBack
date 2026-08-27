# TeachBack — AI That Knows Whether You Actually Understand

Most AI tutors explain. TeachBack flips the direction: **you explain, and the AI
determines whether you genuinely understand.** Read a concept, explain it back in
your own words (typed or spoken), and get a diagnostic — not a chat reply:

- an **understanding score** with a breakdown (conceptual correctness,
  completeness, application readiness),
- exactly which expected ideas you covered and which you missed,
- **misconception detection** ("you're treating 2NF as sufficient for 3NF"),
- a targeted explanation for your specific gap, then a follow-up question
  built on it — closing the loop: **Learn → Explain → Evaluate → Correct → Apply**.

Built for SPPU's B.E. AI & Data Science curriculum, scoped deliberately narrow:
**Semester IV · DBMS · Normalization · 3NF** gets the full loop.

---

## 2. Architecture

```
┌─────────────────────────────┐        ┌──────────────────────────────────────────┐
│  frontend/  (React + Vite)  │  /api  │  backend/app  (FastAPI)                  │
│                             │ ─────► │                                          │
│  pages/                     │ proxy  │  api/        thin routes                 │
│    Curriculum · Learning    │        │      ▼                                   │
│    TeachBack (hero) · PYQ   │        │  services/   business logic              │
│                             │        │    teachback · evaluation                │
│  components/ design system  │        │    curriculum · learning · mastery · pyq │
│    Button · ScoreCard       │        │      ▼                                   │
│    MisconceptionCard …      │        │  ai/         provider abstractions       │
│                             │        │    LLMProvider ── SarvamProvider         │
└─────────────────────────────┘        │                 └ MockLLMProvider        │
                                       │    STTProvider ── SarvamSTTProvider      │
                                       │                 └ MockSTTProvider        │
                                       │    EmbeddingProvider ── (mock | multil.) │
                                       │    KnowledgeRetriever ── LocalRetriever  │
                                       │    prompts/  versioned .txt templates    │
                                       │      ▼                                   │
                                       │  db/  SQLAlchemy models                  │
                                       │    universities → programmes → patterns  │
                                       │    → semesters → subjects → units        │
                                       │    → topics → concepts                   │
                                       │    sessions → attempts → evaluations     │
                                       │    mastery · pyqs ↔ concept_pyqs         │
                                       └───────────────┬──────────────────────────┘
                                                       │ load scripts
                                       ┌───────────────▼──────────────────────────┐
                                       │  backend/knowledge/   (seed data, JSON)  │
                                       │    curriculum/  syllabus hierarchy       │
                                       │    concepts/    rubrics + RAG chunks     │
                                       │    pyqs/        previous-year questions  │
                                       └──────────────────────────────────────────┘
```

Key architectural decisions:

- **Provider abstraction.** The evaluator never talks to an HTTP client; it calls
  `LLMProvider.complete(prompt)`. Swapping Sarvam for another model is one adapter.
  `MockLLMProvider` runs the full loop offline with **no API keys**, deterministically.
- **Prompts are data.** Evaluation prompts live in `ai/prompts/*.txt`, versioned;
  the structured evaluation input is embedded in each prompt as JSON.
- **RAG stays behind an interface.** The evaluator receives `RetrievedKnowledge[]`
  and doesn't know whether chunks came from the local vector store or Qdrant.
- **Generic entities.** No `dbms_3nf_*` tables anywhere. Tomorrow the same schema
  holds thousands of concepts from any university.
- **Data ingestion is separate.** Syllabus/rubric/PYQ content lives in
  `backend/knowledge/*.json`; `scripts/load_data.py` ingests it. Adding a subject
  is data entry, not code.

## 3. MVP scope

| Layer    | Contents                                                                 |
| -------- | ------------------------------------------------------------------------ |
| Path     | SPPU → B.E. AI&DS → Semester IV → DBMS → Normalization → **3NF**          |
| Full loop| 3NF only (`teachback_enabled`); sibling concepts are readable "coming soon" |
| PYQs     | Two real-format SPPU end-semester questions linked to 3NF                |
| Audio    | Record answer → speech-to-text → same evaluation pipeline                |

## 4. Setup

Prerequisites: **Python 3.12+** and **Node 18+**.

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      # Windows
# .venv/bin/pip install -r requirements.txt        # macOS/Linux

cd ../frontend
npm install
```

## 5. Environment variables

Copy `backend/.env.example` to `backend/.env` and edit. Defaults run the whole
demo offline (mock providers, SQLite):

| Variable             | Purpose                                        | Default            |
| -------------------- | ---------------------------------------------- | ------------------ |
| `DATABASE_URL`       | Any SQLAlchemy URL                              | `sqlite:///./teachback.db` |
| `LLM_PROVIDER`       | `mock` \| `sarvam`                              | `mock`             |
| `LLM_API_KEY`        | Sarvam key (only when provider = sarvam)        | *(empty)*          |
| `LLM_MODEL`          | Chat model name                                 | `sarvam-m`         |
| `STT_PROVIDER`       | `mock` \| `sarvam`                              | `mock`             |
| `STT_API_KEY`        | Sarvam STT key                                  | *(empty)*          |
| `EMBEDDING_PROVIDER` | `mock` \| `multilingual`                        | `mock`             |
| `RETRIEVER_BACKEND`  | `local` \| `qdrant`                             | `local`            |
| `QDRANT_URL` / `QDRANT_API_KEY` | Only when retriever = qdrant         | *(empty)*          |
| `CORS_ORIGINS`       | Comma-separated allowed origins                 | Vite dev origins   |

Credentials are never hard-coded; everything flows through `.env`.

## 6. Running locally

```bash
# terminal 1
cd backend
.venv\Scripts\python -m uvicorn app.main:app --port 8000

# terminal 2
cd frontend
npm run dev
```

Open **http://localhost:5173**. API docs: http://localhost:8000/docs.

## 7. Loading demo data

The API creates its schema on startup; seed *content* is loaded separately:

```bash
cd backend
.venv\Scripts\python scripts\load_data.py
```

This resets tables and loads curriculum + concept rubrics + knowledge chunks
(embeddings computed at ingest) + PYQs. Re-run it any time to restore the demo
to a clean state. `scripts/init_db.py` only creates the empty schema.

## 8. Running tests

```bash
cd backend
.venv\Scripts\python -m pytest tests/
```

Covers the critical contracts: evaluation-schema rejection of invalid AI output,
the 3NF syllabus placement, session/attempt integrity, mastery updates, and PYQ
source metadata.

## 9. Demo flow (90 seconds)

1. Open the app → **Learning path**: SPPU → DBMS → Normalization, six concepts,
   only **Third Normal Form** carries the TeachBack badge.
2. Open 3NF → read Key idea / Explanation / Example / Common mistake.
3. **Start TeachBack** → paste the *weak* answer below → Submit.
4. Report reveals progressively: **Understanding 72%** (78 / 64 / 58), what was
   right, what needs attention, and — the moment —
   **Misconception detected: confusing 2NF with 3NF**, followed by a targeted
   explanation and a follow-up question about transitive dependency.
5. **Try again** → paste the *strong* answer → **86%**, **+14 points**,
   misconception resolved. This is the improvement beat.
6. Scroll to **Previous year questions** → attempt the 5-mark SPPU question to
   close the loop: understanding → application.

Calibrated answers (work verbatim with the default mock provider):

> **Weak (→ 72%):** Third Normal Form builds on 2NF. A relation is in 3NF when it
> is already in second normal form, so all partial dependencies have been removed,
> and every non-key attribute depends only on the candidate key. We use functional
> dependencies to check which attributes determine others. For example, in a table
> STUDENT(StudentID, Name, Department), StudentID determines Name and Department.

> **Strong (→ 86%):** Third Normal Form builds on 2NF, so a relation must already
> be in second normal form with all partial dependencies removed. Beyond that, a
> relation is in 3NF only if there are no transitive dependencies — a non-key
> attribute must not depend on another non-key attribute, only on the candidate
> key. We reason about this using functional dependencies. For example, in
> STUDENT(StudentID, Dept, DeptHead) where StudentID determines Dept and Dept
> determines DeptHead, DeptHead depends transitively on the key, so the relation
> is not in 3NF and must be decomposed.

With `LLM_PROVIDER=sarvam` and a real key, the same flow runs through the live
model instead — the mock answers above simply become ordinary student input.

## 10. Future expansion

All additive, no rewrites:

- **New concept / topic / subject** → add JSON under `backend/knowledge/`, rerun
  `load_data.py`. Set `teachback_enabled` to open a new loop.
- **Another programme or university** → add a curriculum file; entities are generic.
- **Better evaluation** → swap the LLM adapter or improve prompt `.txt` files;
  the strict output schema guards the contract either way.
- **Real vector DB** → implement the `RetrieverBackend` for Qdrant; the evaluator
  keeps receiving plain `RetrievedKnowledge[]`.
- **Multilingual** → multilingual embedding provider slot already exists.
- **Teacher dashboards, cohorts, auth** → sessions/attempts/mastery are already
  keyed by `student_key`; introduce real students without touching the loop.
