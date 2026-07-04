/**
 * Auth state for Google login. Holds the logged-in user (persisted in
 * localStorage so a refresh keeps the session) and exposes login/logout.
 *
 * Guest mode is the default: when VITE_GOOGLE_CLIENT_ID is unset, `isConfigured`
 * is false and the UI hides all login affordances — the app works anonymously
 * via the device id (see lib/deviceId.ts).
 */

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { loginWithGoogle } from "@/services/api";
import { resetDeviceId } from "@/lib/deviceId";
import type { AuthUser } from "@/types/auth";

const STORAGE_KEY = "asahlagi-auth";

/** OAuth Web client id (not a secret — ships in the bundle). Empty => guest-only. */
export const GOOGLE_CLIENT_ID =
  (import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined)?.trim() ?? "";

interface AuthContextValue {
  user: AuthUser | null;
  isConfigured: boolean;
  login: (credential: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function loadStoredUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(loadStoredUser);

  const login = useCallback(async (credential: string) => {
    const loggedIn = await loginWithGoogle(credential);
    setUser(loggedIn);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(loggedIn));
    } catch {
      // localStorage unavailable; session lives only for this tab.
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
    resetDeviceId(); // become a clean anonymous guest again
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isConfigured: GOOGLE_CLIENT_ID.length > 0, login, logout }),
    [user, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within <AuthProvider>");
  }
  return ctx;
}
