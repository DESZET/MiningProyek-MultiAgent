import { useAuth } from "@/context/AuthContext";
import { GoogleLoginButton } from "@/components/auth/GoogleLoginButton";
import { UserMenu } from "@/components/auth/UserMenu";

/**
 * Nav slot for auth. Renders nothing when login is not configured (guest-only
 * mode); otherwise the user menu when logged in, or the Google button.
 */
export function AuthNav() {
  const { isConfigured, user } = useAuth();
  if (!isConfigured) return null;
  return user ? <UserMenu /> : <GoogleLoginButton />;
}
