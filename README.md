<p align="center">
  <img src="assets/logo.svg" alt="Asahlagi" width="240">
</p>

<h1 align="center">Asahlagi</h1>

<p align="center"><em>Asah lagi sampai paham.</em></p>

<p align="center">
  <img alt="React" src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="Tests" src="https://img.shields.io/badge/tests-52%20passing-brightgreen">
</p>

<p align="center">
  <strong><a href="https://tempa-capstone-project.vercel.app">Live demo</a></strong>
</p>

> First request may take ~30-60s while the Hugging Face Spaces wake from sleep.

---

**Asahlagi** turns any learning material into an automatic quiz, evaluates the result, and
surfaces an understanding level, insight, and actionable learning recommendation. Instead of
guessing whether they understood what they read, students get a clear, honest measurement and a
concrete next step. The name encodes the loop: read, *asah* (sharpen), *asah lagi* (sharpen again),
*sampai paham* (until you understand).

**Academic project title:** *Sistem Deteksi Tingkat Pemahaman Mahasiswa dalam Proses Pembelajaran
Berdasarkan Hasil Kuis Berbasis Data*
**Team:** TP-G005, capstone for the Tempa learning program by Dicoding.

---

## Key Features

- **Multi-source input** — paste text, upload a PDF, or drop an article URL. The backend extracts
  clean text from each source.
- **Automatic quiz generation** — a fine-tunable Indonesian T5 model (IndoT5) hosted on Hugging
  Face generates multiple-choice questions, with a resilient rule-based fallback so a quiz is
  always produced, even offline.
- **Understanding detection** — a scikit-learn Random Forest classifies the result as high,
  medium, or low, with a deterministic guardrail and rule-based fallback for reliability.
- **Insight and recommendation** — deterministic, explainable engines (no black-box LLM at
  runtime) give a short explanation and an actionable next step.
- **Focused quiz experience** — one question at a time, keyboard shortcuts, progress pills,
  auto-saved answers, and a per-question review on the result page.
- **Gamification** — XP, streaks, levels, and achievement badges persisted to a cloud database,
  to keep learners coming back. See [`GAMIFICATION.md`](docs/GAMIFICATION.md).
- **Light and dark mode**, motion-respecting animations, and an Indonesian-first interface.

## How It Works

```
                 Text / PDF / URL
                        |
                        v
        Source Extractor (pdfplumber, trafilatura)
                        |
                        v
   Quiz Generator  ──►  Hugging Face Space (IndoT5)
   (3-tier)             ├─ local CPU fallback
                        └─ rule-based fallback
                        |
                        v
              Quiz (one question at a time)
                        |
                        v
   Evaluator ─► Understanding Classifier ─► Insight + Recommendation
                        |
                        v
        Result: score, level, insight, recommendation,
        per-question review, chart, and XP/streak reward
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router, Lucide icons |
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| Quiz generation (DL) | IndoT5 (`Wikidepia/IndoT5-base`) on a Hugging Face Space, queried over HTTP |
| Classification (ML) | scikit-learn Random Forest on synthetic data |
| Insight / recommendation | Deterministic template engines |
| Source extraction | pdfplumber (PDF), trafilatura (URL) |
| Gamification storage | Neon (serverless Postgres) via SQLAlchemy |
| Tooling | pytest, `tsc --noEmit`, Vite build |

## Architecture Highlights

- **Stateless quiz engine, separate state store.** The FastAPI backend handles quiz generation
  and evaluation in memory; user progress (XP, streak, history) lives in Postgres. The two
  concerns stay decoupled.
- **Resilience by design.** Quiz generation degrades gracefully: cloud model, then local model,
  then rule-based. Classification has an ML path plus a rule-based fallback and a score-ceiling
  guardrail. If the gamification database is unavailable, those endpoints return 503 and the core
  quiz experience is unaffected.
- **Anti-cheat.** Correct answers and all XP/streak/level math are computed server-side, never
  trusted from the client.
- **Anonymous identity.** Gamification uses an anonymous device id (no login), with a schema ready
  to upgrade to real authentication later.

## Getting Started

Requires **Python 3.12** and **Node 20+**.

### Backend (`http://localhost:8000`)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in HF_SPACE_URL and DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

- `HF_SPACE_URL` points to the deployed quiz-generator Space. If empty, the rule-based generator
  is used.
