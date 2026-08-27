import { GraduationCap } from "lucide-react";
import { useState, type ReactNode } from "react";
import { Link, NavLink, Outlet, useParams } from "react-router-dom";
import { useCurriculum } from "../lib/curriculum";
import { ConceptBadge } from "./ConceptBadge";
import { LoadingState } from "./LoadingState";
import { ProgressBar } from "./ProgressBar";

/**
 * The application shell: a slim sidebar that doubles as the curriculum rail
 * (so the learner always knows where they are), and a wide content column.
 * On small screens the rail becomes a horizontal strip under the wordmark.
 */
export function AppShell() {
  const { topic, loading, error } = useCurriculum();
  const { conceptId, sessionId } = useParams();
  const [navOpen, setNavOpen] = useState(false);

  let activeConceptId: number | undefined = undefined;
  if (conceptId) {
    activeConceptId = Number(conceptId);
  } else if (sessionId) {
    const raw = sessionStorage.getItem(`tb-session-${sessionId}`);
    if (raw) {
      try {
        const meta = JSON.parse(raw);
        if (meta?.concept_id) activeConceptId = Number(meta.concept_id);
      } catch {
        // ignore
      }
    }
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[264px_1fr]">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:rounded focus:bg-surface focus:px-3 focus:py-1.5 focus:text-sm"
      >
        Skip to content
      </a>

      <aside className="border-b border-rule bg-surface lg:sticky lg:top-0 lg:h-screen lg:border-r lg:border-b-0">
        <div className="flex h-full flex-col">
          {/* Wordmark */}
          <Link
            to="/"
            onClick={() => setNavOpen(false)}
            className="flex items-center gap-2.5 px-5 py-5"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-white">
              <GraduationCap size={17} aria-hidden />
            </span>
            <span>
              <span className="block text-[15px] leading-tight font-semibold tracking-[-0.01em]">
                TeachBack
              </span>
              <span className="block text-[11.5px] text-ink-faint">Prove you understand.</span>
            </span>
          </Link>

          {/* Mobile nav toggle */}
          <button
            type="button"
            onClick={() => setNavOpen((o) => !o)}
            aria-expanded={navOpen}
            className="mx-5 mb-3 rounded-md border border-rule-strong px-3 py-1.5 text-left text-[13px] font-medium text-ink lg:hidden"
          >
            {navOpen ? "Hide" : "Browse"} curriculum
          </button>

          <nav
            aria-label="Curriculum"
            className={`${navOpen ? "block" : "hidden"} flex-1 overflow-y-auto px-3 pb-4 lg:block`}
          >
            <p className="eyebrow mt-1 mb-2 px-2">Curriculum</p>

            {loading ? (
              <LoadingState label="Loading curriculum…" />
            ) : error ? (
              <p className="px-2 text-[13px] text-misconception">{error}</p>
            ) : topic ? (
              <>
                <p className="mb-2 px-2 text-[13px] text-ink-faint">Normalization</p>
                <ul className="space-y-0.5">
                  {topic.concepts.map((concept) => (
                    <li key={concept.id}>
                      <ConceptBadge
                        name={concept.name}
                        code={concept.code}
                        teachbackEnabled={concept.teachback_enabled}
                        mastery={concept.mastery ?? undefined}
                        to={`/concept/${concept.id}`}
                        state={
                          concept.id === activeConceptId
                            ? "active"
                            : concept.mastery != null
                              ? "attempted"
                              : "upcoming"
                        }
                      />
                    </li>
                  ))}
                </ul>

                <p className="eyebrow mt-7 mb-2 px-2">Mastery</p>
                <ul className="space-y-3 px-2">
                  {topic.concepts
                    .filter((c) => c.mastery != null)
                    .map((c) => (
                      <li key={c.id}>
                        <div className="mb-1 flex items-baseline justify-between gap-2">
                          <span className="truncate text-[12.5px] text-ink-soft">{c.name}</span>
                          <span className="tabular-nums text-[12px] font-medium text-correct">
                            {c.mastery}%
                          </span>
                        </div>
                        <ProgressBar value={c.mastery ?? 0} label={`${c.name} mastery`} thin tone="correct" />
                      </li>
                    ))}
                  {topic.concepts.every((c) => c.mastery == null) ? (
                    <li className="text-[12.5px] leading-relaxed text-ink-faint">
                      No attempts yet. Start with Third Normal Form.
                    </li>
                  ) : null}
                </ul>
              </>
            ) : null}
          </nav>

          {/* Demo identity */}
          <div className="mt-auto hidden items-center gap-2.5 border-t border-rule px-5 py-4 lg:flex">
            <span
              aria-hidden
              className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-tint text-[11px] font-semibold text-primary"
            >
              DS
            </span>
            <span className="text-[12.5px] leading-tight">
              <span className="block font-medium text-ink">Demo Student</span>
              <span className="block text-ink-faint">SPPU · B.E. AI&DS</span>
            </span>
          </div>
        </div>
      </aside>

      <main id="main" className="min-w-0 px-5 py-8 sm:px-8 lg:px-14 lg:py-12">
        <div className="mx-auto max-w-[880px]">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

/** Small labelled link used for secondary navigation (e.g. back to learning). */
export function TextLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <NavLink to={to} className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">
      {children}
    </NavLink>
  );
}