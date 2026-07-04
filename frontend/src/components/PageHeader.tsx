import type { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  eyebrow: string;
  title: string;
  subtitle: string;
  icon: LucideIcon;
}

/**
 * Standard page header for the User Hub surfaces: a mono eyebrow with icon,
 * a large title, and a secondary subtitle. Matches ProgressPage's header.
 */
export function PageHeader({ eyebrow, title, subtitle, icon: Icon }: PageHeaderProps) {
  return (
    <header className="space-y-3">
      <div className="flex items-center gap-2 text-brand-green">
        <Icon className="h-5 w-5" aria-hidden="true" />
        <span className="font-mono text-[11px] uppercase tracking-[1.2px]">
          {eyebrow}
        </span>
      </div>
      <h1 className="text-4xl font-medium leading-tight tracking-tight text-text-primary">
        {title}
      </h1>
      <p className="text-lg text-text-secondary">{subtitle}</p>
    </header>
  );
}
