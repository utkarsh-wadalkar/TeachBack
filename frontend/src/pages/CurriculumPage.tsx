import { ArrowRight, Radio } from "lucide-react";
import { Link } from "react-router-dom";
import { ConceptBadge } from "../components/ConceptBadge";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { useCurriculum } from "../lib/curriculum";

/**
 * The learning path: the academic hierarchy rendered as a syllabus index,
 * not a grid of dropdown cards. One topic, its concepts, and where you stand.
 */
export function CurriculumPage() {
  const { tree, topic, loading, error } = useCurriculum();

  if (loading) return <LoadingState label="Loading curriculum…" centered />;
  if (error)
    return (
      <div role="alert" className="rounded-lg border border-misconception-line bg-misconception-bg px-5 py-4 text-[14.5px] text-misconception">
        {error}
      </div>
    );
  if (!tree || !topic) return null;

  const university = tree.universities[0];
  const programme = university?.programmes[0];
  const semester = programme?.patterns[0]?.semesters[0];

  const enabledConcept = topic.concepts.find((c) => c.teachback_enabled);

  return (
    <article className="pb-8">
      <PageHeader
        crumbs={[
          { label: university?.code ?? "SPPU" },
          { label: programme?.name ?? "B.E. AI&DS" },
          { label: semester?.name ?? "Semester IV" },
        ]}
        title="Understand the system. Then prove it."
        lede="TeachBack turns studying into an honest signal: explain a concept in your own words, then see exactly what your understanding can carry."
      />

      <section className="panel-surface relative mb-10 overflow-hidden rounded-[1.6rem] px-6 py-6 sm:px-8">
        <div className="pointer-events-none absolute top-0 right-0 h-32 w-32 rounded-full bg-primary/15 blur-3xl" />
        <div className="relative flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div>
            <p className="eyebrow mb-3 text-primary">Active protocol</p>
            <p className="max-w-[50ch] text-[16px] leading-relaxed text-ink-soft">
              Learn the model. Explain its logic. Receive an actionable diagnostic. Improve with proof.
            </p>
            <p className="data-label mt-5 flex flex-wrap items-center gap-x-2 gap-y-1 text-ink-faint">
              <span>Learn</span><span className="text-primary">/</span><span>Explain</span><span className="text-primary">/</span><span>Evaluate</span><span className="text-primary">/</span><span>Apply</span>
            </p>
          </div>
          <div className="flex items-center gap-4 rounded-2xl border border-primary-line bg-void/70 px-4 py-3">
            <span className="signal-orbit flex h-9 w-9 items-center justify-center rounded-full bg-primary text-void">
              <Radio size={17} aria-hidden />
            </span>
            <span><span className="data-label block text-primary">Diagnostic mode</span><span className="mt-1 block text-[13px] text-ink-soft">Ready for a first attempt</span></span>
          </div>
        </div>
      </section>

      <section aria-labelledby="normalization-heading">
        <div className="mb-4 flex items-baseline justify-between gap-4">
          <h2 id="normalization-heading" className="display-type text-[24px] leading-none">
            Normalization
          </h2>
          <span className="data-label text-right text-ink-faint">Unit III / Relational design</span>
        </div>

        <ul className="panel-surface divide-y divide-rule overflow-hidden rounded-[1.35rem] px-3 py-1.5">
          {topic.concepts.map((concept) => (
            <li key={concept.id}>
              <ConceptBadge
                name={concept.name}
                code={concept.code}
                teachbackEnabled={concept.teachback_enabled}
                mastery={concept.mastery ?? undefined}
                to={`/concept/${concept.id}`}
                state={concept.teachback_enabled && concept.mastery == null ? "active" : concept.mastery != null ? "attempted" : "upcoming"}
              />
            </li>
          ))}
        </ul>

        {enabledConcept ? (
          <div className="panel-surface mt-6 flex flex-wrap items-center justify-between gap-4 rounded-[1.35rem] px-6 py-5">
            <p className="max-w-[52ch] text-[14px] leading-relaxed text-ink-soft">
              The full TeachBack loop is open for{" "}
              <Link to={`/concept/${enabledConcept.id}`} className="font-medium text-primary hover:underline">
                {enabledConcept.name}
              </Link>
              . Other concepts are readable now; their loops are on the way.
            </p>
            <Link
              to={`/concept/${enabledConcept.id}`}
              className="inline-flex h-10 items-center gap-2 rounded-full bg-primary px-5 text-sm font-semibold text-void transition-colors hover:bg-primary-deep hover:text-white"
            >
              Start with {enabledConcept.code}
              <ArrowRight size={15} aria-hidden />
            </Link>
          </div>
        ) : null}
      </section>
    </article>
  );
}
