import { ArrowRight, Check, Circle } from "lucide-react";
import { Link } from "react-router-dom";

type State = "attempted" | "active" | "upcoming";

interface ConceptBadgeProps {
  name: string;
  code: string;
  state: State;
  teachbackEnabled?: boolean;
  mastery?: number | null;
  to?: string;
}

const STATE_GLYPH: Record<State, React.ReactNode> = {
  attempted: <Check size={14} strokeWidth={2.5} className="text-correct" aria-hidden />,
  active: <ArrowRight size={14} strokeWidth={2.5} className="text-primary" aria-hidden />,
  upcoming: <Circle size={9} className="text-rule-strong" aria-hidden />,
};

/**
 * One row of a curriculum list — the syllabus-index vernacular:
 * status glyph, concept name, and (optionally) its mastery score.
 */
export function ConceptBadge({
  name,
  state,
  teachbackEnabled = false,
  mastery,
  to,
}: ConceptBadgeProps) {
  const body = (
    <>
      <span className="flex h-5 w-5 shrink-0 items-center justify-center">{STATE_GLYPH[state]}</span>
      <span className="min-w-0 flex-1 truncate">
        <span
          className={`text-[15px] ${state === "active" ? "font-semibold text-ink" : state === "upcoming" ? "text-ink-soft" : "font-medium text-ink"}`}
        >
          {name}
        </span>
        {teachbackEnabled ? (
          <span className="ml-2 align-middle text-[11px] font-medium tracking-[0.07em] text-primary uppercase">
            TeachBack
          </span>
        ) : null}
      </span>
      {mastery != null ? (
        <span className="tabular-nums text-[13px] font-medium text-correct">{mastery}%</span>
      ) : null}
    </>
  );

  const rowClass = `flex w-full items-center gap-3 px-3 py-3 text-left transition-colors ${
    to ? "hover:bg-primary-tint/60 cursor-pointer rounded-xl" : ""
  } ${state === "active" ? "bg-primary-tint ring-1 ring-primary-line/60" : ""}`;

  return to ? (
    <Link to={to} className={`rounded-xl ${rowClass}`} aria-current={state === "active" ? "page" : undefined}>
      {body}
    </Link>
  ) : (
    <div className={rowClass}>{body}</div>
  );
}
