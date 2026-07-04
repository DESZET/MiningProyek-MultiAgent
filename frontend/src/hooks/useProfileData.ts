import { useEffect, useState } from "react";
import {
  getAchievements,
  getGamificationHistory,
  getGamificationStats,
} from "@/services/api";
import type {
  Badge,
  GamificationStats,
  HistoryItem,
  HistorySummary,
} from "@/types/gamification";

/**
 * Profile hub data: gamification stats + badges + a small recent-history
 * preview, fetched in parallel. `stats` is the availability signal — if it is
 * null (503 / network failure) the whole hub renders its "off" state.
 */
export type ProfileState =
  | { status: "loading" }
  | { status: "unavailable" }
  | {
      status: "ready";
      stats: GamificationStats;
      achievements: Badge[];
      summary: HistorySummary | null;
      recent: HistoryItem[];
    };

const RECENT_LIMIT = 5;

export function useProfileData(): ProfileState {
  const [state, setState] = useState<ProfileState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    void Promise.all([
      getGamificationStats(),
      getAchievements(),
      getGamificationHistory(RECENT_LIMIT),
    ]).then(([stats, achievements, history]) => {
      if (!active) return;
      if (!stats) {
        setState({ status: "unavailable" });
        return;
      }
      setState({
        status: "ready",
        stats,
        achievements,
        summary: history?.summary ?? null,
        recent: history?.items ?? [],
      });
    });
    return () => {
      active = false;
    };
  }, []);

  return state;
}
