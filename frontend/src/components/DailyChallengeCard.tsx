import { useNavigate } from "react-router-dom";
import { Sparkles, Zap } from "lucide-react";
import { useQuiz } from "@/hooks/useQuiz";
import { DAILY_CHALLENGE, getErrorMessage } from "@/utils/i18n";

/**
 * Daily Challenge surfacing (ROADMAP §4.8i). Fetches today's curated quiz and
 * drops into the normal quiz flow. The first request of the day runs DL
 * inference (slow) and is cached server-side; the button shows a loading state.
 * Self-contained so it can sit on both Home and Profil.
 */
export function DailyChallengeCard() {
  const navigate = useNavigate();
  const { startDailyChallenge, generating, generateError } = useQuiz();

  async function handleStart() {
    const quiz = await startDailyChallenge();
    if (quiz) navigate("/quiz", { state: { quiz } });
  }

  return (
    <section
      aria-labelledby="daily-challenge-title"
      className="overflow-hidden rounded-2xl border border-border-standard bg-bg-page shadow-level-1"
    >
      <div className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 space-y-1.5">
          <div className="flex items-center gap-2 text-brand-green">
            <Sparkles className="h-4 w-4" aria-hidden="true" />
            <span className="font-mono text-[11px] uppercase tracking-[1.2px]">
              {DAILY_CHALLENGE.eyebrow}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-brand-green/10 px-2 py-0.5 text-[10px] font-medium text-brand-green">
              <Zap className="h-3 w-3" aria-hidden="true" />
              {DAILY_CHALLENGE.bonusBadge}
            </span>
          </div>
          <h2
            id="daily-challenge-title"
            className="text-xl font-medium text-text-primary"
          >
            {DAILY_CHALLENGE.title}
          </h2>
          <p className="max-w-prose text-sm text-text-secondary">
            {DAILY_CHALLENGE.body}
          </p>
        </div>
        <div className="shrink-0">
          <button
            type="button"
            onClick={handleStart}
            disabled={generating}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-pill border border-brand-button bg-brand-button px-6 py-2.5 text-sm font-medium text-white shadow-level-1 outline-none transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover focus-visible:[box-shadow:var(--focus-ring)] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {generating ? DAILY_CHALLENGE.starting : DAILY_CHALLENGE.start}
          </button>
        </div>
      </div>
      {generateError && (
        <p
          role="alert"
          className="border-t border-border-standard px-6 py-3 text-sm text-status-rendah"
        >
          {getErrorMessage(generateError.code, generateError.message)}
        </p>
      )}
    </section>
  );
}
