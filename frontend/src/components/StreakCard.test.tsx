import "@testing-library/jest-dom/vitest";
import { describe, it, expect } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { StreakCard } from "@/components/StreakCard";

function litCellCount(container: HTMLElement): number {
  const items = container.querySelectorAll("ul > li");
  // A lit day renders a Flame svg inside its cell; an empty day renders none.
  return Array.from(items).filter((li) => li.querySelector("svg")).length;
}

describe("StreakCard", () => {
  it("always renders a 7-day strip", () => {
    const { container } = render(<StreakCard current={0} longest={0} />);
    expect(container.querySelectorAll("ul > li")).toHaveLength(7);
  });

  it("lights the most recent `current` days (capped at the strip width)", () => {
    const { container: c3 } = render(<StreakCard current={3} longest={9} />);
    expect(litCellCount(c3)).toBe(3);

    const { container: c10 } = render(<StreakCard current={10} longest={10} />);
    expect(litCellCount(c10)).toBe(7);
  });

  it("shows the longest streak when there is an active streak", () => {
    render(<StreakCard current={4} longest={8} />);
    expect(screen.getByText(/8 hari/)).toBeInTheDocument();
  });

  it("shows an encouraging hint when there is no streak", () => {
    render(<StreakCard current={0} longest={0} />);
    expect(
      screen.getByText(/kerjakan kuis hari ini untuk memulai/i),
    ).toBeInTheDocument();
  });

  it("renders the current streak count prominently", () => {
    const { container } = render(<StreakCard current={5} longest={5} />);
    const header = container.querySelector("section > div");
    expect(within(header as HTMLElement).getByText("5")).toBeInTheDocument();
  });
});
