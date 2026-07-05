"""Quiz generator — turns learning material text into a quiz.

OWNER: Audry (Backend — Quiz Generator)

This is a THIN WRAPPER around `ml/generator/inference.py` (the DL model).
The wrapper:
    1. Validates input (length checks)
    2. Tries DL inference via ml.generator
    3. Falls back to rule-based generation if DL is unavailable
    4. Wraps result in QuizInternal with a fresh quiz_id

Multi-Agent upgrade (AI_AGENT_IDEAS.md §Agent Quiz Maker — Fase 2):
    - Setelah soal dari DL/rule-based terkumpul, agent_quiz_maker.polish_questions()
      dipanggil untuk memperbaiki grammar dan distractor via LLM.
    - Fallback graceful: kalau LLM tidak tersedia, soal dikembalikan apa adanya.

The actual model loading + question generation logic lives in
`backend/ml/generator/inference.py`. See ML.md §3 for details.

If you want to swap the DL approach for something else, edit
`ml/generator/inference.py`. This wrapper file should rarely change.
"""

from __future__ import annotations

import logging
import random
import re
import uuid
import difflib
from datetime import datetime, timezone

from app.schemas.internal import QuestionInternal, QuizInternal
from app.services.material_quality import assess as _assess_material
from app.utils.errors import (
    ApiException,
    MATERIAL_LOW_QUALITY,
    MATERIAL_TOO_SHORT,
    QUIZ_GENERATION_FAILED,
)
from ml.generator import inference as ml_generator

logger = logging.getLogger(__name__)

DEFAULT_QUESTION_COUNT = 5
MIN_QUESTION_COUNT = 3        # for DL path — we expect quality
FALLBACK_MIN_COUNT = 2        # rule-based fallback — accept fewer if needed
MIN_MATERIAL_LENGTH = 100


# Indonesian question starters.
_QUESTION_STARTERS = (
    "Apa", "Apakah", "Bagaimana", "Mengapa", "Kenapa", "Siapa", "Kapan",
    "Di mana", "Dimana", "Berapa", "Manakah", "Mana yang", "Sebutkan",
    "Jelaskan", "Tulislah", "Tuliskan", "Tentukan", "Hitunglah",
)

def _normalize_for_dedup(text: str) -> str:
    # Remove punctuation and normalize whitespace
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Remove common question starters to focus on the core topic
    for starter in _QUESTION_STARTERS:
        if text.startswith(starter.lower()):
            text = text[len(starter):].strip()
    return " ".join(text.split())

def _is_duplicate(new_q_text: str, existing_questions: list[QuestionInternal], threshold: float = 0.8) -> bool:
    norm_new = _normalize_for_dedup(new_q_text)
    for q in existing_questions:
        norm_existing = _normalize_for_dedup(q.question)
        # Sequence matching on core text
        similarity = difflib.SequenceMatcher(None, norm_new, norm_existing).ratio()
        
        # Word overlap check (Jaccard similarity)
        words_new = set(norm_new.split())
        words_exist = set(norm_existing.split())
        jaccard = len(words_new & words_exist) / len(words_new | words_exist) if words_new and words_exist else 0.0
            
        if similarity > threshold or jaccard > 0.65:
            return True
    return False


def _extract_quiz_topic(text: str) -> str:
    """Extract a lightweight topic tag from source material."""
    cleaned = text.strip().replace("\n", " ")
    if not cleaned:
        return "Umum"

    sentence = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0].strip()
    if not sentence:
        sentence = cleaned

    if len(sentence) > 80:
        sentence = sentence[:80].rsplit(" ", 1)[0]
    return sentence or "Umum"


def _order_mc_options(
    options: list[str] | None,
    correct_index: int,
    shuffle_options: bool,
) -> tuple[list[str] | None, int]:
    """§4.3: when shuffle is off, present MC options in a stable alphabetical
    order (not the generator's randomised order), re-pointing the correct index.

    Alphabetical (rather than generation order) is used because generation order
    puts the correct answer first — a predictable "always A" leak. Returns the
    options unchanged when shuffling is on or there is nothing to reorder."""
    if shuffle_options or not options:
        return options, correct_index
    correct_value = options[correct_index]
    ordered = sorted(options)
    return ordered, ordered.index(correct_value)


