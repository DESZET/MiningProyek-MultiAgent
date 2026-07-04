import { useEffect, useRef, useState } from "react";
import type { SourceType } from "@/types/quiz";
import { EMPTY_STATES, BUTTON_LABELS, QUIZ_PAGE } from "@/utils/i18n";
import { validatePdfFile } from "@/lib/pdfValidation";
import { cn } from "@/lib/cn";

interface MaterialInputFormProps {
  sourceType: SourceType;
  onSubmitText: (materialText: string) => void;
  onSubmitUrl: (url: string) => void;
  onSubmitPdf: (file: File) => void;
  isSubmitting?: boolean;
  loadingMessage?: string;
  error?: string | null;
  /** External source can push a value into the text input (e.g. sample button). */
  prefillText?: string | null;
  /** External source can push a value into the URL input (e.g. smart paste). */
  prefillUrl?: string | null;
  /** Called when the user pastes a URL into the text textarea. Caller should
   * switch to the URL tab and populate the URL field via `prefillUrl`. */
  onSmartUrlPaste?: (url: string) => void;
  /** §4.8: save the current text material as a bookmark (text tab only). */
  onSaveText?: (text: string) => void;
  saveTextLabel?: string;
}

const URL_PASTE_RE = /^https?:\/\/\S+$/i;

/**
 * Material input form supporting 3 source types: text, URL, PDF.
 * Renders the appropriate input based on `sourceType`.
 */
