import type { SourceType } from "@/types/quiz";
import { SOURCE_TYPE_LABELS } from "@/utils/i18n";
import { cn } from "@/lib/cn";

interface SourceTypeTabsProps {
  value: SourceType;
  onChange: (next: SourceType) => void;
  disabled?: boolean;
}

const TABS: ReadonlyArray<{ value: SourceType; icon: React.ReactNode }> = [
  { value: "text", icon: <TextIcon /> },
  { value: "pdf", icon: <PdfIcon /> },
  { value: "url", icon: <UrlIcon /> },
];

export function SourceTypeTabs({ value, onChange, disabled }: SourceTypeTabsProps) {
  return (
    <div
      role="tablist"
      aria-label="Jenis sumber materi"
      className="inline-flex rounded-full border border-border-standard bg-bg-page p-1 shadow-level-1"
    >
      {TABS.map((tab) => {
        const isActive = tab.value === value;
        return (
          <button
            key={tab.value}
            type="button"
            role="tab"
            aria-selected={isActive}
            disabled={disabled}
            onClick={() => onChange(tab.value)}
            className={cn(
              "flex min-h-[44px] items-center gap-2 rounded-full px-3 py-2 text-sm font-medium transition-colors sm:px-4",
              isActive
                ? "bg-text-primary text-bg-page"
                : "text-text-muted hover:text-text-primary active:text-text-primary",
              disabled && "cursor-not-allowed opacity-60",
            )}
          >
            {tab.icon}
            <span>{SOURCE_TYPE_LABELS[tab.value]}</span>
          </button>
        );
      })}
    </div>
  );
}

function TextIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" className="h-4 w-4" aria-hidden="true">
      <line x1="2" y1="4" x2="14" y2="4" strokeLinecap="round" />
      <line x1="2" y1="8" x2="14" y2="8" strokeLinecap="round" />
      <line x1="2" y1="12" x2="10" y2="12" strokeLinecap="round" />
    </svg>
  );
}

function PdfIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" className="h-4 w-4" aria-hidden="true">
      <path d="M3 2 H10 L13 5 V14 H3 Z" />
      <path d="M10 2 V5 H13" />
    </svg>
  );
}

function UrlIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4" aria-hidden="true">
      <path d="M6 9.5 a3 3 0 0 1 0 -4 l2 -2 a3 3 0 0 1 4.2 4.2 l -1 1" />
      <path d="M10 6.5 a3 3 0 0 1 0 4 l-2 2 a3 3 0 0 1 -4.2 -4.2 l 1 -1" />
    </svg>
  );
}
