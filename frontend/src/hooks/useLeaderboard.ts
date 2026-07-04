import { useEffect, useState } from "react";
import { getLeaderboard } from "@/services/api";
import type { LeaderboardResponse } from "@/types/gamification";

export type LeaderboardState =
  | { status: "loading" }
  | { status: "ready"; data: LeaderboardResponse }
  | { status: "unavailable" };

/** §4.8 — top players by XP. `unavailable` covers DB-off / network failure. */
export function useLeaderboard(limit = 20): LeaderboardState {
  const [state, setState] = useState<LeaderboardState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    void getLeaderboard(limit).then((data) => {
      if (!active) return;
      setState(data ? { status: "ready", data } : { status: "unavailable" });
    });
    return () => {
      active = false;
    };
  }, [limit]);

  return state;
}
