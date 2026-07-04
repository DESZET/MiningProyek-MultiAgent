"""Create gamification tables from the ORM models.

Convenience alternative to running schema.sql manually. Run once after
setting DATABASE_URL:

    python -m app.db.init_db
"""

from __future__ import annotations

from dotenv import load_dotenv

# Load backend/.env so DATABASE_URL is available when run as a standalone script.
load_dotenv()

from app.db.models import Base
from app.db.session import get_engine, is_db_configured


def main() -> None:
    if not is_db_configured():
        raise SystemExit(
            "DATABASE_URL is not set. Add your Neon connection string to "
            "backend/.env first."
        )
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Gamification tables created (or already existed).")


if __name__ == "__main__":
    main()
