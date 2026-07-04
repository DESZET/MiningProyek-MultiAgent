import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { QuizPage } from "@/pages/QuizPage";
import type { QuizGenerateResponse } from "@/types/quiz";

vi.mock("@/services/api", () => ({
  submitQuiz: vi.fn(),
  recordQuizAttempt: vi.fn(),
  generateQuiz: vi.fn(),
  generateQuizFromUrl: vi.fn(),
  generateQuizFromPdf: vi.fn(),
  getDailyChallenge: vi.fn(),
  regenerateQuiz: vi.fn(),
}));

const quiz: QuizGenerateResponse = {
  quiz_id: "quiz-kbd",
  total_questions: 2,
  generated_at: "2026-06-07T10:00:00Z",
  questions: [
    {
      id: 1,
      type: "multiple_choice",
      question: "Apa ibu kota Indonesia?",
      options: ["Jakarta", "Bandung", "Surabaya", "Medan"],
    },
    {
      id: 2,
      type: "multiple_choice",
      question: "Berapa 2 + 2?",
      options: ["3", "4", "5", "6"],
    },
  ],
};

function renderQuiz() {
  return render(
    <MemoryRouter initialEntries={[{ pathname: "/quiz", state: { quiz } }]}>
      <Routes>
        <Route path="/quiz" element={<QuizPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("QuizPage keyboard shortcuts", () => {
  it("selects an option on the current question when pressing 1-4", () => {
    renderQuiz();

    const optionA = screen.getByRole("button", { name: /Jakarta/ });
    // Selected options use `border-brand-accent`; unselected use the standard
    // border. (`bg-bg-alt` also appears in the unselected `hover:` class, so we
    // key off the border instead.)
    expect(optionA.className).toContain("border-border-standard");
    expect(optionA.className).not.toContain("border-brand-accent");

    fireEvent.keyDown(document.body, { key: "2" });

    const optionB = screen.getByRole("button", { name: /Bandung/ });
    expect(optionB.className).toContain("border-brand-accent");
    // Pressing a different key changes the selection, not adds a second one.
    expect(optionA.className).not.toContain("border-brand-accent");
  });
});
