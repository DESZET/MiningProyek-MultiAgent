/**
 * Asahi chatbot types — mirrors backend app/schemas/chat.py and docs/CHATBOT.md.
 * Interaction is button-based: `intent` is a closed union.
 */

import type { UnderstandingLevel } from "@/types/result";

export type ChatIntent =
  | "opening"
  | "weak_points"
  | "study_tips"
  | "encouragement";

export interface ChatContext {
  quiz_id?: string;
  score_percentage: number;
  understanding_level: UnderstandingLevel;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  weak_topics?: string[];
}

export interface ChatRequest {
  intent: ChatIntent;
  context: ChatContext;
}

export interface ChatResponse {
  reply: string;
}

// Free chat (open text box on the home page) — mirrors backend FreeChat* schemas.
export type ChatRole = "user" | "asahi";

export interface FreeChatMessage {
  role: ChatRole;
  content: string;
}

export interface FreeChatRequest {
  message: string;
  history: FreeChatMessage[];
}

export interface FreeChatResponse {
  reply: string;
}

export interface ChatHistoryResponse {
  messages: FreeChatMessage[];
}
