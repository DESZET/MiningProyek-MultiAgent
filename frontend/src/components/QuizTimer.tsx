import { STAT_LABELS, formatSeconds } from "@/utils/i18n";

interface QuizTimerProps {
  seconds: number;
}

/**
 * Display-only timer. Counts up. Driven by useTimer hook from parent.
 */
export function QuizTimer({ seconds }: QuizTimerProps) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-border-standard bg-bg-page px-3 py-1 font-mono text-xs text-text-secondary shadow-level-1">
      <span className="font-medium text-text-muted">{STAT_LABELS.time}</span>
      <span className="font-medium text-text-primary">
        {formatSeconds(seconds)}
      </span>
    </div>
  );
}
