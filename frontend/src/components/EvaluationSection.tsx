import type { ReactNode } from "react";

interface EvaluationSectionProps {
  eyebrow: string;
  title?: string;
  children: ReactNode;
}

/**
 * One labelled block of the diagnostic report. Sections stack in a fixed,
 * meaningful order (understanding → breakdown → right → attention →
 * misconception → explanation → follow-up); the eyebrow carries the identity.
 */
export function EvaluationSection({ eyebrow, title, children }: EvaluationSectionProps) {
  return (
    <section className="border-t border-rule pt-6 first:border-t-0 first:pt-0">
      <p className="eyebrow mb-3">{eyebrow}</p>
      {title ? (
        <h2 className="mb-3 text-[17px] font-semibold tracking-[-0.01em] text-ink">{title}</h2>
      ) : null}
      {children}
    </section>
  );
}