def _wrap_quiz(
    questions: list[QuestionInternal],
    text: str,
    difficulty: str = "medium",
    quiz_id: str | None = None,
    topic: str | None = None,
    shuffle_options: bool = True,
    apply_polish: bool = True,
) -> QuizInternal:
    """Build a QuizInternal from a list of questions, renumbering IDs.

    Only `multiple_choice` options are reordered when shuffle is off —
    `true_false` keeps its semantic [Benar, Salah] order and `short_answer`
    has no options.

    apply_polish: kalau True, jalankan agent_quiz_maker.polish_questions() sebagai
    post-processing step (LLM grammar/distractor fix). Fallback graceful.
    """
    renumbered = []
    for i, q in enumerate(questions):
        options, correct_index = q.options, q.correct_option_index
        if q.type == "multiple_choice":
            options, correct_index = _order_mc_options(
                q.options, q.correct_option_index, shuffle_options
            )
        renumbered.append(
            QuestionInternal(
                id=i + 1,
                type=q.type,
                question=q.question,
                options=options,
                correct_option_index=correct_index,
                correct_answer_text=q.correct_answer_text,
                left_items=q.left_items,
                right_items=q.right_items,
                correct_matches=q.correct_matches,
            )
        )

    # Agent Quiz Maker — LLM polish step (Fase 2)
    if apply_polish and renumbered:
        try:
            from app.services import agent_quiz_maker
            renumbered = agent_quiz_maker.polish_questions(renumbered, text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("_wrap_quiz: agent_quiz_maker skipped: %s", exc)

    return QuizInternal(
        quiz_id=quiz_id or str(uuid.uuid4()),
        questions=renumbered,
        generated_at=datetime.now(timezone.utc),
        source_material=text[:20_000],
        difficulty=difficulty,
        topic=topic or _extract_quiz_topic(text),
    )


MAX_QUESTION_COUNT = 10       # §4.3 — hard ceiling on user-requested count


def generate_quiz(
    material_text: str,
    difficulty: str | None = None,
    quiz_id: str | None = None,
    topic: str | None = None,
    num_questions: int | None = None,
    shuffle_options: bool = True,
) -> QuizInternal:
    """Generate a multiple-choice quiz from raw material text.

    `difficulty` controls question hardness (keyword/sentence selection).
    `num_questions` (§4.3) is an INDEPENDENT target count (3/5/7/10); when given
    it overrides the difficulty-derived count. `shuffle_options` (§4.3) keeps the
    generator's randomised option order when True, or sorts MC options into a
    stable alphabetical order when False.

    Strategy:
        1. Try DL (HF Space → local). Collect questions that pass cleanup.
        2. If DL yields >= target_count, ship DL only.
        3. If DL yields 1..N-1, supplement with rule-based questions to top up.
        4. If DL yields 0 (or fails), use rule-based alone.
        5. If everything fails, raise a friendly 400.
    """
    diff = difficulty or "medium"
    if diff == "easy":
        target_count = 3
        fallback_floor = 2
    elif diff == "hard":
        target_count = 7
        fallback_floor = 4
    else:
        target_count = 5
        fallback_floor = 3

    # §4.3: an explicit num_questions overrides the difficulty-derived count.
    if num_questions is not None:
        target_count = max(MIN_QUESTION_COUNT, min(MAX_QUESTION_COUNT, num_questions))
        fallback_floor = max(2, min(fallback_floor, target_count))

    text = material_text.strip()
    if len(text) < MIN_MATERIAL_LENGTH:
        raise ApiException(
            status_code=400,
            code=MATERIAL_TOO_SHORT,
            detail="Materinya terlalu pendek. Tambahkan minimal 100 karakter agar sistem bisa membuat kuis.",
        )

    # Quizability pre-check (ROADMAP §3.2): bail early on clearly unsuitable
    # material (CV / English / bare lists) with a helpful hint, before spending
    # ~15s producing a nonsensical quiz.
    suitable, hint = _assess_material(text)
    if not suitable:
        raise ApiException(status_code=400, code=MATERIAL_LOW_QUALITY, detail=hint)

    # === Path 1: DL via ml/generator (preferred) ===
    dl_questions: list[QuestionInternal] = []
    if ml_generator.is_available():
        try:
            raw_questions = ml_generator.generate(text, num_questions=target_count)
            for q in raw_questions:
                cleaned = _clean_question_text(q["question"])
                if cleaned is None:
                    continue
                if _is_duplicate(cleaned, dl_questions):
                    logger.info("quiz_generator: skipping duplicate question from DL")
                    continue
                dl_questions.append(
                    QuestionInternal(
                        id=len(dl_questions) + 1,
                        question=cleaned,
                        options=q["options"],
                        correct_option_index=q["correct_option_index"],
                    )
                )

            if len(dl_questions) >= target_count:
                logger.info(
                    "quiz_generator: DL path produced %d questions",
                    len(dl_questions),
                )
                final = list(dl_questions[:target_count])
                # §6.2: DL produces only MC/cloze — inject one matching question
                # into larger quizzes so the type is actually reachable in prod.
                if target_count >= 5:
                    mrng = random.Random(abs(hash(text)) & 0xFFFFFFFF)
                    matching_q = _build_matching_from_text(text, len(final), mrng)
                    if matching_q is not None:
                        final[-1] = matching_q
                return _wrap_quiz(
                    final, text, diff, quiz_id,
                    shuffle_options=shuffle_options,
                )

            if dl_questions:
                logger.info(
                    "quiz_generator: DL produced %d, supplementing with rule-based",
                    len(dl_questions),
                )
                try:
                    rule_quiz = _generate_rule_based(text, diff, target=target_count)
                    combined: list[QuestionInternal] = list(dl_questions)
                    for rq in rule_quiz.questions:
                        if len(combined) >= target_count:
                            break
                        if _is_duplicate(rq.question, combined):
                            continue
                        combined.append(
                            QuestionInternal(
                                id=len(combined) + 1,
                                type=rq.type,
                                question=rq.question,
                                options=rq.options,
                                correct_option_index=rq.correct_option_index,
                                correct_answer_text=rq.correct_answer_text,
                                # §6.2: carry matching pairing data through the
                                # DL+rule supplement path (else matching renders
                                # empty/unanswerable).
                                left_items=rq.left_items,
                                right_items=rq.right_items,
                                correct_matches=rq.correct_matches,
                            )
                        )
                    if len(combined) >= fallback_floor:
                        logger.info(
                            "quiz_generator: mixed DL+rule produced %d questions",
                            len(combined),
                        )
                        return _wrap_quiz(
                            combined, text, diff, quiz_id,
                            shuffle_options=shuffle_options,
                        )
                except ApiException as exc:
                    logger.info(
                        "quiz_generator: rule-based supplement failed (%s), "
                        "checking if DL alone is enough",
                        exc.code,
                    )

                # Rule-based couldn't help; ship DL alone if it meets the floor.
                if len(dl_questions) >= fallback_floor:
                    logger.warning(
                        "quiz_generator: shipping %d DL questions (below target=%d)",
                        len(dl_questions),
                        target_count,
                    )
                    return _wrap_quiz(
                        dl_questions, text, diff, quiz_id,
                        shuffle_options=shuffle_options,
                    )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "quiz_generator: DL path failed (%s), falling back to rule-based",
                exc,
            )

    # === Path 2: rule-based fallback (DL unavailable, empty, or below floor) ===
    return _generate_rule_based(
        text, diff, quiz_id, target=target_count, shuffle_options=shuffle_options
    )


