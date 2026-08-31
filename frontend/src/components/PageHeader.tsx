import { ChevronRight } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

export interface Crumb {
  label: string;
  /** Omit for the current page (rendered as plain text). */
  to?: string;
}

interface PageHeaderProps {
  crumbs: Crumb[];
  title: string;
  lede?: string;
  meta?: ReactNode;
}

/** Breadcrumb trail + display heading — the top of every content page. */
export function PageHeader({ crumbs, title, lede, meta }: PageHeaderProps) {
  return (
    <header className="mb-9 border-b border-rule pb-7">
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex flex-wrap items-center gap-1 text-[13px] text-ink-faint">
          {crumbs.map((crumb, i) => (
            <li key={`${crumb.label}-${i}`} className="flex items-center gap-1">
              {i > 0 ? (
                <ChevronRight size={13} aria-hidden className="text-rule-strong" />
              ) : null}
              {crumb.to ? (
                <Link to={crumb.to} className="hover:text-primary hover:underline">
                  {crumb.label}
                </Link>
              ) : (
                <span aria-current="page">{crumb.label}</span>
              )}
            </li>
          ))}
        </ol>
      </nav>
      <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3">
        <h1 className="display-type max-w-[19ch] text-[clamp(2.1rem,5vw,3.9rem)] leading-[0.95] text-ink">
          {title}
        </h1>
        {meta}
      </div>
      {lede ? <p className="mt-2 max-w-[68ch] text-[15px] leading-relaxed text-ink-soft">{lede}</p> : null}
    </header>
  );
}
