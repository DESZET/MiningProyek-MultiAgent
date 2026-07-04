import { Link } from "react-router-dom";
import { History } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { MessageCard } from "@/components/MessageCard";
import { StatTile } from "@/components/StatTile";
import { HistoryItemRow } from "@/components/HistoryItemRow";
import { useGamificationHistory } from "@/hooks/useGamificationHistory";
import type { HistorySummary } from "@/types/gamification";
import { HISTORY_PAGE } from "@/utils/i18n";

/**
 * Quiz history (ROADMAP §4.8c). DB-backed via /gamification/history, scoped to
 * the device id (carries over to the account after Google login). Degrades
 * gracefully to an "off" state when gamification is unavailable.
 */
export function HistoryPage() {
  const state = useGamificationHistory(50);

  if (state.status === "loading") {
    return (
      <p className="py-16 text-center text-sm text-text-muted">
        {HISTORY_PAGE.loading}
      </p>
    );
  }

  if (state.status === "unavailable") {
    return (
      <MessageCard
        title={HISTORY_PAGE.unavailableTitle}
        body={HISTORY_PAGE.unavailableBody}
      />
    );
  }

  const { summary, items } = state.data;

  if (items.length === 0) {
    return (
      <MessageCard title={HISTORY_PAGE.emptyTitle} body={HISTORY_PAGE.emptyBody}>
        <Link
          to="/app"
          className="rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover"
        >
          {HISTORY_PAGE.emptyCta}
        </Link>
      </MessageCard>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={HISTORY_PAGE.eyebrow}
        title={HISTORY_PAGE.title}
        subtitle={HISTORY_PAGE.subtitle}
        icon={History}
      />
      <HistorySummaryGrid summary={summary} />
      <ul className="space-y-3">
        {items.map((item) => (
          <HistoryItemRow key={item.quiz_id} item={item} />
        ))}
      </ul>
    </div>
  );
}

function HistorySummaryGrid({ summary }: { summary: HistorySummary }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <StatTile label={HISTORY_PAGE.summaryQuizzes} value={summary.total_quizzes} />
      <StatTile label={HISTORY_PAGE.summaryAvg} value={summary.average_score} />
      <StatTile label={HISTORY_PAGE.summaryBest} value={summary.best_score} />
      <StatTile label={HISTORY_PAGE.summaryXp} value={summary.total_xp} />
    </div>
  );
}
