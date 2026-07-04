# API Contract — TempaCapstoneProject

**Project**: Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data
**Team**: TP-G005
**Status**: v1.1 — core contract locked; gamification + adaptive difficulty added
**Last updated**: 2026-05-26

---

## 1. Overview

This document is the **single source of truth** for the HTTP contract between the React frontend and the Python backend. Any field added, renamed, or removed must be reflected here AND signed off by both sides before merging.

### Why this document exists
- Frontend (Ravi) and Backend (Audry / Ariq / Desta) work in parallel.
- The dependency chain is: `material_text → quiz → answers → result → display`. A drift in any shape blocks the whole chain.
- Discovering an API mismatch in Week 5 = demo failure. Locking the contract in Week 1 = predictable integration.

### Scope
- Quiz endpoints: `/health`, `/quiz/generate`, `/quiz/generate-from-url`, `/quiz/generate-from-pdf`, `/quiz/submit`, `/quiz/regenerate`, `/quiz/daily-challenge`.
- Gamification endpoints: `/gamification/record-attempt`, `/gamification/stats`, `/gamification/history`, `/gamification/achievements`.
- All data shapes used in those endpoints.
- All error codes and validation rules.
- Side-by-side TypeScript + Pydantic models for shared types.

> **v1.1 additions** (gamification phase, merged 2026-05-26): adaptive `difficulty`
> param on all generate endpoints, `/quiz/regenerate` + `/quiz/daily-challenge`,
> `question_reviews[]` in the submit response, and the four `/gamification/*`
> endpoints (anonymous `X-Device-Id` identity). See §4.6–§4.9 and the changelog.

### Out of scope (NOT this document)
- Internal classification / insight / recommendation rule logic → see `CLASSIFICATION_RULES.md` (TBD).
- Architecture diagrams of internal modules → see `ARCHITECTURE.md` (TBD).
- Frontend component design → see `DESIGN.md`.

### Relationship to CLAUDE.md / PRD.md

The API sketches in `CLAUDE.md` §"API Contract Suggestions" and `PRD.md` were preliminary. **This document supersedes them.** Two intentional differences from those sketches — please review:

1. **`correct_answer` is no longer returned in the `/quiz/generate` response.**
   _Why_: returning correct answers to the client lets users see them in DevTools → Network tab. The correct answer is now stored server-side and used internally by `/quiz/submit`. See §8 for storage strategy.

2. **`selected_answer: "A"` → `selected_option_index: 0`** in `/quiz/submit` request.
   _Why_: integer index (0–3) is robust to display reordering and avoids letter-parsing on the backend. Frontend can map index → letter label for display only.

If the team prefers the original sketches, raise it in the §12 sign-off discussion **before** Audry/Ariq start implementing. Otherwise these changes are in effect.

---

## 2. Conventions

### Base URL
- **Development**: `http://localhost:8000`
- **Demo**: TBD (likely tunneled via `ngrok` or similar for the demo session)
- All endpoint paths in this document are **relative to base URL**.

### Content type
- All requests: `Content-Type: application/json`
- All responses: `Content-Type: application/json; charset=utf-8`

### HTTP methods
- `GET` for read-only operations
- `POST` for creating quizzes and submitting answers
- No `PUT`/`PATCH`/`DELETE` in MVP

### Status codes used

| Code | Meaning | When |
|---|---|---|
| `200 OK` | Success | All successful responses |
| `400 Bad Request` | Validation failure | Empty material, material too short, missing required field |
| `404 Not Found` | Resource missing | `quiz_id` not found at submit time |
| `422 Unprocessable Entity` | Schema validation failure | Pydantic-level type errors (FastAPI default) |
| `500 Internal Server Error` | Unexpected backend error | Any uncaught exception |

### Response envelope

**Success responses** return the resource directly (no envelope):
```json
{ "quiz_id": "...", "questions": [...] }
```

**Error responses** use a consistent error envelope:
```json
{
  "detail": "Human-readable error message in Indonesian by default",
  "code": "MATERIAL_TOO_SHORT"
}
```

- `detail`: localized message safe to show to users
- `code`: machine-readable error code (uppercase, snake-case, stable across versions)

> FastAPI default uses just `{"detail": "..."}` without `code`. We extend it with `code` for robust frontend error handling. Backend wraps all custom errors via a shared exception handler (see implementation note in §10).

### Localization
- API response **enum values** use lowercase English codes (`"high"`, `"medium"`, `"low"`) — language-agnostic.
- API response **display strings** (`insight`, `recommendation`, error `detail`) come in **Indonesian by default**.
- Future-proofing: `?lang=en` query param can be added later without breaking changes (out of scope for MVP).

### IDs
- `quiz_id`: UUID v4 string, e.g., `"550e8400-e29b-41d4-a716-446655440000"`
- `question.id`: simple integer (1-based) within a quiz, e.g., `1, 2, 3, ...`

### Time
- Always integer seconds (e.g., `time_taken_seconds: 120` = 2 minutes).
- All timestamps (if added later) use ISO 8601 UTC: `"2026-05-04T15:30:00Z"`.

---

## 3. Authentication

**No login / no accounts.** All endpoints are open. This is consistent with the
project scope — no passwords, no PII.

**Anonymous device identity (`X-Device-Id`).** Gamification (§4.8–§4.9) and
adaptive difficulty (§4.10) identify a returning user by an `X-Device-Id`
request header: a UUID the frontend generates once on first visit and persists
in `localStorage`. It is optional on the quiz endpoints (only enables adaptive
difficulty) and **required** on `/gamification/*` (missing → `400
DEVICE_ID_REQUIRED`). Clearing browser storage resets the identity — acceptable
for this scope.

