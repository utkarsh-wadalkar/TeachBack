# TeachBack Dark Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a dark, reference-inspired TeachBack interface that keeps the existing learning loop functional.

**Architecture:** Tailwind theme tokens and low-specificity component classes supply the visual system. Existing React routes and API interfaces remain stable. A Vercel entrypoint packages FastAPI as a same-origin demo API and uses a writable temporary database populated with bundled seed content.

**Tech Stack:** React 19, Vite 6, Tailwind CSS 4, TypeScript, FastAPI, SQLAlchemy, Vercel Python functions.

**Spec:** `docs/superpowers/specs/2026-08-31-teachback-dark-interface-design.md`

## Global Constraints

- Keep all existing frontend routes and typed API method signatures unchanged.
- Use only `#ff6a1a` as the primary interaction accent; use green/red/amber solely for feedback meaning.
- Support desktop and mobile layouts, keyboard focus, and `prefers-reduced-motion`.
- Set no secret in source control; deployment requires no third-party API token for its mock demo mode.

---

### Task 1: Establish the visual system

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/components/AppShell.tsx`
- Test: `frontend/tests/visual-system.test.mjs`

**Interfaces:**
- Consumes: Tailwind class names in existing page and component JSX.
- Produces: `dark-grid`, `signal-orbit`, `panel-surface`, and dark semantic color tokens available to the UI.

- [ ] **Step 1: Write the failing test**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("the dark visual system exposes its reference-inspired primitives", async () => {
  const css = await readFile(new URL("../src/index.css", import.meta.url), "utf8");
  for (const token of ["--color-void", "--color-signal", ".dark-grid", ".signal-orbit"]) {
    assert.match(css, new RegExp(token.replace(/[.*+?^${}()|[\\]\\]/g, "\\$&")));
  }
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test frontend/tests/visual-system.test.mjs`

Expected: FAIL because the token names and utility classes do not exist.

- [ ] **Step 3: Write minimal implementation**

```css
@theme { --color-void: #070806; --color-signal: #ff6a1a; }
.dark-grid {
  background-image:
    linear-gradient(rgba(229, 231, 221, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(229, 231, 221, 0.045) 1px, transparent 1px);
  background-size: 40px 40px;
}
.signal-orbit { border: 1px solid color-mix(in srgb, var(--color-signal), transparent 45%); }
```

Apply the tokens to the page background, command rail, navigation signal, focus state, and mobile menu without changing route behavior.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test frontend/tests/visual-system.test.mjs`

Expected: PASS with one passing subtest.

### Task 2: Reshape the learning workspace

**Files:**
- Modify: `frontend/src/pages/CurriculumPage.tsx`
- Modify: `frontend/src/pages/LearningPage.tsx`
- Modify: `frontend/src/pages/TeachBackPage.tsx`
- Modify: `frontend/src/pages/PYQPage.tsx`
- Modify: `frontend/src/components/Button.tsx`
- Modify: `frontend/src/components/ConceptBadge.tsx`
- Modify: `frontend/src/components/EvaluationReport.tsx`
- Test: `frontend/tests/workspace-copy.test.mjs`

**Interfaces:**
- Consumes: current `api` interface and route parameters.
- Produces: reference-inspired semantic markup and class names while retaining each component's prop contract.

- [ ] **Step 1: Write the failing test**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("the curriculum presents the TeachBack loop as a mission control sequence", async () => {
  const page = await readFile(new URL("../src/pages/CurriculumPage.tsx", import.meta.url), "utf8");
  assert.match(page, /Understand the system/);
  assert.match(page, /signal-orbit/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test frontend/tests/workspace-copy.test.mjs`

Expected: FAIL because the new copy and signal marker are absent.

- [ ] **Step 3: Write minimal implementation**

```tsx
<p className="eyebrow text-signal">TeachBack / Active module</p>
<h1>Understand the system. Then prove it.</h1>
<span className="signal-orbit" aria-hidden />
```

Use `panel-surface` for interactive modules, a thin grid on large surfaces, concise diagnostic copy, responsive layout, and semantic feedback colors. Do not alter API calls or session storage keys.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test frontend/tests/workspace-copy.test.mjs`

Expected: PASS with one passing subtest.

### Task 3: Package the full demo for Vercel

**Files:**
- Create: `api/index.py`
- Create: `vercel.json`
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/main.py`
- Create: `frontend/tests/vercel-config.test.mjs`

**Interfaces:**
- Consumes: FastAPI app at `backend/app/main.py` and seed JSON under `backend/knowledge`.
- Produces: a Vercel Python ASGI entrypoint at `/api/*`; Vercel routes static requests to `frontend/dist`.

- [ ] **Step 1: Write the failing test**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("Vercel routes API requests to the Python entrypoint", async () => {
  const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));
  assert.deepEqual(config.rewrites[0], { source: "/api/(.*)", destination: "/api/index.py" });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test frontend/tests/vercel-config.test.mjs`

Expected: FAIL because the Vercel configuration does not exist.

- [ ] **Step 3: Write minimal implementation**

```py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.main import app
```

Configure Vercel to build `frontend`, serve its `dist` output, route API requests to the entrypoint, use `/tmp/teachback.db` under `VERCEL=1`, and idempotently load bundled seed data on FastAPI startup when the curriculum table is empty.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test frontend/tests/vercel-config.test.mjs`

Expected: PASS with one passing subtest.

### Task 4: Verify and release

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: build command, production deployment output, and Vercel deployment URL.
- Produces: reproducible deployment instructions and a deployed production URL.

- [ ] **Step 1: Verify unit-level regression checks**

Run: `node --test frontend/tests/*.test.mjs`

Expected: every UI-token and Vercel-config test passes.

- [ ] **Step 2: Build the frontend**

Run: `npm run build`

Working directory: `frontend`

Expected: TypeScript and Vite succeed, producing `frontend/dist`.

- [ ] **Step 3: Inspect the interface at desktop and mobile sizes**

Run the frontend with the FastAPI demo API, capture `/`, `/concept/1`, and a session screen at 1440px and 390px widths. Confirm legible text, no overflow, readable focus styling, and working navigation.

- [ ] **Step 4: Deploy production and inspect it**

Run: `vercel --prod --yes`

Expected: Vercel prints a `READY` production URL. Fetch `/api/health` through `vercel curl` and load the app URL to confirm both the frontend and API routes respond.

- [ ] **Step 5: Document the live endpoint**

Add the final production URL and the ephemeral-demo persistence note to `README.md`.
