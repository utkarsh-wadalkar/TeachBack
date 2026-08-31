# TeachBack Dark Interface Design

## Purpose

TeachBack helps SPPU students prove, rather than merely claim, that they understand a concept. The app's one job is to make the loop **learn → explain → evaluate → improve** feel focused, credible, and rewarding.

## Direction

The interface will become a dark learning control room informed by the supplied references: cinematic black surfaces, fine technical grids, controlled chrome linework, large geometric headings, and a single warm-orange signal. It will not copy the references' agency/marketing layouts or add a marketing site; this remains a task-focused learning product.

### Tokens

| Role | Value | Use |
| --- | --- | --- |
| void | `#070806` | Page background |
| graphite | `#11130f` | Raised panels |
| carbon | `#191b16` | Input and card interiors |
| silver | `#e5e7dd` | Primary text and dividers |
| muted silver | `#9b9e95` | Secondary information |
| signal orange | `#ff6a1a` | Primary actions and active states |
| signal amber | `#ffb56b` | Warm highlights |
| signal green | `#8bd982` | Positive mastery and correct feedback |

### Type and layout

`Space Grotesk` is the restrained display face for headings; `Inter` continues as the highly legible content face; the built-in monospace stack labels diagnostics and data. A 272px desktop command rail contains the curriculum. The content pane is centered at 920px and organized around large, airy concept cards. On small screens, navigation collapses to a compact command bar.

### Signature interaction

An orange **understanding signal** appears as a circular diagnostic ring: it frames the current TeachBack concept in the rail and carries across actions and evaluation feedback. Low-opacity grid lines and a slow, one-time scan animation make the app feel active without distracting from reading and writing.

## Components and data flow

- `AppShell` owns the persistent dark navigation frame, active-concept signal, responsive menu, and the student identity area.
- Existing pages retain their routes and API calls. `CurriculumPage` becomes the mission overview; `LearningPage` remains a reading surface; `TeachBackPage` remains the diagnostic workspace; `PYQPage` remains the exam-practice view.
- Existing utility components retain their public interfaces, but adopt the new tokens so every feedback state still communicates correctly.
- The frontend API base remains configurable by `VITE_API_URL`. A Vercel rewrite will proxy `/api/*` to the bundled FastAPI application for the portable demo.

## Deployment

Vercel will build the Vite client from `frontend`, host the static assets, and route `/api/*` to a Python FastAPI entrypoint. The backend will seed the bundled demo data into the serverless writable `/tmp` directory when it starts, so the deployed experience works without a separate database service. Sessions and mastery are explicitly demo-persistent only: serverless restarts reset them.

## Quality requirements

- Preserve all existing routes, visible learning content, API contracts, and error states.
- Meet responsive, keyboard-focus, and reduced-motion requirements.
- Add a regression check for the Vercel configuration and run the TypeScript/Vite production build.
- Verify the rendered desktop and mobile views in a browser before deployment.
