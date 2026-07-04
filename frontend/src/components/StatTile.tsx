import type { LucideIcon } from "lucide-react";

interface StatTileProps {
  label: string;
  value: string | number;
  icon?: LucideIcon;
}

/**
 * Compact stat card used across the User Hub (Profil, Riwayat). Mono uppercase
 * label + large tabular value, matching the design tokens in DESIGN.md.
 */
export function StatTile({ label, value, icon: Icon }: StatTileProps) {
  return (
    <div className="rounded-2xl border border-border-standard bg-bg-page p-3 shadow-level-1 sm:p-4">
      <div className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
        {Icon && <Icon className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />}
        <span className="truncate">{label}</span>
      </div>
      <div className="mt-1 text-xl font-medium tabular-nums text-text-primary sm:text-2xl">
        {value}
      </div>
    </div>
  );
}
