import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { CircleUserRound, History, LogOut, Settings, TrendingUp, Trophy } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AUTH_LABELS } from "@/utils/i18n";

function initial(name: string | null, email: string | null): string {
  const base = (name ?? email ?? "?").trim();
  return base ? base.charAt(0).toUpperCase() : "?";
}

/**
 * Avatar + dropdown for the logged-in user. Shows name/email and a logout
 * action. Closes on outside click and Escape.
 */
export function UserMenu() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onPointer(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  if (!user) return null;

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={AUTH_LABELS.accountMenu}
        className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border border-border-standard bg-bg-page text-sm font-semibold text-text-primary shadow-level-1 outline-none transition-colors hover:bg-[var(--hover-tint)] active:bg-[var(--hover-tint)] focus-visible:[box-shadow:var(--focus-ring)]"
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt=""
            className="h-full w-full object-cover"
            referrerPolicy="no-referrer"
          />
        ) : (
          initial(user.name, user.email)
        )}
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-2 w-56 overflow-hidden rounded-xl border border-border-standard bg-bg-page shadow-level-2"
        >
          <div className="border-b border-border-standard px-4 py-3">
            <p className="truncate text-sm font-medium text-text-primary">
              {user.name ?? AUTH_LABELS.guestName}
            </p>
            {user.email && (
              <p className="truncate text-xs text-text-muted">{user.email}</p>
            )}
          </div>
          <MenuLink
            to="/profil"
            icon={CircleUserRound}
            label={AUTH_LABELS.menuProfile}
            onNavigate={() => setOpen(false)}
          />
          <MenuLink
            to="/progress"
            icon={TrendingUp}
            label={AUTH_LABELS.menuProgress}
            onNavigate={() => setOpen(false)}
          />
          <MenuLink
            to="/riwayat"
            icon={History}
            label={AUTH_LABELS.menuHistory}
            onNavigate={() => setOpen(false)}
          />
          <MenuLink
            to="/peringkat"
            icon={Trophy}
            label={AUTH_LABELS.menuLeaderboard}
            onNavigate={() => setOpen(false)}
          />
          <MenuLink
            to="/pengaturan"
            icon={Settings}
            label={AUTH_LABELS.menuSettings}
            onNavigate={() => setOpen(false)}
          />
          <div className="border-t border-border-standard">
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                logout();
                window.location.reload();
              }}
              className="flex min-h-[44px] w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-text-primary outline-none transition-colors hover:bg-[var(--hover-tint)] active:bg-[var(--hover-tint)] focus-visible:bg-[var(--hover-tint)]"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
              {AUTH_LABELS.logout}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function MenuLink({
  to,
  icon: Icon,
  label,
  onNavigate,
}: {
  to: string;
  icon: typeof LogOut;
  label: string;
  onNavigate: () => void;
}) {
  return (
    <Link
      to={to}
      role="menuitem"
      onClick={onNavigate}
      className="flex min-h-[44px] w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-text-primary outline-none transition-colors hover:bg-[var(--hover-tint)] active:bg-[var(--hover-tint)] focus-visible:bg-[var(--hover-tint)]"
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {label}
    </Link>
  );
}
