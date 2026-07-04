import type { TrendPoint } from "@/types/gamification";
import { barExtent, formatTrendDate, scoreTone } from "@/lib/mastery";
import { PROGRESS_PAGE } from "@/utils/i18n";

interface ScoreTrendChartProps {
  points: TrendPoint[];
}

// Keep the chart readable on mobile: show the most recent N days only.
const MAX_POINTS = 14;

/**
 * Vertical bar chart of average score per day. Pure CSS, no chart library —
 * consistent with ScoreChart. Bar height encodes score (0-100), color encodes
 * the mastery tier.
 */
export function ScoreTrendChart({ points }: ScoreTrendChartProps) {
  const recent = points.slice(-MAX_POINTS);

  return (
    <section className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1">
      <header className="mb-1 flex items-baseline justify-between gap-3">
        <h2 className="font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
          {PROGRESS_PAGE.trendTitle}
        </h2>
        <span className="text-[11px] text-text-muted">
          {PROGRESS_PAGE.trendCaption}
        </span>
      </header>

      {recent.length === 0 ? (
        <p className="py-8 text-center text-sm text-text-muted">
          {PROGRESS_PAGE.trendEmpty}
        </p>
      ) : (
        <ul className="mt-4 flex h-40 items-end gap-2" aria-label={PROGRESS_PAGE.trendCaption}>
          {recent.map((point) => {
            const height = barExtent(point.average_score);
            const tone = scoreTone(point.average_score);
            const dateLabel = formatTrendDate(point.date);
            return (
              <li
                key={point.date}
                className="flex h-full flex-1 flex-col items-center justify-end gap-1.5"
                title={`${dateLabel}: ${point.average_score} (${point.attempt_count}×)`}
              >
                <span className="text-[10px] font-medium tabular-nums text-text-secondary">
                  {point.average_score}
                </span>
                <span
                  className={`w-full rounded-t-md ${tone.bar} transition-all duration-500 ease-out`}
                  style={{ height: `${height}%` }}
                  aria-label={`${dateLabel}: rata-rata ${point.average_score} dari ${point.attempt_count} kuis`}
                />
                <span className="font-mono text-[9px] uppercase tracking-[0.6px] text-text-muted">
                  {dateLabel}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
