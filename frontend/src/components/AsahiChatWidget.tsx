import { useEffect, useRef, useState } from "react";
import { Send, X } from "lucide-react";
import { Asahi } from "@/components/mascot/Asahi";
import { askAsahi, getAsahiHistory } from "@/services/api";
import { ApiException } from "@/types/api";
import type { FreeChatMessage } from "@/types/chat";
import { cn } from "@/lib/cn";

/**
 * Floating Asahi chat (home page) — a free-text chat bubble. Guardrails live in
 * the backend system prompt (Asahi only discusses studying / the app, refuses
 * off-topic, resists prompt-injection). If the backend is unreachable, replies
 * fall back to a friendly local message so the widget never breaks.
 */

const GREETING =
  "Hai, kamu! Ada yang mau ditanya soal belajar atau cara pakai Asahlagi? Tanya aja ya.";
const ERROR_REPLY = "Maaf, aku lagi nggak bisa nyaut. Coba lagi sebentar ya.";
const MAX_LEN = 600;

export function AsahiChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<FreeChatMessage[]>([
    { role: "asahi", content: GREETING },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Keep the conversation scrolled to the latest message.
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  // Focus the input when the panel opens.
  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  // Restore recent conversation from the server the first time the panel opens.
  const loadedRef = useRef(false);
  useEffect(() => {
    if (!open || loadedRef.current) return;
    loadedRef.current = true;
    getAsahiHistory()
      .then((res) => {
        if (res.messages.length > 0) setMessages(res.messages);
      })
      .catch(() => {
        /* no memory yet (offline / migration not applied) — keep the greeting */
      });
  }, [open]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    const history = messages.slice(-16); // keep the request within backend limits
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await askAsahi({ message: text, history });
      setMessages((prev) => [...prev, { role: "asahi", content: res.reply }]);
    } catch (err) {
      // Surface the backend's friendly message (e.g. "lagi rame" on rate limit),
      // but only when it's a plain string — a 422 detail is an array of objects
      // and would crash rendering. Fall back to a generic line otherwise.
      const detail = err instanceof ApiException ? err.error.detail : undefined;
      const reply = typeof detail === "string" ? detail : ERROR_REPLY;
      setMessages((prev) => [...prev, { role: "asahi", content: reply }]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  return (
    <>
      {open && (
        <div
          role="dialog"
          aria-label="Ngobrol dengan Asahi"
          className="fixed bottom-24 right-4 z-40 flex h-[28rem] max-h-[70vh] w-[22rem] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl border border-border-standard bg-bg-page shadow-level-2 sm:right-6"
        >
          {/* Header */}
          <div className="flex items-center gap-3 border-b border-border-standard px-4 py-3">
            <Asahi mood="wave" size={36} circle className="shrink-0" />
            <div className="min-w-0 flex-1 leading-tight">
              <p className="text-sm font-semibold text-text-primary">Asahi</p>
              <p className="text-xs text-text-secondary">teman belajarmu</p>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Tutup obrolan"
              className="rounded-full p-1.5 text-text-secondary outline-none transition-colors hover:bg-[var(--hover-tint)] hover:text-text-primary focus-visible:[box-shadow:var(--focus-ring)]"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div
            ref={scrollRef}
            className="flex-1 space-y-2.5 overflow-y-auto px-4 py-3"
            aria-live="polite"
          >
            {messages.map((m, i) => (
              <div key={i} className={cn("flex", m.role === "user" && "justify-end")}>
                <p
                  className={cn(
                    "max-w-[85%] whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-[14px] leading-relaxed",
                    m.role === "user"
                      ? "rounded-tr-sm bg-status-tinggi text-[var(--status-tinggi-text)]"
                      : "rounded-tl-sm bg-bg-alt text-text-primary",
                  )}
                >
                  {m.content}
                </p>
              </div>
            ))}
            {loading && (
              <div className="flex">
                <p className="rounded-2xl rounded-tl-sm bg-bg-alt px-3.5 py-2.5">
                  <span className="inline-flex gap-1 align-middle">
                    <Dot /> <Dot delay="150ms" /> <Dot delay="300ms" />
                  </span>
                  <span className="sr-only">Asahi sedang mengetik</span>
                </p>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex items-end gap-2 border-t border-border-standard p-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value.slice(0, MAX_LEN))}
              onKeyDown={onKeyDown}
              rows={1}
              placeholder="Tanya soal belajar…"
              className="max-h-24 min-h-[2.5rem] flex-1 resize-none rounded-xl border border-border-standard bg-bg-page px-3 py-2 text-sm text-text-primary outline-none placeholder:text-text-muted focus-visible:[box-shadow:var(--focus-ring)]"
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={loading || !input.trim()}
              aria-label="Kirim"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-button text-white shadow-level-1 transition-colors hover:bg-brand-button-hover disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Floating bubble */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Tutup obrolan Asahi" : "Ngobrol dengan Asahi"}
        aria-expanded={open}
        className="fixed bottom-5 right-4 z-40 flex h-14 w-14 items-center justify-center overflow-hidden rounded-full border border-border-standard bg-bg-page shadow-level-2 outline-none transition-transform hover:scale-105 focus-visible:[box-shadow:var(--focus-ring)] motion-reduce:transition-none sm:right-6"
      >
        {open ? (
          <X className="h-5 w-5 text-text-primary" />
        ) : (
          <Asahi mood="wave" size={52} circle />
        )}
      </button>
    </>
  );
}

function Dot({ delay = "0ms" }: { delay?: string }) {
  return (
    <span
      className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-text-secondary motion-reduce:animate-none"
      style={{ animationDelay: delay }}
    />
  );
}
