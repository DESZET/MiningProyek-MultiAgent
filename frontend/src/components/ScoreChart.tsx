import type { ChartData } from "@/types/result";
import { CARD_LABELS, STAT_LABELS } from "@/utils/i18n";

interface ScoreChartProps {
  data: ChartData;
}

/**
 * Minimal stacked-bar chart: correct / wrong / unanswered.
 * Pure CSS, no chart library dependency.
 */
export function ScoreChart({ data }: ScoreChartProps) {
  const total = data.correct + data.wrong + data.unanswered;
  if (total === 0) return null;

  const correctPct = (data.correct / total) * 100;
  const wrongPct = (data.wrong / total) * 100;
  const unansweredPct = (data.unanswered / total) * 100;

  return (
    <div className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1">
      <div className="mb-3 font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
        {CARD_LABELS.chartDistribution}
      </div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-bg-subtle">
        {data.correct > 0 && (
          <div
            className="h-full bg-status-tinggi"
            style={{ width: `${correctPct}%` }}
            aria-label={`${data.correct} ${STAT_LABELS.correct.toLowerCase()}`}
          />
        )}
        {data.wrong > 0 && (
          <div
            className="h-full bg-status-rendah"
            style={{ width: `${wrongPct}%` }}
            aria-label={`${data.wrong} ${STAT_LABELS.wrong.toLowerCase()}`}
          />
        )}
        {data.unanswered > 0 && (
          <div
            className="h-full bg-status-sedang"
            style={{ width: `${unansweredPct}%` }}
            aria-label={`${data.unanswered} ${STAT_LABELS.unanswered.toLowerCase()}`}
          />
        )}
      </div>
      <div className="mt-3 flex flex-wrap gap-4 font-mono text-[11px] uppercase tracking-[1.2px]">
        <Legend color="bg-status-tinggi" label={STAT_LABELS.correct} value={data.correct} />
        <Legend color="bg-status-rendah" label={STAT_LABELS.wrong} value={data.wrong} />
        <Legend color="bg-status-sedang" label={STAT_LABELS.unanswered} value={data.unanswered} />
      </div>
    </div>
  );
}

function Legend({ color, label, value }: { color: string; label: string; value: number }) {
  return (
    <div className="flex items-center gap-2 text-text-muted">
      <span className={`inline-block h-2 w-2 rounded-sm ${color}`} aria-hidden="true" />
      <span className="text-text-secondary">{label}</span>
      <span className="font-medium text-text-primary">{value}</span>
    </div>
  );
}