# ============================================================================
# Quality cleanup (defense-in-depth — runs on top of ml/generator output)
# ============================================================================

import re

# Patterns to strip from the start (and embedded) of generated questions.
# Non-fine-tuned T5 sometimes echoes instruction prefixes back into output.
_PROMPT_PREFIX_PATTERNS = (
    "buat pertanyaan:",
    "buatlah pertanyaan:",
    "pertanyaan seperti ini:",
    "pertanyaan:",
)

# Indonesian question starters (moved to top for dedup logic)

_MIN_CLEANED_LENGTH = 15  # after cleanup, need at least this much text

# Compile a regex to find any question starter as a word boundary
_QUESTION_STARTER_RE = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in _QUESTION_STARTERS) + r")\b",
    re.IGNORECASE,
)


def _clean_question_text(raw: str) -> str | None:
    """Defense-in-depth cleanup on each generated question.

    Strips prompt-prefix leakage, leading garbage, and rejects outputs that
    don't look like proper questions. Returns None if not salvageable.
    """
    if not raw:
        return None

    text = raw.strip()

    # Iteratively strip prompt-prefix patterns from the start.
    # Loop because models sometimes repeat: "Buat pertanyaan: Buat pertanyaan: ..."
    for _ in range(4):
        stripped = False
        for pattern in _PROMPT_PREFIX_PATTERNS:
            if text.lower().startswith(pattern):
                text = text[len(pattern):].strip()
                stripped = True
                break
        if not stripped:
            break

    # Aggressive scan: find the FIRST Indonesian question starter and trim
    # everything before it. Handles cases like "Inflasi  Buat pertanyaan: Apa..."
    # where the prefix isn't at position 0.
    match = _QUESTION_STARTER_RE.search(text)
    if match:
        text = text[match.start():].strip()
    else:
        # No proper question starter found → not a valid question
        return None

    # Truncate at first '?' if present (drops trailing artifacts)
    if "?" in text:
        text = text.split("?", 1)[0].strip() + "?"

    # Drop leading non-letter chars (defensive — should be moot after starter match)
    while text and not text[0].isalnum():
        text = text[1:].strip()

    # Capitalize first letter for readability
    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    # Ensure ends with '?' (model sometimes truncates mid-sentence)
    if text and text[-1] not in "?.!":
        text += "?"

    # Reject if too short
    if len(text) < _MIN_CLEANED_LENGTH:
        return None

    # Reject single-character-dominated output (model collapse)
    letters = [c for c in text.lower() if c.isalpha()]
    if not letters:
        return None
    if letters.count(max(letters, key=letters.count)) / len(letters) > 0.5:
        return None

    # Reject if no meaningful content (need at least 1 word with 5+ chars)
    if not any(
        len("".join(c for c in w if c.isalpha())) >= 5 for w in text.split()
    ):
        return None

    return text