export function MaterialInputForm({
  sourceType,
  onSubmitText,
  onSubmitUrl,
  onSubmitPdf,
  isSubmitting,
  loadingMessage,
  error,
  prefillText,
  prefillUrl,
  onSmartUrlPaste,
  onSaveText,
  saveTextLabel,
}: MaterialInputFormProps) {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Pull in externally-supplied text (e.g. when user clicks a sample button).
  useEffect(() => {
    if (prefillText) setText(prefillText);
  }, [prefillText]);

  // Pull in externally-supplied URL (e.g. smart paste detection switched tabs).
  useEffect(() => {
    if (prefillUrl) setUrl(prefillUrl);
  }, [prefillUrl]);

  function handleTextPaste(e: React.ClipboardEvent<HTMLTextAreaElement>) {
    if (!onSmartUrlPaste) return;
    // Only intercept when textarea is empty AND the paste is a single URL.
    // Anything else (mixed content, partial URL, follow-on paste) flows through normally.
    if (text.trim().length > 0) return;
    const pasted = e.clipboardData.getData("text/plain").trim();
    if (URL_PASTE_RE.test(pasted)) {
      e.preventDefault();
      onSmartUrlPaste(pasted);
    }
  }

  // Per-source validation
  const trimmedText = text.trim();
  const textValid = trimmedText.length >= 100;
  const textTooShort = trimmedText.length > 0 && trimmedText.length < 100;

  const trimmedUrl = url.trim();
  const urlValid =
    trimmedUrl.startsWith("http://") || trimmedUrl.startsWith("https://");

  const pdfValid = pdfFile !== null;

  const canSubmit =
    !isSubmitting &&
    ((sourceType === "text" && textValid) ||
      (sourceType === "url" && urlValid) ||
      (sourceType === "pdf" && pdfValid));

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    if (sourceType === "text") onSubmitText(trimmedText);
    else if (sourceType === "url") onSubmitUrl(trimmedUrl);
    else if (sourceType === "pdf" && pdfFile) onSubmitPdf(pdfFile);
  }

  function acceptFile(file: File | null) {
    setPdfError(null);
    if (!file) {
      setPdfFile(null);
      return;
    }
    const error = validatePdfFile(file);
    if (error) {
      setPdfError(
        error === "NOT_PDF"
          ? EMPTY_STATES.pdfMustBePdf
          : EMPTY_STATES.pdfTooLarge,
      );
      setPdfFile(null);
      return;
    }
    setPdfFile(file);
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    acceptFile(e.target.files?.[0] ?? null);
  }

  // Drag-and-drop for the PDF tab: the whole input area is a drop target so the
  // user doesn't have to hit the button precisely.
  const dropActive = sourceType === "pdf" && !isSubmitting;

  function handleDragOver(e: React.DragEvent) {
    if (!dropActive) return;
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    if (sourceType !== "pdf") return;
    // Ignore drags moving onto child elements; only clear when leaving the form.
    if (e.currentTarget.contains(e.relatedTarget as Node | null)) return;
    setIsDragging(false);
  }

  function handleDrop(e: React.DragEvent) {
    if (!dropActive) return;
    e.preventDefault();
    setIsDragging(false);
    acceptFile(e.dataTransfer.files?.[0] ?? null);
  }

  return (
    <form
      onSubmit={handleSubmit}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="space-y-4"
    >
      {sourceType === "text" && (
        <>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onPaste={handleTextPaste}
            placeholder={EMPTY_STATES.materialPlaceholder}
            rows={10}
            autoCapitalize="sentences"
            autoCorrect="on"
            spellCheck
            className="w-full resize-y rounded-xl border border-border-standard bg-bg-page p-4 text-base text-text-primary shadow-level-1 placeholder:text-text-muted focus:border-border-prominent focus:outline-none focus-visible:[box-shadow:var(--focus-ring)] disabled:opacity-70"
            disabled={isSubmitting}
          />
          {!isSubmitting && !error && !textTooShort && (
            <p className="text-sm text-text-muted">{EMPTY_STATES.materialHelp}</p>
          )}
          {textTooShort && !isSubmitting && (
            <p className="text-sm text-text-muted">
              {QUIZ_PAGE.minCharsTemplate(trimmedText.length)}
            </p>
          )}
        </>
      )}

      {sourceType === "url" && (
        <>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={EMPTY_STATES.urlPlaceholder}
            inputMode="url"
            autoCapitalize="none"
            autoCorrect="off"
            autoComplete="url"
            spellCheck={false}
            enterKeyHint="go"
            className="w-full rounded-xl border border-border-standard bg-bg-page p-4 text-base text-text-primary shadow-level-1 placeholder:text-text-muted focus:border-border-prominent focus:outline-none focus-visible:[box-shadow:var(--focus-ring)] disabled:opacity-70"
            disabled={isSubmitting}
          />
          {!isSubmitting && !error && (
            <p className="text-sm text-text-muted">{EMPTY_STATES.urlHelp}</p>
          )}
        </>
      )}

      {sourceType === "pdf" && (
        <>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="hidden"
            disabled={isSubmitting}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isSubmitting}
            className={cn(
              "flex w-full items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border-standard bg-bg-alt p-8 text-text-muted transition-colors hover:border-brand-accent hover:text-text-primary",
              "disabled:cursor-not-allowed disabled:opacity-60",
              pdfFile && "border-brand-accent text-text-primary",
              isDragging && "border-brand-accent bg-bg-page text-text-primary",
            )}
          >
            {pdfFile ? (
              <span className="flex flex-col items-center gap-1">
                <span className="font-medium">{pdfFile.name}</span>
                <span className="text-xs text-text-muted">
                  {(pdfFile.size / 1024).toFixed(0)} KB · {EMPTY_STATES.pdfChangeFile}
                </span>
              </span>
            ) : (
              <span className="flex flex-col items-center gap-1">
                <PdfUploadIcon />
                <span>
                  {isDragging
                    ? EMPTY_STATES.pdfDropActive
                    : EMPTY_STATES.pdfDropzone}
                </span>
              </span>
            )}
          </button>
          {pdfError && <p className="text-sm text-status-rendah">{pdfError}</p>}
          {!isSubmitting && !error && !pdfError && (
            <p className="text-sm text-text-muted">{EMPTY_STATES.pdfHelp}</p>
          )}
        </>
      )}

      {error && <p className="text-sm text-status-rendah">{error}</p>}

      {isSubmitting && loadingMessage && (
        <div
          className="flex items-center gap-3 rounded-xl border border-brand-accent bg-bg-alt p-4 shadow-level-1"
          role="status"
          aria-live="polite"
        >
          <PulsingDot />
          <p className="flex-1 text-sm font-medium text-text-primary">
            {loadingMessage}
          </p>
          <span className="font-mono text-[10px] uppercase tracking-[1.2px] text-text-muted">
            {EMPTY_STATES.pleaseWait}
          </span>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={!canSubmit}
          className="min-h-[44px] rounded-pill border border-brand-button bg-brand-button px-8 py-2.5 text-sm font-medium text-white shadow-level-1 transition-colors hover:bg-brand-button-hover active:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? BUTTON_LABELS.homeLoading : BUTTON_LABELS.homePrimary}
        </button>

        {sourceType === "text" && onSaveText && textValid && !isSubmitting && (
          <button
            type="button"
            onClick={() => onSaveText(trimmedText)}
            className="min-h-[44px] rounded-pill border border-border-standard bg-bg-page px-5 py-2 text-sm font-medium text-text-secondary shadow-level-1 transition-colors hover:bg-bg-alt hover:text-text-primary active:bg-bg-alt"
          >
            {saveTextLabel}
          </button>
        )}
      </div>
    </form>
  );
}

function PulsingDot() {
  return (
    <span className="relative inline-flex h-3 w-3 flex-shrink-0">
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-green opacity-60" />
      <span className="relative inline-flex h-3 w-3 rounded-full bg-brand-green" />
    </span>
  );
}

function PdfUploadIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-8 w-8"
      aria-hidden="true"
    >
      <path d="M5 4 H14 L19 9 V20 H5 Z" />
      <path d="M14 4 V9 H19" />
      <path d="M9 14 L12 11 L15 14" />
      <path d="M12 11 V18" />
    </svg>
  );
}
