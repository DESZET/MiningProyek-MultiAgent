import { cn } from "@/lib/cn";

interface LogoProps {
  variant?: "full" | "icon";
  className?: string;
}

/**
 * Asahlagi logo. Renders the inline SVG mark + (optional) wordmark.
 * Per BRAND.md §3:
 *   - icon mark always emerald (#3ecf8e), mode-agnostic
 *   - wordmark uses currentColor → adapts to light/dark via CSS
 */
export function Logo({ variant = "full", className }: LogoProps) {
  if (variant === "icon") {
    return (
      <svg
        viewBox="0 0 64 64"
        xmlns="http://www.w3.org/2000/svg"
        className={cn("h-6 w-6", className)}
        role="img"
        aria-label="Asahlagi"
      >
        <path
          fill="#3ecf8e"
          d="M32 8 L56 56 L43 56 L32 30 L21 56 L8 56 Z M19 47 L43 32 L46 37 L22 52 Z"
        />
      </svg>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 font-medium tracking-tight",
        className,
      )}
    >
      <svg
        viewBox="0 0 64 64"
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6 flex-shrink-0"
        aria-hidden="true"
      >
        <path
          fill="#3ecf8e"
          d="M32 8 L56 56 L43 56 L32 30 L21 56 L8 56 Z M19 47 L43 32 L46 37 L22 52 Z"
        />
      </svg>
      {/* Hide the wordmark below 360px so the nav cluster (logo + XP + theme +
          auth) doesn't overflow on tiny phones. 375px+ keeps it. */}
      <span className="hidden text-[17px] text-text-primary min-[360px]:inline">
        asahlagi
      </span>
    </span>
  );
}
