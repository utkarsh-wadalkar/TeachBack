type Tone = "neutral" | "correct" | "attention";

interface ProgressBarProps {
  /** 0–100 */
  value: number;
  label: string;
  tone?: Tone;
  thin?: boolean;
}

const TONE_FILL: Record<Tone, string> = {
  neutral: "bg-primary",
  correct: "bg-correct",
  attention: "bg-attention",
};

/** Thin horizontal meter used for every score in the product. */
export function ProgressBar({ value, label, tone = "neutral", thin = false }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
      className={`w-full overflow-hidden rounded-full bg-rule ${thin ? "h-1" : "h-1.5"}`}
    >
      <div
        className={`h-full rounded-full transition-[width] duration-700 ease-out ${TONE_FILL[tone]}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
