import { ArrowRight } from "lucide-react";
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
    <article>
      <PageHeader
        crumbs={[
          { label: university?.code ?? "SPPU" },
          { label: programme?.name ?? "B.E. AI&DS" },
          { label: semester?.name ?? "Semester IV" },
        ]}
        title="Database Management Systems"
        lede="Pick up where the syllabus leaves off: explain a concept in your own words, and TeachBack tells you whether you actually understand it."
      />

      {/* The loop, stated once, quietly */}
      <p className="mb-10 flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px] text-ink-faint">
        <span className="font-medium text-ink-soft">Learn</span>
        <span aria-hidden>→</span>
        <span className="font-medium text-ink-soft">Explain</span>
        <span aria-hidden>→</span>
        <span className="font-medium text-ink-soft">Evaluate</span>
        <span aria-hidden>→</span>
        <span className="font-medium text-ink-soft">Correct</span>
        <span aria-hidden>→</span>
        <span className="font-medium text-ink-soft">Apply</span>
      </p>

      <section aria-labelledby="normalization-heading">
        <div className="mb-3 flex items-baseline justify-between">
          <h2 id="normalization-heading" className="text-[19px] font-semibold tracking-[-0.01em]">
            Normalization
          </h2>
          <span className="text-[12.5px] text-ink-faint">Unit III · Relational Database Design</span>
        </div>

        <ul className="divide-y divide-rule rounded-lg border border-rule bg-surface px-3 py-1.5">
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
          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-rule pt-6">
            <p className="max-w-[52ch] text-[14px] leading-relaxed text-ink-soft">
              The full TeachBack loop is open for{" "}
              <Link to={`/concept/${enabledConcept.id}`} className="font-medium text-primary hover:underline">
                {enabledConcept.name}
              </Link>
              . Other concepts are readable now; their loops are on the way.
            </p>
            <Link
              to={`/concept/${enabledConcept.id}`}
              className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-white transition-colors hover:bg-primary-deep"
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
