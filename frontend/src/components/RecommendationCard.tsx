import { CARD_LABELS } from "@/utils/i18n";

interface RecommendationCardProps {
  recommendation: string;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <div className="rounded-2xl border border-brand-accent bg-bg-page p-5 shadow-level-1">
      <div className="mb-2 font-mono text-[11px] uppercase tracking-[1.2px] text-brand-link">
        {CARD_LABELS.recommendation}
      </div>
      <p className="text-base leading-relaxed text-text-primary">
        {recommendation}
      </p>
    </div>
  );
}
