import { ChevronDown } from "lucide-react";
import type { SelectHTMLAttributes } from "react";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options: SelectOption[];
  label?: string;
}

/** Styled native select — keyboard and screen-reader behaviour for free. */
export function Select({ options, label, className = "", id, ...rest }: SelectProps) {
  return (
    <div className={`inline-flex flex-col gap-1.5 ${className}`}>
      {label ? (
        <label htmlFor={id} className="eyebrow">
          {label}
        </label>
      ) : null}
      <div className="relative">
        <select
          id={id}
          className="h-9 w-full appearance-none rounded-md border border-rule-strong bg-surface pr-8 pl-3 text-sm text-ink hover:border-ink-faint"
          {...rest}
        >
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown
          size={15}
          aria-hidden
          className="pointer-events-none absolute top-1/2 right-2.5 -translate-y-1/2 text-ink-faint"
        />
      </div>
    </div>
  );
}
