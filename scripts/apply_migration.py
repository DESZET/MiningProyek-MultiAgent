"""Apply a SQL migration file to the Neon database.

Reads DATABASE_URL from backend/.env (never hard-coded), reuses the app's URL
normalization + engine, and executes the migration as one batch. Migrations are
idempotent (CREATE TABLE IF NOT EXISTS), so re-running is safe.

Usage:
    python3 scripts/apply_migration.py backend/app/db/migrations/0005_add_preferences_bookmarks.sql
"""

import os
import sys
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / "backend" / ".env"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: apply_migration.py <path-to-.sql>", file=sys.stderr)
        return 2

    sql_path = Path(sys.argv[1])
    if not sql_path.is_absolute():
        sql_path = ROOT / sql_path
    if not sql_path.exists():
        print(f"ERROR: migration not found: {sql_path}", file=sys.stderr)
        return 1

    env = dotenv_values(ENV_PATH)
    db_url = env.get("DATABASE_URL")
    if not db_url:
        print(f"ERROR: DATABASE_URL missing in {ENV_PATH}", file=sys.stderr)
        return 1
    os.environ["DATABASE_URL"] = db_url

    # Import after setting the env var; reuse the app's normalized engine.
    sys.path.insert(0, str(ROOT / "backend"))
    from sqlalchemy import text
    from app.db.session import get_engine

    sql = sql_path.read_text()
    engine = get_engine()
    print(f"→ Applying {sql_path.name} ...")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
    print("  done.")

    # Verify the expected tables now exist.
    expected = ["user_preferences", "material_bookmarks"]
    with engine.connect() as conn:
        present = {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = ANY(:names)"
                ),
                {"names": expected},
            )
        }
    for t in expected:
        print(f"  {'✓' if t in present else '✗'} {t}")
    return 0 if all(t in present for t in expected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
