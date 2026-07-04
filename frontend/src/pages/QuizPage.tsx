import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { KeyboardShortcutHelp } from "@/components/KeyboardShortcutHelp";
import { QuestionPills } from "@/components/QuestionPills";
import { QuizQuestionCard } from "@/components/QuizQuestionCard";
import { QuizTimer } from "@/components/QuizTimer";
import { useQuiz } from "@/hooks/useQuiz";
import {
  clearQuizState,
  loadQuizState,
  useQuizPersistence,
} from "@/hooks/useQuizPersistence";
import { useTimer } from "@/hooks/useTimer";
import { recordQuizAttempt } from "@/services/api";
import type { Answer, QuizGenerateResponse } from "@/types/quiz";
import { isAnswered } from "@/lib/answerStatus";
import {
  BUTTON_LABELS,
  EMPTY_STATES,
  QUIZ_PAGE,
  getErrorMessage,
} from "@/utils/i18n";

interface QuizPageState {
  quiz: QuizGenerateResponse;
}

/**
 * Quiz page: one-question-at-a-time flow. User answers the current question,
 * clicks Lanjut (or Enter) to advance, and submits on the last question.
 *
 * Owner: Ravi.
 *
 * Includes:
 *   - keyboard shortcuts (1-4 to select, J/K nav, Enter advance, ? help)
 *   - auto-save to localStorage so refresh / accidental close doesn't wipe progress
 *   - slide-in animation between questions (skipped under prefers-reduced-motion)
 */
