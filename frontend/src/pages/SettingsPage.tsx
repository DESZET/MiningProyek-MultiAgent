import { LogOut, Settings as SettingsIcon } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LearningPreferences } from "@/components/LearningPreferences";
import { GoogleLoginButton } from "@/components/auth/GoogleLoginButton";
import { useAuth } from "@/context/AuthContext";
import { LEARNING_PREFS, SETTINGS_PAGE } from "@/utils/i18n";

/**
 * Settings (ROADMAP §4.8b): appearance (theme) + account (info / logout).
 * Theme works for everyone; the account card adapts to guest vs logged-in.
 */
export function SettingsPage() {
  const { user, isConfigured, logout } = useAuth();

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <PageHeader
        eyebrow={SETTINGS_PAGE.eyebrow}
        title={SETTINGS_PAGE.title}
        subtitle={SETTINGS_PAGE.subtitle}
        icon={SettingsIcon}
      />

      <SettingsCard
        title={SETTINGS_PAGE.appearanceTitle}
        caption={SETTINGS_PAGE.appearanceCaption}
      >
        <ThemeToggle />
      </SettingsCard>

      <SettingsCard
        title={LEARNING_PREFS.title}
        caption={LEARNING_PREFS.subtitle}
      >
        <LearningPreferences />
      </SettingsCard>

      {isConfigured && (
        <SettingsCard
          title={SETTINGS_PAGE.accountTitle}
          caption={
            user ? SETTINGS_PAGE.accountCaption : SETTINGS_PAGE.guestTitle
          }
        >
          {user ? (
            <div className="space-y-4">
              <dl className="space-y-2 text-sm">
                {user.name && (
                  <div className="flex justify-between gap-4">
                    <dt className="text-text-muted">
                      {SETTINGS_PAGE.accountNameLabel}
                    </dt>
                    <dd className="truncate font-medium text-text-primary">
                      {user.name}
                    </dd>
                  </div>
                )}
                {user.email && (
                  <div className="flex justify-between gap-4">
                    <dt className="text-text-muted">
                      {SETTINGS_PAGE.accountEmailLabel}
                    </dt>
                    <dd className="truncate font-medium text-text-primary">
                      {user.email}
                    </dd>
                  </div>
                )}
              </dl>
              <button
                type="button"
                onClick={() => {
                  logout();
                  window.location.reload();
                }}
                className="inline-flex min-h-[44px] items-center gap-2 rounded-pill border border-border-standard bg-bg-page px-5 py-2 text-sm font-medium text-status-rendah shadow-level-1 outline-none transition-colors hover:bg-[var(--hover-tint)] active:bg-[var(--hover-tint)] focus-visible:[box-shadow:var(--focus-ring)]"
              >
                <LogOut className="h-4 w-4" aria-hidden="true" />
                {SETTINGS_PAGE.logout}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-text-secondary">
                {SETTINGS_PAGE.guestBody}
              </p>
              <GoogleLoginButton />
            </div>
          )}
        </SettingsCard>
      )}
    </div>
  );
}

function SettingsCard({
  title,
  caption,
  children,
}: {
  title: string;
  caption: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4 rounded-2xl border border-border-standard bg-bg-page p-6 shadow-level-1">
      <div>
        <h2 className="text-lg font-medium text-text-primary">{title}</h2>
        <p className="mt-0.5 text-sm text-text-muted">{caption}</p>
      </div>
      {children}
    </section>
  );
}
