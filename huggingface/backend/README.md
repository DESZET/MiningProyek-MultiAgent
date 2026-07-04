---
title: Asahlagi Backend
emoji: 📚
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Asahlagi API backend (TP-G005)
---

# Asahlagi Backend (HF Space)

FastAPI backend for the [Asahlagi capstone project](https://github.com/ravi-arnan/TempaCapstoneProject):
quiz generation orchestration, evaluation, understanding classification, insight,
recommendation, and gamification (XP/streak/level).

This Space builds by cloning the `backend/` folder from the public GitHub repo.

## Required secrets

Set these in the Space settings (Settings, Variables and secrets):

| Secret | Value |
|---|---|
| `DATABASE_URL` | Neon Postgres connection string (for gamification) |
| `HF_SPACE_URL` | `https://raviarnan-asahlagi-quizgen.hf.space` (the quiz-generator Space) |
| `CORS_ALLOWED_ORIGINS` | frontend origins, e.g. `https://<vercel-app>.vercel.app,https://localhost` |

If `DATABASE_URL` is unset, gamification endpoints return 503 and the core quiz
flow still works.

## Updating

This Space clones the repo at build time. To deploy the latest commit, use
**Factory rebuild** (Settings, Factory rebuild) so the clone runs fresh.

## Endpoints

See [`API.md`](https://github.com/ravi-arnan/TempaCapstoneProject/blob/main/API.md).
Health check: `GET /health`.

## Project context

Capstone project TP-G005 for the Tempa learning program by Dicoding.
Brand: Asahlagi, *Asah lagi sampai paham.*
