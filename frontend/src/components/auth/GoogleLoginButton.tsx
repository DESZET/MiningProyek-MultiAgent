import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "@/context/AuthContext";
import { AUTH_LABELS } from "@/utils/i18n";

/**
 * "Masuk dengan Google" — Google's official GIS button. On success it yields a
 * Google ID token (credential) which we verify on the backend. A full reload
 * after login keeps every identity-bound view (nav XP, progress) consistent.
 */
export function GoogleLoginButton() {
  const { login } = useAuth();
  const [error, setError] = useState(false);

  return (
    <div className="flex flex-col items-end gap-1">
      <GoogleLogin
        onSuccess={async (response) => {
          if (!response.credential) {
            setError(true);
            return;
          }
          try {
            setError(false);
            await login(response.credential);
            window.location.reload();
          } catch {
            setError(true);
          }
        }}
        onError={() => setError(true)}
        theme="outline"
        size="medium"
        shape="pill"
        text="signin"
      />
      {error && (
        <span role="alert" className="text-[11px] text-status-rendah">
          {AUTH_LABELS.loginError}
        </span>
      )}
    </div>
  );
}
