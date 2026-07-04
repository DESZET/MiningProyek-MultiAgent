import { Zap } from "lucide-react";
import type { HistoryItem } from "@/types/gamification";
import { UnderstandingBadge } from "@/components/UnderstandingBadge";
import { HISTORY_PAGE, formatDate, toUnderstandingLevel } from "@/utils/i18n";

interface HistoryItemRowProps {
  item: HistoryItem;
}

/**
 * One quiz attempt: date + topic, understanding level, score, and XP earned.
 * Display-only — quiz sessions are ephemeral server-side, so we don't promise
 * re-opening the exact quiz (see Product Rules: stay honest).
 */
export function HistoryItemRow({ item }: HistoryItemRowProps) {
  const level = toUnderstandingLevel(item.understanding_level);

  return (
    <li className="flex items-center justify-between gap-4 rounded-2xl border border-border-standard bg-bg-page p-4 shadow-level-1">
      <div className="min-w-0 space-y-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-medium text-text-primary">
            {item.topic?.trim() || HISTORY_PAGE.noTopic}
          </span>
          {level && <UnderstandingBadge level={level} />}
        </div>
        <div className="flex items-center gap-3 text-xs text-text-muted">
          <span>{formatDate(item.completed_at)}</span>
          <span className="inline-flex items-center gap-1">
            <Zap className="h-3 w-3 text-brand-green" aria-hidden="true" />
            {HISTORY_PAGE.xpTemplate(item.xp_earned)}
          </span>
        </div>
      </div>
      <div className="shrink-0 text-right">
        <div className="text-2xl font-medium tabular-nums text-text-primary">
          {item.score}
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
          {HISTORY_PAGE.scoreUnit}
        </div>
      </div>
    </li>
  );
}