If real auth is added post-MVP, the convention will be: `Authorization: Bearer
<token>` header. Reserve this header now; do not use it for other purposes.

---

## 4. Endpoints

### 4.1 Health check

```
GET /health
```

Returns backend liveness. Used by frontend to detect "backend is down" state and by demo runner to verify boot.

#### Response · 200 OK

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

#### Errors
None defined. Any non-200 = backend dead.

#### Example
```bash
curl http://localhost:8000/health
```

---

### 4.2 Generate quiz

```
POST /quiz/generate
```

Generates a multiple-choice quiz from learning material.

#### Request body

```json
{
  "material_text": "Fotosintesis adalah proses pembentukan glukosa...",
  "difficulty": "medium",
  "num_questions": 5,
  "shuffle_options": true
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `material_text` | string | yes | min 100 chars, max 20,000 chars; non-empty after trimming |
| `difficulty` | string | no | one of `"easy"` \| `"medium"` \| `"hard"`. Omit to let the backend choose adaptively — see §4.10 |
| `num_questions` | int | no | one of `3` \| `5` \| `7` \| `10` (§4.3). Overrides the difficulty-derived count. Omit to use the difficulty default |
| `shuffle_options` | bool | no | default `true`. When `false`, multiple-choice options are returned in a stable alphabetical order instead of randomised (§4.3) |

> **Adaptive difficulty**: when `difficulty` is omitted, the backend picks one
> based on the caller's gamification level (via the `X-Device-Id` header, if sent
> and the DB is configured): level ≤3 → `easy`, ≤8 → `medium`, else `hard`.
> Falls back to `medium` when there is no device id or no DB. An explicit
> `difficulty` always wins.
>
> **Question count** (§4.3): `num_questions` is independent of difficulty and
> wins when provided (clamped to 3–10). When omitted, `difficulty` sets the
> count: `easy` = 3, `medium` = 5, `hard` = 7. The same `num_questions` /
> `shuffle_options` fields apply to `/quiz/generate-from-url` (body) and
> `/quiz/generate-from-pdf` (query params).

#### Response · 200 OK

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "id": 1,
      "question": "Apa peran utama klorofil dalam fotosintesis?",
      "options": [
        "Menyerap cahaya matahari",
        "Menghasilkan oksigen",
        "Menyimpan glukosa",
        "Memecah air"
      ]
    }
  ],
  "total_questions": 5,
  "generated_at": "2026-05-04T15:30:00Z",
  "difficulty": "medium"
}
```

| Field | Type | Notes |
|---|---|---|
| `quiz_id` | string (UUID) | Use this when calling `/quiz/submit` |
| `questions[]` | Question[] | 3 / 5 / 7 items per `easy` / `medium` / `hard` |
| `questions[].id` | int | 1-based, sequential within this quiz |
| `questions[].question` | string | Question prompt in Indonesian |
| `questions[].options` | string[] | Always 4 options (A, B, C, D positions) |
| `total_questions` | int | Convenience count, equals `questions.length` |
| `generated_at` | string (ISO 8601) | UTC timestamp |
| `difficulty` | string | the difficulty actually used (`easy` \| `medium` \| `hard`); echoes the resolved value, useful when it was chosen adaptively |

> **IMPORTANT — `correct_answer` is NOT exposed.**
> The correct answer is stored server-side keyed by `quiz_id`. Returning correct answers to the client would let users inspect the network tab and "win" trivially. This also keeps the request/response payload smaller.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `MATERIAL_EMPTY` | `material_text` is missing/empty/whitespace | "Materi tidak boleh kosong." |
| 400 | `MATERIAL_TOO_SHORT` | < 100 chars after trim | "Materi terlalu pendek. Minimal 100 karakter." |
| 400 | `MATERIAL_TOO_LONG` | > 20,000 chars | "Materi terlalu panjang. Maksimal 20.000 karakter." |
| 422 | (FastAPI auto) | wrong types, missing field | (FastAPI default body) |
| 500 | `QUIZ_GENERATION_FAILED` | Generator raises | "Gagal menghasilkan kuis. Silakan coba lagi." |

### Response time expectation

> ⚠️ **`POST /quiz/generate` is the slowest endpoint by design.**
> The DL model (fine-tuned IndoT5) runs inference on CPU (no GPU at runtime). Expected latency:
> - **Cold start** (first request after server boot): 25-50s — includes ~10s model load + ~15-40s generation
> - **Warm inference** (subsequent requests): 15-40s for 5 questions
> - **Per question**: 3-8s on typical CPU
>
> Frontend MUST show loading state with progress messages during this wait. See `BRAND.md` §7.3 for copy.
> Frontend timeout for this endpoint should be set to at least **60 seconds** to avoid spurious "connection lost" errors.
>
> All other endpoints (`/health`, `/quiz/submit`) respond in < 100ms.
>
> See `ML.md` §7 for full latency breakdown and optimization options.

#### Example

```bash
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "material_text": "Fotosintesis adalah proses pembentukan glukosa oleh tumbuhan hijau dengan bantuan cahaya matahari dan klorofil. Proses ini terjadi di kloroplas dan menghasilkan oksigen sebagai produk samping..."
  }'
```

---

### 4.3 Generate quiz from URL

