import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useCountUp } from "@/hooks/useCountUp";

function setReducedMotion(matches: boolean) {
  Object.defineProperty(window, "matchMedia", {
    configurable: true,
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

// The animated (requestAnimationFrame) path is intentionally not asserted here:
// jsdom's rAF timestamp doesn't share an origin with performance.now(), so the
// easing math is unreliable under test. The reduced-motion path lands on the
// exact same target value and is fully deterministic, so we cover that contract.
// Full motion is better verified via visual/E2E testing (see web/testing rules).
describe("useCountUp (reduced motion)", () => {
  beforeEach(() => {
    setReducedMotion(true);
  });

  it("snaps straight to the target", () => {
    const { result } = renderHook(() => useCountUp(80));
    expect(result.current).toBe(80);
  });

  it("tracks the exact target value, including when it changes", () => {
    const { result, rerender } = renderHook(
      ({ target }) => useCountUp(target),
      { initialProps: { target: 50 } },
    );
    expect(result.current).toBe(50);

    rerender({ target: 92 });
    expect(result.current).toBe(92);
  });
});
