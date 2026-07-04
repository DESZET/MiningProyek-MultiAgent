import { useState } from "react";
import { cn } from "@/lib/cn";

interface MatchingFieldProps {
  leftItems: string[];
  rightItems: string[];
  /** matches[i] = chosen right index for left i, or -1 when unpaired. */
  matches: number[];
  onChange: (matches: number[]) => void;
}

function letter(i: number): string {
  return String.fromCharCode(65 + i);
}

/**
 * §6.2 matching interaction: tap a term (left), then tap the statement (right)
 * to pair them. Tapping a paired term again clears it. Keyboard-accessible
 * (everything is a real button). 1:1 is not enforced — the user can repoint a
 * statement, and scoring credits each correct pair independently.
 */
export function MatchingField({
  leftItems,
  rightItems,
  matches,
  onChange,
}: MatchingFieldProps) {
  const [activeLeft, setActiveLeft] = useState<number | null>(null);

  function handleLeftClick(i: number) {
    if ((matches[i] ?? -1) >= 0) {
      // Clear an existing pairing on tap.
      const next = [...matches];
      next[i] = -1;
      onChange(next);
      setActiveLeft(null);
      return;
    }
    setActiveLeft((cur) => (cur === i ? null : i));
  }

  function handleRightClick(j: number) {
    if (activeLeft === null) return;
    const next = [...matches];
    next[activeLeft] = j;
    onChange(next);
    setActiveLeft(null);
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {/* Terms (left) */}
      <ul className="space-y-2">
        {leftItems.map((term, i) => {
          const matchIdx = matches[i] ?? -1;
          const paired = matchIdx >= 0;
          const isActive = activeLeft === i;
          return (
            <li key={i}>
              <button
                type="button"
                onClick={() => handleLeftClick(i)}
                aria-pressed={isActive}
                className={cn(
                  "flex w-full items-center justify-between gap-2 rounded-xl border px-3 py-2.5 text-left text-sm transition-colors",
                  isActive
                    ? "border-brand-accent bg-bg-alt text-text-primary ring-1 ring-brand-accent/40"
                    : paired
                      ? "border-brand-accent/60 bg-bg-page text-text-primary"
                      : "border-border-standard bg-bg-page text-text-primary hover:bg-bg-alt",
                )}
              >
                <span className="font-medium">{term}</span>
                <span
                  className={cn(
                    "inline-flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 font-mono text-xs",
                    paired
                      ? "bg-brand-accent text-white"
                      : "bg-bg-subtle text-text-muted",
                  )}
                >
                  {paired ? letter(matchIdx) : "–"}
                </span>
              </button>
            </li>
          );
        })}
      </ul>

      {/* Statements (right / answer bank) */}
      <ul className="space-y-2">
        {rightItems.map((statement, j) => {
          const usedBy = matches.indexOf(j);
          const isUsed = usedBy >= 0;
          return (
            <li key={j}>
              <button
                type="button"
                onClick={() => handleRightClick(j)}
                disabled={activeLeft === null}
                className={cn(
                  "flex w-full items-start gap-3 rounded-xl border px-3 py-2.5 text-left text-sm transition-colors",
                  "disabled:cursor-default",
                  activeLeft !== null
                    ? "border-border-standard bg-bg-page hover:border-brand-accent hover:bg-bg-alt"
                    : "border-border-standard bg-bg-page",
                  isUsed && "border-brand-accent/60",
                )}
              >
                <span className="mt-0.5 inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-bg-subtle px-1.5 font-mono text-xs font-medium text-text-muted">
                  {letter(j)}
                </span>
                <span className="text-text-primary">{statement}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
