import { useEffect } from "react";

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/**
 * Fires a brand-aligned confetti burst once when `trigger` flips true.
 * Skips entirely when the user prefers reduced motion.
 *
 * Colors mirror DESIGN.md emerald palette + a couple of warm accents so
 * the burst feels celebratory but stays on-brand (no rainbow chaos).
 */
export function useConfetti(trigger: boolean): void {
  useEffect(() => {
    if (!trigger || prefersReducedMotion()) return;

    let cancelled = false;
    let followUp: number | undefined;

    // Load canvas-confetti on demand so it never weighs down the initial
    // bundle — it's only needed here, and only when the burst actually fires.
    void import("canvas-confetti").then(({ default: confetti }) => {
      if (cancelled) return;

      const colors = ["#3ecf8e", "#00875a", "#a8e6c8", "#fafafa"];

      function fireBurst(x: number, originY: number = 0.6) {
        confetti({
          particleCount: 60,
          spread: 70,
          startVelocity: 35,
          origin: { x, y: originY },
          colors,
          ticks: 200,
          scalar: 0.9,
          disableForReducedMotion: true,
        });
      }

      // Two off-screen bursts converging toward center for a balanced look.
      fireBurst(0.15);
      fireBurst(0.85);

      // Tiny follow-up after a short delay for a satisfying "tail".
      followUp = window.setTimeout(() => {
        confetti({
          particleCount: 40,
          spread: 100,
          startVelocity: 25,
          origin: { x: 0.5, y: 0.3 },
          colors,
          ticks: 150,
          scalar: 0.8,
          disableForReducedMotion: true,
        });
      }, 280);
    });

    return () => {
      cancelled = true;
      if (followUp) window.clearTimeout(followUp);
    };
  }, [trigger]);
}
