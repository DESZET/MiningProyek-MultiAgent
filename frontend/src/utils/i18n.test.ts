import { describe, it, expect } from "vitest";
import {
  ERROR_MESSAGES,
  formatDate,
  formatSeconds,
  getErrorMessage,
  toUnderstandingLevel,
} from "@/utils/i18n";

describe("getErrorMessage", () => {
  it("returns the canned message for a known code", () => {
    expect(getErrorMessage("MATERIAL_EMPTY")).toBe(
      ERROR_MESSAGES.MATERIAL_EMPTY,
    );
  });

  it("prefers the backend detail for context-rich codes", () => {
    const detail = "URL spesifik tidak bisa diambil karena butuh login.";
    expect(getErrorMessage("URL_FETCH_FAILED", detail)).toBe(detail);
  });

  it("falls back to the provided message for an unknown code", () => {
    expect(getErrorMessage("SOMETHING_NEW", "pesan cadangan")).toBe(
      "pesan cadangan",
    );
  });

  it("falls back to INTERNAL_ERROR when nothing else is available", () => {
    expect(getErrorMessage(undefined)).toBe(ERROR_MESSAGES.INTERNAL_ERROR);
  });
});

describe("formatSeconds", () => {
  it("formats seconds as m:ss with zero-padding", () => {
    expect(formatSeconds(0)).toBe("0:00");
    expect(formatSeconds(65)).toBe("1:05");
    expect(formatSeconds(600)).toBe("10:00");
  });
});

describe("formatDate", () => {
  it("formats an ISO timestamp to an Indonesian date", () => {
    const out = formatDate("2026-06-07T10:00:00Z");
    expect(out).toContain("2026");
    expect(out).toMatch(/jun/i);
  });

  it("returns an empty string for an invalid date", () => {
    expect(formatDate("not-a-date")).toBe("");
  });
});

describe("toUnderstandingLevel", () => {
  it("normalizes casing to the typed union", () => {
    expect(toUnderstandingLevel("High")).toBe("high");
    expect(toUnderstandingLevel("MEDIUM")).toBe("medium");
    expect(toUnderstandingLevel(" low ")).toBe("low");
  });

  it("returns null for anything outside the union", () => {
    expect(toUnderstandingLevel("unknown")).toBeNull();
    expect(toUnderstandingLevel("")).toBeNull();
  });
});
