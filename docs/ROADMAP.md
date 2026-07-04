# Roadmap — Asahlagi

**Status**: OPEN. Living document.
**Owner**: Ravi
**Created**: 2026-05-18
**Last updated**: 2026-06-14

---

## Context

Setelah batch polishing + UX delight (lihat git history 2026-05-18), state product sekarang:
- Frontend end-to-end working: text/URL/PDF input, one-question-at-a-time quiz, keyboard shortcuts, auto-save, score animation, confetti, "Asah Lagi" regenerate, per-question breakdown
- Backend: HF Space DL + rule-based mix fallback, all-mode reliability
- 43 backend tests + typecheck/build hijau
- Belum di-deploy publik, belum ada frontend tests

Dokumen ini menangkap arah pengembangan setelah batch hari ini, supaya keputusan bisa diambil saat sudah punya bandwidth tanpa harus brainstorming ulang.

---

## 1. Buat orang lain bisa coba (high ROI untuk capstone)

### 1.1 Deploy public URL (lihat `DEPLOY.md`)
- Frontend: Vercel (auto-deploy dari GitHub branch `main`)
- Backend: **Hugging Face Spaces (Docker)** — tanpa kartu kredit; config di `huggingface/backend/`. HTTPS otomatis (`*.hf.space`). Render disimpan sebagai alternatif (`render.yaml`).
- HF Space quiz-gen: sudah live di `https://raviarnan-asahlagi-quizgen.hf.space`
- Secrets di Space backend: `HF_SPACE_URL`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS` (point ke Vercel + origin Capacitor `https://localhost`)
- Frontend env: `VITE_API_BASE_URL` (point ke URL Space backend)

