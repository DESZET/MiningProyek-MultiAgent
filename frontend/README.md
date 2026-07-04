# Asahlagi — Frontend

React + TypeScript + Vite. UI for the Asahlagi capstone product.

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ (comes with Node)

## Setup

```bash
cd frontend
npm install
cp .env.example .env.development
# Edit .env.development if backend runs on a non-default URL
```

## Development

```bash
npm run dev
```

Opens at http://localhost:5173. Vite provides hot module replacement.

The dev server expects the backend at `http://localhost:8000` by default (configurable via `VITE_API_BASE_URL`).

## Build

```bash
npm run build      # Type-check + build static assets to dist/
npm run preview    # Preview the production build
npm run typecheck  # Type-check only, no build
```

## Project structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/    # UI components (Layout, Logo, ThemeToggle, QuizQuestionCard, ...)
│   ├── hooks/         # useTheme, useQuiz, useTimer
│   ├── lib/           # cn() utility for Tailwind class composition
│   ├── pages/         # HomePage, QuizPage, ResultPage
│   ├── services/      # api.ts — single source of HTTP access
│   ├── types/         # quiz.ts, result.ts, api.ts (mirror /API.md §5)
│   ├── utils/         # i18n.ts (mirror /BRAND.md §7)
│   ├── App.tsx
│   ├── index.css      # Tailwind + theme tokens
│   └── main.tsx
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## How the pieces connect

- **Routing** (`App.tsx`): three routes — `/` → `HomePage`, `/quiz` → `QuizPage`, `/result` → `ResultPage`. State passes between pages via React Router's `location.state`.
- **API access** (`services/api.ts`): single source. Components do not call `fetch()` directly — they use `generateQuiz()` / `submitQuiz()` from this module.
- **Types** (`types/`): mirror `/API.md` §5 word-for-word. Any change to API shapes must be reflected here.
- **Copy** (`utils/i18n.ts`): mirror `/BRAND.md` §7. Components do not inline copy strings — they import from here.
- **Theme** (`hooks/useTheme.ts` + `index.css`): toggling sets `data-theme="light|dark"` on `<html>`; CSS variables flip accordingly. State persists in `localStorage` under key `asahlagi-theme`.

## Source of truth references

If something is unclear, consult these in order:
1. `/API.md` — the HTTP contract
2. `/ARCHITECTURE.md` §4 — frontend module layout
3. `/DESIGN.md` — visual design tokens
4. `/BRAND.md` — copy library and brand voice
