import { TrendingUp } from "lucide-react";
import type { Improvement } from "../lib/api";
import { ProgressBar } from "./ProgressBar";

interface ScoreCardProps {
  understanding: number;
  improvement?: Improvement | null;
}

/**
 * The headline diagnostic: one big tabular number over a single meter.
 * When a previous attempt exists, the delta line leads — improvement is the
 * story, not the score itself.
 */
export function ScoreCard({ understanding, improvement }: ScoreCardProps) {
  const improved = (improvement?.delta ?? 0) > 0;

  return (
    <div>
      <div className="panel-surface flex flex-wrap items-end gap-x-6 gap-y-4 rounded-[1.45rem] px-6 py-6">
        <div className="flex items-baseline gap-1">
          <span className="display-type text-[70px] leading-none text-primary tabular-nums">
            {understanding}
          </span>
          <span className="text-[22px] font-medium text-ink-faint">%</span>
        </div>

        {improvement ? (
          <div className="flex items-center gap-2 pb-1.5">
            <span
              className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[13px] font-medium tabular-nums ${
                improved
                  ? "border-correct-line bg-correct-bg text-correct"
                  : "border-rule bg-paper text-ink-faint"
              }`}
            >
              <TrendingUp size={13} aria-hidden className={improved ? "" : "opacity-40"} />
              {improved ? `+${improvement.delta} points` : `${improvement.delta} points`}
            </span>
            <span className="tabular-nums text-[13px] text-ink-faint">
              from {improvement.previous_understanding}% on your previous attempt
            </span>
          </div>
        ) : null}
      </div>

      <div className="mt-5 max-w-xl">
        <ProgressBar
          value={understanding}
          label={`Understanding ${understanding}%`}
          tone={understanding >= 75 ? "correct" : understanding >= 50 ? "neutral" : "attention"}
        />
      </div>

      {improvement?.message ? (
        <p className="mt-3 max-w-[60ch] text-[14px] leading-relaxed text-ink-soft">
          {improvement.message}
        </p>
      ) : null}
    </div>
  );
}
