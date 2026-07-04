import type { ScoreSummary } from "@/types/result";
import { useCountUp } from "@/hooks/useCountUp";
import { STAT_LABELS, formatSeconds } from "@/utils/i18n";

interface ResultSummaryProps {
  score: ScoreSummary;
  timeTakenSeconds: number;
}

/**
 * Three-stat summary block: SKOR / WAKTU / BENAR.
 * Score and correct count animate up on mount for a small reveal moment.
 */
export function ResultSummary({ score, timeTakenSeconds }: ResultSummaryProps) {
  const animatedScore = useCountUp(score.score_percentage);
  const animatedCorrect = useCountUp(score.correct_count, { durationMs: 600 });

  return (
    <div className="flex flex-wrap gap-x-8 gap-y-4 border-t border-border-subtle pt-4">
      <Stat label={STAT_LABELS.score} value={`${animatedScore}%`} />
      <Stat label={STAT_LABELS.time} value={formatSeconds(timeTakenSeconds)} />
      <Stat
        label={STAT_LABELS.correct}
        value={`${animatedCorrect}/${score.total_questions}`}
      />
    </div>
  );
}

interface StatProps {
  label: string;
  value: string;
}

function Stat({ label, value }: StatProps) {
  return (
    <div>
      <div className="text-3xl font-medium leading-none text-text-primary">
        {value}
      </div>
      <div className="mt-1 font-mono text-[10px] font-medium uppercase tracking-[1.2px] text-text-muted">
        {label}
      </div>
    </div>
  );
}