```
POST /quiz/generate-from-url
```

Fetches an article from a public URL, extracts the main text, then generates a quiz the same way as `/quiz/generate`.

#### Request body

```json
{
  "url": "https://contoh.com/artikel-pelajaran",
  "difficulty": "medium"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `url` | string | yes | must start with `http://` or `https://`; publicly reachable; HTML page (not PDF/binary); max 2048 chars |
| `difficulty` | string | no | `"easy"` \| `"medium"` \| `"hard"`; same adaptive behaviour as §4.2 |

#### Response · 200 OK

Same shape as §4.2 `/quiz/generate` response. The backend extracts the article text via `trafilatura` (with optional Playwright fallback for SPA/lazy-loaded pages), then applies the standard quiz pipeline.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `URL_INVALID` | not http(s) or malformed | "URL tidak valid. Pastikan dimulai dengan http:// atau https://" |
| 400 | `URL_FETCH_FAILED` | DNS/connection failure or non-200 status | "Gagal mengambil halaman dari URL." |
| 400 | `URL_EMPTY_CONTENT` | trafilatura returned nothing extractable | "Halaman tidak punya artikel yang bisa diambil." |
| 400 | `URL_TOO_SHORT` | extracted text < 100 chars | "Artikel di URL terlalu pendek." |
| 400 | `URL_TOO_LONG` | extracted text > 20,000 chars (auto-truncated, warning) | "Artikel terlalu panjang." |
| 500 | `QUIZ_GENERATION_FAILED` | downstream generator failure | "Gagal membuat kuis dari URL." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/generate-from-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://id.wikipedia.org/wiki/Fotosintesis"}'
```

> **User-Agent**: backend sends `AsahlagiBot/1.0` when fetching pages, so server logs can identify the source.

---

### 4.4 Generate quiz from PDF

```
POST /quiz/generate-from-pdf
```

Accepts a PDF file upload, extracts text via `pdfplumber`, then generates a quiz.

#### Request body

`multipart/form-data` with one part:

| Field | Type | Required | Validation |
|---|---|---|---|
| `file` | binary PDF | yes | content-type `application/pdf`; file size ≤ 10 MB; PDF must contain extractable text (not scanned images) |

Optional `difficulty` query parameter (`?difficulty=easy|medium|hard`) with the
same adaptive behaviour as §4.2; omit to let the backend choose.

#### Response · 200 OK

Same shape as §4.2 `/quiz/generate` response.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `PDF_INVALID` | file is not a valid PDF | "File PDF tidak bisa diproses." |
| 400 | `PDF_EMPTY` | pdfplumber returns no text (scan or empty) | "PDF tidak punya teks yang bisa diekstrak." |
| 400 | `PDF_TOO_SHORT` | extracted text < 100 chars | "Teks PDF terlalu pendek." |
| 400 | `PDF_TOO_LONG` | extracted text > 20,000 chars (auto-truncated, warning) | "PDF terlalu panjang." |
| 413 | (FastAPI auto) | file > 10 MB | (FastAPI default body) |
| 500 | `QUIZ_GENERATION_FAILED` | downstream generator failure | "Gagal membuat kuis dari PDF." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/generate-from-pdf \
  -F "file=@/path/to/material.pdf"
```

---

### 4.5 Submit quiz

```
POST /quiz/submit
```

Submits user's answers and returns full result analysis.

#### Request body

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "answers": [
    { "question_id": 1, "selected_option_index": 0 },
    { "question_id": 2, "selected_option_index": 2 },
    { "question_id": 3, "selected_option_index": null }
  ],
  "time_taken_seconds": 245
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `quiz_id` | string (UUID) | yes | must match an existing generated quiz |
| `answers[]` | Answer[] | yes | length must equal `total_questions` from generate response |
| `answers[].question_id` | int | yes | must reference an existing question in the quiz |
| `answers[].selected_option_index` | int \| null | for MC/TF | 0–3 (matches `options` array index), or `null` for unanswered |
| `answers[].text_answer` | string \| null | for short_answer | the typed answer; `null`/empty = unanswered |
| `answers[].matches` | int[] \| null | for matching | `matches[i]` = chosen `right_items` index for `left_items[i]`, or `-1` when unpaired (§6.2) |
| `time_taken_seconds` | int | yes | ≥ 0, ≤ 7200 (2 hours sanity cap) |

> **Why `selected_option_index` (int 0–3) instead of `selected_answer` (string "A"–"D")?**
> Index is robust to display reordering and avoids parsing. Frontend can map index→letter label for display purposes only.

> **Question types (§6.2)**: `type` is one of `multiple_choice`, `true_false`,
> `short_answer`, `matching`. A `matching` question carries `left_items` (terms)
> and `right_items` (a shuffled answer bank) instead of `options`; the user
> submits `matches`. Scoring gives **partial credit** for matching — each correct
> pair counts fractionally toward `score_percentage` — but `correct_count`
> only counts a question as correct when *fully* correct. `question_reviews[]`
> for a matching row includes `left_items`, `right_items`, `matches`, and
> `correct_matches`.

