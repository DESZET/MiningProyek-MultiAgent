/**
 * Result-related types — mirrors API.md §5.1, 5.5.
 * Source of truth: /API.md
 */

export type UnderstandingLevel = "high" | "medium" | "low";

export interface ScoreSummary {
  score_percentage: number;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  total_questions: number;
}

export interface ChartData {
  correct: number;
  wrong: number;
  unanswered: number;
}

export type QuestionType =
  | "multiple_choice"
  | "true_false"
  | "short_answer"
  | "matching";

export interface QuestionReview {
  question_id: number;
  type: QuestionType;
  question: string;
  options: string[];
  selected_option_index: number | null;
  correct_option_index: number | null;
  is_correct: boolean;
  is_unanswered: boolean;
  // §6.2 matching review
  left_items?: string[] | null;
  right_items?: string[] | null;
  matches?: number[] | null;
  correct_matches?: number[] | null;
}

export interface QuizSubmitResponse {
  quiz_id: string;
  score: ScoreSummary;
  time_taken_seconds: number;
  understanding_level: UnderstandingLevel;
  insight: string;
  recommendation: string;
  chart_data: ChartData;
  submitted_at: string;
  question_reviews: QuestionReview[];
}
