import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import type { PyqOut } from "../lib/api";

interface QuestionCardProps {
  pyq: PyqOut;
}

/** Formats the exam header: SPPU • DBMS • 2023 • End Semester Examination. */
function sourceLine(source: PyqOut["source"], year: string, marks: number): string {
  const parts = [source.university, source.subject, year || source.year, source.exam]
    .filter(Boolean)
    .map(String);
  parts.push(`${marks} marks`);
  return parts.join(" • ");
}

/**
 * A previous-year question presented as an examination paper — authentic
 * header line, question, and the concepts it tests. Not a dashboard card.
 */
export function QuestionCard({ pyq }: QuestionCardProps) {
  return (
    <article className="panel-surface rounded-[1.35rem] px-6 py-5">
      <p className="eyebrow mb-3">{sourceLine(pyq.source, pyq.year, pyq.marks)}</p>
      <h3 className="max-w-[70ch] text-[16.5px] leading-snug font-medium text-ink">
        {pyq.question}
      </h3>

      <div className="mt-4 border-t border-rule pt-3">
        <p className="eyebrow mb-1.5">Concepts tested</p>
        <ul className="flex flex-wrap gap-x-4 gap-y-1">
          {pyq.concepts_tested.map((name) => (
            <li key={name} className="text-[13.5px] text-ink-soft">
              {name}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-4 flex justify-end">
        <Link
          to={`/pyq/${pyq.id}`}
          className="inline-flex h-9 items-center gap-2 rounded-full bg-primary px-4 text-[13.5px] font-semibold text-void transition-colors hover:bg-primary-deep hover:text-white"
        >
          Attempt question
          <ArrowRight size={14} aria-hidden />
        </Link>
      </div>
    </article>
  );
}
