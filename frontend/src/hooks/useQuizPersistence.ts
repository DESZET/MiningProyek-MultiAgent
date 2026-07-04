import { useEffect } from "react";
import type { Answer } from "@/types/quiz";

const STORAGE_KEY_PREFIX = "asahlagi-quiz-";
// Stale state expires after 24 hours so an old quiz doesn't haunt the user
// if they ever return to the app days later.
const EXPIRY_MS = 24 * 60 * 60 * 1000;

interface SavedQuizState {
  answers: Answer[];
  seconds: number;
  savedAt: number;
}

function getKey(quizId: string): string {
  return `${STORAGE_KEY_PREFIX}${quizId}`;
}

export function loadQuizState(
  quizId: string,
): { answers: Answer[]; seconds: number } | null {
  try {
    const raw = localStorage.getItem(getKey(quizId));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as SavedQuizState;
    if (Date.now() - parsed.savedAt > EXPIRY_MS) {
      localStorage.removeItem(getKey(quizId));
      return null;
    }
    return { answers: parsed.answers, seconds: parsed.seconds };
  } catch {
    return null;
  }
}

function saveQuizState(
  quizId: string,
  answers: Answer[],
  seconds: number,
): void {
  try {
    const payload: SavedQuizState = { answers, seconds, savedAt: Date.now() };
    localStorage.setItem(getKey(quizId), JSON.stringify(payload));
  } catch {
    // localStorage may fail (quota exceeded, private browsing). Ignore.
  }
}

export function clearQuizState(quizId: string): void {
  try {
    localStorage.removeItem(getKey(quizId));
  } catch {
    // ignore
  }
}

/**
 * Continuously persist the quiz state (answers + elapsed time) so a refresh
 * or accidental tab close doesn't wipe progress. Caller restores via
 * `loadQuizState` before initialising local state, and calls `clearQuizState`
 * once the quiz has been submitted successfully.
 */
export function useQuizPersistence(
  quizId: string,
  answers: Answer[],
  seconds: number,
): void {
  // Save on every answer change.
  useEffect(() => {
    saveQuizState(quizId, answers, seconds);
    // We intentionally do NOT depend on seconds here; the polling effect
    // below handles time updates so we don't write on every tick.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [quizId, answers]);

  // Low-frequency time-only save so timer position survives a crash too.
  useEffect(() => {
    const interval = setInterval(() => {
      saveQuizState(quizId, answers, seconds);
    }, 10_000);
    return () => clearInterval(interval);
  }, [quizId, answers, seconds]);
}
