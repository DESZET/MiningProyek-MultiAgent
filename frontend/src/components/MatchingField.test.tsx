import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MatchingField } from "@/components/MatchingField";

const LEFT = ["Fotosintesis", "Mitokondria", "Ribosom"];
const RIGHT = ["respirasi sel", "sintesis protein", "pembentukan glukosa"];

describe("MatchingField", () => {
  it("pairs a term to a statement via tap-tap", () => {
    const onChange = vi.fn();
    render(
      <MatchingField
        leftItems={LEFT}
        rightItems={RIGHT}
        matches={[-1, -1, -1]}
        onChange={onChange}
      />,
    );
    // Tap the first term, then the third statement (index 2).
    fireEvent.click(screen.getByRole("button", { name: /Fotosintesis/ }));
    fireEvent.click(screen.getByRole("button", { name: /pembentukan glukosa/ }));
    expect(onChange).toHaveBeenCalledWith([2, -1, -1]);
  });

  it("right items are not clickable until a term is active", () => {
    const onChange = vi.fn();
    render(
      <MatchingField
        leftItems={LEFT}
        rightItems={RIGHT}
        matches={[-1, -1, -1]}
        onChange={onChange}
      />,
    );
    // No active term yet → clicking a statement does nothing.
    fireEvent.click(screen.getByRole("button", { name: /respirasi sel/ }));
    expect(onChange).not.toHaveBeenCalled();
  });

  it("tapping an already-paired term clears it", () => {
    const onChange = vi.fn();
    render(
      <MatchingField
        leftItems={LEFT}
        rightItems={RIGHT}
        matches={[0, -1, -1]}
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /Fotosintesis/ }));
    expect(onChange).toHaveBeenCalledWith([-1, -1, -1]);
  });
});
