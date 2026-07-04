import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

vi.mock("@/hooks/useGamificationAnalytics", () => ({
  useGamificationAnalytics: vi.fn(),
}));

import { ProgressPage } from "@/pages/ProgressPage";
import { useGamificationAnalytics } from "@/hooks/useGamificationAnalytics";

function renderProgress() {
  return render(
    <MemoryRouter>
      <ProgressPage />
    </MemoryRouter>,
  );
}

beforeEach(() => vi.clearAllMocks());

describe("ProgressPage", () => {
  it("shows a loading state", () => {
    vi.mocked(useGamificationAnalytics).mockReturnValue({ status: "loading" });
    renderProgress();
    expect(screen.getByText(/memuat progresmu/i)).toBeInTheDocument();
  });

  it("shows an unavailable state", () => {
    vi.mocked(useGamificationAnalytics).mockReturnValue({ status: "unavailable" });
    renderProgress();
    expect(screen.getByText(/fitur progres belum aktif/i)).toBeInTheDocument();
  });

  it("shows an empty state when there are no quizzes", () => {
    vi.mocked(useGamificationAnalytics).mockReturnValue({
      status: "ready",
      data: { quiz_count: 0, average_score: 0, total_xp: 0, score_trend: [], topic_mastery: [] },
    });
    renderProgress();
    expect(screen.getByText(/belum ada progres/i)).toBeInTheDocument();
  });

  it("renders summary, trend chart and topic mastery when ready", () => {
    vi.mocked(useGamificationAnalytics).mockReturnValue({
      status: "ready",
      data: {
        quiz_count: 5,
        average_score: 82,
        total_xp: 300,
        score_trend: [
          { date: "2026-06-06", average_score: 70, attempt_count: 2 },
          { date: "2026-06-07", average_score: 90, attempt_count: 3 },
        ],
        topic_mastery: [
          { topic: "Fotosintesis", average_score: 60, attempt_count: 2 },
          { topic: "Tata Surya", average_score: 95, attempt_count: 3 },
        ],
      },
    });
    renderProgress();
    expect(screen.getByText("5")).toBeInTheDocument(); // quiz count
    expect(screen.getByText("Fotosintesis")).toBeInTheDocument(); // mastery row
    expect(screen.getByText("Tata Surya")).toBeInTheDocument();
  });
});