# ============================================================================
# Rule-based fallback (used when DL unavailable or fails)
# ============================================================================

_STOP_WORDS: frozenset[str] = frozenset(
    {
        "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "ini",
        "itu", "atau", "adalah", "akan", "tidak", "juga", "dapat", "sebagai",
        "telah", "oleh", "dalam", "saat", "yaitu", "namun", "agar", "karena",
        "lebih", "secara", "menjadi", "sangat", "harus", "bahwa", "hanya",
        "kita", "mereka", "kami", "kamu", "saya", "anda", "tetapi", "sehingga",
        "sudah", "belum", "masih", "bisa", "tersebut", "ialah", "ada", "tiap",
        # Common functional/filler words that aren't great quiz answers.
        "beberapa", "kemudian", "berbagai", "seperti", "biasanya", "umumnya",
        "selalu", "sering", "kadang", "bahkan", "sekitar", "sebagian",
        "banyak", "sedikit", "semua", "setiap", "selain", "termasuk", "antara",
        "sebelum", "setelah", "sesudah", "ketika", "sementara", "selama",
        "begitu", "demikian", "meskipun", "walaupun", "sambil",
        "sebenarnya", "ternyata", "kemudian", "lalu", "akhirnya", "akhir",
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "and", "or", "but", "of", "in", "on", "at", "to", "for", "with",
        "this", "that", "these", "those", "it", "its", "they", "them",
        "from", "as", "by", "has", "have", "had",
    }
)

