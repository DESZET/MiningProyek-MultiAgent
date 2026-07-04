import { describe, it, expect, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import {
  clearQuizState,
  loadQuizState,
  useQuizPersistence,
} from "@/hooks/useQuizPersistence";
import type { Answer } from "@/types/quiz";

const QUIZ_ID = "quiz-abc";
const KEY = `asahlagi-quiz-${QUIZ_ID}`;
const answers: Answer[] = [
  { question_id: 1, selected_option_index: 2, text_answer: null },
  { question_id: 2, selected_option_index: null, text_answer: null },
];

describe("useQuizPersistence", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("saves on mount so the state can be loaded back", () => {
    renderHook(() => useQuizPersistence(QUIZ_ID, answers, 42));
    const loaded = loadQuizState(QUIZ_ID);
    expect(loaded).toEqual({ answers, seconds: 42 });
  });

  it("clearQuizState removes the saved state", () => {
    renderHook(() => useQuizPersistence(QUIZ_ID, answers, 10));
    expect(loadQuizState(QUIZ_ID)).not.toBeNull();
    clearQuizState(QUIZ_ID);
    expect(loadQuizState(QUIZ_ID)).toBeNull();
  });

  it("returns null and evicts state older than the expiry window", () => {
    const stale = {
      answers,
      seconds: 5,
      savedAt: Date.now() - 25 * 60 * 60 * 1000, // 25h ago > 24h expiry
    };
    localStorage.setItem(KEY, JSON.stringify(stale));
    expect(loadQuizState(QUIZ_ID)).toBeNull();
    expect(localStorage.getItem(KEY)).toBeNull();
  });

  it("returns null for a quiz with no saved state", () => {
    expect(loadQuizState("never-saved")).toBeNull();
  });
});
