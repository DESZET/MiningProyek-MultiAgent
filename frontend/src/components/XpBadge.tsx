import { Flame, Zap } from "lucide-react";
import type { GamificationStats } from "@/types/gamification";
import { GAMIFICATION } from "@/utils/i18n";

interface XpBadgeProps {
  stats: GamificationStats | null;
}

/**
 * Compact nav widget: level + XP progress + streak. Hidden when stats is null
 * (gamification unavailable). Lives in the top nav next to the theme toggle.
 */
export function XpBadge({ stats }: XpBadgeProps) {
  if (!stats) return null;

  const pct =
    stats.xp_for_next_level > 0
      ? Math.min(100, Math.round((stats.xp_into_level / stats.xp_for_next_level) * 100))
      : 0;

  return (
    <div className="flex items-center gap-2.5">
      {/* Level + XP progress */}
      <div
        className="flex items-center gap-2 rounded-full border border-border-standard bg-bg-page px-3 py-1 shadow-level-1"
        title={`${stats.total_xp} XP total`}
      >
        <Zap className="h-3.5 w-3.5 text-brand-green" aria-hidden="true" />
        <span className="whitespace-nowrap font-mono text-[11px] font-medium uppercase tracking-[1.2px] text-text-primary">
          {GAMIFICATION.levelShort} {stats.level}
        </span>
        <span
          className="hidden h-1 w-12 overflow-hidden rounded-full bg-bg-subtle sm:block"
          aria-label={`${pct}% menuju level berikutnya`}
        >
          <span
            className="block h-full bg-brand-green transition-all duration-500 ease-out"
            style={{ width: `${pct}%` }}
          />
        </span>
      </div>

      {/* Streak — hidden on mobile to keep the dense nav from overflowing; the
          full streak lives on Profil (StreakCard). */}
      {stats.current_streak > 0 && (
        <div
          className="hidden items-center gap-1 rounded-full border border-border-standard bg-bg-page px-2.5 py-1 shadow-level-1 sm:flex"
          title={`Streak ${stats.current_streak} hari`}
        >
          <Flame className="h-3.5 w-3.5 text-status-sedang" aria-hidden="true" />
          <span className="font-mono text-[11px] font-medium tabular-nums text-text-primary">
            {stats.current_streak}
          </span>
        </div>
      )}
    </div>
  );
}
