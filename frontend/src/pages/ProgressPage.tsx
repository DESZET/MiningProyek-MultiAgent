import { Link } from "react-router-dom";
import { TrendingUp } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { MessageCard } from "@/components/MessageCard";
import { StatTile } from "@/components/StatTile";
import { ScoreTrendChart } from "@/components/ScoreTrendChart";
import { TopicMasteryList } from "@/components/TopicMasteryList";
import { useGamificationAnalytics } from "@/hooks/useGamificationAnalytics";
import type { GamificationAnalytics } from "@/types/gamification";
import { PROGRESS_PAGE } from "@/utils/i18n";

/**
 * Progress dashboard: score trend + per-topic mastery (Gamification Fase 3).
 * Owner: Ravi. Degrades gracefully when gamification is unavailable (503).
 */
export function ProgressPage() {
  const state = useGamificationAnalytics();

  if (state.status === "loading") {
    return (
      <p className="py-16 text-center text-sm text-text-muted">
        {PROGRESS_PAGE.loading}
      </p>
    );
  }

  if (state.status === "unavailable") {
    return (
      <MessageCard
        title={PROGRESS_PAGE.unavailableTitle}
        body={PROGRESS_PAGE.unavailableBody}
      />
    );
  }

  const { data } = state;
  if (data.quiz_count === 0) {
    return (
      <MessageCard title={PROGRESS_PAGE.emptyTitle} body={PROGRESS_PAGE.emptyBody}>
        <Link
          to="/app"
          className="inline-flex min-h-[44px] items-center rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover"
        >
          {PROGRESS_PAGE.emptyCta}
        </Link>
      </MessageCard>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={PROGRESS_PAGE.title}
        title={PROGRESS_PAGE.title}
        subtitle={PROGRESS_PAGE.subtitle}
        icon={TrendingUp}
      />
      <AnalyticsSummary data={data} />
      <ScoreTrendChart points={data.score_trend} />
      <TopicMasteryList items={data.topic_mastery} />
    </div>
  );
}

function AnalyticsSummary({ data }: { data: GamificationAnalytics }) {
  return (
    <div className="grid grid-cols-3 gap-3">
      <StatTile label={PROGRESS_PAGE.summaryQuizzes} value={data.quiz_count} />
      <StatTile label={PROGRESS_PAGE.summaryAvg} value={data.average_score} />
      <StatTile label={PROGRESS_PAGE.summaryXp} value={data.total_xp} />
    </div>
  );
}
