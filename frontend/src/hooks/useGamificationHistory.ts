import { useEffect, useState } from "react";
import { getGamificationHistory } from "@/services/api";
import type { HistoryResponse } from "@/types/gamification";

/**
 * Loading / ready / unavailable states for the History page.
 * `unavailable` covers the 503 case (DATABASE_URL unset) and any network
 * failure, so the page degrades gracefully instead of crashing.
 */
export type HistoryState =
  | { status: "loading" }
  | { status: "ready"; data: HistoryResponse }
  | { status: "unavailable" };

/**
 * Fetches quiz history (summary + items) once on mount. Page-scoped, so it does
 * not refetch on every route change.
 */
export function useGamificationHistory(limit = 50): HistoryState {
  const [state, setState] = useState<HistoryState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    void getGamificationHistory(limit).then((data) => {
      if (!active) return;
      setState(data ? { status: "ready", data } : { status: "unavailable" });
    });
    return () => {
      active = false;
    };
  }, [limit]);

  return state;
}
