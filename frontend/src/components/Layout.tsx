import type { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";
import { XpBadge } from "@/components/XpBadge";
import { AuthNav } from "@/components/auth/AuthNav";
import { useAuth } from "@/context/AuthContext";
import { useGamificationStats } from "@/hooks/useGamificationStats";
import { ONBOARDING } from "@/utils/i18n";

interface LayoutProps {
  children: ReactNode;
}

/**
 * App-level layout: nav + main content area.
 * Nav: Asahlagi logo (left); XP/streak widget, theme toggle, account menu
 * (right). Profil / Progres / Riwayat / Pengaturan live inside the account menu.
 */
export function Layout({ children }: LayoutProps) {
  const { stats } = useGamificationStats();
  const { user } = useAuth();
  const { pathname } = useLocation();
  const navigate = useNavigate();

  // §4.6: replay the onboarding tour on demand. The tour lives on the home page,
  // so send the user there with a flag the page reads to auto-start it.
  const isAppArea = pathname !== "/";
  function handleReplayTour() {
    navigate("/app?tour=1");
  }

  return (
    <div className="min-h-screen bg-bg-page">
      <header className="safe-pt border-b border-border-standard bg-bg-page">
        <nav className="safe-px mx-auto flex max-w-5xl items-center justify-between gap-2 py-4 [--safe-gutter:1rem] sm:gap-3 sm:[--safe-gutter:1.5rem]">
          <Link
            to={pathname === "/" ? "/" : "/app"}
            className="rounded-md outline-none focus-visible:[box-shadow:var(--focus-ring)]"
            aria-label="Asahlagi, Beranda"
          >
            <Logo variant="full" />
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            {/* XP/streak only for logged-in users (gamification is account-bound);
                guests and the marketing landing nav stay clean. */}
            {pathname !== "/" && user && <XpBadge stats={stats} />}
            {isAppArea && (
              <button
                type="button"
                onClick={handleReplayTour}
                aria-label={ONBOARDING.replayLabel}
                title={ONBOARDING.replayLabel}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-border-standard bg-bg-page text-text-secondary shadow-level-1 transition-colors hover:bg-bg-alt hover:text-text-primary focus-visible:[box-shadow:var(--focus-ring)]"
              >
                <HelpIcon />
              </button>
            )}
            <ThemeToggle />
            <AuthNav />
          </div>
        </nav>
      </header>
      <main className="safe-px mx-auto max-w-5xl pt-12 pb-[calc(6rem_+_env(safe-area-inset-bottom,0px))] [--safe-gutter:1.5rem]">
        {children}
      </main>
    </div>
  );
}

function HelpIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .8-1 1.7" />
      <path d="M12 17h.01" />
    </svg>
  );
}
