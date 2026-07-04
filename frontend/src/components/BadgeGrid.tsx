import {
  Award,
  Flame,
  type LucideIcon,
  Lock,
  Sparkles,
  Star,
  TrendingUp,
  Trophy,
} from "lucide-react";
import type { Badge } from "@/types/gamification";
import { cn } from "@/lib/cn";
import { PROFILE_PAGE } from "@/utils/i18n";

// Explicit allow-list of the Lucide icons used by badges. Importing the full
// `icons` object pulls all ~1000 Lucide icons into the bundle (~800kB); this
// keeps tree-shaking working. Keep in sync with backend achievements.py.
const BADGE_ICONS: Record<string, LucideIcon> = {
  Sparkles,
  Star,
  Flame,
  TrendingUp,
  Trophy,
};

/** Resolve a badge's Lucide icon by its PascalCase name; fall back to Award. */
function iconFor(name: string): LucideIcon {
  return BADGE_ICONS[name] ?? Award;
}

interface BadgeGridProps {
  badges: Badge[];
}

/**
 * Achievement showcase. Unlocked badges show their icon in brand green; locked
 * ones are dimmed with a lock so progress is visible without spoiling the goal.
 */
export function BadgeGrid({ badges }: BadgeGridProps) {
  if (badges.length === 0) {
    return <p className="text-sm text-text-muted">{PROFILE_PAGE.badgesEmpty}</p>;
  }

  return (
    <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {badges.map((badge) => {
        const unlocked = badge.unlocked_at != null;
        const Icon = unlocked ? iconFor(badge.icon) : Lock;
        return (
          <li
            key={badge.code}
            className={cn(
              "rounded-2xl border p-4 shadow-level-1",
              unlocked
                ? "border-border-standard bg-bg-page"
                : "border-dashed border-border-standard bg-bg-subtle",
            )}
          >
            <div
              className={cn(
                "flex h-9 w-9 items-center justify-center rounded-full",
                unlocked
                  ? "bg-brand-green/10 text-brand-green"
                  : "bg-bg-subtle text-text-muted",
              )}
            >
              <Icon className="h-5 w-5" aria-hidden="true" />
            </div>
            <p
              className={cn(
                "mt-2 text-sm font-medium",
                unlocked ? "text-text-primary" : "text-text-muted",
              )}
            >
              {badge.label}
            </p>
            <p className="mt-0.5 text-xs text-text-muted">{badge.description}</p>
          </li>
        );
      })}
    </ul>
  );
}
