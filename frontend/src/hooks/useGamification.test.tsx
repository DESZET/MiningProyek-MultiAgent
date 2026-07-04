import { describe, it, expect, beforeEach, vi } from "vitest";
import type { ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

vi.mock("@/services/api", () => ({
  getGamificationStats: vi.fn(),
  getGamificationAnalytics: vi.fn(),
  getGamificationHistory: vi.fn(),
  getAchievements: vi.fn(),
}));

import {
  getAchievements,
  getGamificationAnalytics,
  getGamificationHistory,
  getGamificationStats,
} from "@/services/api";
import { useGamificationStats } from "@/hooks/useGamificationStats";
import { useGamificationAnalytics } from "@/hooks/useGamificationAnalytics";
import { useGamificationHistory } from "@/hooks/useGamificationHistory";
import { useProfileData } from "@/hooks/useProfileData";

const routerWrapper = ({ children }: { children: ReactNode }) => (
  <MemoryRouter>{children}</MemoryRouter>
);

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useGamificationStats", () => {
  it("loads stats on mount", async () => {
    vi.mocked(getGamificationStats).mockResolvedValue({
      total_xp: 50,
      level: 2,
      xp_into_level: 0,
      xp_for_next_level: 100,
      current_streak: 1,
      longest_streak: 3,
    });
    const { result } = renderHook(() => useGamificationStats(), {
      wrapper: routerWrapper,
    });
    await waitFor(() => expect(result.current.stats?.level).toBe(2));
  });

  it("leaves stats null when gamification is unavailable", async () => {
    vi.mocked(getGamificationStats).mockResolvedValue(null);
    const { result } = renderHook(() => useGamificationStats(), {
      wrapper: routerWrapper,
    });
    await waitFor(() => expect(getGamificationStats).toHaveBeenCalled());
    expect(result.current.stats).toBeNull();
  });
});

describe("useGamificationAnalytics", () => {
  it("transitions loading → ready with data", async () => {
    vi.mocked(getGamificationAnalytics).mockResolvedValue({
      quiz_count: 3,
      average_score: 80,
      total_xp: 100,
      score_trend: [],
      topic_mastery: [],
    });
    const { result } = renderHook(() => useGamificationAnalytics());
    expect(result.current.status).toBe("loading");
    await waitFor(() => expect(result.current.status).toBe("ready"));
  });

  it("transitions loading → unavailable on null", async () => {
    vi.mocked(getGamificationAnalytics).mockResolvedValue(null);
    const { result } = renderHook(() => useGamificationAnalytics());
    await waitFor(() => expect(result.current.status).toBe("unavailable"));
  });
});

describe("useGamificationHistory", () => {
  it("returns ready with the history payload", async () => {
    vi.mocked(getGamificationHistory).mockResolvedValue({
      summary: {
        total_quizzes: 1,
        average_score: 90,
        total_xp: 100,
        best_score: 90,
        worst_score: 90,
      },
      items: [],
    });
    const { result } = renderHook(() => useGamificationHistory(10));
    await waitFor(() => expect(result.current.status).toBe("ready"));
  });

  it("returns unavailable on null", async () => {
    vi.mocked(getGamificationHistory).mockResolvedValue(null);
    const { result } = renderHook(() => useGamificationHistory());
    await waitFor(() => expect(result.current.status).toBe("unavailable"));
  });
});

describe("useProfileData", () => {
  it("is unavailable when stats are missing (even if other calls succeed)", async () => {
    vi.mocked(getGamificationStats).mockResolvedValue(null);
    vi.mocked(getAchievements).mockResolvedValue([]);
    vi.mocked(getGamificationHistory).mockResolvedValue(null);
    const { result } = renderHook(() => useProfileData());
    await waitFor(() => expect(result.current.status).toBe("unavailable"));
  });

  it("aggregates stats, achievements and recent history when available", async () => {
    vi.mocked(getGamificationStats).mockResolvedValue({
      total_xp: 50,
      level: 2,
      xp_into_level: 0,
      xp_for_next_level: 100,
      current_streak: 1,
      longest_streak: 3,
    });
    vi.mocked(getAchievements).mockResolvedValue([
      { code: "first_quiz", label: "L", description: "d", icon: "Star", unlocked_at: null },
    ]);
    vi.mocked(getGamificationHistory).mockResolvedValue({
      summary: {
        total_quizzes: 4,
        average_score: 75,
        total_xp: 200,
        best_score: 100,
        worst_score: 50,
      },
      items: [
        { quiz_id: "q1", score: 80, understanding_level: "high", xp_earned: 10, completed_at: "2026-06-07T00:00:00Z" },
      ],
    });
    const { result } = renderHook(() => useProfileData());
    await waitFor(() => expect(result.current.status).toBe("ready"));
    if (result.current.status === "ready") {
      expect(result.current.stats.level).toBe(2);
      expect(result.current.achievements).toHaveLength(1);
      expect(result.current.summary?.total_quizzes).toBe(4);
      expect(result.current.recent).toHaveLength(1);
    }
  });
});
