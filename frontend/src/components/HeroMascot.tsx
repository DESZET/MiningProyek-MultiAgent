import { useEffect, useState } from "react";

/**
 * Interactive hero mascot.
 *
 * - Default: `high` (a cheerful welcome).
 * - Hover (mouse only): `blush` — Asahi gets shy when you pay attention.
 * - Click / tap (works on touch too): "poke" → a random playful expression.
 *
 * Only the colour-consistent "puppet" set is used — every frame shares the same
 * framing and warm-cream lighting (all inpainted from one base render), so the
 * character never jumps in size or tone when swapping. `wave` (a vivid close-up
 * generation) and `think` (a cooler, whiter-haired render) are deliberately
 * excluded as they break that consistency.
 *
 * Uses optimised 768x732 WebP frames (see public/mascot/*.webp). Reaction frames
 * are warmed on mount so the first interaction swaps instantly with no flicker.
 * Scale/active motion is gated behind motion-safe for reduced-motion users; the
 * expression swap itself is user-initiated and always allowed.
 */
type Expression = "high" | "blush" | "shocked" | "low";

const SRC: Record<Expression, string> = {
  high: "/mascot/asahi-high.webp",
  blush: "/mascot/asahi-blush.webp",
  shocked: "/mascot/asahi-shocked.webp",
  low: "/mascot/asahi-low.webp",
};

const LABEL: Record<Expression, string> = {
  high: "Asahi terlihat senang",
  blush: "Asahi tersipu",
  shocked: "Asahi kaget",
  low: "Asahi termenung",
};

const DEFAULT_EXPRESSION: Expression = "high";

// Expressions a "poke" can land on. blush is reused from the hover reaction.
const POKE_POOL: Expression[] = ["shocked", "low", "blush"];

export function HeroMascot() {
  const [expression, setExpression] = useState<Expression>(DEFAULT_EXPRESSION);

  // Warm the reaction frames so the first hover/tap has no download flicker.
  useEffect(() => {
    for (const expr of POKE_POOL) {
      const img = new Image();
      img.src = SRC[expr];
    }
  }, []);

  function poke() {
    setExpression((current) => {
      const options = POKE_POOL.filter((expr) => expr !== current);
      const index = Math.floor(Math.random() * options.length);
      return options[index] ?? current;
    });
  }

  return (
    <div className="relative isolate w-full max-w-sm">
      {/* Ground ellipse — reads as a surface the character stands on. A wider
          background glow was removed: against the mascot's pale hair it read as
          an uncut halo. The ground + bottom fade ground the figure on their own. */}
      <div
        aria-hidden
        className="pointer-events-none absolute bottom-2 left-1/2 z-0 h-5 w-2/3 -translate-x-1/2 rounded-[100%] bg-[radial-gradient(ellipse_at_center,color-mix(in_oklab,var(--status-tinggi)_22%,transparent),transparent_72%)] blur-[6px] transition-none dark:bg-[radial-gradient(ellipse_at_center,color-mix(in_oklab,var(--status-tinggi)_10%,transparent),transparent_72%)]"
      />
      <button
        type="button"
        onClick={poke}
        onPointerEnter={(event) => {
          if (event.pointerType === "mouse") setExpression("blush");
        }}
        onPointerLeave={(event) => {
          if (event.pointerType === "mouse") setExpression(DEFAULT_EXPRESSION);
        }}
        aria-label="Asahi, maskot Asahlagi — colek untuk mengganti ekspresinya"
        className="relative z-10 block w-full rounded-3xl outline-none transition-transform focus-visible:[box-shadow:var(--focus-ring)] motion-safe:hover:scale-[1.03] motion-safe:active:scale-95"
      >
        <img
          src={SRC[expression]}
          alt={LABEL[expression]}
          width={768}
          height={732}
          fetchPriority="high"
          draggable={false}
          className="h-auto w-full select-none object-contain [-webkit-mask-image:linear-gradient(to_bottom,#000_85%,transparent_100%)] [mask-image:linear-gradient(to_bottom,#000_85%,transparent_100%)]"
        />
      </button>
    </div>
  );
}
