import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useOnboardingTour } from "@/hooks/useOnboardingTour";
import { ONBOARDING } from "@/utils/i18n";

describe("useOnboardingTour", () => {
  beforeEach(() => localStorage.clear());
  afterEach(() => {
    // driver.js leaves its overlay/popover in the DOM until destroyed; clean up.
    document
      .querySelectorAll(".driver-popover, .driver-overlay")
      .forEach((el) => el.remove());
  });

  it("starting the tour mounts a popover with the welcome copy", async () => {
    const { result } = renderHook(() => useOnboardingTour());
    result.current.startTour();

    await waitFor(() => {
      expect(document.querySelector(".driver-popover")).toBeTruthy();
    });
    expect(document.body.textContent).toContain(ONBOARDING.steps.welcome.title);
  });
});
