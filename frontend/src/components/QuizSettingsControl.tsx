import { useState } from "react";
import type {
  Difficulty,
  QuestionCount,
  QuizSettings,
} from "@/types/quiz";
import { QUIZ_SETTINGS } from "@/utils/i18n";
import { cn } from "@/lib/cn";

const QUESTION_COUNTS: QuestionCount[] = [3, 5, 7, 10];
const DIFFICULTIES: Difficulty[] = ["easy", "medium", "hard"];

interface QuizSettingsControlProps {
  settings: QuizSettings;
  onChange: (settings: QuizSettings) => void;
  disabled?: boolean;
}

/**
 * Pre-generate quiz settings (ROADMAP §4.3): question count, difficulty, and an
 * "acak opsi" toggle. Collapsed by default so the main flow stays uncluttered;
 * the summary line shows the current choices at a glance.
 */
export function QuizSettingsControl({
  settings,
  onChange,
  disabled,
}: QuizSettingsControlProps) {
  const [open, setOpen] = useState(false);

  const summary = `${settings.num_questions} soal · ${
    QUIZ_SETTINGS.difficulty[settings.difficulty]
  }${settings.shuffle_options ? " · acak" : ""}`;

  return (
    <div className="rounded-xl border border-border-standard bg-bg-page shadow-level-1">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        disabled={disabled}
        aria-expanded={open}
        className="flex min-h-[44px] w-full items-center justify-between gap-3 rounded-xl px-4 py-3 text-left transition-colors hover:bg-bg-alt disabled:opacity-60"
      >
        <span className="flex flex-col">
          <span className="text-sm font-medium text-text-primary">
            {QUIZ_SETTINGS.toggle}
          </span>
          <span className="text-xs text-text-muted">{summary}</span>
        </span>
        <ChevronIcon className={cn("h-4 w-4 text-text-muted transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div className="space-y-4 border-t border-border-standard px-4 py-4">
          <SegmentedField<QuestionCount>
            label={QUIZ_SETTINGS.countLabel}
            options={QUESTION_COUNTS}
            value={settings.num_questions}
            renderOption={(n) => String(n)}
            onSelect={(num_questions) => onChange({ ...settings, num_questions })}
            disabled={disabled}
          />

          <SegmentedField<Difficulty>
            label={QUIZ_SETTINGS.difficultyLabel}
            options={DIFFICULTIES}
            value={settings.difficulty}
            renderOption={(d) => QUIZ_SETTINGS.difficulty[d]}
            onSelect={(difficulty) => onChange({ ...settings, difficulty })}
            disabled={disabled}
          />

          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-text-secondary">
              {QUIZ_SETTINGS.shuffleLabel}
            </span>
            <button
              type="button"
              role="switch"
              aria-checked={settings.shuffle_options}
              aria-label={QUIZ_SETTINGS.shuffleLabel}
              disabled={disabled}
              onClick={() =>
                onChange({
                  ...settings,
                  shuffle_options: !settings.shuffle_options,
                })
              }
              className={cn(
                "relative inline-flex h-6 w-11 flex-shrink-0 items-center rounded-full transition-colors disabled:opacity-60",
                settings.shuffle_options ? "bg-brand-button" : "bg-border-standard",
              )}
            >
              <span
                className={cn(
                  "inline-block h-5 w-5 transform rounded-full bg-white shadow-level-1 transition-transform",
                  settings.shuffle_options ? "translate-x-5" : "translate-x-0.5",
                )}
              />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

interface SegmentedFieldProps<T extends string | number> {
  label: string;
  options: readonly T[];
  value: T;
  renderOption: (option: T) => string;
  onSelect: (option: T) => void;
  disabled?: boolean;
}

function SegmentedField<T extends string | number>({
  label,
  options,
  value,
  renderOption,
  onSelect,
  disabled,
}: SegmentedFieldProps<T>) {
  return (
    <div className="space-y-2">
      <span className="text-sm text-text-secondary">{label}</span>
      <div role="radiogroup" aria-label={label} className="flex flex-wrap gap-2">
        {options.map((option) => {
          const selected = option === value;
          return (
            <button
              key={String(option)}
              type="button"
              role="radio"
              aria-checked={selected}
              disabled={disabled}
              onClick={() => onSelect(option)}
              className={cn(
                "min-h-[40px] min-w-[44px] rounded-pill border px-4 py-1.5 text-sm font-medium transition-colors disabled:opacity-60",
                selected
                  ? "border-brand-button bg-brand-button text-white shadow-level-1"
                  : "border-border-standard bg-bg-page text-text-secondary hover:bg-bg-alt hover:text-text-primary",
              )}
            >
              {renderOption(option)}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="m6 9 6 6 6-6" />
    </svg>
  );
}
