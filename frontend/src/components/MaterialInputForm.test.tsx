import "@testing-library/jest-dom/vitest";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MaterialInputForm } from "@/components/MaterialInputForm";
import { EMPTY_STATES } from "@/utils/i18n";

function renderPdfForm() {
  const onSubmitPdf = vi.fn();
  const utils = render(
    <MaterialInputForm
      sourceType="pdf"
      onSubmitText={vi.fn()}
      onSubmitUrl={vi.fn()}
      onSubmitPdf={onSubmitPdf}
    />,
  );
  const form = utils.container.querySelector("form") as HTMLFormElement;
  return { ...utils, form, onSubmitPdf };
}

function pdf(name: string): File {
  return new File(["%PDF-1.4"], name, { type: "application/pdf" });
}

describe("MaterialInputForm drag-and-drop (PDF)", () => {
  it("accepts a dropped PDF and shows its name", () => {
    const { form } = renderPdfForm();
    fireEvent.drop(form, { dataTransfer: { files: [pdf("materi.pdf")] } });
    expect(screen.getByText("materi.pdf")).toBeInTheDocument();
  });

  it("rejects a dropped non-PDF with an error", () => {
    const { form } = renderPdfForm();
    fireEvent.drop(form, {
      dataTransfer: { files: [new File(["x"], "catatan.docx")] },
    });
    expect(screen.getByText(EMPTY_STATES.pdfMustBePdf)).toBeInTheDocument();
    expect(screen.queryByText("catatan.docx")).not.toBeInTheDocument();
  });

  it("shows the drop-active hint while dragging over", () => {
    const { form } = renderPdfForm();
    fireEvent.dragOver(form);
    expect(screen.getByText(EMPTY_STATES.pdfDropActive)).toBeInTheDocument();
  });
});

describe("MaterialInputForm mobile keyboard hints (§6.5-A)", () => {
  it("sets prose-friendly attributes on the material textarea", () => {
    render(
      <MaterialInputForm
        sourceType="text"
        onSubmitText={vi.fn()}
        onSubmitUrl={vi.fn()}
        onSubmitPdf={vi.fn()}
      />,
    );
    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveAttribute("autocapitalize", "sentences");
    expect(textarea).toHaveAttribute("spellcheck", "true");
  });

  it("sets URL-friendly keyboard attributes on the URL input", () => {
    render(
      <MaterialInputForm
        sourceType="url"
        onSubmitText={vi.fn()}
        onSubmitUrl={vi.fn()}
        onSubmitPdf={vi.fn()}
      />,
    );
    const input = screen.getByRole("textbox");
    expect(input).toHaveAttribute("inputmode", "url");
    expect(input).toHaveAttribute("autocapitalize", "none");
    expect(input).toHaveAttribute("autocomplete", "url");
  });
});
