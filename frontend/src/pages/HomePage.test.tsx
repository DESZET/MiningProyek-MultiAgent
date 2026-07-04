import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { HomePage } from "@/pages/HomePage";
import { HOMEPAGE, SAMPLE_MATERIALS } from "@/utils/i18n";

// No network in tests — the page only calls these on submit, but useQuiz /
// DailyChallengeCard import them at module load.
vi.mock("@/services/api", () => ({
  generateQuiz: vi.fn(),
  generateQuizFromUrl: vi.fn(),
  generateQuizFromPdf: vi.fn(),
  getDailyChallenge: vi.fn(),
  regenerateQuiz: vi.fn(),
  submitQuiz: vi.fn(),
  recordQuizAttempt: vi.fn(),
  // §4.8: HomePage seeds settings from prefs + can save bookmarks.
  getPreferences: vi.fn(() => Promise.resolve(null)),
  createBookmark: vi.fn(() => Promise.resolve(null)),
}));

function renderHome() {
  return render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>,
  );
}

describe("HomePage", () => {
  it("renders the hero and the Daily Challenge entry point", () => {
    renderHome();
    expect(
      screen.getByRole("heading", { name: HOMEPAGE.hero }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /mulai tantangan/i }),
    ).toBeInTheDocument();
  });

  it("fills the textarea with the sample material when the sample is clicked", async () => {
    const user = userEvent.setup();
    renderHome();

    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveValue("");

    await user.click(
      screen.getByRole("button", { name: SAMPLE_MATERIALS.fotosintesis.label }),
    );

    expect(textarea).toHaveValue(SAMPLE_MATERIALS.fotosintesis.text);
  });
});
