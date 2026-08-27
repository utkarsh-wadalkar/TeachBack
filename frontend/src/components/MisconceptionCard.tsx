import { XCircle } from "lucide-react";
import type { ReactNode } from "react";
import type { MisconceptionOut } from "../lib/api";

interface MisconceptionCardProps {
  misconception: MisconceptionOut;
  /** Optional footer action (e.g. “Explain this concept”). */
  action?: ReactNode;
}

/**
 * The examiner's note. Visually distinct by design: a solid misconception-red
 * left border and tinted ground mark this as a diagnosis, not ordinary prose.
 */
export function MisconceptionCard({ misconception, action }: MisconceptionCardProps) {
  return (
    <div className="rounded-lg border border-misconception-line border-l-4 border-l-misconception bg-misconception-bg px-5 py-4">
      <div className="flex items-start gap-3">
        <XCircle size={17} aria-hidden className="mt-0.5 shrink-0 text-misconception" />
        <div className="min-w-0">
          <p className="eyebrow mb-1 text-misconception">Misconception detected</p>
          <h3 className="text-[16px] font-semibold text-ink">{misconception.title}</h3>
          <p className="mt-1.5 max-w-[64ch] text-[14.5px] leading-relaxed text-ink-soft">
            {misconception.description}
          </p>
          <div className="mt-3 border-t border-misconception-line/70 pt-3">
            <p className="eyebrow mb-1">Why this matters</p>
            <p className="max-w-[64ch] text-[14px] leading-relaxed text-ink-soft">
              {misconception.why_it_matters}
            </p>
          </div>
          {action ? <div className="mt-4">{action}</div> : null}
        </div>
      </div>
    </div>
  );
}
