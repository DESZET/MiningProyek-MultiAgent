import type { UnderstandingLevel } from "@/types/result";
import { UNDERSTANDING_LEVEL_LABEL } from "@/utils/i18n";
import { cn } from "@/lib/cn";

interface UnderstandingBadgeProps {
  level: UnderstandingLevel;
  className?: string;
}

const LEVEL_STYLES: Record<UnderstandingLevel, string> = {
  high: "bg-status-tinggi text-[var(--status-tinggi-text)]",
  medium: "bg-status-sedang text-[var(--status-sedang-text)]",
  low: "bg-status-rendah text-[var(--status-rendah-text)]",
};

export function UnderstandingBadge({
  level,
  className,
}: UnderstandingBadgeProps) {
  return (
    <span
      className={cn(
        "inline-block rounded-full px-3 py-1 font-mono text-[11px] font-medium uppercase tracking-[1.2px]",
        LEVEL_STYLES[level],
        className,
      )}
    >
      {UNDERSTANDING_LEVEL_LABEL[level]}
    </span>
  );
}
