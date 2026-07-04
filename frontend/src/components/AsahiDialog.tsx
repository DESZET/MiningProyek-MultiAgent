import { useEffect, useRef, useState } from "react";
import { Asahi } from "@/components/mascot/Asahi";
import { sendChat } from "@/services/api";
import type { ChatContext, ChatIntent } from "@/types/chat";

/**
 * Asahi game-dialog on the result page (docs/CHATBOT.md). Modeled on a
 * visual-novel / RPG dialogue box: Asahi's portrait on the left, her current
 * line on the right, and the player's choices as options below. One line shows
 * at a time (a choice replaces it with Asahi's reply) — not a scrolling log.
 *
 * Guardrails: opening fetched once (ref survives StrictMode), each intent asked
 * once (buttons disable), closing ends the dialog, local fallback if offline.
 */

interface AsahiDialogProps {
  context: ChatContext;
}

const ACTIONS: { intent: ChatIntent; label: string }[] = [
  { intent: "weak_points", label: "Lihat kelemahanku" },
  { intent: "study_tips", label: "Tips belajar" },
  { intent: "encouragement", label: "Semangatin aku" },
];

const CLOSING = "Sip! Semangat terus ya — asah lagi kapan pun kamu siap.";

const FALLBACK: Record<ChatIntent, (c: ChatContext) => string> = {
  opening: (c) =>
    `Hai, kamu! Skor kamu ${c.score_percentage}%. ${
      c.score_percentage >= 80
        ? "Mantap, pemahamanmu sudah kuat."
        : c.score_percentage >= 50
          ? "Lumayan — masih ada yang bisa diasah lagi."
          : "Belum apa-apa, ini langkah awal yang baik."
    }`,
  weak_points: (c) =>
    `Kamu salah di ${c.wrong_count} soal${
      c.unanswered_count ? ` dan ${c.unanswered_count} belum dijawab` : ""
    }. Coba baca ulang bagian itu, lalu asah lagi ya.`,
  study_tips: () =>
    "Coba baca ulang materinya, buat catatan singkat pakai kata-katamu sendiri, lalu asah lagi.",
  encouragement: () =>
    "Tiap kali kamu asah lagi, pemahamanmu nambah sedikit demi sedikit. Kamu pasti bisa!",
};

export function AsahiDialog({ context }: AsahiDialogProps) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [closed, setClosed] = useState(false);
  const [used, setUsed] = useState<ChatIntent[]>([]);
  const startedRef = useRef(false);

  // Opening line — fetched exactly once. The ref dedupes StrictMode's double
  // invoke; setState after unmount is a harmless no-op in React 18.
  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    (async () => {
      setLoading(true);
      try {
        const res = await sendChat({ intent: "opening", context });
        setMessage(res.reply);
      } catch {
        setMessage(FALLBACK.opening(context));
      } finally {
        setLoading(false);
      }
    })();
  }, [context]);

  async function handleIntent(intent: ChatIntent) {
    if (loading || closed || used.includes(intent)) return;
    setUsed((prev) => [...prev, intent]);
    setLoading(true);
    try {
      const res = await sendChat({ intent, context });
      setMessage(res.reply);
    } catch {
      setMessage(FALLBACK[intent](context));
    } finally {
      setLoading(false);
    }
  }

  function handleClose() {
    setMessage(CLOSING);
    setLoading(false);
    setClosed(true);
  }

  const allAsked = used.length === ACTIONS.length;

  return (
    <section
      aria-labelledby="asahi-dialog-heading"
      className="overflow-hidden rounded-2xl border-2 border-border-prominent bg-bg-page shadow-level-1"
    >
      <div className="flex items-stretch gap-4 p-5 sm:gap-5 sm:p-6">
        {/* Portrait */}
        <div className="flex h-[92px] w-[88px] shrink-0 items-end justify-center overflow-hidden rounded-xl border border-border-standard bg-gradient-to-b from-bg-alt to-bg-subtle">
          <Asahi mood="wave" size={84} />
        </div>

        {/* Speaker + current line */}
        <div className="flex min-w-0 flex-1 flex-col">
          <div className="mb-1.5 flex items-baseline gap-2">
            <span
              id="asahi-dialog-heading"
              className="text-sm font-semibold text-text-primary"
            >
              Asahi
            </span>
            <span className="text-xs text-text-secondary">teman belajarmu</span>
          </div>
          <div
            className="flex min-h-[3.5rem] flex-1 items-center"
            aria-live="polite"
          >
            {loading ? (
              <span className="inline-flex gap-1">
                <Dot /> <Dot delay="150ms" /> <Dot delay="300ms" />
                <span className="sr-only">Asahi sedang mengetik</span>
              </span>
            ) : (
              <p className="text-[15px] leading-relaxed text-text-primary sm:text-base">
                {message}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Choices */}
      {!closed && (
        <div className="flex flex-wrap items-center gap-2 border-t border-border-standard bg-bg-alt/40 px-5 py-3 sm:px-6">
          {ACTIONS.map((a) => (
            <button
              key={a.intent}
              type="button"
              onClick={() => handleIntent(a.intent)}
              disabled={loading || used.includes(a.intent)}
              className="rounded-pill border border-border-standard bg-bg-page px-4 py-1.5 text-sm text-text-primary shadow-level-1 transition-colors hover:bg-bg-alt active:bg-bg-alt disabled:cursor-not-allowed disabled:opacity-40"
            >
              {a.label}
            </button>
          ))}
          <button
            type="button"
            onClick={handleClose}
            disabled={loading}
            className="ml-auto rounded-pill px-4 py-1.5 text-sm text-text-secondary transition-colors hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-50"
          >
            {allAsked ? "Selesai" : "Makasih, Asahi"}
          </button>
        </div>
      )}
    </section>
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
