"""Persistence for Asahi's free-chat (home page) — "light memory".

Stores recent turns in Postgres (Neon) keyed to the anonymous device_id, so
Asahi can recall context across sessions. Best-effort: if the DB is unset or a
write fails, the chat still works (memory just won't persist) — it must never
break the conversation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select

from app.db.models import ChatMessage, User
from app.db.session import get_session, is_db_configured

logger = logging.getLogger("asahlagi")

_MAX_CONTENT = 2000


def _get_or_create_user(session, device_id: str) -> User:
    user = session.scalar(select(User).where(User.device_id == device_id))
    if user is None:
        user = User(device_id=device_id)
        session.add(user)
        session.flush()
    return user


def save_turn(device_id: str | None, user_text: str, asahi_text: str) -> None:
    """Persist one user message + Asahi's reply. Silently skips on any problem."""
    if not device_id or not is_db_configured():
        return
    try:
        with get_session() as session:
            user = _get_or_create_user(session, device_id.strip())
            # Both rows are inserted in one transaction, so func.now() would give
            # them the same created_at and the order would be ambiguous. Stamp the
            # user turn just before the reply so ordering by created_at is stable.
            now = datetime.now(timezone.utc)
            session.add(
                ChatMessage(
                    user_id=user.id,
                    role="user",
                    content=user_text[:_MAX_CONTENT],
                    created_at=now,
                )
            )
            session.add(
                ChatMessage(
                    user_id=user.id,
                    role="asahi",
                    content=asahi_text[:_MAX_CONTENT],
                    created_at=now + timedelta(milliseconds=1),
                )
            )
    except Exception:  # noqa: BLE001 — memory is best-effort, never break chat
        logger.warning("Asahi chat memory: save failed", exc_info=False)


def load_recent(device_id: str | None, limit: int = 20) -> list[dict]:
    """Return recent turns (chronological) as [{role, content}]. Empty on any miss."""
    if not device_id or not is_db_configured():
        return []
    try:
        with get_session() as session:
            user = session.scalar(
                select(User).where(User.device_id == device_id.strip())
            )
            if user is None:
                return []
            rows = session.scalars(
                select(ChatMessage)
                .where(ChatMessage.user_id == user.id)
                .order_by(desc(ChatMessage.created_at))
                .limit(limit)
            ).all()
            rows.reverse()  # oldest first
            return [{"role": r.role, "content": r.content} for r in rows]
    except Exception:  # noqa: BLE001
        logger.warning("Asahi chat memory: load failed", exc_info=False)
        return []
