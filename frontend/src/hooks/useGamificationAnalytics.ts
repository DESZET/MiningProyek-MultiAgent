import { useEffect, useState } from "react";
import { getGamificationAnalytics } from "@/services/api";
import type { GamificationAnalytics } from "@/types/gamification";

/**
 * Loading / ready / unavailable states for the progress dashboard.
 * `unavailable` covers the 503 case (DATABASE_URL unset) and any network
 * failure — the page shows a graceful "feature off" message instead of crashing.
 */
export type AnalyticsState =
  | { status: "loading" }
  | { status: "ready"; data: GamificationAnalytics }
  | { status: "unavailable" };

/**
 * Fetches gamification analytics once on mount. Unlike the nav stats hook this
 * is page-scoped, so it does not refetch on every route change.
 */
export function useGamificationAnalytics(): AnalyticsState {
  const [state, setState] = useState<AnalyticsState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    void getGamificationAnalytics().then((data) => {
      if (!active) return;
      setState(
        data ? { status: "ready", data } : { status: "unavailable" },
      );
    });
    return () => {
      active = false;
    };
  }, []);

  return state;
}
