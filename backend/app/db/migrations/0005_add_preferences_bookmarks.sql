-- Migration 0005 — §4.8 Batch 2-B: user preferences + material bookmarks
--
-- Apply by hand in the Neon SQL Editor (see migrations/README.md). Idempotent.
-- Until applied, the /gamification/preferences and /gamification/bookmarks
-- endpoints fail at query time and the global handler returns 503 — the rest of
-- the app keeps working (graceful-degradation contract).

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id               UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_num_questions INTEGER      NOT NULL DEFAULT 5,
    default_difficulty    VARCHAR(16)  NOT NULL DEFAULT 'medium',
    shuffle_options       BOOLEAN      NOT NULL DEFAULT true,
    weekly_goal           INTEGER      NOT NULL DEFAULT 5,
    favorite_topic        VARCHAR(80),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS material_bookmarks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         VARCHAR(120)  NOT NULL,
    material_text VARCHAR(20000) NOT NULL,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_material_bookmarks_user_id
    ON material_bookmarks (user_id);
