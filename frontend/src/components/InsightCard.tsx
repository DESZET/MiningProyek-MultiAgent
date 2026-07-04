import { CARD_LABELS } from "@/utils/i18n";

interface InsightCardProps {
  insight: string;
}

export function InsightCard({ insight }: InsightCardProps) {
  return (
    <div className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1">
      <div className="mb-2 font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
        {CARD_LABELS.insight}
      </div>
      <p className="text-base leading-relaxed text-text-secondary">{insight}</p>
    </div>
  );
}
