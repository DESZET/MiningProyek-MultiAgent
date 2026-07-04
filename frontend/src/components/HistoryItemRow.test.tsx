import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { HistoryItemRow } from "@/components/HistoryItemRow";
import type { HistoryItem } from "@/types/gamification";

function renderRow(item: HistoryItem) {
  return render(
    <ul>
      <HistoryItemRow item={item} />
    </ul>,
  );
}

const base: HistoryItem = {
  quiz_id: "q1",
  score: 90,
  understanding_level: "high",
  xp_earned: 115,
  completed_at: "2026-06-07T10:00:00Z",
  topic: "Fotosintesis",
};

describe("HistoryItemRow", () => {
  it("shows topic, score, XP, and the understanding badge", () => {
    renderRow(base);
    expect(screen.getByText("Fotosintesis")).toBeInTheDocument();
    expect(screen.getByText("90")).toBeInTheDocument();
    expect(screen.getByText("+115 XP")).toBeInTheDocument();
    expect(screen.getByText("TINGGI")).toBeInTheDocument(); // high -> TINGGI
  });

  it("falls back to a placeholder when there is no topic", () => {
    renderRow({ ...base, topic: null });
    expect(screen.getByText(/tanpa topik/i)).toBeInTheDocument();
  });

  it("omits the badge when the understanding level is unrecognized", () => {
    renderRow({ ...base, understanding_level: "weird" });
    expect(screen.queryByText("TINGGI")).not.toBeInTheDocument();
    expect(screen.queryByText(/sedang|rendah/i)).not.toBeInTheDocument();
  });
});
