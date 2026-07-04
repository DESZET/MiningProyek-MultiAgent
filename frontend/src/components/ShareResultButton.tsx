import { useState } from "react";
import type { QuizSubmitResponse } from "@/types/result";
import { buildShareUrl } from "@/lib/shareResult";
import { RESULT_SHARE } from "@/utils/i18n";

interface ShareResultButtonProps {
  result: QuizSubmitResponse;
}

/**
 * Share the current result (ROADMAP §4.2). Uses the native share sheet when
 * available (mobile), otherwise copies a self-contained link to the clipboard
 * and shows a brief "tersalin" confirmation.
 */
export function ShareResultButton({ result }: ShareResultButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleShare() {
    const url = buildShareUrl(result);
    const shareData = {
      title: RESULT_SHARE.shareTitle,
      text: RESULT_SHARE.shareText(result.score.score_percentage),
      url,
    };

    if (typeof navigator !== "undefined" && navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch (err) {
        // User dismissed the sheet — not an error worth surfacing.
        if (err instanceof DOMException && err.name === "AbortError") return;
        // Otherwise fall through to clipboard.
      }
    }

    if (navigator?.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch {
        // Clipboard blocked — nothing more we can gracefully do.
      }
    }
  }

  return (
    <button
      type="button"
      onClick={handleShare}
      className="inline-flex min-h-[44px] items-center gap-2 rounded-pill border border-border-standard bg-bg-page px-5 py-2 text-sm font-medium text-text-primary shadow-level-1 transition-colors hover:bg-bg-alt active:bg-bg-alt"
    >
      <ShareIcon />
      {copied ? RESULT_SHARE.copied : RESULT_SHARE.button}
    </button>
  );
}

function ShareIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4"
      aria-hidden="true"
    >
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <path d="M8.6 13.5 15.4 17.5" />
      <path d="M15.4 6.5 8.6 10.5" />
    </svg>
  );
}
