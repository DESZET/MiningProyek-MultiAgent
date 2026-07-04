"""Answer-aware question-generation core (pure, model-free helpers).

This module fixes the central quiz-quality bug: previously the "correct answer"
was just `max(keywords, key=len)` — the longest word in a passage, with no
relation to the generated question (e.g. "Berapa jumlah planet?" → "mengitarinya").

The answer-aware flow guarantees the correct answer actually answers the question:

    1. select_answer_span(passage)  -> pick a SALIENT span first (number /
       proper noun / content noun; verbs and function words are penalised).
    2. answer_aware_prompt(passage, answer) -> highlight the span so the DL
       model is biased to ask about it.
    3. (model generates a question)
    4. question_is_consistent(question, answer) -> reject mismatches
       (e.g. "berapa" must map to a number). On failure the caller builds a
       make_cloze_question() for the SAME span, which is coherent by construction.
    5. build_distractors(answer, ...) -> same-category options (numbers for a
       number answer, proper nouns for a name, length-similar otherwise).

Everything here is dependency-free (no torch / transformers) so it unit-tests
fast. The actual model call lives in inference.py (local) and the HF Space app.py;
both share an identical copy of this file. Keep them in sync.

OWNER: Audry (Quiz Generator)
"""

from __future__ import annotations

import difflib
import random
import re

# ---------------------------------------------------------------------------
# Vocab
# ---------------------------------------------------------------------------

_STOP_WORDS: frozenset[str] = frozenset({
    "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "ini",
    "itu", "atau", "adalah", "akan", "tidak", "juga", "dapat", "sebagai",
    "telah", "oleh", "dalam", "saat", "yaitu", "namun", "agar", "karena",
    "lebih", "secara", "menjadi", "sangat", "harus", "bahwa", "hanya",
    "kita", "mereka", "kami", "kamu", "saya", "anda", "tetapi", "sehingga",
    "sudah", "belum", "masih", "bisa", "tersebut", "ialah", "ada", "tiap",
    "seperti", "sehingga", "maupun", "serta", "hingga", "sampai", "antara",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
    "this", "that", "these", "those", "it", "its", "they", "them",
})

# Indonesian number words (ordered so we can build "nearby" numeric distractors).
_NUMBER_WORDS: tuple[str, ...] = (
    "nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh",
    "delapan", "sembilan", "sepuluh", "sebelas", "duabelas", "dua belas",
)
_NUMBER_WORD_SET = frozenset(_NUMBER_WORDS) | frozenset({
    "belas", "puluh", "ratus", "ribu", "juta", "miliar", "milyar",
    "setengah", "seperempat", "puluhan", "ratusan", "ribuan",
})

# Indonesian verb affixes — strong signal a token is NOT a good answer.
_VERB_PREFIX_RE = re.compile(r"^(memper|member|menge|meng|meny|mem|men|me|di|ter|ber)[a-z]")
_VERB_SUFFIX_RE = re.compile(r"(kan|nya|lah|i)$")

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{3,}")
_DIGIT_RE = re.compile(r"^\d[\d.,]*$")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Question starters (also used to detect/strip the question form).
_QUESTION_STARTERS = (
    "Apa", "Apakah", "Bagaimana", "Mengapa", "Kenapa", "Siapa", "Siapakah",
    "Kapan", "Di mana", "Dimana", "Berapa", "Berapakah", "Manakah",
    "Mana yang", "Sebutkan", "Jelaskan", "Tentukan", "Hitunglah",
)


# ---------------------------------------------------------------------------
# Tokenising / passages
# ---------------------------------------------------------------------------

