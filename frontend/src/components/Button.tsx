import { LoaderCircle } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children: ReactNode;
}

const VARIANTS: Record<Variant, string> = {
  primary:
    "rounded-full bg-primary text-void hover:bg-primary-deep hover:text-white disabled:hover:bg-primary border border-transparent shadow-[0_0_24px_rgba(255,106,26,0.18)]",
  secondary:
    "bg-surface text-ink border border-rule-strong hover:border-ink-faint hover:text-ink",
  ghost: "bg-transparent text-primary hover:bg-primary-tint border border-transparent",
};

const SIZES: Record<Size, string> = {
  sm: "h-8 px-3 text-[13px] gap-1.5 rounded-full",
  md: "h-10 px-4 text-sm gap-2 rounded-full",
};

/** The single button style in the product. Loading swaps content for a spinner. */
export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  className = "",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center font-medium transition-colors select-none disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...rest}
    >
      {loading ? <LoaderCircle size={15} className="animate-spin" aria-hidden /> : null}
      {children}
    </button>
  );
}
