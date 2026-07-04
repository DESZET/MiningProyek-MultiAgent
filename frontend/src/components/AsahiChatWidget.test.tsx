import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AsahiChatWidget } from "@/components/AsahiChatWidget";
import { askAsahi } from "@/services/api";

vi.mock("@/services/api", () => ({
  askAsahi: vi.fn(),
  getAsahiHistory: vi.fn(() => Promise.resolve({ messages: [] })),
}));
const mockAsk = vi.mocked(askAsahi);

beforeEach(() => mockAsk.mockReset());

describe("AsahiChatWidget", () => {
  it("opens, sends a question, and shows Asahi's reply", async () => {
    const user = userEvent.setup();
    mockAsk.mockResolvedValue({ reply: "Coba buat catatan singkat, lalu asah lagi." });
    render(<AsahiChatWidget />);

    await user.click(screen.getByRole("button", { name: "Ngobrol dengan Asahi" }));
    expect(screen.getByText(/Ada yang mau ditanya/)).toBeInTheDocument();

    await user.type(
      screen.getByPlaceholderText(/Tanya soal belajar/),
      "gimana cara belajar efektif?",
    );
    await user.click(screen.getByRole("button", { name: "Kirim" }));

    expect(screen.getByText("gimana cara belajar efektif?")).toBeInTheDocument();
    expect(
      await screen.findByText("Coba buat catatan singkat, lalu asah lagi."),
    ).toBeInTheDocument();
    expect(mockAsk).toHaveBeenCalledTimes(1);
  });

  it("falls back to a local message when the backend fails", async () => {
    const user = userEvent.setup();
    mockAsk.mockRejectedValueOnce(new Error("offline"));
    render(<AsahiChatWidget />);

    await user.click(screen.getByRole("button", { name: "Ngobrol dengan Asahi" }));
    await user.type(screen.getByPlaceholderText(/Tanya soal belajar/), "halo");
    await user.click(screen.getByRole("button", { name: "Kirim" }));

    expect(await screen.findByText(/nggak bisa nyaut/)).toBeInTheDocument();
  });
});
