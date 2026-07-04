import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BadgeGrid } from "@/components/BadgeGrid";
import type { Badge } from "@/types/gamification";

const badges: Badge[] = [
  {
    code: "first_quiz",
    label: "Langkah Pertama",
    description: "Menyelesaikan kuis pertamamu",
    icon: "Sparkles",
    unlocked_at: "2026-06-07T10:00:00Z",
  },
  {
    code: "perfect_score",
    label: "Sempurna",
    description: "Meraih skor 100",
    icon: "Star",
    unlocked_at: null,
  },
];

describe("BadgeGrid", () => {
  it("renders an empty hint when there are no badges", () => {
    render(<BadgeGrid badges={[]} />);
    expect(screen.getByText(/belum ada badge/i)).toBeInTheDocument();
  });

  it("renders one card per badge with its label and description", () => {
    const { container } = render(<BadgeGrid badges={badges} />);
    expect(container.querySelectorAll("ul > li")).toHaveLength(2);
    expect(screen.getByText("Langkah Pertama")).toBeInTheDocument();
    expect(screen.getByText("Meraih skor 100")).toBeInTheDocument();
  });

  it("renders an icon for each badge (unlocked icon or a lock for locked)", () => {
    const { container } = render(<BadgeGrid badges={badges} />);
    const cells = container.querySelectorAll("ul > li");
    cells.forEach((li) => {
      expect(li.querySelector("svg")).not.toBeNull();
    });
  });
});
