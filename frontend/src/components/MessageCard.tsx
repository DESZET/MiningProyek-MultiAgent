import type { ReactNode } from "react";

interface MessageCardProps {
  title: string;
  body: string;
  children?: ReactNode;
}

/**
 * Centered card for empty / unavailable / loading states across the app
 * (Progress, Profil, Riwayat). Optional children render a CTA below the body.
 */
export function MessageCard({ title, body, children }: MessageCardProps) {
  return (
    <div className="mx-auto max-w-md space-y-4 rounded-2xl border border-border-standard bg-bg-page p-8 text-center shadow-level-1">
      <h1 className="text-2xl font-medium text-text-primary">{title}</h1>
      <p className="text-text-secondary">{body}</p>
      {children && <div className="flex justify-center pt-2">{children}</div>}
    </div>
  );
}
