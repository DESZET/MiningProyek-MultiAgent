import type { TopicMasteryItem } from "@/types/gamification";
import { barExtent, scoreTone } from "@/lib/mastery";
import { PROGRESS_PAGE } from "@/utils/i18n";

interface TopicMasteryListProps {
  items: TopicMasteryItem[];
}

/**
 * Per-topic mastery list, sorted weakest-first so the topics that need the most
 * work surface at the top. Each row shows an average-score bar (tone by tier)
 * and the attempt count; the weakest topic gets a subtle "needs work" hint.
 */
export function TopicMasteryList({ items }: TopicMasteryListProps) {
  // Immutable sort (ascending average) — do not mutate the prop array.
  const sorted = [...items].sort((a, b) => a.average_score - b.average_score);

  return (
    <section className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1">
      <header className="mb-1 flex items-baseline justify-between gap-3">
        <h2 className="font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
          {PROGRESS_PAGE.masteryTitle}
        </h2>
        {sorted.length > 0 && (
          <span className="text-[11px] text-text-muted">
            {PROGRESS_PAGE.masteryCaption}
          </span>
        )}
      </header>

      {sorted.length === 0 ? (
        <p className="py-8 text-center text-sm text-text-muted">
          {PROGRESS_PAGE.masteryEmpty}
        </p>
      ) : (
        <ul className="mt-4 space-y-4">
          {sorted.map((item, index) => {
            const tone = scoreTone(item.average_score);
            const width = barExtent(item.average_score);
            const isWeakest = index === 0;
            return (
              <li key={item.topic}>
                <div className="mb-1 flex items-baseline justify-between gap-3">
                  <span className="truncate text-sm font-medium text-text-primary">
                    {item.topic}
                  </span>
                  <span className={`text-sm font-medium tabular-nums ${tone.text}`}>
                    {item.average_score}
                  </span>
                </div>
                <div
                  className="h-2 w-full overflow-hidden rounded-full bg-bg-subtle"
                  role="meter"
                  aria-valuenow={item.average_score}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={item.topic}
                >
                  <div
                    className={`h-full rounded-full ${tone.bar} transition-all duration-500 ease-out`}
                    style={{ width: `${width}%` }}
                  />
                </div>
                <div className="mt-1 flex items-center justify-between gap-3">
                  <span className="font-mono text-[10px] uppercase tracking-[0.6px] text-text-muted">
                    {PROGRESS_PAGE.attemptsTemplate(item.attempt_count)}
                  </span>
                  {isWeakest && (
                    <span className="text-[10px] font-medium text-status-rendah">
                      {PROGRESS_PAGE.masteryWeakestHint}
                    </span>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
