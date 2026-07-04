/**
 * Shareable result links (ROADMAP §4.2).
 *
 * The result is encoded into the URL itself (URL-safe base64 of a compact JSON),
 * so a shared link is fully self-contained — it does NOT depend on the backend,
 * whose quiz store is in-memory and whose free HF Space sleeps. Anyone opening
 * the link sees a read-only result view.
 *
 * Only the summary is shared (score, level, insight, recommendation, time) — NOT
 * the per-question breakdown, so we don't leak full quiz content in a public URL.
 */

import type {
  ChartData,
  QuizSubmitResponse,
  ScoreSummary,
  UnderstandingLevel,
} from "@/types/result";

export interface SharedResult {
  score: ScoreSummary;
  time_taken_seconds: number;
  understanding_level: UnderstandingLevel;
  insight: string;
  recommendation: string;
  chart_data: ChartData;
}

const LEVELS: readonly UnderstandingLevel[] = ["high", "medium", "low"];

// Compact wire shape — short keys keep the URL short.
interface Wire {
  p: number; // score_percentage
  c: number; // correct_count
  w: number; // wrong_count
  u: number; // unanswered_count
  t: number; // total_questions
  ts: number; // time_taken_seconds
  l: UnderstandingLevel;
  i: string; // insight
  r: string; // recommendation
}

function toBase64Url(bytes: Uint8Array): string {
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(s: string): Uint8Array {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/");
  const pad = b64.length % 4 ? "=".repeat(4 - (b64.length % 4)) : "";
  const bin = atob(b64 + pad);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

/** Encode a result summary into a URL-safe token. */
export function encodeSharedResult(result: SharedResult): string {
  const wire: Wire = {
    p: result.score.score_percentage,
    c: result.score.correct_count,
    w: result.score.wrong_count,
    u: result.score.unanswered_count,
    t: result.score.total_questions,
    ts: result.time_taken_seconds,
    l: result.understanding_level,
    i: result.insight,
    r: result.recommendation,
  };
  return toBase64Url(new TextEncoder().encode(JSON.stringify(wire)));
}

function isNum(v: unknown): v is number {
  return typeof v === "number" && Number.isFinite(v);
}

/** Decode a token back into a result summary. Returns null if malformed. */
export function decodeSharedResult(token: string): SharedResult | null {
  try {
    const json = new TextDecoder().decode(fromBase64Url(token));
    const w = JSON.parse(json) as Partial<Wire>;
    if (
      !isNum(w.p) || !isNum(w.c) || !isNum(w.w) || !isNum(w.u) ||
      !isNum(w.t) || !isNum(w.ts) ||
      typeof w.l !== "string" || !LEVELS.includes(w.l as UnderstandingLevel) ||
      typeof w.i !== "string" || typeof w.r !== "string"
    ) {
      return null;
    }
    return {
      score: {
        score_percentage: w.p,
        correct_count: w.c,
        wrong_count: w.w,
        unanswered_count: w.u,
        total_questions: w.t,
      },
      time_taken_seconds: w.ts,
      understanding_level: w.l as UnderstandingLevel,
      insight: w.i,
      recommendation: w.r,
      chart_data: { correct: w.c, wrong: w.w, unanswered: w.u },
    };
  } catch {
    return null;
  }
}

/** Pull the shareable summary out of a full submit response. */
export function toSharedResult(result: QuizSubmitResponse): SharedResult {
  return {
    score: result.score,
    time_taken_seconds: result.time_taken_seconds,
    understanding_level: result.understanding_level,
    insight: result.insight,
    recommendation: result.recommendation,
    chart_data: result.chart_data,
  };
}

/** Build the absolute share URL for a result. */
export function buildShareUrl(result: QuizSubmitResponse): string {
  const token = encodeSharedResult(toSharedResult(result));
  const origin =
    typeof window !== "undefined" ? window.location.origin : "";
  return `${origin}/result?s=${token}`;
}
