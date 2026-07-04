import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AsahiDialog } from "@/components/AsahiDialog";
import { sendChat } from "@/services/api";
import type { ChatContext } from "@/types/chat";

vi.mock("@/services/api", () => ({ sendChat: vi.fn() }));
const mockSendChat = vi.mocked(sendChat);

const context: ChatContext = {
  quiz_id: "q1",
  score_percentage: 60,
  understanding_level: "medium",
  correct_count: 3,
  wrong_count: 2,
  unanswered_count: 0,
  weak_topics: [],
};

beforeEach(() => mockSendChat.mockReset());

describe("AsahiDialog", () => {
  it("shows Asahi's opening line and the choice buttons", async () => {
    mockSendChat.mockResolvedValue({ reply: "Hai, kamu! Skor 60%." });
    render(<AsahiDialog context={context} />);

    expect(await screen.findByText("Hai, kamu! Skor 60%.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Lihat kelemahanku" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tips belajar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Semangatin aku" })).toBeInTheDocument();
  });

  it("replaces the line with Asahi's reply for the chosen intent", async () => {
    const user = userEvent.setup();
    mockSendChat
      .mockResolvedValueOnce({ reply: "Pembuka" })
      .mockResolvedValueOnce({ reply: "Coba baca ulang, lalu asah lagi." });
    render(<AsahiDialog context={context} />);
    await screen.findByText("Pembuka");

    await user.click(screen.getByRole("button", { name: "Tips belajar" }));

    expect(
      await screen.findByText("Coba baca ulang, lalu asah lagi."),
    ).toBeInTheDocument();
    expect(screen.queryByText("Pembuka")).not.toBeInTheDocument(); // replaced, not stacked
    expect(mockSendChat).toHaveBeenLastCalledWith({
      intent: "study_tips",
      context,
    });
  });

  it("falls back to a local message when the backend fails", async () => {
    const user = userEvent.setup();
    mockSendChat
      .mockResolvedValueOnce({ reply: "Pembuka" })
      .mockRejectedValueOnce(new Error("offline"));
    render(<AsahiDialog context={context} />);
    await screen.findByText("Pembuka");

    await user.click(screen.getByRole("button", { name: "Tips belajar" }));

    expect(await screen.findByText(/baca ulang materinya/)).toBeInTheDocument();
  });

  it("fetches the opening line once and disables a used choice", async () => {
    const user = userEvent.setup();
    mockSendChat
      .mockResolvedValueOnce({ reply: "Pembuka" })
      .mockResolvedValueOnce({ reply: "Balasan" });
    render(<AsahiDialog context={context} />);
    await screen.findByText("Pembuka");

    expect(mockSendChat).toHaveBeenCalledTimes(1);

    const tips = screen.getByRole("button", { name: "Tips belajar" });
    await user.click(tips);
    await screen.findByText("Balasan");

    expect(tips).toBeDisabled();
  });

  it("ends the dialog and hides the choices on close", async () => {
    const user = userEvent.setup();
    mockSendChat.mockResolvedValue({ reply: "Pembuka" });
    render(<AsahiDialog context={context} />);
    await screen.findByText("Pembuka");

    await user.click(screen.getByRole("button", { name: "Makasih, Asahi" }));

    expect(await screen.findByText(/Semangat terus ya/)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Tips belajar" }),
    ).not.toBeInTheDocument();
  });
});
