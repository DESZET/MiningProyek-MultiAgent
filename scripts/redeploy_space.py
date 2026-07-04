"""Redeploy the Asahlagi backend Hugging Face Space.

Reads tokens from backend/.env (never hard-coded), pushes the GITHUB_TOKEN
secret to the Space, then triggers a factory rebuild so the Space re-clones
the latest `main` (which includes the /chat/* chatbot routes).

Usage:
    python3 scripts/redeploy_space.py

Requires in backend/.env:
    HF_WRITE_TOKEN   — Hugging Face token with write access to the Space
    GITHUB_TOKEN     — GitHub PAT that powers the Asahi chatbot (GitHub Models)
"""

import sys
from pathlib import Path

from dotenv import dotenv_values
from huggingface_hub import HfApi

SPACE_REPO_ID = "raviarnan/asahlagi-backend"
ENV_PATH = Path(__file__).resolve().parent.parent / "backend" / ".env"


def main() -> int:
    env = dotenv_values(ENV_PATH)
    hf_token = env.get("HF_WRITE_TOKEN")
    github_token = env.get("GITHUB_TOKEN")

    if not hf_token:
        print(f"ERROR: HF_WRITE_TOKEN missing in {ENV_PATH}", file=sys.stderr)
        return 1
    if not github_token:
        print(f"ERROR: GITHUB_TOKEN missing in {ENV_PATH}", file=sys.stderr)
        return 1

    api = HfApi(token=hf_token)

    print(f"→ Setting GITHUB_TOKEN secret on {SPACE_REPO_ID} ...")
    api.add_space_secret(repo_id=SPACE_REPO_ID, key="GITHUB_TOKEN", value=github_token)
    print("  done.")

    print(f"→ Factory-rebuilding {SPACE_REPO_ID} (re-clones latest main) ...")
    api.restart_space(repo_id=SPACE_REPO_ID, factory_reboot=True)
    print("  rebuild triggered. Build takes ~1-2 min.")

    print(
        "\nVerify once build finishes:\n"
        "  curl -s -o /dev/null -w '%{http_code}\\n' -X POST "
        "https://raviarnan-asahlagi-backend.hf.space/chat/ask "
        "-H 'Content-Type: application/json' -d '{\"message\":\"halo\",\"history\":[]}'"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
