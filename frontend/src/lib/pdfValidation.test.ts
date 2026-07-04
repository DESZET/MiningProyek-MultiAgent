import { describe, it, expect } from "vitest";
import { MAX_PDF_BYTES, validatePdfFile } from "@/lib/pdfValidation";

function fakeFile(name: string, size: number): File {
  const file = new File(["x"], name, { type: "application/pdf" });
  Object.defineProperty(file, "size", { value: size });
  return file;
}

describe("validatePdfFile", () => {
  it("accepts a reasonable .pdf (case-insensitive extension)", () => {
    expect(validatePdfFile(fakeFile("materi.pdf", 1024))).toBeNull();
    expect(validatePdfFile(fakeFile("MATERI.PDF", 1024))).toBeNull();
  });

  it("rejects a non-PDF extension", () => {
    expect(validatePdfFile(fakeFile("materi.docx", 1024))).toBe("NOT_PDF");
  });

  it("rejects a file over the size limit", () => {
    expect(validatePdfFile(fakeFile("besar.pdf", MAX_PDF_BYTES + 1))).toBe(
      "TOO_LARGE",
    );
  });

  it("accepts a file exactly at the size limit", () => {
    expect(validatePdfFile(fakeFile("pas.pdf", MAX_PDF_BYTES))).toBeNull();
  });
});
