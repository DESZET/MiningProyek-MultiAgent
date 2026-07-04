import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QuizSettingsControl } from "@/components/QuizSettingsControl";
import { DEFAULT_QUIZ_SETTINGS } from "@/types/quiz";

describe("QuizSettingsControl", () => {
  it("shows a summary of the current settings when collapsed", () => {
    render(
      <QuizSettingsControl
        settings={DEFAULT_QUIZ_SETTINGS}
        onChange={() => {}}
      />,
    );
    // 5 soal · Sedang · acak
    expect(screen.getByText(/5 soal/)).toBeInTheDocument();
    expect(screen.getByText(/Sedang/)).toBeInTheDocument();
  });

  it("changes the question count", () => {
    const onChange = vi.fn();
    render(
      <QuizSettingsControl
        settings={DEFAULT_QUIZ_SETTINGS}
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /atur kuis/i }));
    fireEvent.click(screen.getByRole("radio", { name: "10" }));
    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_QUIZ_SETTINGS,
      num_questions: 10,
    });
  });

  it("changes the difficulty", () => {
    const onChange = vi.fn();
    render(
      <QuizSettingsControl
        settings={DEFAULT_QUIZ_SETTINGS}
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /atur kuis/i }));
    fireEvent.click(screen.getByRole("radio", { name: "Sulit" }));
    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_QUIZ_SETTINGS,
      difficulty: "hard",
    });
  });

  it("toggles shuffle off via the switch", () => {
    const onChange = vi.fn();
    render(
      <QuizSettingsControl
        settings={DEFAULT_QUIZ_SETTINGS}
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /atur kuis/i }));
    const sw = screen.getByRole("switch");
    expect(sw).toHaveAttribute("aria-checked", "true");
    fireEvent.click(sw);
    expect(onChange).toHaveBeenCalledWith({
      ...DEFAULT_QUIZ_SETTINGS,
      shuffle_options: false,
    });
  });

  it("does not expand the panel when disabled", () => {
    render(
      <QuizSettingsControl
        settings={DEFAULT_QUIZ_SETTINGS}
        onChange={() => {}}
        disabled
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /atur kuis/i }));
    // The disabled toggle button can't open the panel, so no radios appear.
    expect(screen.queryByRole("radio", { name: "10" })).not.toBeInTheDocument();
  });
});
