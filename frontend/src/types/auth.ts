/**
 * Auth types — mirror backend/app/schemas/auth.py (AuthUserResponse).
 */

export interface AuthUser {
  id: string;
  email: string | null;
  name: string | null;
  avatar_url: string | null;
  /** Canonical device id the client adopts after login (gamification identity). */
  device_id: string;
}
