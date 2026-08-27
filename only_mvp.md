Build a MVP just to show judges of hackathon, so that they can shortlist our team, our idea is to make: “TeachBack” — AI That Knows Whether You Actually Understand



Domain: Smart Education



Instead of an AI tutor that keeps explaining things, make one that determines whether the student genuinely understands the concept.



Student selects:



SPPU-> SEMESTER-> DBMS subject -> Normalization topic → 3NF all concepts in that topic from sppu syllabus, so we will need knowledge base of all subjects and experties in them, so sujjest me which tech would be appropriate and we can make it expandable also with silimar university's subjects. 



AI teaches the concept briefly and then asks the student to explain it back in their own words.



for now we support only sppu only 



It analyzes:



Conceptual correctness



Missing concepts



Misconceptions



Confidence



Ability to apply the concept



Then generates:



Understanding: 72%



You understand functional dependencies but are confusing 2NF and 3NF.



Then it gives a targeted question.



This creates a loop:



Learn → Explain → Evaluate → Correct → Apply



TeachBack — Final MVP Engineering & UI Requirements

These requirements extend the existing TeachBack shortlisting MVP specification.

The MVP has two equally important goals:





Look polished enough to make judges take the product seriously.



Be architecturally clean enough that, if selected, the team can continue development without throwing away the MVP.

The MVP is intentionally narrow in content scope, not careless in engineering quality.

1. Product Scope — DO NOT EXPAND

The functional demo remains exactly:

SPPU
 → B.E. Artificial Intelligence & Data Science
 → Semester IV
 → DBMS
 → Normalization
 → 3NF


Only 3NF needs the complete TeachBack loop.

Do not implement additional subjects or universities.

However, the software architecture must be reusable.

2. IMPORTANT PRINCIPLE

Build:

A production-shaped vertical slice, not a disposable prototype.

This means:

Narrow data

Only one subject/topic/concept.

Clean architecture

The services, database schema, API contracts, AI adapters, and frontend components should already support future expansion.

If the team gets selected, we should be able to continue by:

adding data
+
adding ingestion
+
adding concepts
+
adding PYQs
+
adding evaluation rubrics


rather than rewriting the application.

3. Frontend Quality Is A Core Requirement

The frontend must NOT look like generic AI-generated UI.

Avoid the typical:





Huge gradient hero



Excessive glassmorphism



Neon purple AI aesthetic



Floating glowing blobs



Excessive rounded cards



Random dashboard charts



Generic "AI-powered" badges



Excessive shadows



Unnecessary animations



Every section inside a card



Giant text with little information



Stock AI illustrations

The product should look like a real education product designed by a professional product/UI team.

Think:

calm + academic + modern + focused

rather than:

"look, this is AI!"

4. Visual Design Direction

Use a restrained design system.

Typography

Use a high-quality modern sans-serif such as:





Inter



Geist



Plus Jakarta Sans

Choose ONE and use it consistently.

Layout

Prefer:

wide content area
clear hierarchy
generous whitespace
strong alignment
consistent spacing


Do not fill the screen with cards.

Color

Use a restrained primary color and neutral palette.

AI should not be represented through gradients everywhere.

Use color primarily for meaning:

Normal
Positive
Warning
Error
Information


For example:

✓ Correct concept
⚠ Needs attention
✕ Misconception


Do not use color alone to communicate information.

5. Create A Small Design System

Before building pages, define:

colors
typography
spacing
border radius
shadows
buttons
inputs
cards
badges
progress indicators
modal/dialog
toast
loading states


Create reusable components.

For example:

components/
├── Button
├── Select
├── ProgressBar
├── ConceptBadge
├── ScoreCard
├── EvaluationSection
├── MisconceptionCard
├── QuestionCard
├── AudioRecorder
└── PageHeader


Do not duplicate styles across pages.

6. Navigation Should Feel Like A Learning Product

Use a simple application shell.

Example:

┌──────────────────────────────────────────────────────┐
│ TeachBack                              Profile       │
├──────────────┬───────────────────────────────────────┤
│              │                                       │
│ My Learning  │                                       │
│              │                                       │
│ Curriculum   │       Main Learning Area              │
│              │                                       │
│ Progress     │                                       │
│              │                                       │
└──────────────┴───────────────────────────────────────┘


But don't create unnecessary pages.

For the demo, navigation can be minimal.

7. Curriculum Selection Should Feel Real

Instead of five giant dropdown cards, create a clear academic hierarchy.

Example:

Learning Path

