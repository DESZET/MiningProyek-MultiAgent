import {
  Award,
  Flame,
  Sparkles,
  Star,
  TrendingUp,
  Trophy,
  Zap,
  type LucideIcon,
} from "lucide-react";
import type { RecordAttemptResult } from "@/types/gamification";
import { GAMIFICATION } from "@/utils/i18n";

const BADGE_ICONS: Record<string, LucideIcon> = {
  Sparkles,
  Star,
  Flame,
  TrendingUp,
  Trophy,
  Award,
  Zap,
};

interface RewardBannerProps {
  reward: RecordAttemptResult | null;
}

/**
 * Shows the gamification reward for the just-completed quiz: XP earned,
 * an optional level-up, and any newly unlocked badges. Renders nothing when
 * gamification is unavailable (reward null).
 */
export function RewardBanner({ reward }: RewardBannerProps) {
  if (!reward) return null;

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-brand-accent bg-bg-alt p-4 shadow-level-1">
      <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-green px-3 py-1 text-sm font-medium text-[#0f0f0f]">
        <Zap className="h-4 w-4" aria-hidden="true" />
        {GAMIFICATION.xpEarnedTemplate(reward.xp_earned)}
      </span>

      {reward.leveled_up && (
        <span className="inline-flex items-center gap-1.5 text-sm font-medium text-text-primary">
          <TrendingUp className="h-4 w-4 text-brand-link" aria-hidden="true" />
          {GAMIFICATION.levelUpTemplate(reward.new_level)}
        </span>
      )}

      {reward.newly_unlocked.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          {reward.newly_unlocked.map((badge) => {
            const Icon = BADGE_ICONS[badge.icon] ?? Award;
            return (
              <span
                key={badge.code}
                className="inline-flex items-center gap-1.5 rounded-full border border-border-standard bg-bg-page px-3 py-1 text-sm text-text-primary shadow-level-1"
                title={badge.description}
              >
                <Icon className="h-4 w-4 text-status-sedang" aria-hidden="true" />
                {badge.label}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
