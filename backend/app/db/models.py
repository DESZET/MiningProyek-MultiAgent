"""SQLAlchemy ORM models for gamification.

Identity note: for the capstone we identify users by an anonymous `device_id`
(a UUID generated client-side, stored in localStorage, sent via the
`X-Device-Id` header). The schema already uses a separate surrogate `id` so
that upgrading to real auth later (e.g. Neon Auth) only requires adding an
`auth_user_id` column — no data migration of the gamification tables.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    device_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Google login (OAuth). All nullable so anonymous guests stay valid; a row is
    # "logged in" once google_sub is set. google_sub is Google's stable subject id.
    google_sub: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    total_xp: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    level: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    current_streak: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    quiz_id: Mapped[str] = mapped_column(String(64))
    topic: Mapped[str] = mapped_column(String(80), default="Umum", server_default="Umum")
    score: Mapped[int] = mapped_column(Integer)
    understanding_level: Mapped[str] = mapped_column(String(16))
    xp_earned: Mapped[int] = mapped_column(Integer)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    badge_code: Mapped[str] = mapped_column(String(48))
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("user_id", "badge_code", name="uq_user_badge"),
    )


class PersistentQuiz(Base):
    __tablename__ = "persistent_quizzes"

    quiz_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_material: Mapped[str] = mapped_column(String(20000))
    questions_json: Mapped[str] = mapped_column(String)  # stored as JSON string
    difficulty: Mapped[str] = mapped_column(String(16), default="medium", server_default="medium")
    topic: Mapped[str] = mapped_column(String(80), default="Umum", server_default="Umum")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserPreference(Base):
    """§4.8 — per-user learning preferences. Defaults seeded on first read so a
    missing row behaves like sensible defaults (5 / medium / shuffle / goal 5)."""

    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    default_num_questions: Mapped[int] = mapped_column(
        Integer, default=5, server_default="5"
    )
    default_difficulty: Mapped[str] = mapped_column(
        String(16), default="medium", server_default="medium"
    )
    shuffle_options: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    weekly_goal: Mapped[int] = mapped_column(Integer, default=5, server_default="5")
    favorite_topic: Mapped[str | None] = mapped_column(String(80), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MaterialBookmark(Base):
    """§4.8 — material the user saved to re-quiz later."""

    __tablename__ = "material_bookmarks"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(120))
    material_text: Mapped[str] = mapped_column(String(20000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ChatMessage(Base):
    """One turn of free-chat with Asahi (home-page chat bubble), so she can
    recall recent context across sessions. role is "user" or "asahi"."""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