# Attribution / parenthetical patterns that signal a sentence is not educational.
_NON_EDUCATIONAL_PATTERNS = (
    "dalam bahasa ", "menurut ", "dilansir ", "dikutip ", "dilaporkan ",
    "ditulis oleh", "ditulis pada", "diunggah ", "diposting ",
    " ujar ", " kata ", " tutur ", " ucap ", " sebut ",
    "baca juga", "lihat juga", "sumber:",
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{4,}")

# Pattern matching brand/proper-noun-like tokens that aren't good fill-in targets,
# e.g. "detikcom", "iPhone", "BBC", "WhatsApp". A 4+ letter token that mixes
# upper and lower case in the middle (not just title case) tends to be a brand.
_BRAND_LIKE_RE = re.compile(r"^[a-z]+[A-Z][a-zA-Z]*$|^[A-Z]{2,}[a-z]+$")


def _sanitize_sentence(s: str) -> str:
    """Strip outer quotes and collapse internal whitespace/newlines.

    Multi-line "sentences" (e.g. table cells joined by a single \\n) get
    collapsed to a single line so quality filtering can judge them properly
    and so the cloze prompt doesn't render with embedded newlines.
    """
    s = " ".join(s.split())  # collapse all whitespace including newlines/tabs
    # Repeatedly strip leading/trailing quote-like chars.
    quote_chars = '"\'“”‘’«»'
    while s and (s[0] in quote_chars or s[-1] in quote_chars):
        if s[0] in quote_chars:
            s = s[1:].strip()
        if s and s[-1] in quote_chars:
            s = s[:-1].strip()
    return s


# Chars that signal non-prose content (tables, citations, list markers).
_STRUCTURAL_NOISE_CHARS = '|↑↓→←↳·•►▪'


def _is_quality_sentence(s: str) -> bool:
    """Return True if a sentence is suitable for cloze question generation.

    Strict tier: also enforces length/word-count/attribution checks. Used
    as the first pass; if no sentence passes, we fall back to the relaxed
    `_is_safe_sentence` filter.
    """
    if not _is_safe_sentence(s):
        return False
    if len(s) < 50 or len(s) > 280:
        return False
    # Need at least 7 word-like tokens.
    words = [w for w in s.split() if any(c.isalpha() for c in w)]
    if len(words) < 7:
        return False
    # Must have at least one content word with 6+ letters.
    if not any(len("".join(c for c in w if c.isalpha())) >= 6 for w in words):
        return False
    # Reject attribution / parenthetical patterns at the strict tier.
    if any(pat in s.lower() for pat in _NON_EDUCATIONAL_PATTERNS):
        return False
    return True


def _is_safe_sentence(s: str) -> bool:
    """Relaxed filter: rejects only obviously non-prose junk.

    Used as the safety net so we never emit table cells, citations,
    or punctuation-dominated fragments as quiz questions, even when
    the strict filter would leave us with zero candidates.
    """
    if not s or len(s) < 40 or len(s) > 280:
        return False
    # Any structural-noise char (e.g. table pipe, citation arrow) → reject.
    if any(c in s for c in _STRUCTURAL_NOISE_CHARS):
        return False
    # High alpha ratio. Punctuation-heavy junk fails this.
    alpha = sum(1 for c in s if c.isalpha())
    if alpha / len(s) < 0.65:
        return False
    # Reject quote- or exclamation-dominated content.
    if s.count('"') >= 2 or s.count("'") >= 2 or "!" in s or "..." in s:
        return False
    # Need at least 6 word-like tokens — short citations / archive notes fail.
    words = [w for w in s.split() if any(c.isalpha() for c in w)]
    if len(words) < 6:
        return False
    # Reject parenthetical-only content (e.g. "detikcom (dalam bahasa X)").
    paren_chars = s.count("(") + s.count(")")
    if paren_chars >= 2 and len(words) < 8:
        return False
    # Attribution patterns disqualify even at the safe tier.
    if any(pat in s.lower() for pat in _NON_EDUCATIONAL_PATTERNS):
        return False
    return True


def _split_sentences(text: str) -> list[str]:
    """Split text into sensible-length sentences (bulletproof — always returns >= 1 if text is non-trivial).

    Fallback chain:
        1. Sentence terminators (. ! ?)
        2. Line breaks (handles list-style content)
        3. Punctuation breaks (commas, semicolons, dashes)
        4. Sliding window (90-char chunks — last resort for unstructured text)
    """
    # Path 1: proper sentences
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    sensible = [s for s in sentences if 30 <= len(s) <= 280]
    if len(sensible) >= FALLBACK_MIN_COUNT:
        return sensible

    # Path 2: line-based
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    line_sensible = [l for l in lines if 30 <= len(l) <= 280]
    if len(line_sensible) >= FALLBACK_MIN_COUNT:
        return line_sensible

    # Path 3: punctuation-based (split on commas, semicolons, dashes)
    chunks = re.split(r"[,;—–-]\s+", text)
    chunks = [c.strip() for c in chunks if c.strip()]
    chunk_sensible = [c for c in chunks if 30 <= len(c) <= 280]
    if len(chunk_sensible) >= FALLBACK_MIN_COUNT:
        return chunk_sensible

    # Path 4: sliding window — guarantees >= 2 chunks for any text >= 90 chars
    window_size = 90
    overlap = 30
    windowed: list[str] = []
    text_clean = " ".join(text.split())  # collapse whitespace
    pos = 0
    while pos < len(text_clean):
        chunk = text_clean[pos : pos + window_size]
        if len(chunk) >= 30:
            windowed.append(chunk)
        pos += window_size - overlap
    if len(windowed) >= 1:
        return windowed

    # Absolute fallback: return whole text as single chunk
    cleaned = text.strip()
    return [cleaned] if cleaned else []


def _extract_keywords(text: str) -> list[str]:
    seen: set[str] = set()
    words: list[str] = []
    for m in _WORD_RE.finditer(text):
        w = m.group(0)
        wl = w.lower()
        if wl in _STOP_WORDS or wl in seen:
            continue
        # Skip brand-like tokens (e.g. detikcom, iPhone) — never a good answer.
        if _BRAND_LIKE_RE.match(w):
            continue
        seen.add(wl)
        words.append(w)
    return sorted(words, key=len, reverse=True)


def _pick_keyword_from_by_difficulty(
    sentence: str,
    used_lower: set[str],
    difficulty: str,
) -> str | None:
    for w in _extract_keywords(sentence):
        wl = w.lower()
        if wl not in used_lower:
            if difficulty == "easy" and 4 <= len(w) <= 8:
                used_lower.add(wl)
                return w
            elif difficulty == "hard" and len(w) >= 6:
                used_lower.add(wl)
                return w
            elif difficulty == "medium" and len(w) >= 4:
                used_lower.add(wl)
                return w
    # Fallback if no matching keyword met the specific criteria
    for w in _extract_keywords(sentence):
        wl = w.lower()
        if wl not in used_lower:
            used_lower.add(wl)
            return w
    return None


def _build_rule_question(
    qid: int,
    sentence: str,
    correct: str,
    pool: list[str],
    rng: random.Random,
) -> QuestionInternal | None:
    pattern = re.compile(r"\b" + re.escape(correct) + r"\b")
    blanked = pattern.sub("____", sentence, count=1)
    if blanked == sentence:
        return None

    from app.services._distractors import _pick_similar_length_distractors

    # Roll a die to determine question type (60% MC, 20% TF, 20% SA)
    q_type_roll = rng.random()
    if q_type_roll < 0.2:
        # True/False
        is_true = rng.choice([True, False])
        if is_true:
            question_text = f'Pernyataan berikut ini Benar atau Salah?\n"{sentence}"'
            return QuestionInternal(
                id=qid,
                type="true_false",
                question=question_text,
                options=["Benar", "Salah"],
                correct_option_index=0,
            )
        else:
            distractors = _pick_similar_length_distractors(correct, pool, 1)
            if not distractors:
                return None
            false_sentence = pattern.sub(distractors[0], sentence, count=1)
            question_text = f'Pernyataan berikut ini Benar atau Salah?\n"{false_sentence}"'
            return QuestionInternal(
                id=qid,
                type="true_false",
                question=question_text,
                options=["Benar", "Salah"],
                correct_option_index=1,
            )
            
    elif q_type_roll < 0.4:
        # Short Answer
        return QuestionInternal(
            id=qid,
            type="short_answer",
            question=f'Isi bagian yang rumpang dengan kata yang tepat:\n"{blanked}"',
            correct_answer_text=correct,
        )

    # Multiple Choice
    distractors = _pick_similar_length_distractors(correct, pool, 3)
    if len(distractors) < 3:
        return None

    options: list[str] = [correct, *distractors]
    rng.shuffle(options)
    correct_idx = options.index(correct)

    return QuestionInternal(
        id=qid,
        type="multiple_choice",
        question=f'Lengkapi kalimat berikut: "{blanked}"',
        options=options,
        correct_option_index=correct_idx,
    )


_MATCHING_MIN_PAIRS = 3
_MATCHING_MAX_PAIRS = 4
_MATCHING_RIGHT_MAXLEN = 120


def _shorten_clause(s: str, maxlen: int) -> str:
    s = " ".join(s.split())
    if len(s) <= maxlen:
        return s
    return s[:maxlen].rsplit(" ", 1)[0].strip() + "…"


def _build_matching_question(
    qid: int,
    candidate_sentences: list[str],
    used_correct_lower: set[str],
    rng: random.Random,
) -> QuestionInternal | None:
    """§6.2: build ONE matching question from several sentences.

    Each pair is (keyword, the keyword's sentence with the keyword blanked). The
    user matches the term to the statement it completes. The keyword is blanked
    out of the right-hand text so the answer isn't given away. Returns None if
    fewer than _MATCHING_MIN_PAIRS distinct usable pairs can be formed.
    """
    pairs: list[tuple[str, str]] = []
    seen_keywords: set[str] = set()
    for sentence in candidate_sentences:
        if len(pairs) >= _MATCHING_MAX_PAIRS:
            break
        keyword = _pick_keyword_from_by_difficulty(
            sentence, used_correct_lower, "medium"
        )
        if not keyword or keyword.lower() in seen_keywords:
            continue
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b")
        blanked = pattern.sub("___", sentence, count=1)
        if blanked == sentence:
            continue
        seen_keywords.add(keyword.lower())
        pairs.append((keyword, _shorten_clause(blanked, _MATCHING_RIGHT_MAXLEN)))

    if len(pairs) < _MATCHING_MIN_PAIRS:
        return None

    left_items = [kw for kw, _ in pairs]
    right_texts = [text for _, text in pairs]

    # Shuffle the answer bank; record where each correct right text landed.
    order = list(range(len(right_texts)))
    rng.shuffle(order)
    shuffled_right = [right_texts[j] for j in order]
    landed_at = {orig: idx for idx, orig in enumerate(order)}
    correct_matches = [landed_at[i] for i in range(len(right_texts))]

    return QuestionInternal(
        id=qid,
        type="matching",
        question="Pasangkan setiap istilah dengan pernyataan yang tepat.",
        left_items=left_items,
        right_items=shuffled_right,
        correct_matches=correct_matches,
    )


def _build_matching_from_text(
    text: str, qid: int, rng: random.Random
) -> QuestionInternal | None:
    """Build a matching question straight from raw text (used to inject one into
    a DL-only quiz, which otherwise never produces matching)."""
    sentences = [_sanitize_sentence(s) for s in _split_sentences(text)]
    candidates = [s for s in sentences if _is_quality_sentence(s)] or [
        s for s in sentences if _is_safe_sentence(s)
    ]
    if len(candidates) < _MATCHING_MIN_PAIRS + 1:
        return None
    return _build_matching_question(qid, candidates, set(), rng)


def _generate_rule_based(
    text: str,
    difficulty: str = "medium",
    quiz_id: str | None = None,
    target: int | None = None,
    shuffle_options: bool = True,
) -> QuizInternal:
    """Rule-based fill-in-the-blank quiz generator. Used as fallback.

    Bulletproof: any text >= MIN_MATERIAL_LENGTH (100 chars) should produce
    at least 2 questions. Returns 400 only when input genuinely can't be
    used (e.g., < 4 distinct keywords).
    """
    try:
        sentences = _split_sentences(text)

        # If even sliding-window can't produce 2 chunks, content is too thin
        if len(sentences) < 1:
            raise ApiException(
                status_code=400,
                code=QUIZ_GENERATION_FAILED,
                detail=(
                    "Materi tidak cocok untuk membuat kuis. "
                    "Sistem butuh teks dengan minimal 100 karakter berisi konten substantif."
                ),
            )

        all_keywords = _extract_keywords(text)
        if len(all_keywords) < 4:
            raise ApiException(
                status_code=400,
                code=QUIZ_GENERATION_FAILED,
                detail=(
                    "Materi terlalu seragam untuk membuat kuis pilihan ganda. "
                    "Sistem butuh minimal 4 kata bermakna yang berbeda. "
                    "Coba materi dengan kosakata lebih beragam."
                ),
            )

        # Two-tier quality filter:
        #   1. Strict: prefer proper prose sentences for the best questions.
        #   2. Safe (relaxed): if strict yields none, accept anything that
        #      isn't table-cell / citation / punctuation-only junk.
        sentences = [_sanitize_sentence(s) for s in sentences]
        quality_sentences = [s for s in sentences if _is_quality_sentence(s)]
        if quality_sentences:
            candidate_sentences = quality_sentences
        else:
            candidate_sentences = [s for s in sentences if _is_safe_sentence(s)]

        # §4.3: explicit target wins; otherwise derive from difficulty.
        if target is None:
            if difficulty == "easy":
                target = 3
            elif difficulty == "hard":
                target = 7
            else:
                target = 5

        # Apply sentence length filter based on difficulty
        filtered_sentences = []
        if difficulty == "easy":
            filtered_sentences = [s for s in candidate_sentences if 40 <= len(s) <= 120]
        elif difficulty == "hard":
            filtered_sentences = [s for s in candidate_sentences if 80 <= len(s) <= 280]
        else:  # medium
            filtered_sentences = [s for s in candidate_sentences if 50 <= len(s) <= 200]

        # Graceful fallback if difficulty filtering yields too few sentences than target
        if len(filtered_sentences) < target:
            filtered_sentences = candidate_sentences

        rng = random.Random(abs(hash(text)) & 0xFFFFFFFF)
        used_correct_lower: set[str] = set()
        questions: list[QuestionInternal] = []

        # §6.2: include ONE matching question for larger quizzes (target >= 5),
        # consuming a few sentences/keywords before the per-sentence loop fills
        # the rest. Skipped for short quizzes so matching never dominates.
        if target >= 5 and len(filtered_sentences) >= _MATCHING_MIN_PAIRS + 1:
            matching_q = _build_matching_question(
                len(questions) + 1, filtered_sentences, used_correct_lower, rng
            )
            if matching_q is not None:
                questions.append(matching_q)

        # Try sentences first — generates richest questions
        for sentence in filtered_sentences[: target * 3]:
            if len(questions) >= target:
                break
            correct = _pick_keyword_from_by_difficulty(sentence, used_correct_lower, difficulty)
            if not correct:
                continue
            q = _build_rule_question(
                len(questions) + 1, sentence, correct, all_keywords, rng
            )
            if q is not None:
                if _is_duplicate(q.question, questions):
                    continue
                questions.append(q)

        # Last-resort: if still no questions, generate from whole-text passages
        # using different keywords as the blank
        if len(questions) < 2 and len(all_keywords) >= 4:
            whole_text = " ".join(text.split())[:280]  # collapse whitespace + truncate
            for keyword in all_keywords[:target]:
                if len(questions) >= 2:
                    break
                if keyword.lower() in used_correct_lower:
                    continue
                used_correct_lower.add(keyword.lower())
                q = _build_rule_question(
                    len(questions) + 1, whole_text, keyword, all_keywords, rng
                )
                if q is not None:
                    if _is_duplicate(q.question, questions):
                        continue
                    questions.append(q)

        if not questions:
            raise ApiException(
                status_code=400,
                code=QUIZ_GENERATION_FAILED,
                detail=(
                    "Tidak bisa membuat pertanyaan dari materi ini. "
                    "Coba materi yang lebih panjang dengan konten penjelasan, "
                    "bukan sekadar daftar atau angka."
                ),
            )

        logger.info("quiz_generator: rule-based path produced %d questions", len(questions))
        return _wrap_quiz(
            questions, text, difficulty, quiz_id, shuffle_options=shuffle_options
        )
    except ApiException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ApiException(
            status_code=500,
            code=QUIZ_GENERATION_FAILED,
            detail="Gagal membuat kuis. Coba materi lain atau ulangi sebentar lagi.",
        ) from exc
