# Database setup (gamification)

Gamification (XP, streak, level, achievements, history) is the only feature
that uses a database. Core quiz features stay in-memory and work without it.

We use **Neon** (serverless Postgres, free tier). Identity is an anonymous
`device_id` for now; the schema supports adding real auth later without a
data migration.

## 1. Create a Neon project

1. Sign up at https://neon.tech (GitHub login).
2. New Project, region **Singapore** (`ap-southeast-1`) for lowest latency.
3. Copy the **connection string** (looks like
   `postgresql://user:pass@ep-xxx.ap-southeast-1.aws.neon.tech/dbname?sslmode=require`).

## 2. Configure the backend

Add the connection string to `backend/.env`:

```
DATABASE_URL=postgresql://user:pass@ep-xxx.ap-southeast-1.aws.neon.tech/dbname?sslmode=require
```

(You can paste the raw `postgresql://` string. The backend rewrites it to use
the psycopg v3 driver automatically.)

Install deps:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Create the tables

Either run the migration from the ORM models:

```bash
python -m app.db.init_db
```

Or paste `app/db/schema.sql` into the Neon SQL Editor and run it.

## 4. Verify

```bash
uvicorn app.main:app --reload --port 8000
# in another shell:
curl -H "X-Device-Id: test-device-123" http://localhost:8000/gamification/stats
# -> {"total_xp":0,"level":1,...}
```

If `DATABASE_URL` is unset, gamification endpoints return HTTP 503 and the
rest of the app keeps working.

## Schema

| Table | Purpose |
|---|---|
| `users` | one row per device (or future auth user) |
| `user_stats` | total XP, level, current/longest streak, last active date |
| `quiz_attempts` | history of completed quizzes + XP earned |
| `achievements` | unlocked badges per user |

## Endpoints

| Method | Path | Notes |
|---|---|---|
| POST | `/gamification/record-attempt` | call after `/quiz/submit`; updates XP/streak/level, unlocks badges |
| GET | `/gamification/stats` | current XP/level/streak |
| GET | `/gamification/history?limit=10` | recent attempts |
| GET | `/gamification/achievements` | all badges with unlock status |

All require the `X-Device-Id` header.
