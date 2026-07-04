/**
 * Anonymous device identity for gamification.
 *
 * Generates a UUID once and persists it in localStorage. Sent as the
 * `X-Device-Id` header so the backend can attribute XP/streak/level to a
 * device without requiring login. Designed to be swappable for a real auth
 * user id later.
 */

const KEY = "asahlagi-device-id";

function generateId(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `dev-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function getDeviceId(): string {
  try {
    let id = localStorage.getItem(KEY);
    if (!id) {
      id = generateId();
      localStorage.setItem(KEY, id);
    }
    return id;
  } catch {
    // localStorage unavailable (private mode); ephemeral id for this session.
    return `ephemeral-${Math.random().toString(36).slice(2)}`;
  }
}

/**
 * Adopt a canonical device id after Google login so gamification calls follow
 * the account (the backend returns the account's canonical id).
 */
export function setDeviceId(id: string): void {
  try {
    localStorage.setItem(KEY, id);
  } catch {
    // localStorage unavailable; nothing to persist.
  }
}

/**
 * Drop the current identity and mint a fresh anonymous one. Called on logout so
 * the logged-out browser is a clean guest, not still pointing at the account.
 */
export function resetDeviceId(): string {
  const id = generateId();
  setDeviceId(id);
  return id;
}