def split_passages(text: str, n: int) -> list[str]:
    """Pick up to `n` evenly-spaced sentences from the text."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    if len(sentences) <= n:
        return sentences[:n]
    step = max(1, len(sentences) // n)
    return [sentences[i * step] for i in range(n) if i * step < len(sentences)]


def extract_keywords(text: str) -> list[str]:
    """Distinct content words (>=3 letters, not stopwords), first-seen order."""
    seen: set[str] = set()
    words: list[str] = []
    for m in _WORD_RE.finditer(text):
        w = m.group(0)
        wl = w.lower()
        if wl in _STOP_WORDS or wl in seen:
            continue
        seen.add(wl)
        words.append(w)
    return words


# ---------------------------------------------------------------------------
# Token classification
# ---------------------------------------------------------------------------

def is_number(token: str) -> bool:
    t = token.strip().lower()
    return bool(_DIGIT_RE.match(t)) or t in _NUMBER_WORD_SET


def looks_like_verb(token: str) -> bool:
    """Heuristic: a lowercase me-/di-/ter-/ber- word is almost always a verb in
    prose (mengandung, berlangsung, dilepaskan, mengubah, menyerap). Capitalised
    tokens are proper nouns (Merah, Republik, Indonesia) — never flagged. Soft
    penalty only, so an occasional false positive (berita) still loses gently to
    a cleaner noun rather than being excluded outright."""
    if not token or token[:1].isupper():
        return False
    return bool(_VERB_PREFIX_RE.match(token.lower()))


def answer_type(token: str, passage: str = "") -> str:
    """Coarse category: 'number' | 'proper_noun' | 'common'.

    proper_noun = capitalised AND not the first word of the passage (so it is
    a genuine name, not just a sentence-initial capital).
    """
    if is_number(token):
        return "number"
    if token[:1].isupper():
        first = passage.strip().split(" ", 1)[0] if passage else ""
        if token != first:
            return "proper_noun"
    return "common"


# ---------------------------------------------------------------------------
# Answer-span selection
# ---------------------------------------------------------------------------

def _score_answer(token: str, passage: str) -> float:
    """Higher = better answer. Prefers numbers / proper nouns / content nouns;
    penalises verbs and very short words."""
    kind = answer_type(token, passage)
    score = 0.0
    if kind == "number":
        score += 6.0
    elif kind == "proper_noun":
        score += 4.0
    else:
        score += 1.0
    if looks_like_verb(token):
        score -= 4.0
    # Mild length preference among common nouns (content words tend to be longer).
    score += min(len(token), 10) * 0.15
    return score


def select_answer_span(passage: str, exclude: set[str] | None = None) -> str | None:
    """Pick the most quiz-worthy answer span from a passage.

    Returns None if nothing scores acceptably (e.g. a passage of only verbs /
    function words).
    """
    exclude = exclude or set()
    candidates = [
        w for w in extract_keywords(passage)
        if w.lower() not in exclude and len(w) >= 3
    ]
    if not candidates:
        return None
    best = max(candidates, key=lambda w: (_score_answer(w, passage), len(w)))
    # Reject if even the best candidate is a clear verb with no better option.
    if looks_like_verb(best) and _score_answer(best, passage) < 1.0:
        return None
    return best


# ---------------------------------------------------------------------------
# Answer-aware prompting + question consistency
# ---------------------------------------------------------------------------

_PROMPT_PREFIXES = (
    "buat pertanyaan:", "buatlah pertanyaan:", "buat soal:", "soal:",
    "pertanyaan:", "tuliskan pertanyaan:",
)


def clean_question(raw: str) -> str | None:
    """Normalise raw model output into a single question string (or None).

    Strips prompt-prefix echoes and stray `<hl>` markers, truncates at the first
    '?', capitalises, and ensures terminal punctuation.
    """
    if not raw:
        return None
    text = " ".join(raw.replace("<hl>", " ").split())
    for _ in range(4):
        low = text.lower()
        for p in _PROMPT_PREFIXES:
            if low.startswith(p):
                text = text[len(p):].strip()
                break
        else:
            break
    if "?" in text:
        text = text.split("?", 1)[0].strip() + "?"
    while text and not text[0].isalnum():
        text = text[1:].strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and text[-1] not in "?.!":
        text += "?"
    return text or None


def is_question_quality_acceptable(question: str) -> bool:
    """Reject empty / collapsed / too-short model output."""
    s = (question or "").strip()
    if len(s) < 15:
        return False
    words = [w for w in s.split() if any(c.isalpha() for c in w)]
    if len(words) < 3:
        return False
    if not any(len("".join(c for c in w if c.isalpha())) >= 5 for w in words):
        return False
    letters = [c for c in s.lower() if c.isalpha()]
    if not letters:
        return False
    if letters.count(max(letters, key=letters.count)) / len(letters) > 0.5:
        return False
    return True


def answer_aware_prompt(passage: str, answer: str) -> str:
    """Highlight the answer span (TyDiQA-id `<hl>` convention) so the model is
    biased to ask a question whose answer is that span."""
    highlighted = re.sub(
        r"\b" + re.escape(answer) + r"\b",
        f"<hl> {answer} <hl>",
        passage,
        count=1,
    )
    return f"buat pertanyaan: {highlighted}"


# Superlative markers — a question like "planet terbesar?" / "paling cepat?"
# can't be fact-checked against an arbitrary chosen entity, so we don't trust
# such generated questions. Specific list (not bare `ter\w+`) to avoid matching
# non-superlatives like terdiri / terdapat / terletak / tersebut.
_SUPERLATIVE_RE = re.compile(
    r"\b(ter(besar|kecil|tinggi|rendah|jauh|dekat|panjang|pendek|cepat|lambat|"
    r"berat|ringan|baik|buruk|banyak|sedikit|luas|sempit|lama|baru|kuat|lemah|"
    r"populer|terkenal|utama)|paling)\b"
)


def question_expects(question: str) -> str | None:
    """What answer category a question implies, if detectable.

    'number'      -> berapa / jumlah
    'proper_noun' -> siapa / di mana / kapan / "(apa) nama ..." (names/places)
    None          -> apa / bagaimana / mengapa / ... (any noun is fine)
    """
    q = question.lower()
    if re.search(r"\bberapa(kah)?\b|\bjumlah\b", q):
        return "number"
    # "apa nama ...", "... bernama ..." asks for a name → expect a proper noun.
    if re.search(r"\bnama\b|\bbernama\b", q):
        return "proper_noun"
    if re.search(r"\bsiapa(kah)?\b|\bdi\s?mana\b|\bdimana\b|\bkapan\b", q):
        return "proper_noun"
    return None


def question_is_consistent(question: str, answer: str) -> bool:
    """Reject answer/question mismatches that produce nonsense quizzes.

    - The answer must NOT appear verbatim in the question (would give it away).
    - Superlative questions about a named entity are rejected — we can't verify
      which entity is "the biggest", so we defer to a coherent cloze instead.
    - If the question implies a category, the answer must match it
      (e.g. "Berapa ..." → number, "apa nama ..." → proper noun).
    """
    if not question or not answer:
        return False
    if re.search(r"\b" + re.escape(answer.lower()) + r"\b", question.lower()):
        return False
    if _SUPERLATIVE_RE.search(question.lower()) and answer_type(answer) != "number":
        return False
    expected = question_expects(question)
    if expected is None:
        return True
    return answer_type(answer) == expected


# ---------------------------------------------------------------------------
# Cloze fallback (guaranteed-coherent when the generated question fails)
# ---------------------------------------------------------------------------

def make_cloze_question(passage: str, answer: str) -> str | None:
    """Blank the answer span in the passage. Coherent by construction because
    the answer literally fits the gap."""
    blanked, n = re.subn(
        r"\b" + re.escape(answer) + r"\b", "____", passage, count=1
    )
    if n == 0:
        return None
    blanked = " ".join(blanked.split())
    if len(blanked) > 200:
        # Keep the clause around the blank readable on small screens.
        idx = blanked.find("____")
        start = max(0, idx - 90)
        end = min(len(blanked), idx + 94)
        blanked = ("…" if start else "") + blanked[start:end].strip() + ("…" if end < len(blanked) else "")
    return f'Lengkapi: "{blanked}"'


# ---------------------------------------------------------------------------
# Distractors (same category as the answer)
# ---------------------------------------------------------------------------

_COMMON_PREFIXES = ("me", "pe", "di", "ter", "ke", "se", "ber")
_COMMON_SUFFIXES = ("nya", "kan", "an", "i", "ku", "mu")


def _match_case(word: str, like: str) -> str:
    if like[:1].isupper() and word[:1].islower():
        return word[0].upper() + word[1:]
    if like[:1].islower() and word[:1].isupper():
        return word[0].lower() + word[1:]
    return word


def _numeric_distractors(answer: str, n: int) -> list[str]:
    """Plausible nearby numbers for a numeric answer."""
    a = answer.strip().lower()
    if _DIGIT_RE.match(a):
        try:
            base = int(re.sub(r"[.,]", "", a))
        except ValueError:
            return []
        cands = [base - 2, base - 1, base + 1, base + 2, base + 3]
        return [str(c) for c in cands if c >= 0 and c != base][:n]
    if a in _NUMBER_WORDS:
        i = _NUMBER_WORDS.index(a)
        order = [i - 1, i + 1, i - 2, i + 2, i + 3]
        out = [_NUMBER_WORDS[j] for j in order if 0 <= j < len(_NUMBER_WORDS) and j != i]
        return [_match_case(w, answer) for w in out][:n]
    return []


def _length_affix_distractors(answer: str, pool: list[str], n: int) -> list[str]:
    target = len(answer)

    def affixes(w: str) -> tuple[str, str]:
        wl = w.lower()
        p = next((p for p in _COMMON_PREFIXES if wl.startswith(p)), "")
        s = next((s for s in _COMMON_SUFFIXES if wl.endswith(s)), "")
        return p, s

    ap, asuf = affixes(answer)

    def score(c: str) -> int:
        sc = abs(len(c) - target) * 2
        cp, cs = affixes(c)
        if ap and cp != ap:
            sc += 3
        if asuf and cs != asuf:
            sc += 3
        return sc

    ranked = sorted(
        (w for w in pool if w.lower() != answer.lower()), key=score
    )
    out: list[str] = []
    for c in ranked:
        if difflib.SequenceMatcher(None, answer.lower(), c.lower()).ratio() >= 0.8:
            continue
        c2 = _match_case(c, answer)
        if c2.lower() not in {o.lower() for o in out}:
            out.append(c2)
        if len(out) == n:
            break
    return out


def build_distractors(
    answer: str,
    passage_keywords: list[str],
    all_keywords: list[str],
    n: int = 3,
) -> list[str]:
    """Same-category distractors. Numbers for a number answer; proper nouns for
    a name; otherwise length/affix-similar content words. Falls back gracefully
    so we still return up to `n` when the ideal category is thin."""
    kind = answer_type(answer)
    out: list[str] = []

    if kind == "number":
        out.extend(_numeric_distractors(answer, n))

    if len(out) < n:
        # Prefer same-category pool, then widen.
        same = [
            w for w in all_keywords
            if w.lower() != answer.lower() and answer_type(w) == kind
        ]
        for cand in _length_affix_distractors(answer, same, n - len(out)):
            if cand.lower() not in {o.lower() for o in out}:
                out.append(cand)

    if len(out) < n:
        for cand in _length_affix_distractors(answer, all_keywords, n):
            if cand.lower() != answer.lower() and cand.lower() not in {o.lower() for o in out}:
                out.append(cand)
            if len(out) == n:
                break

    return out[:n]


def assemble_options(
    answer: str, distractors: list[str], rng: random.Random
) -> tuple[list[str], int]:
    """Shuffle answer + distractors; return (options, correct_index)."""
    options = [answer, *distractors]
    rng.shuffle(options)
    return options, options.index(answer)


# ---------------------------------------------------------------------------
# Orchestration — single source of truth for both HF Space and local inference
# ---------------------------------------------------------------------------

from typing import Callable


def build_quiz(
    text: str,
    generate_fn: Callable[[str], str],
    *,
    num_questions: int,
    rng: random.Random,
) -> list[dict]:
    """Assemble an answer-aware MCQ quiz.

    `generate_fn(prompt)` runs the DL model and returns its raw text. For each
    passage we pick the answer span FIRST, ask the model for a question about
    it, and either keep the generated question (when it is consistent with the
    answer) or fall back to a guaranteed-coherent cloze for the SAME span. This
    is what keeps the correct answer actually answering the question.

    Returns a list of {question, options, correct_option_index} dicts (possibly
    empty — the caller decides whether to error or fall back further).
    """
    all_keywords = extract_keywords(text)
    if len(all_keywords) < 4:
        return []

    passages = split_passages(text, num_questions * 2)
    used: set[str] = set()
    out: list[dict] = []

    for passage in passages:
        if len(out) >= num_questions:
            break
        answer = select_answer_span(passage, exclude=used)
        if not answer:
            continue

        try:
            raw = generate_fn(answer_aware_prompt(passage, answer))
        except Exception:  # noqa: BLE001 — a single bad passage shouldn't abort the quiz
            raw = ""
        generated = clean_question(raw)

        if (
            generated
            and is_question_quality_acceptable(generated)
            and question_expects(generated) is not None
            and question_is_consistent(generated, answer)
        ):
            # Keep ONLY typed factoids the guard can vouch for (Siapa→name,
            # Berapa→number, "apa nama"→name). Open untyped questions
            # ("Apa yang dimaksud…", "Apa fungsi…") don't reliably target the
            # chosen span, so they fall through to a coherent cloze below.
            question_text: str | None = generated
        else:
            # Missing / low quality / open / inconsistent → coherent cloze for
            # the same answer span (the answer literally fits the gap).
            question_text = make_cloze_question(passage, answer)
        if not question_text:
            continue

        distractors = build_distractors(
            answer, extract_keywords(passage), all_keywords, 3
        )
        if len(distractors) < 3:
            continue

        used.add(answer.lower())
        options, idx = assemble_options(answer, distractors, rng)
        out.append({
            "question": question_text,
            "options": options,
            "correct_option_index": idx,
        })

    return out
