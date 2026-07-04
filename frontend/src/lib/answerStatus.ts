import type { Answer, QuestionType } from "@/types/quiz";

/**
 * Whether an answer counts as "answered", accounting for the question type.
 * Shared by QuizPage (progress, gating, restore) and QuestionPills (status dots)
 * so all surfaces agree — including short_answer and §6.2 matching.
 */
export function isAnswered(answer: Answer, type?: QuestionType): boolean {
  if (type === "short_answer") {
    return !!answer.text_answer && answer.text_answer.trim() !== "";
  }
  if (type === "matching") {
    return !!answer.matches && answer.matches.some((m) => m >= 0);
  }
  return answer.selected_option_index !== null;
}
