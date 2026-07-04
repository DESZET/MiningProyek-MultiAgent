import { useEffect, useState } from "react";
import type { UnderstandingLevel } from "@/types/result";
import { cn } from "@/lib/cn";

/**
 * Asahi — Asahlagi's study companion mascot (BRAND.md §12).
 *
 * Puppet approach: ONE fixed anime base render, with per-expression variants that
 * are produced by inpainting ONLY the eyes/mouth region (masks + recipe in
 * `assets/mascot/inpaint-masks/`). Because everything outside that mask stays
 * byte-identical, every mood is the exact same character — consistency that full
 * AI re-generation could never hold.
 *
 * Expression PNGs live in `public/mascot/`. `mid` is the base render itself (a warm
 * neutral smile), so it always exists. Any mood whose file is missing falls back to
 * the base, so the app never shows a broken image while art is still being made.
 */

export type AsahiMood = "high" | "mid" | "low" | "wave" | "think" | "shocked" | "blush";

const BASE_SRC = "/mascot/asahi-base.webp";

const MOOD_SRC: Record<AsahiMood, string> = {
  mid: BASE_SRC, // base render = warm neutral
  high: "/mascot/asahi-high.webp",
  low: "/mascot/asahi-low.webp",
  wave: "/mascot/asahi-wave.webp",
  think: "/mascot/asahi-think.webp",
  shocked: "/mascot/asahi-shocked.webp",
  blush: "/mascot/asahi-blush.webp",
};

const MOOD_LABEL: Record<AsahiMood, string> = {
  high: "Asahi terlihat bangga",
  mid: "Asahi tersenyum hangat",
  low: "Asahi menyemangati dengan lembut",
  wave: "Asahi menyapa",
  think: "Asahi sedang berpikir",
  shocked: "Asahi terkejut",
  blush: "Asahi tersipu malu",
};

const LEVEL_TO_MOOD: Record<UnderstandingLevel, AsahiMood> = {
  high: "high",
  medium: "mid",
  low: "low",
};

/** Map an understanding-level result to the matching mascot mood. */
export function moodForLevel(level: UnderstandingLevel): AsahiMood {
  return LEVEL_TO_MOOD[level];
}

interface AsahiProps {
  /** Expression. Defaults to a warm neutral (the base render). */
  mood?: AsahiMood;
  /** Rendered width in px. Default 96. */
  size?: number;
  /** Crop to a square avatar (object-cover, top-anchored) instead of full portrait. */
  circle?: boolean;
  /** Accessible label. Falls back to a per-mood Indonesian description. */
  title?: string;
  className?: string;
}

export function Asahi({ mood = "mid", size = 96, circle = false, title, className }: AsahiProps) {
  const [src, setSrc] = useState(MOOD_SRC[mood]);

  // Reset the src whenever the mood changes (and re-attempt its dedicated art).
  useEffect(() => {
    setSrc(MOOD_SRC[mood]);
  }, [mood]);

  return (
    <img
      src={src}
      alt={title ?? MOOD_LABEL[mood]}
      width={size}
      draggable={false}
      loading="lazy"
      decoding="async"
      // If a mood's dedicated render doesn't exist yet, degrade to the base.
      onError={() => {
        if (src !== BASE_SRC) setSrc(BASE_SRC);
      }}
      className={cn(
        "select-none",
        circle ? "rounded-full object-cover object-top" : "h-auto",
        className,
      )}
      style={circle ? { width: size, height: size } : { width: size, height: "auto" }}
    />
  );
}
