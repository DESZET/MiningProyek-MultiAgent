import { Flame } from "lucide-react";
import { cn } from "@/lib/cn";
import { STREAK } from "@/utils/i18n";

interface StreakCardProps {
  current: number;
  longest: number;
}

const STRIP_DAYS = 7;
const dayFmt = new Intl.DateTimeFormat("id-ID", { weekday: "narrow" });

/**
 * Streak surfacing (ROADMAP §4.8i). Shows current + longest streak with a
 * 7-day strip: the most recent `current` days (ending today) are lit. Derived
 * purely from the streak counts, so it represents the active streak length
 * rather than a precise per-day activity log.
 */
export function StreakCard({ current, longest }: StreakCardProps) {
  const today = new Date();
  const days = Array.from({ length: STRIP_DAYS }, (_, idx) => {
    const offset = STRIP_DAYS - 1 - idx; // leftmost = oldest, rightmost = today
    const date = new Date(today);
    date.setDate(today.getDate() - offset);
    return {
      key: offset,
      label: dayFmt.format(date),
      active: offset < current,
      isToday: offset === 0,
    };
  });

  return (
    <section className="space-y-4 rounded-2xl border border-border-standard bg-bg-page p-6 shadow-level-1">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Flame className="h-4 w-4 text-status-sedang" aria-hidden="true" />
          <h2 className="text-lg font-medium text-text-primary">
            {STREAK.title}
          </h2>
        </div>
        <div className="text-right">
          <div className="text-2xl font-medium tabular-nums text-text-primary">
            {current}
          </div>
          <div className="font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
            {STREAK.currentLabel}
          </div>
        </div>
      </div>

      <ul className="flex justify-between gap-1.5">
        {days.map((day) => (
          <li key={day.key} className="flex flex-1 flex-col items-center gap-1">
            <span
              className={cn(
                "flex h-9 w-full items-center justify-center rounded-lg border",
                day.active
                  ? "border-transparent bg-status-sedang text-[var(--status-sedang-text)]"
                  : "border-border-standard bg-bg-subtle text-text-muted",
                day.isToday && "ring-2 ring-brand-green ring-offset-1 ring-offset-bg-page",
              )}
            >
              {day.active && <Flame className="h-4 w-4" aria-hidden="true" />}
            </span>
            <span className="font-mono text-[10px] uppercase text-text-muted">
              {day.label}
            </span>
          </li>
        ))}
      </ul>

      {current === 0 ? (
        <p className="text-sm text-text-muted">{STREAK.emptyHint}</p>
      ) : (
        <p className="text-sm text-text-muted">
          {STREAK.longestLabel}: {longest} {STREAK.dayUnit}
        </p>
      )}
    </section>
  );
}
