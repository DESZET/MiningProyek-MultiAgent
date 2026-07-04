/**
 * Shared PDF upload validation, used by both the file picker and drag-and-drop
 * on the homepage so the rules stay in one place.
 */

export const MAX_PDF_BYTES = 10 * 1024 * 1024; // 10 MB

export type PdfValidationError = "NOT_PDF" | "TOO_LARGE";

/** Returns an error code for an invalid PDF, or null when the file is accepted. */
export function validatePdfFile(file: File): PdfValidationError | null {
  if (!file.name.toLowerCase().endsWith(".pdf")) return "NOT_PDF";
  if (file.size > MAX_PDF_BYTES) return "TOO_LARGE";
  return null;
}
