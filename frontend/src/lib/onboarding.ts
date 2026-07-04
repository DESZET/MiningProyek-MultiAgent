/**
 * First-visit onboarding flag (ROADMAP §4.6).
 *
 * Stored in localStorage so the guided tour only auto-starts once per browser.
 * Versioned key so a future tour revision can re-trigger for everyone.
 */
const ONBOARDED_KEY = "asahlagi:onboarded:v1";

export function hasOnboarded(): boolean {
  try {
    return localStorage.getItem(ONBOARDED_KEY) === "1";
  } catch {
    // Private mode / storage disabled — treat as onboarded so we never trap the
    // user in a tour that can't remember it already ran.
    return true;
  }
}

export function markOnboarded(): void {
  try {
    localStorage.setItem(ONBOARDED_KEY, "1");
  } catch {
    // Best-effort only; a failed write just means the tour may show again.
  }
}

export function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}
