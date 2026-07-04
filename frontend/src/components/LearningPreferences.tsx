import { useEffect, useState } from "react";
import { getPreferences, updatePreferences } from "@/services/api";
import type { UserPreferences } from "@/types/gamification";
import type { Difficulty, QuestionCount } from "@/types/quiz";
import { LEARNING_PREFS, QUIZ_SETTINGS } from "@/utils/i18n";
import { cn } from "@/lib/cn";

const COUNTS: QuestionCount[] = [3, 5, 7, 10];
const DIFFICULTIES: Difficulty[] = ["easy", "medium", "hard"];
const WEEKLY_GOALS = [3, 5, 7, 10];

type LoadState =
  | { status: "loading" }
  | { status: "ready"; prefs: UserPreferences }
  | { status: "unavailable" };

/**
 * §4.8 — edit learning preferences. Saved per user and used as the default quiz
 * settings on the home page. Saves optimistically on each change; renders an
 * "unavailable" note when gamification is off.
 */
export function LearningPreferences() {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    void getPreferences().then((prefs) => {
      if (!active) return;
      setState(prefs ? { status: "ready", prefs } : { status: "unavailable" });
    });
    return () => {
      active = false;
    };
  }, []);

  if (state.status === "loading") return null;
  if (state.status === "unavailable") {
    return <p className="text-sm text-text-muted">{LEARNING_PREFS.unavailable}</p>;
  }

  const prefs = state.prefs;

  function apply(changes: Partial<UserPreferences>) {
    setState({ status: "ready", prefs: { ...prefs, ...changes } });
    void updatePreferences(changes);
  }

  return (
    <div className="space-y-5">
      <Segmented
        label={LEARNING_PREFS.countLabel}
        options={COUNTS}
        value={prefs.default_num_questions}
        render={(n) => String(n)}
        onSelect={(n) => apply({ default_num_questions: n })}
      />
      <Segmented
        label={LEARNING_PREFS.difficultyLabel}
        options={DIFFICULTIES}
        value={prefs.default_difficulty}
        render={(d) => QUIZ_SETTINGS.difficulty[d]}
        onSelect={(d) => apply({ default_difficulty: d })}
      />
      <Segmented
        label={LEARNING_PREFS.weeklyGoalLabel}
        options={WEEKLY_GOALS}
        value={prefs.weekly_goal}
        render={(n) => String(n)}
        onSelect={(n) => apply({ weekly_goal: n })}
      />

      <div className="flex items-center justify-between gap-3">
        <span className="text-sm text-text-secondary">
          {LEARNING_PREFS.shuffleLabel}
        </span>
        <button
          type="button"
          role="switch"
          aria-checked={prefs.shuffle_options}
          aria-label={LEARNING_PREFS.shuffleLabel}
          onClick={() => apply({ shuffle_options: !prefs.shuffle_options })}
          className={cn(
            "relative inline-flex h-6 w-11 flex-shrink-0 items-center rounded-full transition-colors",
            prefs.shuffle_options ? "bg-brand-button" : "bg-border-standard",
          )}
        >
          <span
            className={cn(
              "inline-block h-5 w-5 transform rounded-full bg-white shadow-level-1 transition-transform",
              prefs.shuffle_options ? "translate-x-5" : "translate-x-0.5",
            )}
          />
        </button>
      </div>
    </div>
  );
}

interface SegmentedProps<T extends string | number> {
  label: string;
  options: readonly T[];
  value: T;
  render: (o: T) => string;
  onSelect: (o: T) => void;
}

function Segmented<T extends string | number>({
  label,
  options,
  value,
  render,
  onSelect,
}: SegmentedProps<T>) {
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
              onClick={() => onSelect(option)}
              className={cn(
                "min-h-[40px] min-w-[44px] rounded-pill border px-4 py-1.5 text-sm font-medium transition-colors",
                selected
                  ? "border-brand-button bg-brand-button text-white shadow-level-1"
                  : "border-border-standard bg-bg-page text-text-secondary hover:bg-bg-alt hover:text-text-primary",
              )}
            >
              {render(option)}
            </button>
          );
        })}
      </div>
    </div>
  );
}
