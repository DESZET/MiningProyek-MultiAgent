import { useEffect, useMemo } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { AsahiDialog } from "@/components/AsahiDialog";
import { InsightCard } from "@/components/InsightCard";
import { QuestionBreakdown } from "@/components/QuestionBreakdown";
import { RecommendationCard } from "@/components/RecommendationCard";
import { ResultSummary } from "@/components/ResultSummary";
import { RewardBanner } from "@/components/RewardBanner";
import { ScoreChart } from "@/components/ScoreChart";
import { ShareResultButton } from "@/components/ShareResultButton";
import { UnderstandingBadge } from "@/components/UnderstandingBadge";
import { useConfetti } from "@/hooks/useConfetti";
import { useQuiz } from "@/hooks/useQuiz";
import { decodeSharedResult } from "@/lib/shareResult";
import type { ChatContext } from "@/types/chat";
import type { RecordAttemptResult } from "@/types/gamification";
import type { QuizSubmitResponse } from "@/types/result";
import {
  BUTTON_LABELS,
  RESULT_HEADERS,
  RESULT_SHARE,
  getErrorMessage,
} from "@/utils/i18n";

const CONFETTI_SCORE_THRESHOLD = 80;

interface ResultPageState {
  result: QuizSubmitResponse;
  reward?: RecordAttemptResult | null;
}

/**
 * Result page: display score, level, insight, recommendation, and chart.
 * Owner: Ravi.
 */
export function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const state = location.state as ResultPageState | null;
  const stateResult = state?.result ?? null;
  const reward = state?.reward ?? null;

  // §4.2: a result opened from a shared link (?s=token) is decoded into a
  // read-only view. Owner-only affordances (retry, chat, reward, breakdown) are
  // hidden in this mode since there is no backend session behind it.
  const sharedToken = searchParams.get("s");
  const sharedResult = useMemo(
    () => (sharedToken ? decodeSharedResult(sharedToken) : null),
    [sharedToken],
  );
  const result: QuizSubmitResponse | null = useMemo(() => {
    if (stateResult) return stateResult;
    if (sharedResult) {
      return {
        quiz_id: "",
        score: sharedResult.score,
        time_taken_seconds: sharedResult.time_taken_seconds,
        understanding_level: sharedResult.understanding_level,
        insight: sharedResult.insight,
        recommendation: sharedResult.recommendation,
        chart_data: sharedResult.chart_data,
        submitted_at: "",
        question_reviews: [],
      };
    }
    return null;
  }, [stateResult, sharedResult]);

  const isShared = !stateResult && !!sharedResult;

  const { regenerate, generating: regenerating, generateError } = useQuiz();

  useEffect(() => {
    if (!result) {
      navigate("/", { replace: true });
    }
  }, [result, navigate]);

  useConfetti(
    !isShared &&
      !!result &&
      result.score.score_percentage >= CONFETTI_SCORE_THRESHOLD,
  );

  const chatContext = useMemo<ChatContext | null>(
    () =>
      result && !isShared
        ? {
            quiz_id: result.quiz_id,
            score_percentage: result.score.score_percentage,
            understanding_level: result.understanding_level,
            correct_count: result.score.correct_count,
            wrong_count: result.score.wrong_count,
            unanswered_count: result.score.unanswered_count,
            weak_topics: [],
          }
        : null,
    [result, isShared],
  );

  if (!result) return null;

  async function handleRetry() {
    if (!result) return;
    const newQuiz = await regenerate(result.quiz_id);
    if (newQuiz) {
      navigate("/quiz", { state: { quiz: newQuiz }, replace: true });
    }
  }

  const headers = RESULT_HEADERS[result.understanding_level];

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <UnderstandingBadge level={result.understanding_level} />
        <h1 className="text-4xl font-medium leading-tight tracking-tight text-text-primary">
          {headers.headline}
        </h1>
        <p className="text-lg text-text-secondary">{headers.subhead}</p>
      </header>

      {isShared ? (
        <p className="rounded-xl border border-border-standard bg-bg-alt p-4 text-sm text-text-secondary">
          {RESULT_SHARE.sharedBanner}
        </p>
      ) : (
        <RewardBanner reward={reward} />
      )}

      <ResultSummary
        score={result.score}
        timeTakenSeconds={result.time_taken_seconds}
      />

      <div className="grid gap-4 md:grid-cols-2">
        <InsightCard insight={result.insight} />
        <RecommendationCard recommendation={result.recommendation} />
      </div>

      <ScoreChart data={result.chart_data} />

      {chatContext && <AsahiDialog context={chatContext} />}

      {result.question_reviews && result.question_reviews.length > 0 && (
        <QuestionBreakdown reviews={result.question_reviews} />
      )}

      {generateError && (
        <p className="rounded-xl border border-status-rendah bg-bg-alt p-3 text-sm text-status-rendah">
          {getErrorMessage(generateError.code, generateError.message)}
        </p>
      )}

      <div className="flex flex-wrap gap-3">
        {isShared ? (
          <button
            type="button"
            onClick={() => navigate("/app")}
            className="min-h-[44px] rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover"
          >
            {RESULT_SHARE.ctaCreate}
          </button>
        ) : (
          <>
            <button
              type="button"
              onClick={handleRetry}
              disabled={regenerating}
              className="min-h-[44px] rounded-pill border border-brand-button bg-brand-button px-8 py-2 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
            >
              {regenerating ? BUTTON_LABELS.resultRetryLoading : BUTTON_LABELS.resultRetry}
            </button>
            <ShareResultButton result={result} />
            <button
              type="button"
              onClick={() => navigate("/", { replace: true })}
              disabled={regenerating}
              className="min-h-[44px] rounded-md border border-transparent bg-transparent px-4 py-2 text-sm font-medium text-text-primary hover:bg-[var(--hover-tint)] active:bg-[var(--hover-tint)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {BUTTON_LABELS.backToHome}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
