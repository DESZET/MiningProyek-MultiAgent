import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { getGamificationStats } from "@/services/api";
import type { GamificationStats } from "@/types/gamification";

/**
 * Fetches gamification stats and refreshes on every route change (so the nav
 * widget updates after a quiz is recorded). Returns null when gamification is
 * unavailable (e.g. DATABASE_URL unset) so the UI can hide itself gracefully.
 */
export function useGamificationStats() {
  const [stats, setStats] = useState<GamificationStats | null>(null);
  const { pathname } = useLocation();

  const refresh = useCallback(async () => {
    const s = await getGamificationStats();
    setStats(s);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh, pathname]);

  return { stats, refresh };
}
