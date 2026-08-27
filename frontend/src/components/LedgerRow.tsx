import type { ReactNode } from "react";

interface LedgerRowProps {
  label: ReactNode;
  value: ReactNode;
  /** Optional leading status glyph slot (✓ / ⚠ …). */
  glyph?: ReactNode;
}

/**
 * A marks-ledger line: label ···· dotted leader ···· tabular value.
 * The one distinctive device of the evaluation report — it reads like an
 * examined answer sheet, and keeps every score aligned on the same grid.
 */
export function LedgerRow({ label, value, glyph }: LedgerRowProps) {
  return (
    <div className="flex items-baseline gap-3 py-2">
      {glyph ? <span className="flex h-4 w-4 shrink-0 self-center">{glyph}</span> : null}
      <span className="min-w-0 text-[14.5px] text-ink-soft">{label}</span>
      <span
        aria-hidden
        className="mx-1 min-w-6 flex-1 -translate-y-[3px] border-b border-dotted border-rule-strong"
      />
      <span className="tabular-nums text-[14.5px] font-medium text-ink">{value}</span>
    </div>
  );
}
