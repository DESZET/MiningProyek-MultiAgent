import { useNavigate } from "react-router-dom";
import { useBookmarks } from "@/hooks/useBookmarks";
import { deleteBookmark } from "@/services/api";
import { BOOKMARKS } from "@/utils/i18n";

/**
 * §4.8 — list of saved materials with "Asah" (load into the home input to make a
 * fresh quiz) and delete. Renders nothing when gamification is unavailable.
 */
export function BookmarksList() {
  const { state, reload } = useBookmarks();
  const navigate = useNavigate();

  if (state.status !== "ready") return null;

  async function handleDelete(id: string) {
    if (!window.confirm(BOOKMARKS.deleteConfirm)) return;
    await deleteBookmark(id);
    reload();
  }

  function handlePractice(material: string) {
    navigate("/app", { state: { prefillMaterial: material } });
  }

  return (
    <section
      aria-labelledby="bookmarks-heading"
      className="space-y-3"
    >
      <h2
        id="bookmarks-heading"
        className="font-mono text-[11px] uppercase tracking-[1.2px] text-text-muted"
      >
        {BOOKMARKS.title}
      </h2>

      {state.items.length === 0 ? (
        <p className="text-sm text-text-muted">{BOOKMARKS.empty}</p>
      ) : (
        <ul className="space-y-2">
          {state.items.map((bm) => (
            <li
              key={bm.id}
              className="flex items-center gap-3 rounded-xl border border-border-standard bg-bg-page p-3 shadow-level-1"
            >
              <span className="flex-1 truncate text-sm font-medium text-text-primary">
                {bm.title}
              </span>
              <button
                type="button"
                onClick={() => handlePractice(bm.material_text)}
                className="min-h-[36px] rounded-pill border border-brand-button bg-brand-button px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover"
              >
                {BOOKMARKS.practice}
              </button>
              <button
                type="button"
                onClick={() => handleDelete(bm.id)}
                aria-label={`${BOOKMARKS.delete}: ${bm.title}`}
                className="min-h-[36px] rounded-pill border border-border-standard bg-bg-page px-3 py-1.5 text-xs text-text-muted transition-colors hover:text-status-rendah active:text-status-rendah"
              >
                {BOOKMARKS.delete}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
