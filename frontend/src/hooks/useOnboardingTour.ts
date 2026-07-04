import { useCallback } from "react";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import { ONBOARDING } from "@/utils/i18n";
import { markOnboarded, prefersReducedMotion } from "@/lib/onboarding";

const S = ONBOARDING.steps;

/**
 * Guided first-visit tour of the home page (ROADMAP §4.6), built on driver.js.
 *
 * Steps target elements by `data-tour="..."` attributes so markup refactors
 * don't silently break the tour. Steps whose target is missing are skipped by
 * driver.js, so the tour is resilient if (e.g.) the Daily Challenge card is
 * absent. Honours `prefers-reduced-motion` by disabling the highlight animation.
 */
export function useOnboardingTour() {
  const startTour = useCallback(() => {
    const reduced = prefersReducedMotion();

    const d = driver({
      showProgress: true,
      animate: !reduced,
      smoothScroll: !reduced,
      allowClose: true,
      overlayOpacity: 0.6,
      nextBtnText: ONBOARDING.next,
      prevBtnText: ONBOARDING.prev,
      doneBtnText: ONBOARDING.done,
      // Mark onboarded whether the user finishes or dismisses early — we never
      // want to nag the same browser again automatically.
      onDestroyed: () => markOnboarded(),
      steps: [
        { popover: { title: S.welcome.title, description: S.welcome.body } },
        {
          element: '[data-tour="source-tabs"]',
          popover: { title: S.source.title, description: S.source.body },
        },
        {
          element: '[data-tour="quiz-settings"]',
          popover: { title: S.settings.title, description: S.settings.body },
        },
        {
          element: '[data-tour="material-input"]',
          popover: { title: S.input.title, description: S.input.body },
        },
        {
          element: '[data-tour="daily-challenge"]',
          popover: { title: S.daily.title, description: S.daily.body },
        },
        { popover: { title: S.finish.title, description: S.finish.body } },
      ],
    });

    d.drive();
  }, []);

  return { startTour };
}
