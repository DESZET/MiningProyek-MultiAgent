import { Trophy } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { LeaderboardCard } from "@/components/LeaderboardCard";
import { LEADERBOARD } from "@/utils/i18n";

/**
 * §4.8 — dedicated leaderboard page (linked from the account menu). Shows the
 * top 50 players by XP.
 */
export function LeaderboardPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <PageHeader
        eyebrow={LEADERBOARD.eyebrow}
        title={LEADERBOARD.title}
        subtitle={LEADERBOARD.subtitle}
        icon={Trophy}
      />
      <LeaderboardCard limit={50} />
    </div>
  );
}
