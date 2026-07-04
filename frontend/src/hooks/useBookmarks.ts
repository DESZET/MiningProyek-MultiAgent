import { useCallback, useEffect, useState } from "react";
import { getBookmarks } from "@/services/api";
import type { Bookmark } from "@/types/gamification";

export type BookmarksState =
  | { status: "loading" }
  | { status: "ready"; items: Bookmark[] }
  | { status: "unavailable" };

/** §4.8 — saved materials, with a reload() to call after add/delete. */
export function useBookmarks() {
  const [state, setState] = useState<BookmarksState>({ status: "loading" });

  const reload = useCallback(() => {
    void getBookmarks().then((data) =>
      setState(
        data ? { status: "ready", items: data.items } : { status: "unavailable" },
      ),
    );
  }, []);

  useEffect(() => reload(), [reload]);

  return { state, reload };
}
