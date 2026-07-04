import { describe, it, expect } from "vitest";
import {
  buildShareUrl,
  decodeSharedResult,
  encodeSharedResult,
  toSharedResult,
} from "@/lib/shareResult";
import type { QuizSubmitResponse } from "@/types/result";

const RESULT: QuizSubmitResponse = {
  quiz_id: "q-123",
  score: {
    score_percentage: 80,
    correct_count: 4,
    wrong_count: 1,
    unanswered_count: 0,
    total_questions: 5,
  },
  time_taken_seconds: 123,
  understanding_level: "high",
  insight: "Kamu paham poin utamanya — termasuk istilah seperti “kloroplas”.",
  recommendation: "Lanjut ke materi berikutnya.",
  chart_data: { correct: 4, wrong: 1, unanswered: 0 },
  submitted_at: "2026-06-17T00:00:00Z",
  question_reviews: [],
};

describe("shareResult", () => {
  it("round-trips a result through encode/decode (incl. UTF-8 copy)", () => {
    const token = encodeSharedResult(toSharedResult(RESULT));
    const decoded = decodeSharedResult(token);
    expect(decoded).toEqual(toSharedResult(RESULT));
    // The decoded insight must preserve non-ASCII characters.
    expect(decoded?.insight).toContain("kloroplas");
  });

  it("produces a URL-safe token (no +, /, or = padding)", () => {
    const token = encodeSharedResult(toSharedResult(RESULT));
    expect(token).not.toMatch(/[+/=]/);
  });

  it("derives chart_data from the counts on decode", () => {
    const decoded = decodeSharedResult(encodeSharedResult(toSharedResult(RESULT)));
    expect(decoded?.chart_data).toEqual({ correct: 4, wrong: 1, unanswered: 0 });
  });

  it("returns null for malformed / tampered tokens", () => {
    expect(decodeSharedResult("not-valid-base64!!")).toBeNull();
    expect(decodeSharedResult("")).toBeNull();
    // Valid base64 but not our shape.
    expect(decodeSharedResult(btoa("hello world"))).toBeNull();
  });

  it("rejects an out-of-range understanding level", () => {
    const token = encodeSharedResult({
      ...toSharedResult(RESULT),
      understanding_level: "bogus" as never,
    });
    expect(decodeSharedResult(token)).toBeNull();
  });

  it("buildShareUrl points at /result with an s= token", () => {
    const url = buildShareUrl(RESULT);
    expect(url).toContain("/result?s=");
    const token = url.split("s=")[1]!;
    expect(decodeSharedResult(token)).toEqual(toSharedResult(RESULT));
  });
});
