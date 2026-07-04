import { describe, it, expect } from "vitest";
import {
  MASTERY_HIGH_THRESHOLD,
  MASTERY_MEDIUM_THRESHOLD,
  MIN_BAR_PERCENT,
  barExtent,
  formatTrendDate,
  scoreTone,
} from "@/lib/mastery";

describe("scoreTone", () => {
  it("returns the high tone at and above the high threshold", () => {
    expect(scoreTone(MASTERY_HIGH_THRESHOLD).bar).toBe("bg-status-tinggi");
    expect(scoreTone(100).text).toBe("text-status-tinggi");
  });

  it("returns the medium tone between the two thresholds", () => {
    expect(scoreTone(MASTERY_MEDIUM_THRESHOLD).bar).toBe("bg-status-sedang");
    expect(scoreTone(MASTERY_HIGH_THRESHOLD - 1).bar).toBe("bg-status-sedang");
  });

  it("returns the low tone below the medium threshold", () => {
    expect(scoreTone(MASTERY_MEDIUM_THRESHOLD - 1).bar).toBe("bg-status-rendah");
    expect(scoreTone(0).text).toBe("text-status-rendah");
  });
});

describe("barExtent", () => {
  it("renders nothing for a true zero or negative score", () => {
    expect(barExtent(0)).toBe(0);
    expect(barExtent(-5)).toBe(0);
  });

  it("floors a small positive score to the minimum visible bar", () => {
    expect(barExtent(1)).toBe(MIN_BAR_PERCENT);
  });

  it("passes through a normal score and clamps to 100", () => {
    expect(barExtent(64)).toBe(64);
    expect(barExtent(150)).toBe(100);
  });
});

describe("formatTrendDate", () => {
  it("formats an ISO date to a short Indonesian label", () => {
    expect(formatTrendDate("2026-06-07")).toBe("7 Jun");
    expect(formatTrendDate("2026-01-31")).toBe("31 Jan");
  });

  it("returns the raw input when it cannot be parsed", () => {
    expect(formatTrendDate("not-a-date")).toBe("not-a-date");
  });
});