SPPU
B.E. Artificial Intelligence & Data Science
Semester IV
Database Management Systems

Normalization

Concepts
────────────────────────────────────

✓ Functional Dependency
✓ 1NF
✓ 2NF
→ 3NF
○ BCNF
○ Decomposition


The selected concept should have an obvious active state.

This should communicate:

"I know exactly where I am in the curriculum."

8. Learning Page

The learning page should feel like a proper educational reading experience.

Example structure:

Normalization / 3NF

3NF — Third Normal Form

Short explanation...

Key idea

Functional dependency...

Example

...

Common mistake

...

────────────────────────────

Ready to explain it?

[ Start TeachBack ]


Do not turn every paragraph into a separate card.

Use typography and spacing to create hierarchy.

9. TeachBack Page Should Be The Hero

This is the most important screen.

The UI should create a feeling of:

"Now I have to prove that I understand this."

Example:

3NF
TeachBack

Can you teach this concept?

Explain 3NF as if you were
teaching it to a classmate.

────────────────────────────────

[ Write your explanation...        ]

                                  0/1000

        🎙 Record answer

────────────────────────────────

                     [ Submit ]


The interface should feel focused and distraction-free.

10. Evaluation Experience

Do not immediately dump a wall of AI-generated text onto the screen.

Use progressive information hierarchy.

First:

Your understanding

72%


Then:

Conceptual correctness       78%
Completeness                 64%
Application readiness        58%


Then:

What you got right

✓ Functional dependency
✓ Candidate key


Then:

What needs attention

⚠ Prime attribute
⚠ Transitive dependency


Then:

Misconception detected

You are confusing...


Then:

Targeted explanation


This makes the evaluation feel like a diagnostic report, not a chatbot response.

11. Avoid Fake "AI Thinking"

Do not implement fake animations such as:

AI is thinking...
Analyzing neural patterns...
Understanding your response...


Do not create fake terminal logs.

Use a simple professional loading state:

Evaluating your explanation...


with a subtle progress indicator.

The product should demonstrate actual intelligence through the result.

12. Score Visualization

Do not create a giant circular gauge just because it looks "AI".

A clean score presentation is preferable:

72%

Understanding
━━━━━━━━━━━━━━━━━━░░░

↑ 14 points from previous attempt


Use meaningful comparison.

The improvement is more important than the number itself.

13. Misconception UI

This is a key product feature.

Make it visually distinct.

Example:

MISCONCEPTION

2NF vs 3NF

You correctly identified functional
dependencies, but your explanation
suggests that removing partial
dependencies is sufficient for 3NF.

Why this matters

3NF also considers transitive
dependencies...


Then:

[Explain This Concept]

This should feel like the system has diagnosed the student.

14. Second Attempt

Make improvement visually obvious.

Before:

72%


After:

86%


Then:

+14 points

Your explanation now correctly
covers transitive dependency.


This is likely the strongest moment in the video.

15. PYQ Experience

Do not make the PYQ look like another random card.

Make it resemble an examination question.

Example:

SPPU • DBMS • 5 Marks

Previous Year Question

Explain Third Normal Form (3NF)
with a suitable example.

────────────────────────────

Concepts tested

Functional Dependency
Candidate Key
Transitive Dependency

[ Attempt Question ]


This connects:

understanding → application → exam preparation

which strengthens the product story.

16. Backend Architecture

Keep the backend production-shaped.

Use:

backend/
└── app/
    ├── api/
    │   ├── curriculum.py
    │   ├── learning.py
    │   ├── teachback.py
    │   ├── pyq.py
    │   └── health.py
    │
    ├── schemas/
    │   ├── curriculum.py
    │   ├── teachback.py
    │   ├── evaluation.py
    │   └── pyq.py
    │
    ├── services/
    │   ├── curriculum_service.py
    │   ├── learning_service.py
    │   ├── teachback_service.py
    │   ├── evaluation_service.py
    │   └── mastery_service.py
    │
    ├── ai/
    │   ├── llm.py
    │   ├── stt.py
    │   ├── embeddings.py
    │   └── prompts/
    │
    ├── db/
    │   ├── models/
    │   └── session.py
    │
    └── core/
        └── config.py


Keep business logic out of API route handlers.

17. AI Provider Abstraction

Do not call the LLM directly from random files.

Create an interface similar to:

LLMProvider
    └── SarvamProvider


Likewise:

STTProvider
    └── SarvamSTTProvider


and:

EmbeddingProvider
    └── MultilingualEmbeddingProvider