**Hasil**: link publik yang bisa di-share ke pembimbing/audience, sekaligus prasyarat untuk app Android (lihat #6.4 + `MOBILE.md`).

**Effort**: ~2-3 jam (setup awal + debugging CORS + healthcheck)

### 1.2 README screenshots + demo GIF
- Setelah deploy, screen-record 60-90 detik full flow
- Embed di README sebagai hero
- Tambah 3-4 screenshot (homepage, quiz, result) di section "Demo"

**Effort**: ~1 jam

---

## 2. Doc sync (cepat tapi penting)

Beberapa dokumen drift dari kode setelah banyak perubahan hari ini.

### 2.1 API.md
- Tambah section §4.X untuk `POST /quiz/regenerate`
- Tambah field `question_reviews[]` di `QuizSubmitResponse`
- Update field name di internal note: `source_material_excerpt` → `source_material`
- Update endpoint count: 5 → 6 endpoints

### 2.2 ARCHITECTURE.md
- §7.1 storage: update "excerpt" mention jadi full material
- §8 atau baru: dokumentasikan mix DL+rule-based strategy
- §5: tambah regenerate endpoint ke routing table
- Update quiz layout: scrolling list → single-question

### 2.3 BRAND.md
- §7.2 button labels: tambah `jumpToUnanswered`, `resultRetryLoading`
- §7.X loading: tambah `LOADING_PROGRESS_MESSAGES` series
- Catat brand-callback "asah lagi" sekarang juga dipakai di "Asah Lagi" button (tidak cuma di recommendation copy)

### 2.4 TASKS.md
- Centang/move tasks yang sudah selesai
- Refleksi: backend trio selesai, frontend delight layer selesai
- Tambah open backlog items dari ROADMAP.md ini

### 2.5 PRD.md
- Update scope: tambah multi-source input (PDF/URL) — sudah keluar dari "Out of Scope"
- Tambah feature "regenerate" (Asah Lagi) ke list MVP

**Effort total**: ~2 jam

---

## 3. Reliability / quality

### 3.1 Frontend tests (Vitest + RTL)
Saat ini 0 tests di frontend.

**Minimum viable suite**:
- Smoke: HomePage renders, sample button populates textarea
- QuizPage: keyboard 1-4 selects option, J/K navigates, Enter advances
- ResultPage: count-up animates to target value
- useQuizPersistence: save → load → clear

**Setup**:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Effort**: ~3-4 jam (setup + 6-8 tests)

### 3.2 Material quality pre-check
**Owner: Ariq** (assigned 2026-06-06)

Sebelum kirim ke generator, score "quizability" cepat:
- Word count, sentence count, alpha ratio
- Cek brand/junk pattern density (mirror filter di quiz_generator.py)
- Kalau jelek → kasih warning + saran ("Materi ini sebagian besar tabel/sitasi. Mungkin tidak menghasilkan kuis bagus.") sebelum loading 15 detik

**Effort**: ~2 jam (logic + UI warning component)

### 3.3 Smart distractors via embeddings
Saat ini distractor = random keyword similar length. Quality bisa naik signifikan dengan semantic similarity:
- Tambah `sentence-transformers` ke HF Space (model `indobenchmark/indobert-base-p1` atau `firqaaa/indo-sentence-bert-base`)
- Generator: encode correct answer + pool, pick 3 dengan similarity 0.5-0.8 (mirip tapi tidak identik)
- Alternative lite: pakai word frequency + POS tagging untuk filter kata kerja vs kata benda

**Effort**: ~1 hari (HF Space change + integration)

### 3.4 Rate limiting backend
**Owner: Ariq** (assigned 2026-06-06)

Per-IP throttle untuk `/quiz/generate*` (3 request/menit), pakai `slowapi` middleware.

**Effort**: ~30 menit

### 3.5 Answer-aware quiz generation (BARU 2026-06-14) — kualitas pertanyaan & opsi
**Owner: Audry (model) · Ravi (inference/integration)**

Masalah: "jawaban benar" diambil `max(keywords, key=len)` (kata terpanjang), tak
nyambung dengan pertanyaan → opsi ngawur ("Berapa jumlah planet?" → "mengitarinya").

- ✅ **Inference fix (live, HF Space `2aa8bc7`)** — `qg_core.py` (dibagi HF Space + local):
  pilih span jawaban dulu (utamakan angka/nama, penalti kata kerja) → highlight `<hl>` →
  guard konsistensi (berapa→angka, nama→nama diri, anti-superlatif, jawaban ∉ pertanyaan) →
  fallback **cloze** koheren → distraktor sekategori. Menutup ~70-75% kasus.
- ⏳ **Model v2 (answer-aware fine-tune)** — `notebooks/train_quiz_generator.ipynb` di-upgrade:
  latih dengan answer span ber-`<hl>` + token khusus (sebelumnya plain QG, makanya `<hl>`
  tak dipatuhi). Audry jalankan di Colab (~1.5-2 jam T4, fp32) → `push_to_hub` ke
  `raviarnan/indot5-quizgen-asahlagi` → Factory rebuild Space. Tanpa ubah kode Space.
- Sisa lever: distraktor via embeddings (#3.3) untuk semantik lebih halus.

**Effort**: inference fix DONE · v2 fine-tune ~0.5 hari (mostly Colab wall-time).

---

## 4. Feature additions (post-MVP)

### 4.1 History page
- LocalStorage based, no backend change
- List 10 kuis terakhir + skor + understanding level
- Click → re-display result page (kalau result masih cached) atau "Asah Lagi" dari kuis itu
- "Bandingkan dengan attempt sebelumnya" di result page (apa kemajuan?)

**Effort**: ~3-4 jam

### 4.2 Share result URL
- Copy URL dengan `?quiz_id=X` (atau short hash)
- Result page accept query param, fetch atau decode
- Optional: OG image generator untuk preview di Twitter/WA
- Optional: download result as image

**Effort**: ~3-5 jam (basic) sampai 1 hari (dengan OG)

> ✅ **Status 2026-06-17**: SELESAI (jalur **decode**, bukan fetch). Ringkasan
> hasil (skor/level/insight/rekomendasi/waktu) di-encode URL-safe base64 ke
> `/result?s=<token>` — **self-contained, tak bergantung backend** (store in-memory
> + Space tidur). ResultPage men-decode `?s=` jadi tampilan read-only: aksi
> owner (asah lagi, chat, breakdown, reward) disembunyikan, ganti banner + CTA
> "Buat kuismu sendiri". Tombol "Bagikan hasil" pakai `navigator.share` (mobile)
> atau clipboard. Per-soal **tidak** ikut di-share (hindari bocor isi kuis).
> OG image / download-as-image = opsional, di-skip. Tests: 6 lib + 3 ResultPage.

### 4.3 Quiz settings (pre-generate)
User pilih sebelum generate:
- Jumlah soal: 3 / 5 / 7 / 10
- Difficulty (kalau ada): mudah / sedang / sulit
- Toggle "Acak urutan opsi"

Implementasi: backend terima parameter, generator hormati.

**Effort**: ~2-3 jam

> ✅ **Status 2026-06-17**: SELESAI. `num_questions` (independen dari difficulty,
> clamp 3–10) + `shuffle_options` di `/quiz/generate` (body), `-from-url` (body),
> `-from-pdf` (query). Generator hormati count via DL+supplement; shuffle-off =
> opsi MC diurut alfabetis (anti "selalu A"). UI: `QuizSettingsControl` collapsible
> di HomePage. HF Space terima `num_questions`. Tests: 8 backend + 6 frontend.

### 4.4 Per-topic mastery tracking (BIG)
Selaras dengan judul capstone "Sistem Deteksi Tingkat Pemahaman".
- Tag tiap kuis dengan topik (auto-extract dari materi atau user input)
- Track score per topik over time
- Dashboard: "Pemahaman kamu di topik X naik dari 60% → 80%"
- Identifikasi weak spots: topik dengan skor rendah konsisten

**Effort**: ~2-3 hari

### 4.5 Landing page — jelaskan fitur aplikasi (BARU 2026-06-06)
**Owner: Audry · polish: Ravi**

Halaman publik sebelum masuk app, buat menjelaskan apa & kenapa aplikasi ini ada.
- App pindah ke route `/app` (atau `/mulai`); `/` jadi landing.
- Section: hero + value prop ("Asah lagi sampai paham"), feature grid (input multi-source teks/URL/PDF, kuis satu-per-satu, analisis tingkat pemahaman, insight + rekomendasi, gamifikasi XP/streak, mastery per-topik), "cara kerja" 3 langkah, CTA "Coba sekarang".
- Pakai Lucide icons, tokens dari `DESIGN.md`, suara dari `BRAND.md` (hindari template generic — lihat anti-template policy).
- Dark/light mode + responsive.

**Effort**: ~1 hari (build) + polish

### 4.6 Step-by-step tour — onboarding (BARU 2026-06-06)
**Owner: Desta · polish: Ravi**

Guided tour saat kunjungan pertama, highlight elemen kunci satu per satu.
- Sorot: input materi → tombol generate → timer → navigasi soal (J/K, 1-4) → halaman hasil (skor, level, insight, rekomendasi, chart).
- Library: **driver.js** (ringan, tanpa dep berat) atau `react-joyride`.
- Trigger: first visit (flag di localStorage) + tombol "?" di nav untuk ulang kapan saja.
- Copy tiap langkah konsisten `BRAND.md` (suara "kamu", calm, no patronizing) — Desta cocok karena sudah pegang voice insight/recommendation.
- Respect `prefers-reduced-motion`.

**Effort**: ~0.5-1 hari

> ✅ **Status 2026-06-17**: SELESAI. `driver.js` (lazy di chunk `/app`, landing
> tetap ringan). Tur first-visit (flag `asahlagi:onboarded:v1`) + tombol "?" di
> nav (navigate `/app?tour=1`). Sorot: source tabs → quiz settings → input materi
> → daily challenge, plus langkah pembuka/penutup yang menjelaskan alur (timer,
> navigasi, hasil). `prefers-reduced-motion` → `animate:false`. Copy suara "kamu"
> per BRAND.md. Target via `data-tour=` (step hilang di-skip otomatis). Tests:
> onboarding lib + hook (driver mount).

### 4.7 Login — Third-party OAuth (BARU 2026-06-06)
**Owner: Ravi (full) · review: Ariq (data layer)**

> ⚠️ **Scope expansion**: `CLAUDE.md` menandai auth sebagai *Out of Scope*. Disepakati masuk sebagai **post-MVP**, pakai jalur paling ringan: **Google Identity Services (GIS) langsung** — login "beneran" tanpa hand-roll password/JWT, dan tanpa layanan auth pihak ketiga (gratis, nol infrastruktur baru).

Ravi pegang full (frontend + backend tipis) karena OAuth mayoritas frontend + verify token, nyambung dengan kerja polishing-nya.
- Frontend: tombol "Masuk dengan Google" (`@react-oauth/google`), avatar + menu di nav, state guest vs logged-in.
- Backend tipis: verify Google ID token pakai public key Google (`google-auth`), tabel `user` minimal di Postgres (`DATABASE_URL` sudah ada), link quiz attempts ke `user_id`. Ariq review bagian data layer (domain-nya).
- Manfaat: history / mastery per-topik (#4.4) / gamifikasi (#6.3) bisa ter-link ke akun, bukan cuma localStorage.
- Tetap bisa dipakai tanpa login (guest mode) supaya demo nggak terblok.

**Effort**: ~1-1.5 hari

> ✅ **Status 2026-06-07**: SELESAI & live. GIS langsung, `/auth/google` verify via `google-auth`, kolom `users.google_sub/email/avatar_url` (migrasi 0003), guest mode utuh. Deployed: Neon migrated, HF Space `GOOGLE_CLIENT_ID` set, Vercel `VITE_GOOGLE_CLIENT_ID` set. (PR #6/#7/#8.)

---

### 4.8 User Hub & fitur akun — post-login (BARU 2026-06-07)
**Owner: Ravi (frontend) · review: Ariq (data layer untuk endpoint baru)**

Cluster fitur yang mengarah ke user, dibangun di atas login (#4.7). Status fondasi ditandai: 🟢 = endpoint/data sudah ada (mostly frontend), 🟡 = butuh backend baru.

- **a) Halaman Profil (hub)** 🟢 — identitas (avatar/nama/email) + ringkasan gamifikasi (level/XP/streak/total kuis) + grid badge + link ke Progress (#4.4). Konsumsi endpoint yang sudah ada (`/gamification/stats`, `/gamification/achievements`, `/gamification/analytics`). Guest → ajak login.
- **b) Halaman Settings** 🟢 — tema (light/dark), info akun, tombol Keluar. Opsi lanjut 🟡: edit nama tampilan (`PATCH /auth/me`), hapus akun & data (`DELETE` + cascade) — review Ariq.
- **c) Halaman Riwayat Kuis (History)** 🟢 — `GET /gamification/history` (items + summary) **sudah jalan**; tinggal UI. List: skor, level pemahaman, topik, XP, tanggal; klik → detail / "Asah Lagi". (Menggantikan rencana #4.1 yang localStorage — kini DB-backed + ter-link akun.)
- **d) Leaderboard** 🟡 — ranking by XP/level. **Desain privasi**: tampil display name (login) atau "Anonim" (guest), idealnya opt-in. Endpoint baru `GET /gamification/leaderboard` (top N). (GAMIFICATION.md dulu menandai ini "far future"; sekarang feasible karena sudah ada auth.)
- **e) Edit preferensi belajar** 🟡 — default jumlah soal, difficulty, acak opsi, topik favorit; disimpan per-user + di-wire ke `/quiz/generate`. Nyambung dengan #4.3 (Quiz settings).
- **f) Target/Goal mingguan** 🟡 — "X kuis minggu ini" + progress bar; booster retensi.
- **g) Simpan materi (bookmark)** 🟡 — simpan materi yang ditempel untuk diasah ulang nanti. Butuh tabel baru. Relevan untuk use-case belajar.
- **h) Badge/Pencapaian showcase** 🟢 — `/gamification/achievements` sudah ada (locked/unlocked); section di Profil atau halaman sendiri.
- **i) Kartu Tantangan Harian + streak** 🟢 — backend `daily-challenge` sudah ada; surface di Home/Profil + streak calendar.
- **j) Share hasil / Export progress** 🟡 — share URL hasil kuis (nyambung #4.2) + export ringkasan progres (gambar/PDF).

**Catatan scope** (CLAUDE.md: utamakan flow end-to-end, jangan semua sekaligus). Saran batching:
- **Batch 1 — "User Hub"** (cepat, mostly frontend): a) Profil + c) History + b) Settings (tema/logout) + h) badge. **~1-1.5 hari.**
- **Batch 2** (butuh backend, review Ariq): e) edit preferensi + d) leaderboard + f) goal + g) bookmark. **~2-3 hari.**
  - 🟡 **2026-06-17 — Batch 2-A SELESAI**: d) **leaderboard** + f) **weekly goal**. Tanpa migrasi (query atas tabel existing `users`/`user_stats`/`quiz_attempts`). Endpoint `GET /gamification/leaderboard` (top-N by XP, guest=Anonim, `you_rank`) + `GET /gamification/weekly-progress` (kuis 7 hari terakhir vs target default 5). Kartu di ProfilePage; degrade ke null kalau DB off. Tests: 6 backend (helper murni + kontrak 503) + 3 frontend.
  - ✅ **2026-06-17 — Batch 2-B SELESAI**: e) **edit preferensi** + g) **bookmark materi**. Tabel baru `user_preferences` + `material_bookmarks` (**migrasi `0005`, dijalankan manual oleh maintainer**). Endpoint `GET/PATCH /gamification/preferences`, `GET/POST/DELETE /gamification/bookmarks`. Prefs nge-seed default `QuizSettingsControl` di HomePage (nyambung §4.3) + editor di SettingsPage; `weekly_goal` dipakai weekly-progress (fallback aman ke default kalau tabel belum ada). Bookmark: tombol "Simpan materi" di MaterialInputForm + daftar di ProfilePage (Asah/Hapus). Semua di belakang fallback 503; tak ada yang sentuh prod sampai migrasi dijalankan. Tests: 6 backend + 5 frontend. **Seluruh §4.8 Batch 2 (d/e/f/g) SELESAI.**
