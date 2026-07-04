import type { QuestionReview } from "@/types/result";
import { CARD_LABELS, QUIZ_PAGE, REVIEW_LABELS } from "@/utils/i18n";
import { cn } from "@/lib/cn";

interface QuestionBreakdownProps {
  reviews: QuestionReview[];
}

/**
 * Per-question review section. For each question, shows the prompt, all
 * options, the user's pick (if any), and the correct answer. Turns the
 * quiz from a pass/fail moment into a learning moment.
 */
export function QuestionBreakdown({ reviews }: QuestionBreakdownProps) {
  if (reviews.length === 0) return null;

  return (
    <section className="space-y-3">
      <h2 className="font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
        {CARD_LABELS.reviewSection}
      </h2>
      <div className="space-y-3">
        {reviews.map((review, i) => (
          <ReviewCard key={review.question_id} review={review} index={i} total={reviews.length} />
        ))}
      </div>
    </section>
  );
}

interface ReviewCardProps {
  review: QuestionReview;
  index: number;
  total: number;
}

function ReviewCard({ review, index, total }: ReviewCardProps) {
  const statusLabel = review.is_unanswered
    ? REVIEW_LABELS.unanswered
    : review.is_correct
      ? REVIEW_LABELS.correct
      : REVIEW_LABELS.wrong;

  const statusClass = review.is_unanswered
    ? "bg-status-sedang text-[var(--status-sedang-text)]"
    : review.is_correct
      ? "bg-status-tinggi text-[var(--status-tinggi-text)]"
      : "bg-status-rendah text-[var(--status-rendah-text)]";

  return (
    <article className="rounded-2xl border border-border-standard bg-bg-page p-5 shadow-level-1">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <span className="font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted">
          {QUIZ_PAGE.questionLabelTemplate(index, total)}
        </span>
        <span
          className={cn(
            "rounded-full px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[1.2px]",
            statusClass,
          )}
        >
          {statusLabel}
        </span>
      </div>

      <h3 className="mb-4 text-base font-medium leading-snug text-text-primary">
        {review.question}
      </h3>

      {review.type === "matching" && review.left_items && review.right_items ? (
        <MatchingReview review={review} />
      ) : (
        <ul className="space-y-1.5">
          {review.options.map((option, i) => {
            const isUserPick = review.selected_option_index === i;
            const isCorrect = review.correct_option_index === i;

            return (
              <li
                key={i}
                className={cn(
                  "flex items-start gap-3 rounded-lg border px-3 py-2 text-sm",
                  isCorrect
                    ? "border-status-tinggi/40 bg-status-tinggi/10 text-text-primary"
                    : isUserPick
                      ? "border-status-rendah/40 bg-status-rendah/10 text-text-primary"
                      : "border-transparent text-text-secondary",
                )}
              >
                <span className="mt-0.5 inline-flex h-5 w-5 flex-shrink-0 items-center justify-center font-mono text-[11px] text-text-muted">
                  {String.fromCharCode(65 + i)}
                </span>
                <span className="flex-1">{option}</span>
                {isCorrect && <CheckIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-status-tinggi" />}
                {isUserPick && !isCorrect && (
                  <CrossIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-status-rendah" />
                )}
              </li>
            );
          })}
        </ul>
      )}

      {review.is_unanswered && (
        <p className="mt-3 text-xs font-mono uppercase tracking-[1.2px] text-text-muted">
          {REVIEW_LABELS.noAnswer}
        </p>
      )}
    </article>
  );
}

function MatchingReview({ review }: { review: QuestionReview }) {
  const left = review.left_items ?? [];
  const right = review.right_items ?? [];
  const matches = review.matches ?? [];
  const correct = review.correct_matches ?? [];

  return (
    <ul className="space-y-2">
      {left.map((term, i) => {
        const userIdx = matches[i] ?? -1;
        const correctIdx = correct[i] ?? -1;
        const isCorrect = userIdx === correctIdx;
        const userText = userIdx >= 0 ? right[userIdx] : REVIEW_LABELS.noAnswer;

        return (
          <li
            key={i}
            className={cn(
              "rounded-lg border px-3 py-2 text-sm",
              isCorrect
                ? "border-status-tinggi/40 bg-status-tinggi/10"
                : "border-status-rendah/40 bg-status-rendah/10",
            )}
          >
            <div className="flex items-start gap-2">
              <span className="font-medium text-text-primary">{term}</span>
              {isCorrect ? (
                <CheckIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-status-tinggi" />
              ) : (
                <CrossIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-status-rendah" />
              )}
            </div>
            <p className="mt-1 text-text-secondary">
              <span className="text-text-muted">{REVIEW_LABELS.yourAnswer}: </span>
              {userText}
            </p>
            {!isCorrect && correctIdx >= 0 && (
              <p className="text-text-secondary">
                <span className="text-text-muted">{REVIEW_LABELS.correctAnswer}: </span>
                {right[correctIdx]}
              </p>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <polyline points="3 8.5 6.5 12 13 4.5" />
    </svg>
  );
}

function CrossIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      className={className}
      aria-hidden="true"
    >
      <line x1="4" y1="4" x2="12" y2="12" />
      <line x1="12" y1="4" x2="4" y2="12" />
    </svg>
  );
}
