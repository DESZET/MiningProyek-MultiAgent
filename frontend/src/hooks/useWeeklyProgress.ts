import { useEffect, useState } from "react";
import { getWeeklyProgress } from "@/services/api";
import type { WeeklyProgress } from "@/types/gamification";

export type WeeklyProgressState =
  | { status: "loading" }
  | { status: "ready"; data: WeeklyProgress }
  | { status: "unavailable" };

/** §4.8 — quizzes completed this week vs target. `unavailable` = DB off. */
export function useWeeklyProgress(): WeeklyProgressState {
  const [state, setState] = useState<WeeklyProgressState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    void getWeeklyProgress().then((data) => {
      if (!active) return;
      setState(data ? { status: "ready", data } : { status: "unavailable" });
    });
    return () => {
      active = false;
    };
  }, []);

  return state;
}
