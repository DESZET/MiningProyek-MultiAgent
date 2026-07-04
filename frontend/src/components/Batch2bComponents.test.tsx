import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LearningPreferences } from "@/components/LearningPreferences";
import { BookmarksList } from "@/components/BookmarksList";
import { LEARNING_PREFS } from "@/utils/i18n";
import * as api from "@/services/api";

vi.mock("@/services/api");

beforeEach(() => vi.resetAllMocks());

describe("LearningPreferences", () => {
  it("loads prefs and saves a change", async () => {
    vi.mocked(api.getPreferences).mockResolvedValue({
      default_num_questions: 5,
      default_difficulty: "medium",
      shuffle_options: true,
      weekly_goal: 5,
      favorite_topic: null,
    });
    vi.mocked(api.updatePreferences).mockResolvedValue(null);

    render(<LearningPreferences />);
    // "10" appears in both the count and weekly-goal groups — scope to count.
    const countGroup = await screen.findByRole("radiogroup", {
      name: LEARNING_PREFS.countLabel,
    });
    fireEvent.click(within(countGroup).getByRole("radio", { name: "10" }));
    expect(api.updatePreferences).toHaveBeenCalledWith({
      default_num_questions: 10,
    });
  });

  it("shows the unavailable note when prefs are off", async () => {
    vi.mocked(api.getPreferences).mockResolvedValue(null);
    render(<LearningPreferences />);
    expect(await screen.findByText(/belum aktif/i)).toBeInTheDocument();
  });
});

describe("BookmarksList", () => {
  it("lists saved materials and deletes one", async () => {
    vi.mocked(api.getBookmarks).mockResolvedValue({
      items: [
        {
          id: "bm-1",
          title: "Fotosintesis",
          material_text: "...",
          created_at: "2026-06-17T00:00:00Z",
        },
      ],
    });
    vi.mocked(api.deleteBookmark).mockResolvedValue(true);
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(
      <MemoryRouter>
        <BookmarksList />
      </MemoryRouter>,
    );
    expect(await screen.findByText("Fotosintesis")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Hapus: Fotosintesis/ }));
    await waitFor(() => expect(api.deleteBookmark).toHaveBeenCalledWith("bm-1"));
  });
});
