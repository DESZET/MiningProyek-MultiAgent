import { describe, it, expect, beforeEach } from "vitest";
import { hasOnboarded, markOnboarded } from "@/lib/onboarding";

describe("onboarding flag", () => {
  beforeEach(() => localStorage.clear());

  it("reports not-onboarded by default", () => {
    expect(hasOnboarded()).toBe(false);
  });

  it("persists the onboarded flag", () => {
    markOnboarded();
    expect(hasOnboarded()).toBe(true);
  });
});