- `DATABASE_URL` is a Neon Postgres connection string. If empty, gamification is disabled but the
  quiz flow still works. See [`backend/app/db/README.md`](backend/app/db/README.md) for database
  setup.
- The trained classifier (`backend/ml/classifier/artifacts/classifier.pkl`) is committed, so no
  training step is needed to run the app.

### Frontend (`http://localhost:5173`)

```bash
cd frontend
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` (defaults to `http://localhost:8000`).

### Tests

```bash
cd backend && pytest                       # 52 tests
cd frontend && npm run typecheck && npm run build
```

## Project Structure

```
.
├─ frontend/                 React + TypeScript + Vite
│  └─ src/{components,pages,hooks,services,types,utils,lib}
├─ backend/
│  ├─ app/
│  │  ├─ routes/             HTTP endpoints (quiz, gamification, health)
│  │  ├─ services/           quiz, evaluator, classifier wrappers, XP/achievement engines
│  │  ├─ schemas/            Pydantic request/response models
│  │  ├─ db/                 SQLAlchemy models + Neon session (gamification)
│  │  └─ utils/
│  ├─ ml/
│  │  ├─ generator/          IndoT5 inference + rule-based fallback
│  │  └─ classifier/         Random Forest training, inference, artifacts
│  └─ tests/
├─ huggingface/             Dockerized HF Spaces (quizgen + backend)
├─ docs/                    all specs: PRD, ARCHITECTURE, API, ML, DESIGN, BRAND,
│                           GAMIFICATION(+_TASKS), MOBILE, DEPLOY, ROADMAP, TASKS, tugas/
├─ README.md                this file
└─ CLAUDE.md                project instructions
```

## API

The HTTP contract is defined in [`API.md`](docs/API.md). Endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | liveness check |
| `POST` | `/quiz/generate` | generate a quiz from text |
| `POST` | `/quiz/generate-from-url` | generate from an article URL |
| `POST` | `/quiz/generate-from-pdf` | generate from an uploaded PDF |
| `POST` | `/quiz/regenerate` | regenerate from a prior quiz's source ("Asah Lagi") |
| `POST` | `/quiz/submit` | score answers, classify, return insight + recommendation |
| `POST` | `/gamification/record-attempt` | award XP/streak/level, unlock badges |
| `GET` | `/gamification/stats` · `/history` · `/achievements` | progress data |

Correct answers are never returned to the client; they are stored server-side and used only at
submit time.

## Roadmap

- **Gamification** Fase 2-4 (adaptive difficulty, analytics + per-topic mastery, achievements +
  daily goals + nudges) — see [`GAMIFICATION_TASKS.md`](docs/GAMIFICATION_TASKS.md).
- **Android app** via Capacitor, with push-notification reminders on the roadmap — see
  [`MOBILE.md`](docs/MOBILE.md).
- **Public deployment**, frontend tests, and analytics — see [`ROADMAP.md`](docs/ROADMAP.md).

## Team

| Member | Role |
|---|---|
| Audry Nabila Anastasya | Backend, Quiz Generator |
| Ariq Marwan Permana | Backend, Data & Analysis |
| Desta Anandhika Rajendra Maheswara | Backend, Logic, Insight & Recommendation |
| Ravi Arnan Irianto | Frontend, React & TypeScript, integration |

## Documentation

| Document | Contents |
|---|---|
| [PRD.md](docs/PRD.md) | product requirements |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | internal system structure |
| [API.md](docs/API.md) | HTTP contract |
| [ML.md](docs/ML.md) | ML/DL strategy, datasets, models |
| [DESIGN.md](docs/DESIGN.md) | visual design tokens |
| [BRAND.md](docs/BRAND.md) | brand identity, voice, copy library |
| [GAMIFICATION.md](docs/GAMIFICATION.md) · [GAMIFICATION_TASKS.md](docs/GAMIFICATION_TASKS.md) | gamification direction + team tasks |
| [MOBILE.md](docs/MOBILE.md) | mobile (Capacitor) strategy |
| [DEPLOY.md](docs/DEPLOY.md) | deployment steps (Render + Vercel) |
| [ROADMAP.md](docs/ROADMAP.md) | prioritized backlog |

---

<p align="center"><sub>Capstone project, TP-G005, Tempa by Dicoding.</sub></p>