- **Batch 3**: j) share/export + i) daily challenge surfacing. **~0.5-1 hari.**
- **Hati-hati / skip**: teman/social (berat, butuh relasi), notifikasi (butuh push infra → lihat #6.4).

---

### 4.9 Maskot Asahi v2 — konsistensi ekspresi (BARU 2026-06-12)
**Owner: Ravi (frontend)**

Maskot "Asahi" lama (AI-render penuh tiap ekspresi) drift wajahnya. Diselesaikan dengan
**puppet approach**: satu base **full-hair transparan**; ekspresi wajah via inpaint
**alis+mulut saja** (mata dilindungi → warna mata tetap), pose gesture via SeaArt "Maintain
Character Consistency". **Semua front-facing**, di-tone-match ke palet base, cutout bg via
rembg lokal. Recipe lengkap: `assets/mascot/inpaint-masks/README.md`. Rig:
`frontend/src/components/mascot/Asahi.tsx` (`mood`→image, `mid`=base, fallback ke base).

Status (branch `feat/mascot-asahi-v2`): ✅ **SELESAI 2026-06-12.** Set 7 ekspresi semua
front-facing, on-model, cutout + tone-match, tersimpan di `frontend/public/mascot/`:
- `mid` (base), `wave`, `think` (re-gen front-facing) — live & ter-wire.
- `high`, `low` (murung) — face-swap inpaint alis+mulut, mata emerald terjaga.
- `shocked`, `blush` — ekspresi ekstra (chat reaction); ter-wire di `AsahiMood`/`MOOD_SRC`.

Prompt preset semua ekspresi disimpan di `assets/mascot/prompts/*.txt` (commit `8b626ba`).

**Sisa (opsional, non-blok)**: surface `shocked`/`blush` ke UI nyata (mis. reaksi chat saat
user nyeleneh / digombal) — butuh sinyal mood dari backend chat. Mood `sleepy` di-skip
(eye-drift; opsi-A aman tapi diputuskan cukup di 7 ekspresi).

---

## 5. Polish layer 3 (kecil-kecil)

- ✅ **Skeleton loader** saat generate — DONE 2026-06-08 (PR #14; preview kartu soal, pesan progres tetap).
- ✅ **Drag-and-drop PDF** di homepage — DONE 2026-06-08 (PR #12; seluruh area input jadi drop target).
- ✅ **prefers-reduced-motion** audit menyeluruh — DONE 2026-06-08 (PR #15; reset global app-wide).
- **Toast notifications** untuk feedback non-fatal (network blip, retry success). *Catatan: trigger genuine sedikit → tunda sampai ada kebutuhan nyata (mis. share/export "tersalin").*
- **Empty state illustration** di homepage (text-only, Lucide-style icon). *Butuh verifikasi visual.*
- **Visual audit dark mode**: cek semua `bg-brand-button` apakah harusnya stay dark (button action) atau emerald (status indicator). PulsingDot fix tadi indikasi mungkin ada yang lain. *Butuh verifikasi visual.*

> Mobile-specific polish (responsif, touch, safe-area, native-feel) dipisah ke **#6.5**.

---

## 6. Bigger directions

### 6.1 Multi-language (Indonesian + English)
- i18n.ts arsitektur sudah siap (`{ id: {...}, en: {...} }`)
- Backend insight/recommendation perlu translation atau parallel template
- Toggle bahasa di nav

**Effort**: 2-3 hari

### 6.2 More question types
**Owner: Ariq** (assigned 2026-06-06)
- True/False ✅
- Isian singkat (free text, butuh string matching atau LLM grading) ✅
- Matching (cocok pernyataan A dengan jawaban B) ✅ (2026-06-17)

Backend evaluator + UI both perlu refactor untuk handle question type variant.

**Effort**: 3-5 hari

> ✅ **Status 2026-06-17 — matching SELESAI.** Lintas-layer: schema (`matching`
> di pattern; `left_items`/`right_items`/`correct_matches` internal, `matches` di
> Answer), generator rule-based bikin 1 soal matching (istilah↔pernyataan dengan
> kata kunci di-blank biar tak bocor) untuk kuis ≥5 soal + **di-inject ke jalur
> DL** (DL hanya hasilkan MC/cloze, jadi soal terakhir diganti matching). Evaluator
> **partial credit**: tiap pasangan benar nyumbang fraksi ke `score_percentage`,
> tapi `correct_count` hanya hitung yang full-benar (fitur classifier tetap int).
> UI: `MatchingField` tap-to-pair (aksesibel, mobile-friendly), QuestionPills &
> progress type-aware (sekalian benerin short_answer), review per-pasangan di
> QuestionBreakdown. Tests: 6 backend + 3 frontend. Catatan: drag-and-drop
> di-skip demi aksesibilitas (tap-to-pair); bisa jadi polish lanjutan.

### 6.3 Gamification (lihat `GAMIFICATION.md`)
Jalur B (hybrid) disetujui tim. Fase 1 (XP/streak/level) sudah selesai.
Pembagian Fase 2-4 ada di `GAMIFICATION_TASKS.md`.

### 6.4 Mobile app — Capacitor, Android-first (lihat `MOBILE.md`)
Bungkus React web yang ada jadi APK Android via Capacitor. **Keputusan**: Android dulu,
iOS ditunda. **Prasyarat**: backend deploy ke HTTPS publik (lihat #1.1).

> **React Native?** Dipertimbangkan demi native feel / smoothness. **Keputusan 2026-06-12:
> TIDAK untuk capstone.** RN = rewrite total frontend (React DOM ≠ RN: semua page, styling,
> router, chart, maskot ditulis ulang) → risiko jebol demo, lawan mandat "simpel + demo
> andal". Untuk app form/kuis/chart ini, gain native feel kecil; Capacitor + polish (#6.5) +
> plugin native (StatusBar/SplashScreen/Haptics) ≈ 85% native feel tanpa rewrite. RN ditaruh
> sebagai **v2 pasca-demo** (pakai **Expo + NativeWind** kalau jadi). Trade-off di decision log.

Roadmap mobile (ditunda, urut prioritas):
- **Push notification** (Capacitor Push + Firebase Cloud Messaging) — reminder streak,
  daily goal, level-up nudge. Nyambung ke Fase 4 (Desta) nudge logic. Nilai jual mobile
  terbesar untuk gamifikasi.
- iOS support — dibatalkan (tim tidak punya Mac); tinjau ulang jika ada akses Mac nanti
- Native storage + file picker (`@capacitor/preferences`, `@capacitor/filesystem`)
- Publish Play Store ($25 sekali bayar)
- Offline mode (rule-based generator + cache)

**Effort wrap dasar**: ~0.5-1 hari (setelah backend ter-deploy). Push notification: +1-2 hari.

### 6.5 Mobile polish — bikin web terasa "native" di Android (BARU 2026-06-08)
**Owner: Ravi (frontend)**

Track polish khusus mobile, melengkapi wrap Capacitor (#6.4). Dipisah menjadi yang **bisa dikerjakan sekarang** (web-responsive murni, tanpa shell Capacitor) vs yang **butuh shell Capacitor dulu**.

**A. Web-responsive & touch — ✅ SELESAI 2026-06-14 (branch `feat/mobile-polish-6.5a`):**
- ✅ **Audit responsif** 320 / 375 / 430px — diverifikasi via Playwright: **0 overflow horizontal** di `/`, `/app`, `/profil`, `/riwayat`, `/pengaturan`, `/progress`. Nav padding `px-4 sm:px-6`; `StatTile`/`ResultSummary`/hero diperkecil di mobile supaya angka besar / kata panjang tidak jebol.
- ✅ **Touch target** ≥ 44px (40px untuk pill nav padat): avatar UserMenu + item dropdown, ThemeToggle, SourceTypeTabs, QuestionPills, dan semua CTA utama (submit home, kuis prev/next/submit/jump, result, daily challenge, progress, sample, logout).
- ✅ **Jangan andalkan hover**: `active:`/pressed state ditambah di semua kontrol yang sebelumnya cuma `hover:`.
- ✅ **Keyboard mobile**: sudah benar dari sebelumnya — textarea `autocapitalize`/`autocorrect`, input URL `inputmode`/`enterkeyhint`, font input 16px (no auto-zoom).
- ✅ **Safe-area**: header/main sudah pakai `safe-pt`/`safe-px` + `viewport-fit=cover`; ditambah **bottom bar kuis** (`safe-px` + `pb-[calc(1rem+env(safe-area-inset-bottom))]`) yang tadinya ketutup gesture-nav.

**B. Capacitor-native polish — butuh #6.4 dulu:**
- **StatusBar plugin**: warna & style status bar ikut tema light/dark.
- **SplashScreen plugin**: splash ber-brand, hide saat app siap.
- **Hardware back (Android)** via `@capacitor/app`: back = navigasi dalam app / konfirmasi keluar saat di root.
- **Keyboard plugin**: resize mode supaya input tidak ketutup keyboard.
- **Haptics** (opsional): getar halus saat pilih jawaban / submit / level-up.

**C. Performa mobile:**
- **Code-split rute** (lazy `import()` per page) — bundle sekarang ~1MB (lihat warning build), berat di jaringan mobile. Lazy-load dep berat (canvas-confetti, chart).
- Target CWV mobile + TTI cepat di 3G/4G.

**Alternatif ringan — PWA dulu:** sebelum (atau selain) Capacitor, tambah `manifest.json` + service worker supaya "Add to Home Screen" + offline shell jalan. Jalur tercepat ke "berasa app" tanpa build Android. Capacitor tetap diperlukan untuk push notification (#6.4) yang di Android tidak andal lewat PWA.

**Effort**: A ~0.5-1 hari (bisa segera) · B ~0.5 hari (setelah wrap) · C ~0.5 hari · PWA ~0.5 hari.

### 6.6 AI Chatbot Asahi — game-dialog (BARU 2026-06-12)
**Owner: TBD · ⚠️ butuh persetujuan tim (scope expansion)**

> CLAUDE.md menandai chatbot/AI canggih sebagai *Out of Scope*. Masuk sebagai **post-MVP**
> yang disepakati (pola seperti login #4.7), HANYA setelah MVP inti (kuis→hasil) solid.

Asahi sebagai teman belajar — **dialog terkekang (game-style)**, bukan chat bebas, supaya
murah/aman/on-brand.
- **Model**: GitHub Models (gratis, auth via **GitHub PAT**) — mis. `gpt-4o-mini`. Free tier
  untuk prototipe, ada rate limit (bukan skala produksi besar).
- **Arsitektur**: Frontend (UI dialog) → `POST /chat` (FastAPI) → ambil konteks user dari DB
  (**scoped ke user login saja**) + system prompt → panggil GitHub Models (**PAT di env server
  `GITHUB_TOKEN`**) → filter output → reply. **PAT server-side only — JANGAN `VITE_`**
  (kalau ke frontend, akun GitHub bocor).
- **Safeguard**: rate limit (`slowapi`), authz konteks DB per-user, input validation +
  anti prompt-injection, system prompt kunci persona BRAND voice + batas topik (belajar/kuis),
  tolak off-topic/berbahaya. **Jangan klaim "AI tutor canggih"** (aturan produk CLAUDE.md).
- **Desain**: respons pendek in-character + **tombol pilihan** (suggested replies), batasi
  giliran → hemat kuota & terasa "game".

**Effort**: ~1-2 hari (endpoint + system prompt + UI dialog + safeguard).
**Prasyarat**: MVP solid + sepakat tim. Catatan klarifikasi: "PAT akses database" itu keliru —
PAT hanya untuk model AI; akses DB terpisah (backend query Neon).

---

## Saran prioritas

**▶ Prioritas terkini (2026-06-12, updated) — urut kerjakan dari atas:**
1. ✅ **Maskot (#4.9)** — SELESAI (7 ekspresi front-facing, ter-wire).
2. ✅ **AI Chatbot Asahi (#6.6)** — BUILT this session (free-chat + memori Neon + konteks kuis +
   rate-limit + material pre-check). Sisa: set `GITHUB_TOKEN` di secret HF Space saat deploy.
3. **▶ BERIKUTNYA: Deploy publik (#1.1)** + **demo GIF/screenshot (#1.2)** — ROI capstone terbesar.
   Prasyarat: merge `feat/mascot-asahi-v2` → main; set HF Space secret `GITHUB_TOKEN` (chat).
4. **Capacitor wrap (#6.4)** — kalau mobile bagian demo. ~1 hari. (Bukan React Native.)
5. **React Native** — **v2 pasca-demo**, jangan sekarang (lihat #6.4 + decision log).

> Yang **bukan** sekarang: RN migration. Fokus: deploy → demo.

**Saat demo capstone deket (≤ 1 minggu)**:
1. **#2 Doc sync** (~2 jam, wajib)
2. **#1 Deploy public URL** (~3 jam, audience impact terbesar)
3. **#1.2 Demo video/screenshots** (~1 jam)

**Pasca demo, kalau lanjut sebagai produk**:
4. **#3.1 Frontend tests** (reliability)
5. **#4.1 History page** + **#4.2 Share URL** (meaningful feature add)
6. **#4.4 Per-topic mastery** (DNA capstone tetap utuh, value naik signifikan)

**Bisa di-defer ke versi 2**:
- #3.3 Smart distractors (real ML upgrade)
- #6 Bigger directions

---

## Decision log

| Tanggal | Keputusan | Reason |
|---|---|---|
| 2026-05-18 | (OPEN) | Dokumen dibuat. Menunggu Ravi pilih prioritas pasca push hari ini. |
| 2026-06-06 | Tambah 3 fitur: landing page (#4.5), onboarding tour (#4.6), login OAuth (#4.7) | Ravi mau fokus polishing; fitur frontend-heavy dibagi ke tim. |
| 2026-06-06 | Owner: Landing→Audry, Tour→Desta, Login→Ravi (full), polish semua→Ravi | Tiap teman bangun frontend fitur-nya end-to-end; Ravi review + polish. Login OAuth ringan jadi Ravi pegang sendiri. |
| 2026-06-06 | Login pakai third-party OAuth (Google/Supabase), bukan auth custom | Login "beneran" tanpa hand-roll password/JWT; scope expansion dari CLAUDE.md disepakati sebagai post-MVP. |
| 2026-06-06 | Provider login: **Google Identity Services (GIS) langsung**, bukan Supabase Auth | GIS gratis tanpa kuota & nol layanan eksternal baru (sejalan KISS/anti over-engineering). Hindari risiko Supabase free-tier auto-pause (~7 hari idle) yang bisa ganggu demo. Verify ID token via public key Google. |
| 2026-06-06 | Ariq ambil track Data & Quality: #3.2 + #3.4 + #6.2 | Ariq tidak ambil fitur baru; kerjakan task roadmap lama yang belum jalan, sesuai domain Data & Analisis. |
| 2026-06-07 | Login (#4.7) selesai & deployed (Neon migrated, HF + Vercel env set) | Verified live: `/auth/google`→401 untuk token invalid, guest mode utuh. Hotfix `requests` dep (PR #8) setelah Space crash di rebuild pertama. |
| 2026-06-07 | Tambah cluster #4.8 "User Hub & fitur akun" (profil, settings, history, leaderboard, edit preferensi, goal, bookmark, badge, daily challenge, share/export) | Lanjutan natural dari login. Owner Ravi (frontend), Ariq review data layer untuk endpoint baru. Dibatch: User Hub dulu (mostly FE), backend-heavy menyusul. |
| 2026-06-08 | Kirim #4.8 Batch 1+3 (User Hub + Daily Challenge + Streak), #3.1 testing (Vitest, coverage ~82%), polish §5 (skeleton, drag-drop PDF, reduced-motion) — semua merged ke main | Eksekusi item Ravi-owned berurutan; fix bug migrasi prod Neon (kolom `topic`) yang sempat bikin history/analytics 500. |
| 2026-06-08 | Tambah track #6.5 "Mobile polish" (responsif/touch, Capacitor-native, performa, opsi PWA) | Polish khusus mobile dipisah dari wrap Capacitor (#6.4); bagian web-responsive bisa dikerjakan sekarang tanpa shell. Owner Ravi. |
| 2026-06-12 | Maskot Asahi v2 (#4.9) via **puppet** (inpaint alis+mulut, mata dilindungi) + pose gesture (SeaArt consistency app), semua **front-facing**, base full-hair transparan (rembg). Live: mid/wave/think; wired ke hero/result/loading. Branch `feat/mascot-asahi-v2`. | AI-render full-image tiap ekspresi drift wajahnya; puppet jaga konsistensi sambil pertahankan look anime yang disukai tim. |
| 2026-06-12 | **AI Chatbot Asahi (#6.6)** diterima sebagai **POST-MVP** (butuh sepakat tim). GitHub Models (PAT server-side) + dialog terkekang + safeguard. | Asahi jadi teman belajar; jalur gratis (GitHub Models) & terkekang supaya aman/murah/on-brand. Scope expansion CLAUDE.md, pola seperti login #4.7. |
| 2026-06-12 | Mobile: tetap **Capacitor** untuk demo; **React Native ditunda ke v2 pasca-demo**. | RN native feel nyata tapi gain kecil untuk app form/kuis ini; cost = rewrite total frontend → risiko jebol demo + lawan mandat "simpel + demo andal". Capacitor reuse 100% kode (~1 hari). RN nanti pakai Expo + NativeWind. |
| 2026-06-14 | **#6.5-A Mobile polish (web-responsive & touch) SELESAI** — branch `feat/mobile-polish-6.5a`. Touch target ≥44px, `active:` states, safe-area bottom bar kuis, responsif 320/375/430 (0 overflow, verified Playwright). | Bagian yang bisa dikerjakan tanpa shell Capacitor; prasyarat ringan untuk #6.4 wrap. §6.5-B (StatusBar/Splash/Haptics) & §6.5-C (code-split) menyusul. Typecheck + 100 test + build hijau. |
| 2026-06-14 | **Kualitas quiz (#3.5)**: bug "jawaban benar = kata terpanjang" diperbaiki **answer-aware** (branch `feat/quiz-answer-aware` + HF Space `9e9e99b/2aa8bc7` live). Pilih span jawaban dulu → highlight → guard konsistensi (angka/nama, anti-superlatif, anti-verb) → fallback cloze koheren → distraktor sekategori. | Fine-tune lama ternyata **plain QG** (tak ber-`<hl>`), jadi model tak patuh span jawaban. Inference-fix menutup ~70-75%; untuk presisi penuh, notebook di-upgrade ke **answer-aware v2** (latih dengan `<hl>`, token khusus) — Audry jalankan di Colab lalu Factory rebuild. |

---

## Reference

- `GAMIFICATION.md` — gamification options (3 jalur)
- `BRAND.md` — voice, copy library
- `CLAUDE.md` — scope lock
- `PRD.md` — capstone requirements
- `TASKS.md` — original 5-week plan
- `API.md` — HTTP contract
- `ARCHITECTURE.md` — internal structure