This means if the hackathon infrastructure changes later, we replace the adapter instead of rewriting the evaluation engine.

18. Prompt Management

Do NOT bury giant prompts inside Python functions.

Store them separately:

ai/
└── prompts/
    ├── evaluate_teachback.txt
    ├── generate_intervention.txt
    ├── generate_followup.txt
    └── evaluate_pyq.txt


Version them.

The evaluator should receive explicit:

curriculum context
concept definition
expected concepts
misconceptions
retrieved knowledge
student response


This will make later prompt improvement much easier.

19. Database Design

Even though the MVP contains one subject, don't create tables such as:

dbms_3nf_questions
dbms_3nf_answers


Instead use generic entities.

Conceptually:

universities
programmes
patterns
semesters
subjects
units
topics
concepts

pyqs
concept_pyqs

sessions
attempts
evaluations
mastery


Today they contain:

SPPU
AI&DS
Semester IV
DBMS
Normalization
3NF


Tomorrow they can contain thousands of concepts.

20. Data Ingestion Must Be Separate From Application Code

Create seed/ingestion data:

knowledge/
├── curriculum/
│   └── sppu_ai_ds_sem4.json
│
├── concepts/
│   └── dbms_normalization.json
│
└── pyqs/
    └── dbms_normalization.json


Create scripts that load this data.

Do not hard-code syllabus data inside React components or FastAPI routes.

This is extremely important for future expansion.

21. RAG Architecture

Keep retrieval isolated:

KnowledgeRetriever
        │
        ├── metadata filter
        └── semantic search


The evaluator should not know whether the knowledge came from:





Qdrant



PostgreSQL



local JSON



another vector database

It only receives:

RetrievedKnowledge[]


This makes the architecture easier to expand.

22. Don't Overbuild RAG

For the MVP, the knowledge corpus is tiny.

Do not create an elaborate multi-stage RAG pipeline.

Use:

Current concept
      ↓
metadata filtering
      ↓
vector retrieval
      ↓
top relevant chunks
      ↓
evaluation


That's sufficient.

If Qdrant adds too much operational overhead for the first demo, implement a clean retrieval interface with a local backend first.

23. Testing

Even for a hackathon MVP, create basic tests for the most important logic.

At minimum:

Evaluation schema

Invalid AI output should be rejected.

Curriculum

3NF must belong to:

SPPU → AI&DS → Sem IV → DBMS → Normalization


Session

A second TeachBack attempt must belong to the same session.

Mastery

A valid second evaluation should update mastery.

PYQ

PYQs must contain valid source metadata.

Do not spend days writing tests.

Test the critical contracts.

24. Environment Configuration

Use:

.env
.env.example


Example:

LLM_API_KEY=
LLM_MODEL=
STT_API_KEY=
DATABASE_URL=
QDRANT_URL=
QDRANT_API_KEY=


Never hard-code credentials.

The project should run locally using documented setup instructions.

25. Documentation

Create a concise README containing:

1. What TeachBack is
2. Architecture
3. MVP scope
4. Setup
5. Environment variables
6. Running locally
7. Loading demo data
8. Running tests
9. Demo flow
10. Future expansion


Also include an architecture diagram.

The README should make it possible for another teammate to understand the project without asking the original developer.

26. Future Development Must Be Additive

After the hackathon, these should be possible without changing the core:

Add another concept
        ↓
Add another topic
        ↓
Add another subject
        ↓
Add another semester
        ↓
Add another SPPU programme
        ↓
Add another university
        ↓
Add multilingual content
        ↓
Add teacher dashboard


The core TeachBack engine should remain:

Curriculum
    ↓
Concept
    ↓
Knowledge
    ↓
Student explanation
    ↓
Evaluation
    ↓
Intervention
    ↓
Reassessment


27. Definition of Engineering Success

Do not optimize for the number of features.

The MVP is successful if:

Product

A judge immediately understands the problem and solution.

UX

The application looks like a real product rather than an AI-generated demo.

AI

The system identifies a real weakness in the student's explanation.

Adaptation

The second question is based on that weakness.

Measurability

The system demonstrates improvement.

Architecture

The implementation can continue into the full product without being rewritten.

28. Final Rule

Before adding any feature ask:

Does this improve the 3NF TeachBack demonstration or make the eventual product easier to build?

If the answer is no, do not build it.

The goal is:

Small scope + high polish + real AI behavior + clean architecture.

Not:

Large scope + shallow features + impressive-looking screenshots.