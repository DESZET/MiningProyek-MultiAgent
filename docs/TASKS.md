# TASKS.md

## Project
**Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data**
**Brand**: Asahlagi — _Asah lagi sampai paham._
**Team ID**: TP-G005

## Objective
Membangun aplikasi web sederhana yang dapat:
- menerima materi pembelajaran dalam bentuk teks,
- menghasilkan kuis otomatis,
- memfasilitasi pengerjaan kuis,
- menganalisis hasil,
- menampilkan tingkat pemahaman, insight, rekomendasi, dan grafik sederhana.

---

## 📸 Status Snapshot (per 2026-05-06)

Sebelum Week 1 coding dimulai, **semua scaffolding sudah selesai**. Setiap orang punya file yang siap diisi (placeholder implementations sudah jalan end-to-end, tinggal direplace dengan logic proper).

### ✅ Sudah selesai
- Repo + GitHub setup (https://github.com/ravi-arnan/TempaCapstoneProject)
- Dokumentasi planning lengkap: `CLAUDE.md`, `PRD.md`, `README.md`, `DESIGN.md`, `API.md`, `ARCHITECTURE.md`, `BRAND.md`, `ML.md`
- Frontend scaffolding (Vite + React + TS + Tailwind): pages, components, hooks, types, API client, i18n labels, theme system (light/dark)
- Backend scaffolding (FastAPI): main app, CORS + exception handler, routes, schemas (public + internal), in-memory storage, submit coordinator
- ML layer scaffolding: `backend/ml/{generator,classifier}/` dengan inference stubs + training script templates
- Brand identity: nama "Asahlagi", logo SVG (V1 slash-crossbar), favicon
- Rule-based fallback implementations (jadi safety net kalau ML/DL fail):
  - `quiz_generator.py` — fallback rule-based fill-in-the-blank
  - `quiz_evaluator.py` — pure scoring logic (NO ML — tetap rule-based, ini benar)
  - `understanding_classifier.py` — fallback rule-based threshold
- Base templates di `insight_engine.py` dan `recommendation_engine.py` dari BRAND.md §7.6-7.7

### ⏳ Yang harus dikerjakan tim — UPDATED untuk scope ML/DL
- **Audry**: implement `ml/generator/inference.py` + train fine-tuned IndoT5 di Colab + push ke HF Hub
- **Ariq**: refine `quiz_evaluator.py` (tetap rule-based, NO ML wajib — bonus opsi: TF-IDF analytics)
- **Desta**: implement `ml/classifier/{data_generation,train,inference}.py` + 3 modules (classifier wrapper, insight, recommendation)
- **Ravi**: polish frontend, terutama loading state untuk 15-40s wait saat generate quiz

---

## Team Members

| Nama | ID | Role |
|---|---|---|
| Audry Nabila Anastasya | AIC161BX0012 | Backend - Quiz Generator |
| Ariq Marwan Permana | AIC012B6Y0004 | Backend - Data & Analisis |
| Desta Anandhika Rajendra Maheswara | AIC183B6Y0048 | Backend - Logic, Insight & Recommendation |
| Ravi Arnan Irianto | AIC014B6Y0008 | Frontend - React & TypeScript |

---

## Working Rules

- **Pendekatan sequential**: Audry → Ariq → Desta. Tiap minggu ada 1 "main owner" yang fokus implementasi inti, sementara yang lain support (review, polish, polishing dokumen demo, dll). Tidak ada anggota yang idle.
- Fokus pada MVP, jangan menambah fitur di luar scope tanpa diskusi tim.
- Prioritaskan flow end-to-end yang berjalan.
- Semua task besar harus punya owner yang jelas.
- **Branch per fitur** dengan prefix owner: `feat/audry-quiz-generator`, `feat/ariq-evaluator`, dll.
- **PR review wajib** dari minimal 1 anggota lain sebelum merge ke `main`.
- **Kalau ubah `backend/app/schemas/internal.py`** (`QuizInternal`, `EvaluationResult`, dll) — HARUS sync ke tim dulu. Itu integration boundary.
- Sync meeting **minimal 1× per minggu** + daily progress update di chat saat sedang giliran main owner.
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`.

---

## MVP Deliverables (status di-update tiap minggu)

- [x] Input materi teks (frontend skeleton sudah jalan)
- [x] Quiz generator sederhana (placeholder; **Audry refine**)
- [x] Halaman pengerjaan kuis (frontend skeleton sudah jalan)
- [x] Penghitungan skor dan waktu (placeholder; **Ariq refine**)
- [x] Klasifikasi tingkat pemahaman (placeholder; **Desta refine**)
- [x] Insight otomatis (base template; **Desta refine** dengan sub-conditions)
- [x] Rekomendasi belajar (base template; **Desta refine** dengan sub-conditions)
- [x] Grafik hasil sederhana (frontend ScoreChart sudah jalan)
- [x] Integrasi frontend dan backend (sudah verified end-to-end)
- [ ] Demo siap presentasi (Week 5)

> Catatan: checkmark `[x]` di atas berarti **sudah berfungsi end-to-end di level placeholder**, bukan berarti final. Tim refine selama Week 2-4.

---

## 🛤️ Critical Path (UPDATED untuk ML/DL scope)

```
Week 1          Week 2              Week 3                Week 4              Week 5
─────────       ─────────           ─────────             ─────────           ─────────
Setup &         AUDRY ⭐ (DL)        ARIQ ⭐ + DESTA ⭐ (ML) DESTA ⭐ (Templates) Polish + Demo
ML prep         IndoT5 fine-tune    Evaluator + sklearn   Insight + recommend
                in Colab            Random Forest         sub-conditions
                push to HF Hub      train .pkl artifact
                + integration       + integration
```

### Critical path slip rules
- Audry's DL training (Week 2) is the **highest-risk slot** — kalau Colab issue / quality kurang, fallback ke pretrained tanpa fine-tune (still DL, just lower quality).
- Desta's ML training (Week 3) is **lower-risk** — sklearn cepat, synthetic data full controlled.
- Frontend (Ravi) tidak di critical path tapi loading state UX harus siap di Week 2 ketika DL pertama kali muncul.

**Aturan critical path**:
- Kalau **main owner minggu ini meleset**, downstream geser. Kabari secepatnya kalau bakal late.
- Buffer ada di Week 5. Jangan jadwalkan coding berat di Week 5.
- Frontend (Ravi) work paralel di semua minggu (polish, integration testing) tapi tidak di critical path.

---

## Milestone Mingguan

### Minggu 1 — Setup & Sync + ML Prep (semua orang aktif)

**Goal**: semua orang setup environment, baca dokumentasi, sepakat soal `EvaluationResult` shape, dan ML setup ready.

| Owner | Task |
|---|---|
| All | Clone repo, install dependencies (frontend + backend + ml), run dev server lokal |
| All | Baca `API.md` (HTTP contract) + `ARCHITECTURE.md` §5b-§6 + `ML.md` (ML strategy) |
| All | Baca section spesifik masing-masing di `BRAND.md` §7 (copy library) |
| All | **Sign-off**: tick checklist di `API.md` §12, `ARCHITECTURE.md` §14, `BRAND.md` §11, `ML.md` §9 |
| All | **Lock `EvaluationResult` shape** — kalau ada usulan perubahan, raise di sync meeting Week 1 |
| **Audry** | Daftar akun **Hugging Face** + generate access token. Test login dari Colab. Familiarize dengan Transformers quickstart. Siapkan 2-3 sampel materi (fotosintesis, fotografi, ekonomi mikro). |
| Ariq | Sketch pseudocode evaluator + test cases. Decide pandas vs native Python. |
| **Desta** | Familiarize dengan sklearn Random Forest. Run `python -m ml.classifier.train` di local untuk test pipeline (placeholder akan dibuat). |
| Ravi | Polish frontend: **add loading state untuk 15-40s wait** saat generate quiz. Progress messages sesuai BRAND.md §7.3 ("Sedang menyusun pertanyaan..."). Mobile responsive. |

---

### Minggu 2 — Audry's Week ⭐ (DL training + integration)

**Goal**: Fine-tuned IndoT5 model published to HF Hub + integrated dengan backend.

| Owner | Task |
|---|---|
| **Audry** ⭐ | **Day 1-2**: Buka Colab notebook `train_quiz_generator.ipynb`. Run cells untuk download TyDiQA-id, set up training. |
| **Audry** ⭐ | **Day 3-4**: Run fine-tuning (3-5 epoch, ~1-2 jam runtime di Colab T4). Manual review 20-30 generated questions dari validation set. Tweak hyperparameter kalau quality kurang. |
| **Audry** ⭐ | **Day 5**: Push fine-tuned model ke HF Hub: `audry-asahlagi/indot5-quizgen-asahlagi`. Verify accessible publicly. |
| **Audry** ⭐ | **Day 6-7**: Implement `ml/generator/inference.py` — load from HF Hub, generate questions + distractors. Update `app/services/quiz_generator.py` thin wrapper. Add fallback ke rule-based. |
| **Audry** ⭐ | Daily progress update di chat (Hari ini training X, BLEU score Y, dll). |
| **Audry** ⭐ | Open PR `feat/audry-quiz-generator-dl` → review by 1+ anggota → merge. |
| Ariq | Review PR Audry. Sketch evaluator pseudocode. Mulai familiar dengan `EvaluationResult` shape. |
| Desta | Refine insight/recommendation TEMPLATES (text saja, belum coding). Brainstorm sub-conditions. Mulai test data_generation script di local. |
| Ravi | Polish frontend: **finalize loading state** untuk DL inference (15-40s). Progress messages "Sedang menyusun pertanyaan..." dengan animation. Test cold start (first request) vs warm. |

**Definition of Done untuk Week 2**: PR Audry merged. `POST /quiz/generate` return real DL-generated questions. Cold start ~30s, warm ~15-25s acceptable. Fallback to rule-based kalau ML fails.

---

### Minggu 3 — Ariq's Week ⭐ + Desta ML training

**Goal**: `quiz_evaluator.py` selesai + Desta's ML conv classifier trained & integrated.

| Owner | Task |
|---|---|
| **Ariq** ⭐ | Implementasi quiz_evaluator (rule-based, NO ML). Audry's `QuizInternal` shape sudah stable. Output: `EvaluationResult` per ARCHITECTURE.md §6.3. |
| **Ariq** | Eksplorasi pandas kalau perlu (per-question time, distribution analysis) — opsional MVP. |
| **Ariq** | Tests di `backend/tests/test_quiz_evaluator.py`. |
| **Ariq** | Open PR `feat/ariq-evaluator` → review → merge. |
| **Desta** | **Day 1-2**: Implement `ml/classifier/data_generation.py` — generate 10k synthetic samples + verify distribution balanced. |
| **Desta** | **Day 3**: Implement `ml/classifier/train.py` — sklearn Random Forest pipeline. Run lokal, verify accuracy ≥ 85%. Commit `.pkl` artifact. |
| **Desta** | **Day 4-5**: Implement `ml/classifier/inference.py` — load + predict. Update `app/services/understanding_classifier.py` wrapper. Add fallback. |
| **Desta** | Tests di `backend/tests/test_understanding_classifier.py`. |
| **Desta** | Open PR `feat/desta-classifier-ml` → review → merge. |
| Audry | Review PRs Ariq + Desta. Fix bugs di DL generator kalau ada laporan. |
| Ravi | Integration testing dengan real backend (DL + ML). Verify cold-warm-cold cycle. |

**Definition of Done Week 3**: PRs Ariq + Desta classifier merged. Full pipeline jalan: DL generates → Ariq evaluates → ML predicts level. End-to-end test pass.

---

### Minggu 4 — Desta's Week ⭐ Insight & Recommendation + integration

**Goal**: insight + recommendation engines selesai dengan sub-conditions + full flow end-to-end pass test.

| Owner | Task |
|---|---|
| **Desta** ⭐ | Implement sub-conditions di `insight_engine.py` — minimum 6-8 variasi based on level + score/time/unanswered patterns. |
| **Desta** ⭐ | Implement sub-conditions di `recommendation_engine.py` (paralel dengan insight). Pastikan brand callback "...lalu asah lagi." tetap muncul. |
| **Desta** | Tests untuk insight + recommendation engines. Pakai sample fixtures untuk cover semua sub-conditions. |
| **Desta** | Tweak ML classifier thresholds/synthetic data kalau testing E2E menunjukkan model behaviour aneh. |
| **Desta** | Open PR `feat/desta-insight-recommendation` → review → merge. |
| All | Integration testing: `pytest tests/test_routes.py::test_generate_then_submit_full_flow` HARUS pass. Test 5 skenario: high/medium/low + edge cases. |
| All | **Fallback verification**: simulate HF Hub down + simulate `classifier.pkl` missing — pastikan rule-based kick in tanpa break demo. |
| Ravi | Result page polish: tuning chart visualization, animation pada result reveal, mobile-responsive verification. |

**Definition of Done Week 4**: full E2E flow jalan dengan real DL + ML implementations, PR Desta merged. Fallback paths verified.

---

### Minggu 5 — Polish & Demo

**Goal**: aplikasi siap demo, bug bersih, presentasi siap.

| Owner | Task |
|---|---|
| All | **Bug bash session** (1-2 hari): cari & fix critical bugs |
| All | Siapkan 2-3 contoh materi demo dengan hasil berbeda (high/medium/low) |
| All | Siapkan slide presentasi + narasi |
| All | Rehearsal demo 1-2× |
| Ravi | Final UI polish, mobile responsive verification |
| Audry/Ariq/Desta | Address any final integration issues |

**Definition of Done Week 5**: demo berjalan tanpa critical error, presentasi siap.

---

## Task Breakdown Per Member

### 1. Audry — Backend Quiz Generator (Deep Learning)

**Main files**:
- `backend/ml/generator/inference.py` (DL inference logic — MAIN focus)
- `backend/ml/generator/notebooks/train_quiz_generator.ipynb` (Colab training)
- `backend/app/services/quiz_generator.py` (thin wrapper, calls ml/)

**Status saat ini**:
- Rule-based fallback sudah ada di `app/services/quiz_generator.py` (placeholder)
- ML layer scaffolding di `ml/generator/` dengan stub inference + training notebook template
- Yang harus dikerjakan: full DL pipeline

**Tasks**:

**Phase 1 — Setup (Week 1)**
- [ ] Daftar akun Hugging Face di huggingface.co (gratis)
- [ ] Generate access token (Settings → Access Tokens, "Write" permissions)
- [ ] Familiarize dengan Hugging Face Transformers (baca quickstart docs)
- [ ] Buka Colab notebook template di `ml/generator/notebooks/train_quiz_generator.ipynb`

**Phase 2 — Training (Week 2)**
- [ ] Run notebook step-by-step di Colab dengan T4 GPU runtime
- [ ] Download TyDiQA-id dataset (auto via HF datasets)
- [ ] Filter Indonesian subset
- [ ] Fine-tune `Wikidepia/IndoT5-base` (3-5 epoch, ~1-2 jam Colab)
- [ ] Evaluasi: BLEU score + manual review 20-30 generated questions
- [ ] Push fine-tuned model ke HF Hub: `audry-asahlagi/indot5-quizgen-asahlagi`
- [ ] Verify model accessible publicly (cek URL)

**Phase 3 — Inference & Integration (Week 2)**
- [ ] Implement `ml/generator/inference.py`: load model dari HF Hub, generate questions
- [ ] Strategy multiple-choice options: extract distractors dari source material
- [ ] Update `app/services/quiz_generator.py` untuk panggil `ml/generator/inference.py`
- [ ] Implement try/except fallback ke rule-based kalau ML inference gagal
- [ ] Test di backend lokal (cold start lama, warm cepat)

**Phase 4 — Testing & Polish (Week 3)**
- [ ] Unit tests di `tests/test_quiz_generator.py` (minimum 5 cases)
- [ ] Test cases: normal text (Indonesian), too short, too long, model unavailable (fallback path)
- [ ] Dokumentasikan asumsi + hyperparameter di docstring + ML.md changelog
- [ ] Siapkan 3-5 dummy materi yang well-tested untuk demo

**Kontrak yang harus dijaga** (jangan diubah tanpa diskusi):
- `app/services/quiz_generator.py` input: `material_text: str` → output: `QuizInternal`
- `ml/generator/inference.py` exposes: `generate(material_text: str) -> list[QuestionInternal]`
- Errors: raise `ApiException(QUIZ_GENERATION_FAILED)` saat fail; fallback path tidak raise
- Setiap question: exactly 4 options + 1 correct_option_index 0-3

**Reference**:
- `ML.md` §3 (DL strategy lengkap)
- `API.md` §4.2 (HTTP layer)
- `ARCHITECTURE.md` §5b (ML layer), §6.1-6.2, §8 (data flow)
- `BRAND.md` §6 (voice & tone)
- HF Transformers docs: https://huggingface.co/docs/transformers
- TyDiQA dataset: https://huggingface.co/datasets/tydiqa

---

### 2. Ariq — Backend Data & Analisis

**Main file**: `backend/app/services/quiz_evaluator.py`

**Status saat ini**: Placeholder standard scoring sudah jalan. Output sesuai `EvaluationResult` shape termasuk `question_results: list[QuestionResult]`.

**Tasks**:
- [ ] Review placeholder code & tentukan extension yang dibutuhkan
- [ ] Decide: pakai pandas atau cukup native Python untuk MVP
- [ ] Implementasi/extend `quiz_evaluator.py` — score, counts, per-question detail
- [ ] (Opsional) Eksplorasi analitik tambahan: time-per-question distribution, pattern detection, dll
- [ ] Unit tests di `tests/test_quiz_evaluator.py`
- [ ] Pastikan invariants di API.md §4.3 selalu hold:
  - `correct_count + wrong_count + unanswered_count === total_questions`
  - `score_percentage === round(correct_count / total_questions × 100)`

**Kontrak yang harus dijaga**:
- Input: `QuizInternal`, `list[Answer]`, `time_taken_seconds: int`
- Output: `EvaluationResult` (`schemas/internal.py`)
- Errors: raise `ApiException`

> ⚠️ **PENTING**: `EvaluationResult` adalah handoff ke 3 modul Desta. Kalau mau ubah shape-nya, sync ke Desta dulu.

**Reference**:
- `API.md` §4.3, §5.5 (HTTP & ScoreSummary)
- `ARCHITECTURE.md` §6.3, §9 (data flow + signatures)

---

### 3. Desta — Backend Logic, Insight & Recommendation (Conventional ML + Templates)

**Main files**:
- `backend/ml/classifier/data_generation.py` — synthetic dataset (NEW, ML)
- `backend/ml/classifier/train.py` — sklearn training (NEW, ML)
- `backend/ml/classifier/inference.py` — load + predict (NEW, ML)
- `backend/app/services/understanding_classifier.py` — thin wrapper, calls ml/
- `backend/app/services/insight_engine.py` (templates)
- `backend/app/services/recommendation_engine.py` (templates)

**Status saat ini**:
- Rule-based fallback classifier ada di `app/services/understanding_classifier.py`
- ML layer scaffolding di `ml/classifier/` dengan stub data_generation/train/inference
- Insight engine: base templates per level (BRAND.md §7.6) sudah ada
- Recommendation engine: base templates per level (BRAND.md §7.7) sudah ada — termasuk brand callback "...lalu asah lagi."

**Tasks**:

**Phase 1 — ML Conv Classifier (Week 3)**
- [ ] Implement `ml/classifier/data_generation.py`:
  - [ ] Generate 10,000 synthetic samples
  - [ ] Features: score_percentage, time_taken_seconds, wrong_count, unanswered_count
  - [ ] Labels: high/medium/low dengan rule-based + 5% noise injection
  - [ ] Verify distribution roughly balanced (~33% each class)
- [ ] Implement `ml/classifier/train.py`:
  - [ ] Load synthetic data
  - [ ] Train/test split 80/20
  - [ ] Fit `RandomForestClassifier(n_estimators=100, max_depth=10)`
  - [ ] Print accuracy + classification report + feature importances
  - [ ] Save model: `joblib.dump(model, "artifacts/classifier.pkl")`
  - [ ] Target: ≥ 85% test accuracy (lebih tinggi 95% expected, tapi noise akan cap)
- [ ] Implement `ml/classifier/inference.py`:
  - [ ] Load `.pkl` at module import
  - [ ] `predict(features: list[float]) -> str` returning level
  - [ ] Try/except fallback ke rule-based
- [ ] Run `python -m ml.classifier.train` lokal, verify `.pkl` artifact created
- [ ] Update `app/services/understanding_classifier.py` untuk call ml/classifier
- [ ] Commit `.pkl` artifact (kecil, ~1-5MB)

**Phase 2 — Insight & Recommendation Refinement (Week 4)**
- [ ] Implement sub-conditions di insight_engine:
  - [ ] High score + fast time → "kamu paham dan cepat"
  - [ ] High score + slow time → "kamu paham tapi mungkin masih ragu"
  - [ ] Medium + many unanswered → "kamu skip beberapa soal"
  - [ ] Low + all answered → "kamu coba semua tapi banyak salah"
  - [ ] dll (minimal 6-8 variasi total)
- [ ] Implement sub-conditions di recommendation_engine (paralel dengan insight)
- [ ] Pastikan voice consistency (BRAND.md §6): "kamu" not "Anda", honest, calm, no patronizing
- [ ] Pastikan brand callback "asah lagi" tetap muncul di recommendation low/medium

**Phase 3 — Testing (Week 4)**
- [ ] Unit tests di `tests/test_understanding_classifier.py` (test ML wrapper + fallback)
- [ ] Unit tests di `tests/test_insight_engine.py` (cover sub-conditions)
- [ ] Unit tests di `tests/test_recommendation_engine.py` (idem)
- [ ] Pakai `sample_eval_result` fixture di `tests/conftest.py`

**Kontrak yang harus dijaga**:
- `ml/classifier/inference.py` exposes: `predict(features: list[float]) -> str` returning "high"|"medium"|"low"
- `app/services/understanding_classifier.py` input: `EvaluationResult`. Output: `UnderstandingLevel`
- Insight & Recommendation input: `UnderstandingLevel + EvaluationResult`. Output: `str` (Indonesian, 1-2 sentences)

**Reference**:
- `ML.md` §4 (ML conv strategy lengkap)
- `PRD.md` §15 (rule starting point untuk synthetic labeling)
- `BRAND.md` §6 (voice rules)
- `BRAND.md` §7.6-7.7 (base templates)
- `ARCHITECTURE.md` §5b (ML layer), §6.3, §9
- sklearn docs: https://scikit-learn.org/stable/modules/ensemble.html#random-forests

---

### 4. Ravi — Frontend React & TypeScript

**Main folder**: `frontend/src/`

**Status saat ini**: Full skeleton sudah jalan end-to-end. Pages, components, hooks, API client, theme system, i18n labels — semua sudah scaffolded.

**Tasks**:
- [ ] Polish loading states (saat generate quiz + submit)
- [ ] Polish error display (sekarang inline; pertimbangkan toast notification)
- [ ] Quiz page: tambah progress indicator ("3 dari 5 terjawab")
- [ ] Quiz page: sticky submit button
- [ ] Result page: animation pada reveal (opsional, P2-P3)
- [ ] Mobile responsive verification (test di chrome devtools mobile mode)
- [ ] Edge cases: backend offline, very long material, very long question text
- [ ] (Opsional) Frontend snapshot/component tests
- [ ] Final UI polish untuk demo

**Sudah selesai (tinggal di-verify)**:
- Pages: `HomePage`, `QuizPage`, `ResultPage` — full routing & state passing
- Components: `Layout`, `Logo`, `ThemeToggle`, `MaterialInputForm`, `QuizQuestionCard`, `QuizTimer`, `ResultSummary`, `UnderstandingBadge`, `InsightCard`, `RecommendationCard`, `ScoreChart`
- Hooks: `useTheme`, `useQuiz`, `useTimer`
- API client: `services/api.ts` (generateQuiz, submitQuiz, checkHealth)
- i18n: `utils/i18n.ts` lengkap dengan copy dari BRAND.md §7

**Reference**:
- `BRAND.md` §7 (copy library)
- `DESIGN.md` (visual tokens)
- `frontend/README.md` (setup & structure)

---

## 🆕 Fitur Tambahan — Post-MVP (assigned 2026-06-06)

Batch fitur baru setelah MVP jalan. Detail rationale + effort ada di `ROADMAP.md` §4.5-4.7.

**Keputusan pembagian**:
- Tiap teman **bangun frontend fitur-nya end-to-end**; **Ravi review + polish** (styling per `DESIGN.md`, animasi, responsive, dark mode, i18n, integrasi).
- **Login pakai Google Identity Services (GIS) langsung** — bukan auth custom, bukan Supabase. ⚠️ Ini scope expansion dari `CLAUDE.md` (auth Out of Scope), disepakati sebagai post-MVP. GIS gratis & nol layanan eksternal baru.
- **Ariq tidak ambil fitur baru** — dia kerjakan track task roadmap lama yang belum jalan (Data & Quality).

### Pembagian

| Fitur | Owner | Polish/Review | Ref |
|---|---|---|---|
| Landing page (jelaskan fitur) | **Audry** | Ravi | ROADMAP §4.5 |
| Step-by-step tour (onboarding) | **Desta** | Ravi | ROADMAP §4.6 |
| Login — OAuth Google | **Ravi** (full) | Ariq (data layer) | ROADMAP §4.7 |
| Track Data & Quality (#3.2 + #3.4 + #6.2) | **Ariq** | Ravi | ROADMAP §3.2, §3.4, §6.2 |

---

### Audry — Landing Page

Halaman publik sebelum app yang menjelaskan fitur & value prop. App pindah ke `/app` (atau `/mulai`), `/` jadi landing.

**Tasks**:
- [ ] Routing: pindahkan app saat ini ke `/app`, buat route `/` baru untuk landing
- [ ] Hero: judul + tagline ("Asah lagi sampai paham") + CTA "Coba sekarang"
- [ ] Feature grid (Lucide icons): input multi-source (teks/URL/PDF), kuis satu-per-satu, analisis tingkat pemahaman, insight + rekomendasi, gamifikasi XP/streak, mastery per-topik
- [ ] Section "Cara kerja" 3 langkah (paste materi → kerjakan kuis → lihat analisis)
- [ ] Pakai tokens `DESIGN.md`, suara `BRAND.md`, hindari template generic (anti-template policy)
- [ ] Dark/light mode + responsive (320/768/1024/1440)
- [ ] PR `feat/audry-landing-page` → review Ravi → merge

**Kontrak**: jangan ubah flow app yang sudah ada; cuma tambah route `/` + redirect. CTA arahkan ke `/app`.

---

### Desta — Step-by-step Tour (Onboarding)

Guided tour saat kunjungan pertama, highlight elemen kunci satu per satu. Desta pegang karena copy-nya harus konsisten voice (domain dia).

**Tasks**:
- [ ] Pilih library: **driver.js** (ringan, rekomendasi) atau `react-joyride`
- [ ] Definisikan langkah: input materi → tombol generate → timer → navigasi soal (J/K, 1-4) → halaman hasil (skor/level/insight/rekomendasi/chart)
- [ ] Trigger first-visit (flag localStorage) + tombol "?" di nav untuk ulang
- [ ] Tulis copy tiap langkah konsisten `BRAND.md` (suara "kamu", calm, no patronizing)
- [ ] Respect `prefers-reduced-motion`
- [ ] PR `feat/desta-onboarding-tour` → review Ravi → merge

**Kontrak**: tour tidak boleh blok interaksi normal; harus bisa di-skip kapan saja. Selector elemen jangan rapuh (pakai `data-tour="..."` attribute, koordinasi dengan Ravi).

---

### Ravi — Login (OAuth Google) + Polish semua fitur

Ravi pegang login full (frontend + backend tipis) karena OAuth mayoritas frontend + verify token.

**Tasks login** (Google Identity Services langsung):
- [ ] Setup Google OAuth Client ID (Google Cloud Console) — Web application
- [ ] Frontend: `@react-oauth/google`, tombol "Masuk dengan Google", avatar + menu di nav, state guest vs logged-in
- [ ] Backend tipis: verify Google ID token di FastAPI (`google-auth`), tabel `user` minimal di Postgres (`DATABASE_URL` sudah ada)
- [ ] Link quiz attempts ke `user_id` (Ariq review bagian data layer / schema)
- [ ] **Guest mode tetap jalan** — app bisa dipakai tanpa login supaya demo nggak terblok
- [ ] PR `feat/ravi-login-oauth` → review Ariq → merge

**Tasks polish** (untuk fitur teman):
- [ ] Polish landing page Audry (styling, animasi, responsive, dark mode)
- [ ] Polish tour Desta (transisi, reduced-motion, mobile)
- [ ] Sediakan `data-tour="..."` attributes di komponen yang relevan untuk Desta

---

### Ariq — Track Data & Quality (task roadmap lama)

Ariq tidak ambil fitur baru; mengerjakan beberapa task roadmap yang belum jalan, sesuai domain Data & Analisis (owner `quiz_evaluator.py`).

**#3.2 Material quality pre-check**:
- [x] Skor "quizability" materi (word/sentence count, alpha ratio, junk/brand pattern density — mirror filter di `quiz_generator.py`)
- [x] Kalau jelek → warning + saran sebelum loading generate (hemat 15 detik user)

**#3.4 Rate limiting backend**:
- [x] Per-IP throttle `/quiz/generate*` (3 req/menit) pakai `slowapi` middleware

**#6.2 More question types**:
- [x] True/False + isian singkat (string matching)
- [x] Refactor `quiz_evaluator.py` untuk handle variant tipe soal (domain dia)
- [x] Koordinasi UI dengan Ravi (rendering tipe soal baru)

- [ ] PR per task atau gabung `feat/ariq-data-quality` → review Ravi → merge

**Kontrak**: kalau #6.2 ubah shape `QuizInternal`/`EvaluationResult`, **sync ke tim dulu** (integration boundary).

---

## Shared Tasks (semua minggu)

### Repository & Collaboration
- [x] Branch strategy (feat/<owner>-<topic>)
- [x] Naming convention (Conventional Commits)
- [x] Struktur folder final (sudah scaffolded)
- [ ] Issue/task tracking system (GitHub Issues atau Notion atau yang tim setuju)
- [ ] Review PR internal — tiap minggu

### Testing
- [x] Test scenario utama (sudah ada di `tests/test_routes.py`)
- [ ] Uji input kosong (sudah ada test, tinggal cover di owner module)
- [ ] Uji materi sangat pendek (idem)
- [ ] Uji generate quiz normal (dilakukan saat owner refine modulnya)
- [ ] Uji submit dengan jawaban lengkap
- [ ] Uji submit dengan jawaban sebagian
- [ ] Uji hasil kategori tinggi/sedang/rendah
- [ ] Uji integrasi frontend-backend (Week 4-5)

### Demo Preparation (Week 5)
- [ ] Menyiapkan 2–3 contoh materi demo
- [ ] Menyiapkan skenario demo dengan hasil berbeda
- [ ] Menyiapkan screenshot/video jika diperlukan
- [ ] Menyiapkan narasi presentasi
- [ ] Rehearsal

---

## Suggested Branch Naming

Convention: `<type>/<owner>-<topic>` atau `<type>/<topic>` untuk shared tasks.

- `feat/audry-quiz-generator` — Audry's main implementation
- `feat/ariq-evaluator` — Ariq's main implementation
- `feat/desta-classifier-insight-recommendation` — Desta's modules (atau pisah jadi 3 PR kalau prefer)
- `feat/ravi-frontend-polish` — Ravi's polish work
- `feat/audry-landing-page` — Landing page (post-MVP)
- `feat/desta-onboarding-tour` — Step-by-step tour (post-MVP)
- `feat/ravi-login-oauth` — Login OAuth Google (post-MVP)
- `feat/ariq-data-quality` — Track #3.2 + #3.4 + #6.2 (post-MVP)
- `fix/api-contract` — bug fix di shared schemas
- `docs/readme` — dokumentasi update
- `test/integration` — shared integration tests

---

## Suggested Definition of Done

Sebuah task dianggap selesai jika:
- [ ] Fiturnya berjalan secara end-to-end (bukan cuma unit-pass)
- [ ] Tidak break flow utama (run `pytest` + manual test browser)
- [ ] Sudah diuji minimal secara manual oleh owner
- [ ] Sudah ada minimal 2-3 unit tests untuk happy path + edge case
- [ ] Sudah commit ke branch yang benar dengan Conventional Commit message
- [ ] PR sudah di-review oleh minimal 1 anggota
- [ ] Tidak ada regression di test suite (`pytest` semua pass)

---

## Priority Order

### P1 — Wajib (Week 1-4 critical path)
- [ ] Quiz generator proper (Audry)
- [ ] Quiz evaluator proper (Ariq)
- [ ] Understanding classifier proper (Desta)
- [ ] Insight & recommendation dengan sub-conditions (Desta)
- [ ] Full E2E test pass

### P2 — Penting (Week 4-5 polish)
- [ ] Frontend loading states & error handling
- [ ] Mobile responsive
- [ ] Demo materials siap
- [ ] UI polish presentable untuk demo

### P3 — Opsional (kalau ada waktu)
- [ ] Pandas analytics di evaluator (Ariq)
- [ ] Animation pada result reveal
- [ ] Frontend component tests
- [ ] Penyimpanan hasil lokal (out of MVP per PRD §22)

---

## Risks to Watch

- **Critical path slip**: kalau Audry meleset, Ariq + Desta geser. Mitigasi: daily update saat giliran main owner.
- **API contract drift**: ubahan di `schemas/internal.py` tanpa sync = breakage. Mitigasi: review PR yang sentuh schema dengan extra hati-hati.
- **Integrasi terlambat**: integrasi muncul masalah di Week 4-5 → demo berisiko. Mitigasi: integration test (`test_generate_then_submit_full_flow`) HARUS pass setiap PR backend.
- **Quiz generator menghasilkan soal lemah**: rule-based ada batasan. Mitigasi: Audry siapkan dummy materi yang well-structured untuk demo.
- **Scope creep**: tambah fitur out-of-MVP. Mitigasi: P3 strict, semua addition perlu diskusi tim.

---

## Weekly Check-in Questions

Tiap minggu (sync meeting), jawab:

- Apa yang sudah selesai minggu ini?
- Apa blocker terbesar? (siapa bisa bantu?)
- Apakah ada perubahan scope?
- Apakah API contract / internal types masih konsisten?
- Apa target konkret minggu berikutnya?
- Apakah main owner minggu depan sudah unblocked?

---

## Cara Memulai (TL;DR)

1. **Clone repo**: `git clone https://github.com/ravi-arnan/TempaCapstoneProject.git`
2. **Baca docs critical**: `API.md` + `ARCHITECTURE.md` §6 + §10 + section spesifik kamu di TASKS.md
3. **Setup environment**: lihat `frontend/README.md` dan `backend/README.md`
4. **Sign-off internal types**: tick checklist di `API.md` §12, `ARCHITECTURE.md` §14, `BRAND.md` §11
5. **Tunggu giliran (sequential)**: lihat critical path. Saat bukan giliran kamu jadi main owner, kerjakan support tasks per "Milestone Mingguan" di atas.
6. **Daily update saat giliran main owner**: post progress di chat tim — apa yang done hari ini, blocker, ETA.

— Ravi
