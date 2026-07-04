"""Prepare TyDiQA-id data for IndoT5 question-generation fine-tuning.

OWNER: Audry (Quiz Generator)

Downloads TyDiQA (Gold Passage / secondary_task), filters the Indonesian subset,
and converts each (context, question, answer) example into training pairs for a
sequence-to-sequence question generator.

Two ready-to-use input templates are emitted per example (pick one in the notebook):

  - input_plain : "buat pertanyaan: {answer_sentence}"
      Answer-agnostic-ish; matches the current inference prompt style. Uses only the
      sentence that contains the answer to reduce ambiguity.

  - input_hl    : "buat pertanyaan: {context with the answer wrapped in <hl> ... <hl>}"
      Answer-aware (highlight) QG, the strongest QG setup. If you use this, the
      inference side must wrap the chosen answer keyword in <hl> ... <hl> too.

target : the human-written question.

Output: JSONL files in this directory:
  tydiqa_id_train.jsonl, tydiqa_id_val.jsonl
Each line: {input_plain, input_hl, target, context, question, answer}

Run (needs `pip install datasets`, see ml/requirements-ml.txt):
    python -m ml.generator.data.prepare_tydiqa
"""

from __future__ import annotations

import json
import re
from pathlib import Path

OUT_DIR = Path(__file__).parent
PREFIX = "buat pertanyaan: "
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _answer_sentence(context: str, answer: str, answer_start: int) -> str:
    """Return the sentence in `context` that contains the answer span."""
    if answer_start is None or answer_start < 0:
        # Fall back to substring search.
        idx = context.find(answer)
        answer_start = idx if idx >= 0 else 0
    end = answer_start + len(answer)
    # Find sentence boundaries around [answer_start, end].
    start_bound = 0
    for m in _SENT_SPLIT.finditer(context):
        if m.end() <= answer_start:
            start_bound = m.end()
        else:
            break
    end_bound = len(context)
    for m in _SENT_SPLIT.finditer(context):
        if m.start() >= end:
            end_bound = m.start()
            break
    return context[start_bound:end_bound].strip()


def _highlight(context: str, answer: str, answer_start: int) -> str:
    """Wrap the answer span in <hl> ... <hl> within the context."""
    if answer_start is None or answer_start < 0 or context[answer_start : answer_start + len(answer)] != answer:
        idx = context.find(answer)
        if idx < 0:
            return context
        answer_start = idx
    end = answer_start + len(answer)
    return f"{context[:answer_start]}<hl> {answer} <hl>{context[end:]}".strip()


def _build_rows(dataset) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for ex in dataset:
        ex_id = str(ex.get("id", ""))
        # TyDiQA secondary_task ids are prefixed with the language name.
        if not ex_id.lower().startswith("indonesian"):
            continue
        context = (ex.get("context") or "").strip()
        question = (ex.get("question") or "").strip()
        answers = ex.get("answers") or {}
        texts = answers.get("text") or []
        starts = answers.get("answer_start") or []
        if not context or not question or not texts:
            continue
        answer = str(texts[0]).strip()
        answer_start = int(starts[0]) if starts else context.find(answer)
        if not answer:
            continue

        key = (context[:80], question)
        if key in seen:
            continue
        seen.add(key)

        rows.append(
            {
                "input_plain": PREFIX + _answer_sentence(context, answer, answer_start),
                "input_hl": PREFIX + _highlight(context, answer, answer_start),
                "target": question,
                "context": context,
                "question": question,
                "answer": answer,
            }
        )
    return rows


def main() -> None:
    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit(
            "Missing `datasets`. Install with: pip install -r backend/ml/requirements-ml.txt"
        )

    print("Loading TyDiQA (secondary_task / Gold Passage)...")
    ds = load_dataset("tydiqa", "secondary_task")

    train_rows = _build_rows(ds["train"])
    val_rows = _build_rows(ds["validation"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, rows in [("train", train_rows), ("val", val_rows)]:
        path = OUT_DIR / f"tydiqa_id_{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  wrote {len(rows):5d} examples -> {path}")

    # Sanity sample
    if train_rows:
        s = train_rows[0]
        print("\nSample (train[0]):")
        print("  input_plain:", s["input_plain"][:120])
        print("  input_hl   :", s["input_hl"][:120])
        print("  target     :", s["target"])
        print("  answer     :", s["answer"])


if __name__ == "__main__":
    main()
