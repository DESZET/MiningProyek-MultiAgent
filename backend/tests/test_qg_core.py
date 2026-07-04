"""Tests for the answer-aware question-generation core (ml/generator/qg_core).

These cover the pure logic that fixes the "correct answer is a random word"
bug — answer-span selection, question/answer consistency, distractors, and the
cloze fallback. The DL model itself is not exercised here (runs on HF Space).
"""

import random

from ml.generator import qg_core as qg

PLANET = "Tata Surya memiliki delapan planet yang mengitari Matahari."
ROCKS = "Planet dalam seperti Merkurius dan Venus tersusun dari batuan padat."


# --- answer-span selection ------------------------------------------------

def test_select_answer_prefers_number_over_verb():
    # "delapan" (number) should beat "mengitari" (verb) and "memiliki".
    assert qg.select_answer_span(PLANET) == "delapan"


def test_select_answer_prefers_proper_noun():
    # "Jakarta" (proper noun) should beat "kota" / "terletak" (common / verb).
    span = qg.select_answer_span("Kota itu terletak di Jakarta.")
    assert span == "Jakarta"


def test_select_answer_skips_excluded():
    span = qg.select_answer_span(PLANET, exclude={"delapan"})
    assert span != "delapan"
    assert span is not None


def test_select_answer_none_for_verb_only():
    assert qg.select_answer_span("dan di ke dari untuk pada") is None


# --- token classification -------------------------------------------------

def test_answer_type():
    assert qg.answer_type("delapan") == "number"
    assert qg.answer_type("8") == "number"
    assert qg.answer_type("Matahari", PLANET) == "proper_noun"
    assert qg.answer_type("planet") == "common"


def test_looks_like_verb():
    assert qg.looks_like_verb("didominasi")
    assert qg.looks_like_verb("mengitarinya")
    # Stronger detection: prefix alone (no -kan/-nya suffix needed).
    assert qg.looks_like_verb("mengandung")
    assert qg.looks_like_verb("berlangsung")
    assert qg.looks_like_verb("dilepaskan")
    # Capitalised tokens are proper nouns, never verbs.
    assert not qg.looks_like_verb("Merah")
    assert not qg.looks_like_verb("Republik")
    assert not qg.looks_like_verb("Matahari")
    assert not qg.looks_like_verb("planet")


def test_select_answer_skips_verbs():
    # Must pick a noun (kloroplas / klorofil), never the verb "mengandung".
    span = qg.select_answer_span("Proses ini terjadi di dalam kloroplas yang mengandung klorofil.")
    assert span in {"kloroplas", "klorofil"}
    assert not qg.looks_like_verb(span)


# --- consistency guard ----------------------------------------------------

def test_berapa_requires_number():
    assert qg.question_is_consistent("Berapa jumlah planet dalam Tata Surya?", "delapan")
    # The original bug: "berapa" question with a verb "answer" must be rejected.
    assert not qg.question_is_consistent("Berapa jumlah planet dalam Tata Surya?", "mengitarinya")


def test_answer_in_question_rejected():
    assert not qg.question_is_consistent("Apa fungsi klorofil pada tumbuhan?", "klorofil")


def test_siapa_requires_proper_noun():
    assert qg.question_is_consistent("Siapa presiden pertama Indonesia?", "Soekarno")
    assert not qg.question_is_consistent("Siapa presiden pertama?", "memimpin")


def test_open_question_accepts_common_noun():
    assert qg.question_is_consistent("Apa yang dihasilkan fotosintesis?", "oksigen")


def test_nama_question_requires_proper_noun():
    # "Apa nama planet ..." must map to a name, not a number like "satu".
    assert qg.question_is_consistent("Apa nama planet dalam?", "Merkurius")
    assert not qg.question_is_consistent("Apa nama planet yang memiliki kehidupan?", "satu")


def test_superlative_rejected_for_entity():
    # Can't fact-check "the biggest" against an arbitrary entity → reject.
    assert not qg.question_is_consistent("Apakah planet terbesar di Tata Surya?", "Saturnus")
    assert not qg.question_is_consistent("Kota apa yang paling padat?", "Bandung")
    # A non-superlative "ter..." word must NOT trigger the guard.
    assert qg.question_is_consistent("Apa yang terdapat di planet dalam?", "batuan")


# --- prompting + cloze ----------------------------------------------------

def test_answer_aware_prompt_highlights():
    p = qg.answer_aware_prompt(PLANET, "delapan")
    assert "<hl> delapan <hl>" in p
    assert p.startswith("buat pertanyaan:")


