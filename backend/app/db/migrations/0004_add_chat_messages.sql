-- 0004: Asahi free-chat memory
-- Stores recent free-chat turns (home-page chat bubble) so Asahi can recall
-- context across sessions. Keyed to users(id) via the anonymous device_id.

CREATE TABLE IF NOT EXISTS chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        VARCHAR(16)  NOT NULL,   -- 'user' | 'asahi'
    content     VARCHAR(2000) NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_chat_messages_user_id ON chat_messages (user_id);
