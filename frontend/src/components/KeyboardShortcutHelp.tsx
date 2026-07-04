import { SHORTCUT_HELP } from "@/utils/i18n";

interface KeyboardShortcutHelpProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Modal overlay listing keyboard shortcuts. Triggered by `?` key on QuizPage.
 * Closes on Esc or backdrop click.
 */
export function KeyboardShortcutHelp({ open, onClose }: KeyboardShortcutHelpProps) {
  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={SHORTCUT_HELP.title}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-border-standard bg-bg-page p-6 shadow-level-3"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="mb-4 text-lg font-medium tracking-tight text-text-primary">
          {SHORTCUT_HELP.title}
        </h2>

        <ul className="space-y-2">
          {SHORTCUT_HELP.shortcuts.map((s, i) => (
            <li
              key={i}
              className="flex items-center justify-between gap-4 rounded-lg px-2 py-1.5"
            >
              <span className="text-sm text-text-secondary">{s.action}</span>
              <span className="flex flex-shrink-0 gap-1">
                {s.keys.map((k) => (
                  <kbd
                    key={k}
                    className="inline-flex h-7 min-w-[28px] items-center justify-center rounded-md border border-border-prominent bg-bg-alt px-2 font-mono text-[11px] font-medium text-text-primary"
                  >
                    {k}
                  </kbd>
                ))}
              </span>
            </li>
          ))}
        </ul>

        <p className="mt-4 font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
          {SHORTCUT_HELP.closeHint}
        </p>
      </div>
    </div>
  );
}
