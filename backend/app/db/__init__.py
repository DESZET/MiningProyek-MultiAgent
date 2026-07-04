"""Database layer for gamification persistence (Neon Postgres).

Core quiz features (generate/submit) do NOT depend on this layer — they stay
in-memory. Only the gamification feature (XP, streak, level, achievements,
history) uses the database. If DATABASE_URL is unset, the app still boots and
quiz features work; gamification endpoints return a clear error.
"""