def test_make_cloze_blanks_answer():
    q = qg.make_cloze_question(PLANET, "delapan")
    assert q is not None
    assert "____" in q
    assert "delapan" not in q


def test_make_cloze_none_when_absent():
    assert qg.make_cloze_question(PLANET, "fotosintesis") is None


# --- distractors ----------------------------------------------------------

def test_numeric_answer_gets_numeric_distractors():
    d = qg.build_distractors("delapan", ["delapan"], ["delapan", "planet", "Matahari"])
    assert len(d) == 3
    # All distractors for a number answer should themselves be number words.
    assert all(qg.is_number(x) for x in d)
    assert "delapan" not in [x.lower() for x in d]


def test_digit_answer_distractors():
    d = qg.build_distractors("8", ["8"], ["8", "kata", "lain"])
    assert len(d) == 3
    assert all(qg.is_number(x) for x in d)


def test_distractors_exclude_answer_and_dedup():
    pool = ["Merkurius", "Venus", "Bumi", "Mars", "batuan"]
    d = qg.build_distractors("Merkurius", pool, pool)
    assert "merkurius" not in [x.lower() for x in d]
    assert len(d) == len(set(x.lower() for x in d))


# --- assembly -------------------------------------------------------------

def test_assemble_options_marks_correct():
    rng = random.Random(42)
    options, idx = qg.assemble_options("delapan", ["tujuh", "sembilan", "sepuluh"], rng)
    assert len(options) == 4
    assert options[idx] == "delapan"


# --- end-to-end build_quiz (stubbed model) --------------------------------

MATERIAL = (
    "Tata Surya memiliki delapan planet yang mengitari Matahari. "
    "Planet dalam tersusun dari batuan padat seperti Merkurius dan Venus. "
    "Planet luar didominasi oleh gas raksasa seperti Jupiter dan Saturnus. "
    "Bumi adalah satu-satunya planet yang diketahui memiliki kehidupan."
)


def _every_mcq_is_coherent(quiz):
    for q in quiz:
        opts = q["options"]
        assert len(opts) == 4
        assert len(set(o.lower() for o in opts)) == 4  # no duplicate options
        correct = opts[q["correct_option_index"]]
        # The correct answer must never appear inside the question text.
        assert correct.lower() not in q["question"].lower()


def test_build_quiz_uses_consistent_generated_question():
    # Stub model returns a good, consistent question regardless of prompt.
    def gen(_prompt):
        return "Berapa jumlah planet dalam Tata Surya?"

    quiz = qg.build_quiz(MATERIAL, gen, num_questions=3, rng=random.Random(1))
    assert len(quiz) >= 1
    _every_mcq_is_coherent(quiz)
    # At least one question should be the generated one with the numeric answer.
    numeric = [q for q in quiz if q["options"][q["correct_option_index"]].lower()
               in {"delapan", "8"} or qg.is_number(q["options"][q["correct_option_index"]])]
    assert any("Berapa" in q["question"] for q in quiz) or numeric


def test_build_quiz_routes_open_questions_to_cloze():
    # Open, untyped "Apa ..." questions don't reliably target the answer span,
    # so they must be routed to a coherent cloze even when "well-formed".
    def gen(_prompt):
        return "Apa fungsi utama dari bagian ini?"

    quiz = qg.build_quiz(MATERIAL, gen, num_questions=3, rng=random.Random(1))
    assert len(quiz) >= 2
    _every_mcq_is_coherent(quiz)
    assert all(q["question"].startswith('Lengkapi: "') for q in quiz)


def test_build_quiz_falls_back_to_cloze_on_garbage_model():
    # Model always returns junk → every question must be a coherent cloze.
    def gen(_prompt):
        return "xxx"

    quiz = qg.build_quiz(MATERIAL, gen, num_questions=3, rng=random.Random(1))
    assert len(quiz) >= 2
    _every_mcq_is_coherent(quiz)
    assert all('Lengkapi: "' in q["question"] for q in quiz)


def test_build_quiz_rejects_inconsistent_generated_question():
    # Model returns a "berapa" question for every passage. Only passages whose
    # chosen answer is numeric may keep it; the rest fall back to cloze. Either
    # way, no nonsense (number question with a word answer) survives.
    def gen(_prompt):
        return "Berapa jumlah hal yang disebutkan?"

    quiz = qg.build_quiz(MATERIAL, gen, num_questions=4, rng=random.Random(7))
    _every_mcq_is_coherent(quiz)
    for q in quiz:
        if "Berapa" in q["question"]:
            assert qg.is_number(q["options"][q["correct_option_index"]])
