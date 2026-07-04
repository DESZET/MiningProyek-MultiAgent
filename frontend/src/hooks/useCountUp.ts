import { useEffect, useState } from "react";

interface UseCountUpOptions {
  durationMs?: number;
  startOnMount?: boolean;
}

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Animates an integer from 0 to `target`. Respects `prefers-reduced-motion`
 * and snaps directly to the target when motion is disabled.
 */
export function useCountUp(
  target: number,
  { durationMs = 900, startOnMount = true }: UseCountUpOptions = {},
): number {
  const [value, setValue] = useState(() => (startOnMount ? 0 : target));

  useEffect(() => {
    if (prefersReducedMotion()) {
      setValue(target);
      return;
    }

    let frame = 0;
    const startTime = performance.now();

    function tick(now: number) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / durationMs);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(target * eased));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    }

    setValue(0);
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}
