import { LoaderCircle } from "lucide-react";

interface LoadingStateProps {
  label: string;
  /** Vertically center in the available space (page-level loads). */
  centered?: boolean;
}

/**
 * The one honest loading state in the product: a real spinner and a plain
 * sentence about what is actually happening. No fake AI theatre.
 */
export function LoadingState({ label, centered = false }: LoadingStateProps) {
  const inner = (
    <div className="flex items-center gap-3" role="status" aria-live="polite">
      <LoaderCircle size={18} aria-hidden className="animate-spin text-primary" />
      <span className="text-[14.5px] text-ink-soft">{label}</span>
    </div>
  );
  return centered ? (
    <div className="flex min-h-[240px] items-center justify-center">{inner}</div>
  ) : (
    <div className="py-10">{inner}</div>
  );
}
