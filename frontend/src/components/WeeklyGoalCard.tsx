import { useWeeklyProgress } from "@/hooks/useWeeklyProgress";
import { WEEKLY_GOAL } from "@/utils/i18n";

/**
 * §4.8 — weekly quiz goal with a progress bar. Renders nothing while loading or
 * when gamification is unavailable, so it never blocks the page.
 */
export function WeeklyGoalCard() {
  const state = useWeeklyProgress();
  if (state.status !== "ready") return null;

  const { completed, target, percent, goal_met, remaining } = state.data;

  return (
    <section
      aria-labelledby="weekly-goal-heading"
      className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1"
    >
      <div className="mb-3 flex items-baseline justify-between gap-3">
        <h2
          id="weekly-goal-heading"
          className="text-sm font-medium text-text-primary"
        >
          {WEEKLY_GOAL.title}
        </h2>
        <span className="font-mono text-xs tabular-nums text-text-secondary">
          {WEEKLY_GOAL.progressTemplate(completed, target)}
        </span>
      </div>

      <div
        className="h-2 w-full overflow-hidden rounded-full bg-bg-subtle"
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full bg-status-tinggi transition-all duration-500 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>

      <p className="mt-2 text-xs text-text-muted">
        {goal_met
          ? WEEKLY_GOAL.met
          : WEEKLY_GOAL.remainingTemplate(remaining)}
      </p>
    </section>
  );
}