#### Response · 200 OK

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "score": {
    "score_percentage": 80,
    "correct_count": 4,
    "wrong_count": 1,
    "unanswered_count": 0,
    "total_questions": 5
  },
  "time_taken_seconds": 245,
  "understanding_level": "high",
  "insight": "Kamu memahami konsep utama materi dengan baik. Skor tinggi disertai waktu pengerjaan yang efisien menunjukkan pemahaman yang mantap.",
  "recommendation": "Lanjut ke materi berikutnya atau coba kuis dengan tingkat kesulitan lebih tinggi.",
  "chart_data": {
    "correct": 4,
    "wrong": 1,
    "unanswered": 0
  },
  "submitted_at": "2026-05-04T15:34:05Z",
  "question_reviews": [
    {
      "question_id": 1,
      "question": "Apa peran utama klorofil dalam fotosintesis?",
      "options": ["Menyerap cahaya matahari", "Menghasilkan oksigen", "Menyimpan glukosa", "Memecah air"],
      "selected_option_index": 0,
      "correct_option_index": 0,
      "is_correct": true,
      "is_unanswered": false
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `quiz_id` | string | echoed back for client correlation |
| `score.score_percentage` | int | 0–100, rounded to nearest int |
| `score.correct_count` | int | 0 ≤ x ≤ total |
| `score.wrong_count` | int | 0 ≤ x ≤ total |
| `score.unanswered_count` | int | 0 ≤ x ≤ total |
| `score.total_questions` | int | matches generate-time count |
| `time_taken_seconds` | int | echoed from request |
| `understanding_level` | enum | `"high"` \| `"medium"` \| `"low"` (lowercase English code) |
| `insight` | string | Indonesian, 1–2 sentences |
| `recommendation` | string | Indonesian, 1–2 sentences, actionable |
| `chart_data` | object | numeric fields for direct chart consumption |
| `submitted_at` | string (ISO 8601) | UTC timestamp |
| `question_reviews[]` | QuestionReview[] | per-question breakdown (the question, its options, what the user picked, the correct index, and correctness flags) — powers the result-page "what you got right/wrong" view without re-fetching the quiz. Length equals `total_questions`. See §5.5 |

> **Frontend display tip**: map `understanding_level` to localized label using a lookup table:
> ```ts
> const LEVEL_LABEL: Record<UnderstandingLevel, { id: string; en: string }> = {
>   high:   { id: "Tinggi", en: "High" },
>   medium: { id: "Sedang", en: "Medium" },
>   low:    { id: "Rendah", en: "Low" }
> };
> ```

#### Invariants (must hold in every successful response)
1. `correct_count + wrong_count + unanswered_count === total_questions`
2. `score_percentage === round(correct_count / total_questions × 100)`
3. `chart_data.correct === score.correct_count`, same for wrong/unanswered
4. `total_questions` equals the number sent at generate time
5. `understanding_level` is one of the 3 enum values (never null, never empty string)

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `ANSWERS_LENGTH_MISMATCH` | `answers.length !== total_questions` | "Jumlah jawaban tidak sesuai dengan jumlah soal." |
| 400 | `INVALID_OPTION_INDEX` | option index out of range | "Pilihan jawaban tidak valid." |
| 400 | `INVALID_QUESTION_ID` | `question_id` not in quiz | "Soal tidak ditemukan dalam kuis." |
| 400 | `INVALID_TIME` | negative or > 7200 | "Waktu pengerjaan tidak valid." |
| 404 | `QUIZ_NOT_FOUND` | `quiz_id` doesn't exist | "Kuis tidak ditemukan atau sudah kedaluwarsa." |
| 422 | (FastAPI auto) | wrong types | (FastAPI default body) |
| 500 | `EVALUATION_FAILED` | evaluator/classifier raises | "Gagal menganalisis hasil kuis." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/submit \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
    "answers": [
      { "question_id": 1, "selected_option_index": 0 },
      { "question_id": 2, "selected_option_index": 2 },
      { "question_id": 3, "selected_option_index": 1 },
      { "question_id": 4, "selected_option_index": null },
      { "question_id": 5, "selected_option_index": 3 }
    ],
    "time_taken_seconds": 245
  }'
```

---

### 4.6 Regenerate quiz

```
POST /quiz/regenerate
```

Generates a **fresh** quiz from the *same source material* as a previously
generated quiz, reusing the same `quiz_id`. Powers the "Asah Lagi" button on the
result page — the user gets a new set of questions on the material they just
studied, without re-pasting it.

#### Request body

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "difficulty": "medium"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `quiz_id` | string | yes | must reference a quiz whose source material is still retrievable (in-memory cache or persisted) |
| `difficulty` | string | no | `"easy"` \| `"medium"` \| `"hard"`; defaults to the previous quiz's difficulty, then adaptive (§4.10) |

#### Response · 200 OK

Same shape as §4.2 `/quiz/generate` response, with the **same `quiz_id`** and new
questions. Optional `X-Device-Id` header is honoured for adaptive difficulty.

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 404 | `QUIZ_NOT_FOUND` | the `quiz_id` (or its source material) is no longer available | "Materi sumber tidak ditemukan. Mulai ulang dari halaman utama." |
| 500 | `QUIZ_GENERATION_FAILED` | generator failure | "Gagal menghasilkan kuis. Silakan coba lagi." |

#### Example

```bash
curl -X POST http://localhost:8000/quiz/regenerate \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: 7b1f...c2" \
  -d '{"quiz_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

---

### 4.7 Daily challenge

```
GET /quiz/daily-challenge
```

Returns today's daily challenge quiz. The quiz id is `daily-YYYY-MM-DD` and the
source material is deterministically selected from a curated set
(`MD5(date) % len(materials)`), so everyone gets the same daily quiz and it is
persisted (generated once per day, then served from storage). Completing a daily
quiz grants a one-time **+50 XP** bonus (see §4.8 `daily_bonus_earned`).

#### Query parameters

| Param | Type | Required | Notes |
|---|---|---|---|
| `difficulty` | string | no | `"easy"` \| `"medium"` \| `"hard"`; adaptive (§4.10) when omitted |

#### Response · 200 OK

Same shape as §4.2 `/quiz/generate` response, with `quiz_id` = `daily-YYYY-MM-DD`.
Optional `X-Device-Id` header is honoured for adaptive difficulty.

#### Example

```bash
curl http://localhost:8000/quiz/daily-challenge \
  -H "X-Device-Id: 7b1f...c2"
```

---

### 4.8 Record quiz attempt (gamification)

```
POST /gamification/record-attempt
```

Records a completed quiz for the calling device and returns the resulting XP /
level / streak changes plus any newly unlocked achievements. Call this once
after a successful `/quiz/submit`, with the same `quiz_id`, `score`, and
`understanding_level` from the submit response.

> **Identity**: all `/gamification/*` endpoints identify the user by an
> anonymous **`X-Device-Id`** header — a UUID the frontend generates once and
> keeps in `localStorage`. No login, no PII. See §3.

#### Request body

```json
{
  "quiz_id": "550e8400-e29b-41d4-a716-446655440000",
  "score": 80,
  "understanding_level": "high"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `quiz_id` | string | yes | 1–64 chars |
| `score` | int | yes | 0–100 |
| `understanding_level` | string | yes | 1–16 chars (`"high"` \| `"medium"` \| `"low"`) |

#### Response · 200 OK

```json
{
  "xp_earned": 105,
  "daily_bonus_earned": 0,
  "leveled_up": true,
  "new_level": 2,
  "stats": {
    "total_xp": 105,
    "level": 2,
    "xp_into_level": 5,
    "xp_for_next_level": 100,
    "current_streak": 1,
    "longest_streak": 1
  },
  "newly_unlocked": [
    {
      "code": "first_quiz",
      "label": "Langkah Pertama",
      "description": "Menyelesaikan kuis pertama.",
      "icon": "sparkles",
      "unlocked_at": "2026-05-26T10:59:21Z"
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `xp_earned` | int | XP from this attempt (score + completion + streak bonus) |
| `daily_bonus_earned` | int | `50` once per day if `quiz_id` starts with `daily-`, else `0` |
| `leveled_up` | bool | true if this attempt crossed a level threshold |
| `new_level` | int | level after applying this attempt |
| `stats` | StatsResponse | full post-attempt stats (see §4.9 / §5.7) |
| `newly_unlocked[]` | Badge[] | achievements unlocked by this attempt (often empty) |

#### Errors

| Status | `code` | Trigger | `detail` (Indonesian) |
|---|---|---|---|
| 400 | `DEVICE_ID_REQUIRED` | `X-Device-Id` header missing/blank | "Identitas perangkat tidak ditemukan. Muat ulang halaman." |
| 503 | `GAMIFICATION_UNAVAILABLE` | `DATABASE_URL` not configured | "Fitur progres belum aktif. Hubungi pengelola aplikasi." |

#### Example

```bash
curl -X POST http://localhost:8000/gamification/record-attempt \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: 7b1f...c2" \
  -d '{"quiz_id": "550e8400-...", "score": 80, "understanding_level": "high"}'
```

---

### 4.9 Stats, history, achievements (gamification)

All three require the `X-Device-Id` header and return `503 GAMIFICATION_UNAVAILABLE`
when the DB is not configured (so the core quiz flow keeps working without one).

```
GET /gamification/stats
```

Returns the device's current progress. Response (`StatsResponse`):

```json
{
  "total_xp": 480,
  "level": 4,
  "xp_into_level": 80,
  "xp_for_next_level": 250,
  "current_streak": 3,
  "longest_streak": 5
}
```

```
GET /gamification/history?limit=10
```

Returns recent attempts, newest first, plus a summary of the user's recent quiz history.
`limit` is clamped to 1–50 (default 10).

```json
{
  "summary": {
    "total_quizzes": 12,
    "average_score": 78,
    "total_xp": 1200,
    "best_score": 95,
    "worst_score": 45,
    "most_recent_topic": "Fotosintesis"
  },
  "items": [
    {
      "quiz_id": "550e8400-...",
      "score": 80,
      "understanding_level": "high",
      "xp_earned": 105,
      "completed_at": "2026-05-26T10:59:21Z",
      "topic": "Fotosintesis"
    }
  ]
}
```

```
GET /gamification/analytics
```

Returns analytics-ready aggregates and topic mastery for the device.

```json
{
  "quiz_count": 12,
  "average_score": 78,
  "total_xp": 1200,
  "score_trend": [
    { "date": "2026-05-20", "average_score": 71, "attempt_count": 2 },
    { "date": "2026-05-21", "average_score": 85, "attempt_count": 1 }
  ],
  "topic_mastery": [
    { "topic": "Fotosintesis", "average_score": 85, "attempt_count": 3 },
    { "topic": "Tata Surya", "average_score": 70, "attempt_count": 2 }
  ]
}
```

```
GET /gamification/achievements
```

Returns the full achievement catalogue with unlock state for this device (array
of `Badge` objects — `code`, `label`, `description`, `icon`, and `unlocked_at`
which is `null` while still locked).

---

### 4.10 Adaptive difficulty resolution

The generate / regenerate / daily-challenge endpoints resolve `difficulty` in
this order:

1. **Explicit** `difficulty` in the request → used as-is.
2. **Adaptive** — if `X-Device-Id` is present *and* `DATABASE_URL` is configured,
   the backend reads the device's level: `≤3 → easy`, `≤8 → medium`, else `hard`.
3. **Fallback** → `medium`.

`difficulty` maps to question count: `easy` = 3, `medium` = 5, `hard` = 7. The
resolved value is echoed back in the response's `difficulty` field.

---

## 5. Shared Data Models

Side-by-side TypeScript interfaces (frontend) and Pydantic models (backend). **These two columns must stay in sync.** Any change requires updating both.

### 5.1 `UnderstandingLevel` (enum)

```ts
// frontend/src/types/result.ts
export type UnderstandingLevel = "high" | "medium" | "low";
```

```python
# backend/app/schemas/result.py
from enum import Enum

class UnderstandingLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### 5.2 `Question`

```ts
// frontend/src/types/quiz.ts
export interface Question {
  id: number;
  question: string;
  options: [string, string, string, string]; // exactly 4
}
```

```python
# backend/app/schemas/quiz.py
from pydantic import BaseModel, Field, conlist

class Question(BaseModel):
    id: int = Field(..., ge=1)
    question: str = Field(..., min_length=1)
    options: conlist(str, min_length=4, max_length=4)
```

> Backend stores a separate `QuestionInternal` that adds `correct_option_index: int` — that field never leaves the backend.

### 5.3 `Answer`

```ts
// frontend/src/types/quiz.ts
export interface Answer {
  question_id: number;
  selected_option_index: number | null; // 0-3 or null for unanswered
}
```

```python
# backend/app/schemas/quiz.py
from typing import Optional
from pydantic import BaseModel, Field

class Answer(BaseModel):
    question_id: int = Field(..., ge=1)
    selected_option_index: Optional[int] = Field(None, ge=0, le=3)
```

### 5.4 `QuizGenerateRequest` / `QuizGenerateResponse`

```ts
// frontend/src/types/quiz.ts
export type Difficulty = "easy" | "medium" | "hard";

export interface QuizGenerateRequest {
  material_text: string;
  difficulty?: Difficulty; // optional — adaptive when omitted
}

export interface QuizRegenerateRequest {
  quiz_id: string;
  difficulty?: Difficulty;
}

export interface QuizGenerateResponse {
  quiz_id: string;
  questions: Question[];
  total_questions: number;
  generated_at: string; // ISO 8601 UTC
  difficulty: Difficulty; // resolved value actually used
}
```

```python
# backend/app/schemas/quiz.py
from datetime import datetime
from typing import Optional

class QuizGenerateRequest(BaseModel):
    material_text: str = Field(..., min_length=100, max_length=20000)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")

class QuizRegenerateRequest(BaseModel):
    quiz_id: str
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")

class QuizGenerateResponse(BaseModel):
    quiz_id: str
    questions: list[Question]
    total_questions: int
    generated_at: datetime
    difficulty: str = Field(default="medium")
```

> `QuizGenerateFromUrlRequest` adds the same optional `difficulty` field to the
> `{ url }` body. The PDF endpoint takes `difficulty` as a query parameter.

### 5.5 `QuizSubmitRequest` / `QuizSubmitResponse`

```ts
// frontend/src/types/quiz.ts
export interface QuizSubmitRequest {
  quiz_id: string;
  answers: Answer[];
  time_taken_seconds: number;
}

export interface ScoreSummary {
  score_percentage: number;
  correct_count: number;
  wrong_count: number;
  unanswered_count: number;
  total_questions: number;
}

export interface ChartData {
  correct: number;
  wrong: number;
  unanswered: number;
}

export interface QuestionReview {
  question_id: number;
  question: string;
  options: string[];
  selected_option_index: number | null;
  correct_option_index: number;
  is_correct: boolean;
  is_unanswered: boolean;
}

export interface QuizSubmitResponse {
  quiz_id: string;
  score: ScoreSummary;
  time_taken_seconds: number;
  understanding_level: UnderstandingLevel;
  insight: string;
  recommendation: string;
  chart_data: ChartData;
  submitted_at: string; // ISO 8601 UTC
  question_reviews: QuestionReview[];
}
```

```python
# backend/app/schemas/result.py
class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: list[Answer]
    time_taken_seconds: int = Field(..., ge=0, le=7200)

class ScoreSummary(BaseModel):
    score_percentage: int = Field(..., ge=0, le=100)
    correct_count: int = Field(..., ge=0)
    wrong_count: int = Field(..., ge=0)
    unanswered_count: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=1)

class ChartData(BaseModel):
    correct: int
    wrong: int
    unanswered: int

class QuestionReview(BaseModel):
    question_id: int
    question: str
    options: list[str]
    selected_option_index: Optional[int]
    correct_option_index: int
    is_correct: bool
    is_unanswered: bool

class QuizSubmitResponse(BaseModel):
    quiz_id: str
    score: ScoreSummary
    time_taken_seconds: int
    understanding_level: UnderstandingLevel
    insight: str
    recommendation: str
    chart_data: ChartData
    submitted_at: datetime
    question_reviews: list[QuestionReview]
```

### 5.6 `ApiError` (error response shape)

```ts
// frontend/src/types/api.ts
export interface ApiError {
  detail: string;
  code?: string; // optional — present on backend-defined errors, absent on FastAPI auto-422
}
```

```python
# backend/app/schemas/error.py
class ApiError(BaseModel):
    detail: str
    code: Optional[str] = None
```

### 5.7 Gamification types

```ts
// frontend/src/types/gamification.ts
export interface RecordAttemptRequest {
  quiz_id: string;
  score: number;              // 0-100
  understanding_level: string; // "high" | "medium" | "low"
}

export interface StatsResponse {
  total_xp: number;
  level: number;
  xp_into_level: number;
  xp_for_next_level: number;
  current_streak: number;
  longest_streak: number;
}

export interface Badge {
  code: string;
  label: string;
  description: string;
  icon: string;
  unlocked_at: string | null; // ISO 8601 UTC, null while locked
}

export interface RecordAttemptResponse {
  xp_earned: number;
  daily_bonus_earned: number; // 0 unless a daily-* quiz, then 50
  leveled_up: boolean;
  new_level: number;
  stats: StatsResponse;
  newly_unlocked: Badge[];
}

export interface HistoryItem {
  quiz_id: string;
  score: number;
  understanding_level: string;
  xp_earned: number;
  completed_at: string; // ISO 8601 UTC
}
```

```python
# backend/app/schemas/gamification.py
class RecordAttemptRequest(BaseModel):
    quiz_id: str = Field(..., min_length=1, max_length=64)
    score: int = Field(..., ge=0, le=100)
    understanding_level: str = Field(..., min_length=1, max_length=16)

class StatsResponse(BaseModel):
    total_xp: int
    level: int
    xp_into_level: int
    xp_for_next_level: int
    current_streak: int
    longest_streak: int

class BadgeResponse(BaseModel):
    code: str
    label: str
    description: str
    icon: str
    unlocked_at: datetime | None = None

class RecordAttemptResponse(BaseModel):
    xp_earned: int
    daily_bonus_earned: int = 0
    leveled_up: bool
    new_level: int
    stats: StatsResponse
    newly_unlocked: list[BadgeResponse]

class HistoryItem(BaseModel):
    quiz_id: str
    score: int
    understanding_level: str
    xp_earned: int
    completed_at: datetime
```

> **XP / level model**: XP per attempt = `score` (0–100) + `20` completion bonus
> + `5 × current_streak` (capped at `50`). Level thresholds are
> `total_xp ≥ 50·L·(L+1)`. The streak increments on consecutive-day activity and
> resets after a missed day. This lives in `backend/app/services/xp_engine.py`.

---

## 6. Error Codes Reference

Centralized list of all error codes for frontend handling. Match the `code` field in error responses.

### Generic
- `INTERNAL_ERROR` (500): unexpected server error — show generic "Terjadi kesalahan. Silakan coba lagi."

### Material input (POST /quiz/generate)
- `MATERIAL_EMPTY` (400)
- `MATERIAL_TOO_SHORT` (400)
- `MATERIAL_TOO_LONG` (400)
- `QUIZ_GENERATION_FAILED` (500)

### Quiz submission (POST /quiz/submit)
- `QUIZ_NOT_FOUND` (404)
- `ANSWERS_LENGTH_MISMATCH` (400)
- `INVALID_QUESTION_ID` (400)
- `INVALID_OPTION_INDEX` (400)
- `INVALID_TIME` (400)
- `EVALUATION_FAILED` (500)

### Regenerate (POST /quiz/regenerate)
- `QUIZ_NOT_FOUND` (404) — source material no longer available
- `QUIZ_GENERATION_FAILED` (500)

### Gamification (POST /gamification/*, GET /gamification/*)
- `DEVICE_ID_REQUIRED` (400) — `X-Device-Id` header missing/blank
- `GAMIFICATION_UNAVAILABLE` (503) — `DATABASE_URL` not configured; core quiz flow still works

### Frontend handling pattern

```ts
// frontend/src/services/api.ts
async function postJson<TReq, TRes>(path: string, body: TReq): Promise<TRes> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err: ApiError = await res.json().catch(() => ({
      detail: "Tidak dapat terhubung ke server."
    }));
    throw new ApiException(err, res.status);
  }
  return res.json();
}
```

---

## 7. Validation Rules Summary

Quick reference for both sides to keep validation consistent.

### Material text
- Trim whitespace before validating
- Min length: **100 characters** (after trim)
- Max length: **20,000 characters**
- Empty string after trim → `MATERIAL_EMPTY`

### Quiz generation output
- Question count is driven by `difficulty`: **easy = 3, medium = 5, hard = 7**
- Every question has **exactly 4 options**
- Every question has **exactly 1 correct option index** stored server-side

### Submit input
- `answers.length` MUST equal `total_questions` from generate
- `selected_option_index`: integer 0–3 or `null` (no other types)
- `time_taken_seconds`: integer 0–7200
- `quiz_id`: must exist in server state (in-memory cache, with Neon persistence when `DATABASE_URL` is set — see §8)

### Submit output invariants
See §4.5 "Invariants" — all 5 must hold for every successful submit response.

---

## 8. State Management (MVP Implementation Note)

> This section documents the **expected internal behavior**, not part of the public contract. Backend implementers (Audry) should follow this approach unless explicitly changed.

### Quiz storage strategy (hybrid, v1.1)
- In-memory `OrderedDict` keyed by `quiz_id` → full quiz object (including `correct_option_index` per question), FIFO-evicted at 100 entries. This is the hot cache, read on `/quiz/submit` and `/quiz/regenerate`.
- When `DATABASE_URL` is set, `save_quiz` **also** upserts the quiz into the Neon `persistent_quizzes` table (`session.merge`), and `get_quiz` falls back to the DB on a cache miss (then re-warms the cache). This lets `/quiz/regenerate` and the daily challenge survive a Space restart.
- Graceful degradation: every DB call is wrapped in try/except — if the DB is unreachable, the app silently falls back to memory-only and keeps serving.
- Persisted columns: `quiz_id`, `source_material`, `questions_json`, `difficulty`, `created_at`.

### Why not return correct_answer to the client?
1. **Security**: any user can open browser DevTools → Network tab → see correct answers before submitting
2. **Cleaner contract**: submit endpoint doesn't need to be told the correct answers (server already knows)
3. **Future-proof**: enables features like "view explanation after submit" without contract changes

### Further work
- Add `expires_at` → auto-evict persisted quizzes older than 24h (table currently keeps rows indefinitely)
- Optional: add `GET /quiz/{quiz_id}` to retrieve a previously generated quiz

---

## 9. CORS

Frontend dev server (Vite default `http://localhost:5173`) is on a different origin from the backend (`http://localhost:8000`). Backend MUST enable CORS for development:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Device-Id"],
)
```

> **`X-Device-Id` must be in `allow_headers`** — gamification requests send it, and
> the browser's CORS preflight rejects the request otherwise (curl bypasses
> preflight, so this surfaces only in the browser).

For demo deployment, the deployed frontend origin is supplied via the
`CORS_ALLOWED_ORIGINS` env/secret (comma-separated) and appended to
`allow_origins`.

---

## 10. Implementation Notes

### Backend (FastAPI suggested)

**Custom exception with `code`:**
```python
# backend/app/utils/errors.py
from fastapi import HTTPException

