import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ResultPage } from "@/pages/ResultPage";
import type { QuizSubmitResponse } from "@/types/result";
import type { RecordAttemptResult } from "@/types/gamification";
import { buildShareUrl, encodeSharedResult, toSharedResult } from "@/lib/shareResult";
import { RESULT_HEADERS, RESULT_SHARE } from "@/utils/i18n";

vi.mock("@/services/api", () => ({
  regenerateQuiz: vi.fn(),
  submitQuiz: vi.fn(),
  generateQuiz: vi.fn(),
  generateQuizFromUrl: vi.fn(),
  generateQuizFromPdf: vi.fn(),
  getDailyChallenge: vi.fn(),
  recordQuizAttempt: vi.fn(),
  // AsahiDialog fires this on mount; keep it pending so it doesn't touch the
  // network or update state during this page smoke test (its own test below).
  sendChat: vi.fn(() => new Promise(() => {})),
}));

const result: QuizSubmitResponse = {
  quiz_id: "q1",
  score: {
    score_percentage: 60, // < 80 so no confetti fires in the test
    correct_count: 3,
    wrong_count: 2,
    unanswered_count: 0,
    total_questions: 5,
  },
  time_taken_seconds: 120,
  understanding_level: "medium",
  insight: "Pemahamanmu sebagian sudah terbentuk.",
  recommendation: "Baca ulang bagian yang masih ragu.",
  chart_data: { correct: 3, wrong: 2, unanswered: 0 },
  submitted_at: "2026-06-07T00:00:00Z",
  question_reviews: [
    {
      question_id: 1,
      type: "multiple_choice",
      question: "Apa itu fotosintesis?",
      options: ["A", "B", "C", "D"],
      selected_option_index: 0,
      correct_option_index: 0,
      is_correct: true,
      is_unanswered: false,
    },
  ],
};

const reward: RecordAttemptResult = {
  xp_earned: 40,
  leveled_up: true,
  new_level: 3,
  stats: {
    total_xp: 300,
    level: 3,
    xp_into_level: 0,
    xp_for_next_level: 100,
    current_streak: 1,
    longest_streak: 2,
  },
  newly_unlocked: [
    { code: "perfect_score", label: "Sempurna", description: "d", icon: "Star", unlocked_at: "2026-06-07T00:00:00Z" },
  ],
};

function renderResult(state: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: "/result", state }]}>
      <Routes>
        <Route path="/result" element={<ResultPage />} />
        <Route path="/" element={<div>home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ResultPage", () => {
  it("renders headline, insight, recommendation and the reward banner", () => {
    renderResult({ result, reward });
    expect(screen.getByText(RESULT_HEADERS.medium.headline)).toBeInTheDocument();
    expect(screen.getByText(result.insight)).toBeInTheDocument();
    expect(screen.getByText(result.recommendation)).toBeInTheDocument();
    expect(screen.getByText("+40 XP")).toBeInTheDocument(); // reward banner
    expect(screen.getByText("Sempurna")).toBeInTheDocument(); // unlocked badge
  });

  it("renders without a reward banner when reward is null", () => {
    renderResult({ result, reward: null });
    expect(screen.getByText(RESULT_HEADERS.medium.headline)).toBeInTheDocument();
    expect(screen.queryByText("+40 XP")).not.toBeInTheDocument();
  });

  // §4.2 — shared-link mode
  function renderSharedLink(token: string) {
    return render(
      <MemoryRouter initialEntries={[`/result?s=${token}`]}>
        <Routes>
          <Route path="/result" element={<ResultPage />} />
          <Route path="/app" element={<div>app home</div>} />
          <Route path="/" element={<div>home</div>} />
        </Routes>
      </MemoryRouter>,
    );
  }

  it("decodes a shared ?s= link into a read-only result with a create CTA", () => {
    const token = encodeSharedResult(toSharedResult(result));
    renderSharedLink(token);
    // Summary content is rendered from the decoded token...
    expect(screen.getByText(result.insight)).toBeInTheDocument();
    expect(screen.getByText(result.recommendation)).toBeInTheDocument();
    // ...the shared banner + create CTA appear...
    expect(screen.getByText(RESULT_SHARE.sharedBanner)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: RESULT_SHARE.ctaCreate }),
    ).toBeInTheDocument();
    // ...and owner-only actions (retry) are hidden.
    expect(
      screen.queryByRole("button", { name: /asah lagi/i }),
    ).not.toBeInTheDocument();
  });

  it("redirects home when the ?s= token is malformed", () => {
    renderSharedLink("not-a-valid-token!!");
    expect(screen.getByText("home")).toBeInTheDocument();
  });

  it("share button copies a self-contained link to the clipboard", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    // No native share sheet → falls back to clipboard.
    Object.defineProperty(navigator, "share", {
      value: undefined,
      configurable: true,
    });
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });
    renderResult({ result, reward: null });

    fireEvent.click(screen.getByRole("button", { name: RESULT_SHARE.button }));
    await waitFor(() => expect(writeText).toHaveBeenCalledTimes(1));
    expect(writeText.mock.calls[0]![0]).toBe(buildShareUrl(result));
  });
});
