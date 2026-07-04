"""Redeploy the Asahlagi quiz-generator Hugging Face Space.

Unlike the backend Space (which clones `backend/` from GitHub at build time and
is rebuilt by scripts/redeploy_space.py), the quiz-gen Space holds its OWN copy
of the code. So redeploying it means UPLOADING the contents of
`huggingface/quizgen/` to the Space repo — pushing files triggers a rebuild
automatically.

Run this whenever you change `huggingface/quizgen/*`, e.g. after syncing
`qg_core.py` from `backend/ml/generator/qg_core.py` (the two must stay
byte-identical — this script verifies that before uploading).

Usage:
    python3 scripts/redeploy_quizgen_space.py

Requires in backend/.env:
    HF_WRITE_TOKEN   — Hugging Face token with write access to the Space
"""

import filecmp
import sys
from pathlib import Path

from dotenv import dotenv_values
from huggingface_hub import HfApi

SPACE_REPO_ID = "raviarnan/asahlagi-quizgen"
ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / "backend" / ".env"
QUIZGEN_DIR = ROOT / "huggingface" / "quizgen"
BACKEND_QG_CORE = ROOT / "backend" / "ml" / "generator" / "qg_core.py"
SPACE_QG_CORE = QUIZGEN_DIR / "qg_core.py"

# Never upload local cruft / secrets to the public Space.
IGNORE_PATTERNS = ["__pycache__/*", "*.pyc", ".venv/*", "venv/*", ".env", ".gitignore"]


def main() -> int:
    env = dotenv_values(ENV_PATH)
    hf_token = env.get("HF_WRITE_TOKEN")
    if not hf_token:
        print(f"ERROR: HF_WRITE_TOKEN missing in {ENV_PATH}", file=sys.stderr)
        return 1

    # Guard: the Space's qg_core.py must match the backend's verbatim. Shipping a
    # stale copy would silently serve a different quiz than the local fallback.
    if not SPACE_QG_CORE.exists():
        print(f"ERROR: {SPACE_QG_CORE} missing — copy it from {BACKEND_QG_CORE}", file=sys.stderr)
        return 1
    if not filecmp.cmp(BACKEND_QG_CORE, SPACE_QG_CORE, shallow=False):
        print(
            "ERROR: qg_core.py differs between backend and Space.\n"
            f"  Sync first:  cp {BACKEND_QG_CORE} {SPACE_QG_CORE}",
            file=sys.stderr,
        )
        return 1

    api = HfApi(token=hf_token)

    print(f"→ Uploading {QUIZGEN_DIR} to {SPACE_REPO_ID} (rebuild triggers on push) ...")
    api.upload_folder(
        folder_path=str(QUIZGEN_DIR),
        repo_id=SPACE_REPO_ID,
        repo_type="space",
        ignore_patterns=IGNORE_PATTERNS,
        commit_message="redeploy: sync quizgen Space from huggingface/quizgen/",
    )
    print("  upload done. Build takes ~1-2 min.")

    print(
        "\nVerify once build finishes:\n"
        "  curl -s https://raviarnan-asahlagi-quizgen.hf.space/   # expect status: ready\n"
        "  curl -s -X POST https://raviarnan-asahlagi-quizgen.hf.space/generate "
        "-H 'Content-Type: application/json' "
        "-d '{\"material_text\":\"<paste >=100 chars of material here>\"}'"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
