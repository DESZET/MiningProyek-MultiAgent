import { Link } from "react-router-dom";
import {
  ChevronRight,
  CircleUserRound,
  Settings,
  Trophy,
  TrendingUp,
  User,
  Zap,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { MessageCard } from "@/components/MessageCard";
import { StatTile } from "@/components/StatTile";
import { BadgeGrid } from "@/components/BadgeGrid";
import { HistoryItemRow } from "@/components/HistoryItemRow";
import { DailyChallengeCard } from "@/components/DailyChallengeCard";
import { StreakCard } from "@/components/StreakCard";
import { WeeklyGoalCard } from "@/components/WeeklyGoalCard";
import { BookmarksList } from "@/components/BookmarksList";
import { GoogleLoginButton } from "@/components/auth/GoogleLoginButton";
import { useProfileData } from "@/hooks/useProfileData";
import { useAuth } from "@/context/AuthContext";
import type { AuthUser } from "@/types/auth";
import { PROFILE_PAGE } from "@/utils/i18n";

/**
 * Profile hub (ROADMAP §4.8a): identity + gamification summary + badges +
 * recent history, with links out to Progress and Settings. Works for guests
 * (device-id identity) and logged-in users alike; gracefully off when the
 * gamification backend is unavailable.
 */
export function ProfilePage() {
  const state = useProfileData();
  const { user, isConfigured } = useAuth();

  if (state.status === "loading") {
    return (
      <p className="py-16 text-center text-sm text-text-muted">
        {PROFILE_PAGE.loading}
      </p>
    );
  }

  if (state.status === "unavailable") {
    return (
      <MessageCard
        title={PROFILE_PAGE.unavailableTitle}
        body={PROFILE_PAGE.unavailableBody}
      />
    );
  }

  const { stats, achievements, summary, recent } = state;
  const totalQuizzes = summary?.total_quizzes ?? 0;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={PROFILE_PAGE.eyebrow}
        title={PROFILE_PAGE.title}
        subtitle={PROFILE_PAGE.subtitle}
        icon={CircleUserRound}
      />

      <IdentityCard user={user} isConfigured={isConfigured} />

      <DailyChallengeCard />

      <div className="grid grid-cols-3 gap-3">
        <StatTile label={PROFILE_PAGE.summaryLevel} value={stats.level} icon={Zap} />
        <StatTile label={PROFILE_PAGE.summaryXp} value={stats.total_xp} />
        <StatTile label={PROFILE_PAGE.summaryQuizzes} value={totalQuizzes} />
      </div>

      <StreakCard current={stats.current_streak} longest={stats.longest_streak} />

      <WeeklyGoalCard />

      <BookmarksList />

      <section className="space-y-3" aria-labelledby="badges-heading">
        <SectionHeading id="badges-heading" icon={Trophy} title={PROFILE_PAGE.badgesTitle} caption={PROFILE_PAGE.badgesCaption} />
        <BadgeGrid badges={achievements} />
      </section>

      <section className="space-y-3" aria-labelledby="recent-heading">
        <SectionHeading id="recent-heading" icon={Zap} title={PROFILE_PAGE.recentTitle} />
        {recent.length === 0 ? (
          <p className="text-sm text-text-muted">{PROFILE_PAGE.recentEmpty}</p>
        ) : (
          <>
            <ul className="space-y-3">
              {recent.map((item) => (
                <HistoryItemRow key={item.quiz_id} item={item} />
              ))}
            </ul>
            <Link
              to="/riwayat"
              className="inline-flex items-center gap-1 text-sm font-medium text-brand-link outline-none hover:underline focus-visible:underline"
            >
              {PROFILE_PAGE.recentSeeAll}
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </>
        )}
      </section>

      <nav className="grid gap-3 sm:grid-cols-2" aria-label="Tautan akun">
        <HubLink to="/progress" icon={TrendingUp} label={PROFILE_PAGE.linkProgress} />
        <HubLink to="/pengaturan" icon={Settings} label={PROFILE_PAGE.linkSettings} />
      </nav>
    </div>
  );
}

function IdentityCard({
  user,
  isConfigured,
}: {
  user: AuthUser | null;
  isConfigured: boolean;
}) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-border-standard bg-bg-page p-6 shadow-level-1 sm:flex-row sm:items-center">
      <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full border border-border-standard bg-bg-subtle text-text-muted">
        {user?.avatar_url ? (
          <img
            src={user.avatar_url}
            alt=""
            className="h-full w-full object-cover"
            referrerPolicy="no-referrer"
          />
        ) : (
          <User className="h-7 w-7" aria-hidden="true" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-lg font-medium text-text-primary">
          {user?.name ?? PROFILE_PAGE.guestName}
        </p>
        {user?.email ? (
          <p className="truncate text-sm text-text-muted">{user.email}</p>
        ) : (
          <p className="text-sm text-text-secondary">{PROFILE_PAGE.guestNote}</p>
        )}
      </div>
      {!user && isConfigured && (
        <div className="shrink-0">
          <GoogleLoginButton />
        </div>
      )}
    </div>
  );
}

function SectionHeading({
  id,
  icon: Icon,
  title,
  caption,
}: {
  id: string;
  icon: typeof Trophy;
  title: string;
  caption?: string;
}) {
  return (
    <div>
      <h2
        id={id}
        className="flex items-center gap-2 text-lg font-medium text-text-primary"
      >
        <Icon className="h-4 w-4 text-brand-green" aria-hidden="true" />
        {title}
      </h2>
      {caption && <p className="mt-0.5 text-sm text-text-muted">{caption}</p>}
    </div>
  );
}

function HubLink({
  to,
  icon: Icon,
  label,
}: {
  to: string;
  icon: typeof Trophy;
  label: string;
}) {
  return (
    <Link
      to={to}
      className="flex items-center justify-between gap-3 rounded-2xl border border-border-standard bg-bg-page p-4 shadow-level-1 outline-none transition-colors hover:bg-[var(--hover-tint)] focus-visible:[box-shadow:var(--focus-ring)]"
    >
      <span className="flex items-center gap-2 text-sm font-medium text-text-primary">
        <Icon className="h-4 w-4 text-brand-green" aria-hidden="true" />
        {label}
      </span>
      <ChevronRight className="h-4 w-4 text-text-muted" aria-hidden="true" />
    </Link>
  );
}
