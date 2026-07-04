-- Migration 0003: Add Google login (OAuth) columns to users
-- Run this once in the Neon SQL Editor after PR is merged.
-- Adds Google identity to the existing anonymous-device user rows so a guest
-- can be "promoted" to a logged-in account without a data migration.

-- google_sub = Google's stable subject id; NULL for anonymous guests.
ALTER TABLE IF EXISTS users
ADD COLUMN IF NOT EXISTS google_sub VARCHAR(64);

ALTER TABLE IF EXISTS users
ADD COLUMN IF NOT EXISTS email VARCHAR(255);

ALTER TABLE IF EXISTS users
ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(512);

-- One account per Google identity. Partial-free unique index is fine here:
-- Postgres treats multiple NULLs as distinct, so guests (google_sub IS NULL)
-- do not collide.
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub);
