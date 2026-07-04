import { useLeaderboard } from "@/hooks/useLeaderboard";
import { LEADERBOARD } from "@/utils/i18n";
import { cn } from "@/lib/cn";

interface LeaderboardCardProps {
  /** How many top players to show (default 10; the dedicated page passes more). */
  limit?: number;
}

/**
 * §4.8 — XP leaderboard. Renders nothing while loading or when gamification is
 * unavailable. Guests show as "Anonim" (privacy handled server-side).
 */
export function LeaderboardCard({ limit = 10 }: LeaderboardCardProps) {
  const state = useLeaderboard(limit);
  if (state.status !== "ready") return null;

  const { entries, you_rank } = state.data;
  if (entries.length === 0) {
    return (
      <Shell>
        <p className="text-sm text-text-muted">{LEADERBOARD.empty}</p>
      </Shell>
    );
  }

  const youInList = entries.some((e) => e.is_you);

  return (
    <Shell>
      <ol className="space-y-1.5">
        {entries.map((e) => (
          <li
            key={e.rank}
            className={cn(
              "flex items-center gap-3 rounded-xl border px-3 py-2 text-sm",
              e.is_you
                ? "border-brand-accent bg-bg-alt text-text-primary"
                : "border-transparent text-text-secondary",
            )}
          >
            <span className="w-6 flex-shrink-0 text-center font-mono text-xs tabular-nums text-text-muted">
              {e.rank}
            </span>
            <span className="flex-1 truncate font-medium text-text-primary">
              {e.is_you ? LEADERBOARD.you : e.name}
            </span>
            <span className="font-mono text-[10px] uppercase tracking-[1px] text-text-muted">
              {LEADERBOARD.levelTemplate(e.level)}
            </span>
            <span className="w-16 flex-shrink-0 text-right font-mono tabular-nums text-text-secondary">
              {e.total_xp} XP
            </span>
          </li>
        ))}
      </ol>

      {!youInList && you_rank != null && (
        <p className="mt-3 border-t border-border-standard pt-3 text-xs font-mono uppercase tracking-[1.2px] text-text-muted">
          {LEADERBOARD.yourRankTemplate(you_rank)}
        </p>
      )}
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <section
      aria-labelledby="leaderboard-heading"
      className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1"
    >
      <div className="mb-3">
        <h2
          id="leaderboard-heading"
          className="text-sm font-medium text-text-primary"
        >
          {LEADERBOARD.title}
        </h2>
        <p className="text-xs text-text-muted">{LEADERBOARD.subtitle}</p>
      </div>
      {children}
    </section>
  );
}
