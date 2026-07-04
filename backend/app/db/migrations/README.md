# Database Migrations

This directory contains SQL migration files for the Neon Postgres database.

## How to apply migrations

1. **Initial setup (first time only)**:
   - Create tables using the SQL in `app/db/schema.sql`
   - Run via `python -m app.db.init_db` (uses SQLAlchemy ORM)

2. **Apply individual migrations**:
   - Open the [Neon Console](https://console.neon.tech)
   - Navigate to your project → SQL Editor
   - Copy-paste the content of each migration file (in order)
   - Execute each migration

## Migration order

- `0001_initial_schema.sql` — Initial gamification schema (XP, streak, badges, quiz attempts, persistent quizzes)
- `0002_add_topic_columns.sql` — Add `topic` columns for per-topic mastery analytics
- `0003_add_google_auth.sql` — Add Google login columns (`google_sub`, `email`, `avatar_url`) to `users`
- `0004_add_chat_messages.sql` — Add `chat_messages` table for Asahi free-chat memory
- `0005_add_preferences_bookmarks.sql` — Add `user_preferences` + `material_bookmarks` tables (§4.8 Batch 2-B). **Until applied, `/gamification/preferences` and `/gamification/bookmarks` return 503 and their UI degrades to off; the rest of the app is unaffected.**

## Notes

- All `ALTER TABLE` statements use `IF EXISTS` and `IF NOT EXISTS` to be idempotent
- Migrations are cumulative — apply in order without skipping
- If a migration has already been applied (column exists), it will be safely skipped