class ApiException(HTTPException):
    def __init__(self, status_code: int, code: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
```

**Wire it up in main.py:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ApiException)
async def api_exception_handler(request: Request, exc: ApiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )
```

**Raise in services:**
```python
raise ApiException(
    status_code=400,
    code="MATERIAL_TOO_SHORT",
    detail="Materi terlalu pendek. Minimal 100 karakter."
)
```

### Frontend (React + TypeScript suggested)

**Centralized API client:**
```ts
// frontend/src/services/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiException extends Error {
  constructor(
    public readonly error: ApiError,
    public readonly status: number,
  ) {
    super(error.detail);
  }
}

export async function generateQuiz(req: QuizGenerateRequest): Promise<QuizGenerateResponse> {
  return postJson("/quiz/generate", req);
}

export async function submitQuiz(req: QuizSubmitRequest): Promise<QuizSubmitResponse> {
  return postJson("/quiz/submit", req);
}
```

**Store API base URL via env:**
```bash
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000
```

---

## 11. Open Questions / Future Work

These are intentionally **out of scope for v1.0** but worth tracking:

- [x] ~~Should `total_questions` be configurable?~~ **Resolved (v1.1)**: driven by the `difficulty` param (easy=3 / medium=5 / hard=7), chosen explicitly or adaptively.
- [ ] Should we support multi-language insight/recommendation via `?lang=en`? Currently Indonesian-only.
- [x] ~~Should generated quizzes persist across server restarts?~~ **Resolved (v1.1)**: hybrid in-memory + Neon persistence when `DATABASE_URL` is set (§8). Falls back to memory-only otherwise.
- [ ] Should we add `GET /quiz/{quiz_id}` for resuming an in-progress quiz? Not needed for single-session demo.
- [ ] Should we add per-question explanation in submit response (`why_correct: string`)? Useful but not MVP.
- [ ] Rate limiting? Not needed for capstone scope.

---

## 12. Sign-off

This contract requires sign-off from all 4 team members before locking. Tick the box and add a date when you have reviewed AND agreed.

- [ ] **Audry** (Backend — Quiz Generator) — produces shapes in §4.2 response, §5.2 `Question`
- [ ] **Ariq** (Backend — Data & Analysis) — consumes §5.3 `Answer`, produces §4.5 `score`, `chart_data`
- [ ] **Desta** (Backend — Logic, Insight & Recommendation) — produces §4.5 `understanding_level`, `insight`, `recommendation`
- [ ] **Ravi** (Frontend) — consumes §4.2 and §4.5 responses, displays per `DESIGN.md`

After all four boxes are ticked, this document moves from "Draft v1.0" to "Locked v1.0". Any subsequent change requires a new minor version + changelog entry at the bottom of this file.

---

## Changelog

- **v1.1 (2026-05-26)** — Gamification + adaptive difficulty phase. Added optional
  `difficulty` param (and resolved-`difficulty` in responses) to all generate
  endpoints (§4.2–§4.4, §4.10); new `POST /quiz/regenerate` (§4.6) and
  `GET /quiz/daily-challenge` (§4.7); `question_reviews[]` in the submit response
  (§4.5, §5.5); four `/gamification/*` endpoints with anonymous `X-Device-Id`
  identity (§4.8–§4.9, §3); gamification shared types (§5.7); new error codes
  `DEVICE_ID_REQUIRED`, `GAMIFICATION_UNAVAILABLE` (§6); `X-Device-Id` added to CORS
  `allow_headers` (§9).
- **v1.0 (2026-05-04)** — Initial draft: 3 endpoints, error codes, shared types, validation rules, implementation notes. Awaiting team review.
