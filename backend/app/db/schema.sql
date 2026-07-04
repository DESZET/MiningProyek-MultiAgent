-- Asahlagi gamification schema (Neon Postgres)
-- Run this once in the Neon SQL Editor, or use: python -m app.db.init_db
--
-- Identity: anonymous device_id for now. Upgrading to real auth later only
-- needs an extra auth_user_id column; gamification tables stay intact.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()

CREATE TABLE IF NOT EXISTS users (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id    VARCHAR(128) UNIQUE NOT NULL,
    display_name VARCHAR(80),
    google_sub   VARCHAR(64) UNIQUE,   -- Google OAuth subject id (NULL for guests)
    email        VARCHAR(255),
    avatar_url   VARCHAR(512),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub);

CREATE TABLE IF NOT EXISTS user_stats (
    user_id          UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_xp         INTEGER NOT NULL DEFAULT 0,
    level            INTEGER NOT NULL DEFAULT 1,
    current_streak   INTEGER NOT NULL DEFAULT 0,
    longest_streak   INTEGER NOT NULL DEFAULT 0,
    last_active_date DATE,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id             VARCHAR(64) NOT NULL,
    topic               VARCHAR(80) NOT NULL DEFAULT 'Umum',
    score               INTEGER NOT NULL,
    understanding_level VARCHAR(16) NOT NULL,
    xp_earned           INTEGER NOT NULL,
    completed_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user ON quiz_attempts(user_id);

CREATE TABLE IF NOT EXISTS achievements (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_code  VARCHAR(48) NOT NULL,
    unlocked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_badge UNIQUE (user_id, badge_code)
);

CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(user_id);

CREATE TABLE IF NOT EXISTS persistent_quizzes (
    quiz_id         VARCHAR(64) PRIMARY KEY,
    source_material TEXT NOT NULL,
    questions_json  TEXT NOT NULL,
    difficulty      VARCHAR(16) NOT NULL DEFAULT 'medium',
    topic           VARCHAR(80) NOT NULL DEFAULT 'Umum',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