export function QuizPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as QuizPageState | null;
  const quiz = state?.quiz;

  const { submit, submitting, submitError } = useQuiz();

  const savedState = quiz ? loadQuizState(quiz.quiz_id) : null;

  const { seconds, start, stop } = useTimer({
    autoStart: true,
    initialSeconds: savedState?.seconds ?? 0,
  });

  const [answers, setAnswers] = useState<Answer[]>(() => {
    if (!quiz) return [];
    if (savedState && savedState.answers.length === quiz.total_questions) {
      return savedState.answers;
    }
    return quiz.questions.map((q) => ({
      question_id: q.id,
      selected_option_index: null,
      text_answer: null,
      matches: null,
    }));
  });

  // When restoring, jump to the first unanswered question instead of always starting at 0.
  const [currentIndex, setCurrentIndex] = useState(() => {
    if (!savedState) return 0;
    const idx = savedState.answers.findIndex(
      (a, i) => !isAnswered(a, quiz?.questions[i]?.type),
    );
    return idx === -1 ? 0 : idx;
  });
  const [helpOpen, setHelpOpen] = useState(false);
  const [showRestoredNotice, setShowRestoredNotice] = useState(
    () =>
      savedState !== null &&
      savedState.answers.some((a, i) =>
        isAnswered(a, quiz?.questions[i]?.type),
      ),
  );

  useEffect(() => {
    if (!quiz) {
      navigate("/", { replace: true });
    }
  }, [quiz, navigate]);

  useEffect(() => {
    if (!showRestoredNotice) return;
    const t = setTimeout(() => setShowRestoredNotice(false), 5000);
    return () => clearTimeout(t);
  }, [showRestoredNotice]);

  useQuizPersistence(quiz?.quiz_id ?? "", answers, seconds);

  const handleSelect = useCallback(
    (questionIndex: number, optionIndex: number) => {
      setAnswers((prev) =>
        prev.map((a, i) =>
          i === questionIndex ? { ...a, selected_option_index: optionIndex } : a,
        ),
      );
    },
    [],
  );

  const handleTextChange = useCallback(
    (questionIndex: number, text: string) => {
      setAnswers((prev) =>
        prev.map((a, i) =>
          i === questionIndex ? { ...a, text_answer: text } : a,
        ),
      );
    },
    [],
  );

  const handleMatchChange = useCallback(
    (questionIndex: number, matches: number[]) => {
      setAnswers((prev) =>
        prev.map((a, i) => (i === questionIndex ? { ...a, matches } : a)),
      );
    },
    [],
  );

  const gotoQuestion = useCallback(
    (index: number) => {
      const clamped = Math.max(
        0,
        Math.min(index, (quiz?.total_questions ?? 1) - 1),
      );
      setCurrentIndex(clamped);
    },
    [quiz?.total_questions],
  );

  const answeredCount = answers.filter((a, i) =>
    isAnswered(a, quiz?.questions[i]?.type),
  ).length;
  const allAnswered = quiz ? answeredCount === quiz.total_questions : false;
  const progressPercent = quiz
    ? (answeredCount / quiz.total_questions) * 100
    : 0;
  const isLast = !!quiz && currentIndex === quiz.total_questions - 1;
  const isFirst = currentIndex === 0;

  const handleSubmit = useCallback(async () => {
    if (!quiz) return;
    stop();
    const result = await submit({
      quiz_id: quiz.quiz_id,
      answers,
      time_taken_seconds: seconds,
    });
    if (result) {
      clearQuizState(quiz.quiz_id);
      // Record gamification before navigating so the nav widget refetches
      // fresh stats on the /result route change. Non-blocking: reward is null
      // if gamification is unavailable.
      const reward = await recordQuizAttempt({
        quiz_id: result.quiz_id,
        score: result.score.score_percentage,
        understanding_level: result.understanding_level,
      });
      navigate("/result", { state: { result, reward } });
    } else {
      start();
    }
  }, [answers, navigate, quiz, seconds, start, stop, submit]);

  const jumpToFirstUnanswered = useCallback(() => {
    const idx = answers.findIndex(
      (a, i) => !isAnswered(a, quiz?.questions[i]?.type),
    );
    if (idx !== -1) gotoQuestion(idx);
  }, [answers, gotoQuestion, quiz]);

  // Keyboard shortcuts.
  useEffect(() => {
    if (!quiz) return;

    function handleKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) {
        return;
      }

      if (e.key === "?") {
        e.preventDefault();
        setHelpOpen((s) => !s);
        return;
      }
      if (e.key === "Escape") {
        if (helpOpen) setHelpOpen(false);
        return;
      }
      if (helpOpen) return;

      if (["1", "2", "3", "4"].includes(e.key)) {
        e.preventDefault();
        handleSelect(currentIndex, Number(e.key) - 1);
        return;
      }

      if (e.key === "Enter") {
        e.preventDefault();
        if (!isLast) {
          gotoQuestion(currentIndex + 1);
        } else if (allAnswered && !submitting) {
          void handleSubmit();
        } else if (!allAnswered) {
          jumpToFirstUnanswered();
        }
        return;
      }

      if (e.key === "j" || e.key === "ArrowDown" || e.key === "ArrowRight") {
        e.preventDefault();
        gotoQuestion(currentIndex + 1);
      }
      if (e.key === "k" || e.key === "ArrowUp" || e.key === "ArrowLeft") {
        e.preventDefault();
        gotoQuestion(currentIndex - 1);
      }
    }

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [
    allAnswered,
    currentIndex,
    gotoQuestion,
    handleSelect,
    handleSubmit,
    helpOpen,
    isLast,
    jumpToFirstUnanswered,
    quiz,
    submitting,
  ]);

  if (!quiz) return null;

  const currentQuestion = quiz.questions[currentIndex];
  if (!currentQuestion) return null;

  return (
    <div className="space-y-6 pb-28">
      {/* Sticky header: title + timer + progress bar + pills */}
      <div className="sticky top-0 z-10 -mx-6 bg-bg-page/80 px-6 py-3 backdrop-blur-sm sm:-mx-0 sm:rounded-xl sm:border sm:border-border-standard sm:bg-bg-page sm:px-4 sm:shadow-level-1">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-xl font-medium tracking-tight text-text-primary sm:text-2xl">
            {QUIZ_PAGE.title}
          </h1>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setHelpOpen(true)}
              className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-border-standard bg-bg-page px-3 py-1 font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted shadow-level-1 transition-colors hover:text-text-primary"
            >
              <kbd className="inline-flex h-4 w-4 items-center justify-center rounded border border-border-prominent bg-bg-alt text-[10px]">
                ?
              </kbd>
              Shortcut
            </button>
            <QuizTimer seconds={seconds} />
          </div>
        </div>

        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-mono uppercase tracking-[1.2px] text-text-muted">
              {QUIZ_PAGE.answeredProgressTemplate(
                answeredCount,
                quiz.total_questions,
              )}
            </span>
            <span className="font-mono tabular-nums text-text-secondary">
              {Math.round(progressPercent)}%
            </span>
          </div>
          <div className="h-1 w-full overflow-hidden rounded-full bg-bg-subtle">
            <div
              className="h-full bg-status-tinggi transition-all duration-300 ease-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <QuestionPills
            answers={answers}
            currentIndex={currentIndex}
            onJump={gotoQuestion}
            questions={quiz.questions}
          />
        </div>
      </div>

      {showRestoredNotice && (
        <div
          role="status"
          className="rounded-xl border border-brand-accent bg-bg-alt p-3 text-sm text-text-secondary"
        >
          {QUIZ_PAGE.progressRestored}
        </div>
      )}

      {/* Single current question (re-mounted on index change for animation) */}
      <div
        key={currentIndex}
        className="animate-question-in"
        aria-live="polite"
      >
        <QuizQuestionCard
          question={currentQuestion}
          index={currentIndex}
          total={quiz.total_questions}
          selectedOptionIndex={
            answers[currentIndex]?.selected_option_index ?? null
          }
          textAnswer={answers[currentIndex]?.text_answer ?? null}
          matches={answers[currentIndex]?.matches ?? null}
          isCurrent
          onSelect={(opt) => handleSelect(currentIndex, opt)}
          onTextChange={(text) => handleTextChange(currentIndex, text)}
          onMatchChange={(m) => handleMatchChange(currentIndex, m)}
        />
      </div>

      {submitError && (
        <p className="rounded-xl border border-status-rendah bg-bg-alt p-3 text-sm text-status-rendah">
          {getErrorMessage(submitError.code, submitError.message)}
        </p>
      )}

      {/* Sticky bottom nav: Prev / (Next or Submit) */}
      <div className="safe-px fixed inset-x-0 bottom-0 z-10 border-t border-border-standard bg-bg-page/95 py-4 pb-[calc(1rem_+_env(safe-area-inset-bottom,0px))] backdrop-blur-sm shadow-level-3 [--safe-gutter:1.5rem]">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => gotoQuestion(currentIndex - 1)}
            disabled={isFirst || submitting}
            className="min-h-[44px] rounded-pill border border-border-standard bg-bg-page px-6 py-2.5 text-sm font-medium text-text-primary shadow-level-1 transition-colors hover:bg-bg-alt active:bg-bg-alt disabled:cursor-not-allowed disabled:opacity-40"
          >
            {BUTTON_LABELS.prevQuestion}
          </button>

          {!isLast ? (
            <button
              type="button"
              onClick={() => gotoQuestion(currentIndex + 1)}
              className="min-h-[44px] rounded-pill border border-brand-button bg-brand-button px-8 py-2.5 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover"
            >
              {BUTTON_LABELS.nextQuestion}
            </button>
          ) : allAnswered ? (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="min-h-[44px] rounded-pill border border-brand-button bg-brand-button px-8 py-2.5 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting
                ? EMPTY_STATES.submitProcessing
                : BUTTON_LABELS.submitQuiz}
            </button>
          ) : (
            <button
              type="button"
              onClick={jumpToFirstUnanswered}
              className="min-h-[44px] rounded-pill border border-brand-button bg-brand-button px-8 py-2.5 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover"
            >
              {BUTTON_LABELS.jumpToUnanswered}
            </button>
          )}
        </div>
      </div>

      <KeyboardShortcutHelp open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}
