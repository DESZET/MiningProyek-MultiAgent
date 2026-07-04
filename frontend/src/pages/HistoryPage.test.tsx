import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

vi.mock("@/hooks/useGamificationHistory", () => ({
  useGamificationHistory: vi.fn(),
}));

import { HistoryPage } from "@/pages/HistoryPage";
import { useGamificationHistory } from "@/hooks/useGamificationHistory";

function renderHistory() {
  return render(
    <MemoryRouter>
      <HistoryPage />
    </MemoryRouter>,
  );
}

beforeEach(() => vi.clearAllMocks());

describe("HistoryPage", () => {
  it("shows a loading state", () => {
    vi.mocked(useGamificationHistory).mockReturnValue({ status: "loading" });
    renderHistory();
    expect(screen.getByText(/memuat riwayatmu/i)).toBeInTheDocument();
  });

  it("shows an unavailable state", () => {
    vi.mocked(useGamificationHistory).mockReturnValue({ status: "unavailable" });
    renderHistory();
    expect(screen.getByText(/riwayat belum aktif/i)).toBeInTheDocument();
  });

  it("shows an empty state with a CTA when there are no attempts", () => {
    vi.mocked(useGamificationHistory).mockReturnValue({
      status: "ready",
      data: {
        summary: { total_quizzes: 0, average_score: 0, total_xp: 0, best_score: 0, worst_score: 0 },
        items: [],
      },
    });
    renderHistory();
    expect(screen.getByText(/belum ada riwayat/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /mulai mengasah/i })).toBeInTheDocument();
  });

  it("renders the summary and attempt rows when there is history", () => {
    vi.mocked(useGamificationHistory).mockReturnValue({
      status: "ready",
      data: {
        summary: { total_quizzes: 2, average_score: 85, total_xp: 200, best_score: 100, worst_score: 70 },
        items: [
          { quiz_id: "q1", score: 100, understanding_level: "high", xp_earned: 120, completed_at: "2026-06-07T00:00:00Z", topic: "Tata Surya" },
          { quiz_id: "q2", score: 70, understanding_level: "medium", xp_earned: 80, completed_at: "2026-06-06T00:00:00Z", topic: null },
        ],
      },
    });
    renderHistory();
    expect(screen.getByText("Tata Surya")).toBeInTheDocument();
    // "100" appears in both the best-score summary tile and the row score.
    expect(screen.getAllByText("100")).toHaveLength(2);
    expect(screen.getByText(/tanpa topik/i)).toBeInTheDocument(); // null topic fallback
    expect(screen.getByText("2")).toBeInTheDocument(); // total quizzes summary
  });
});
