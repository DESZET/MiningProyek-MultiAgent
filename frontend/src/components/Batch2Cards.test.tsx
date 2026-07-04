import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { WeeklyGoalCard } from "@/components/WeeklyGoalCard";
import { LeaderboardCard } from "@/components/LeaderboardCard";
import * as api from "@/services/api";

vi.mock("@/services/api");

beforeEach(() => vi.resetAllMocks());

describe("WeeklyGoalCard", () => {
  it("renders weekly progress when available", async () => {
    vi.mocked(api.getWeeklyProgress).mockResolvedValue({
      completed: 2,
      target: 5,
      percent: 40,
      goal_met: false,
      remaining: 3,
    });
    render(<WeeklyGoalCard />);
    expect(await screen.findByText(/2 dari 5 kuis minggu ini/)).toBeInTheDocument();
    expect(screen.getByText(/3 kuis lagi/)).toBeInTheDocument();
  });

  it("renders nothing when gamification is unavailable", async () => {
    vi.mocked(api.getWeeklyProgress).mockResolvedValue(null);
    const { container } = render(<WeeklyGoalCard />);
    // Give the effect a tick; nothing should appear.
    await Promise.resolve();
    expect(container).toBeEmptyDOMElement();
  });
});

describe("LeaderboardCard", () => {
  it("lists ranked players and highlights you", async () => {
    vi.mocked(api.getLeaderboard).mockResolvedValue({
      entries: [
        { rank: 1, name: "Alice", total_xp: 300, level: 4, is_you: false },
        { rank: 2, name: "Anonim", total_xp: 150, level: 2, is_you: true },
      ],
      you_rank: 2,
    });
    render(<LeaderboardCard />);
    expect(await screen.findByText("Alice")).toBeInTheDocument();
    // The current user's row shows "Kamu" instead of their stored name.
    expect(screen.getByText("Kamu")).toBeInTheDocument();
    expect(screen.getByText("300 XP")).toBeInTheDocument();
  });
});
