import type { Answer, Question } from "@/types/quiz";
import { isAnswered } from "@/lib/answerStatus";
import { cn } from "@/lib/cn";

interface QuestionPillsProps {
  answers: Answer[];
  currentIndex: number;
  onJump: (index: number) => void;
  /** Questions, so status reflects each type (short_answer, matching, …). */
  questions?: Question[];
}

/**
 * Compact pills showing per-question status: answered / current / pending.
 * Clicking a pill jumps to that question. Lives in the sticky quiz header.
 */
export function QuestionPills({
  answers,
  currentIndex,
  onJump,
  questions,
}: QuestionPillsProps) {
  return (
    <div
      role="navigation"
      aria-label="Navigasi soal"
      className="flex flex-wrap items-center gap-1.5"
    >
      {answers.map((a, i) => {
        const answered = isAnswered(a, questions?.[i]?.type);
        const isCurrent = i === currentIndex;
        return (
          <button
            key={a.question_id}
            type="button"
            onClick={() => onJump(i)}
            aria-label={`Soal ${i + 1}${answered ? ", terjawab" : ""}`}
            aria-current={isCurrent ? "step" : undefined}
            className={cn(
              "inline-flex h-8 w-8 items-center justify-center rounded-full font-mono text-[11px] font-medium transition-all",
              isCurrent
                ? "bg-text-primary text-bg-page ring-2 ring-brand-accent ring-offset-2 ring-offset-bg-page"
                : answered
                  ? "bg-status-tinggi text-[var(--status-tinggi-text)] hover:opacity-90 active:opacity-80"
                  : "border border-border-prominent bg-bg-page text-text-muted hover:border-text-muted hover:text-text-primary active:text-text-primary",
            )}
          >
            {i + 1}
          </button>
        );
      })}
    </div>
  );
}
