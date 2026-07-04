# Gamification — Pembagian Task Tim

**Status**: Aktif. Tim sudah setuju jalur Hybrid (Jalur B di GAMIFICATION.md).
**Database**: Neon Postgres (akses lewat FastAPI, identitas anonymous device ID).
**Last updated**: 2026-05-19

Acuan: `GAMIFICATION.md` (keputusan jalur), `backend/app/db/README.md` (setup DB + kontrak endpoint).

---

## Status saat ini

**Backend Fase 1 SELESAI** (XP/streak/level engine + persistence + 4 endpoint + 9 unit test):
- `app/services/xp_engine.py` — rumus XP/streak/level (pure, teruji)
- `app/services/achievements.py` — 6 badge deterministik
- `app/services/gamification_service.py` — persistence
- `app/routes/gamification.py` — endpoint
- `app/db/` — models, session, schema, init

**Sisa**: Fase 2 (Audry), Fase 3 (Ariq), Fase 4 (Desta). Ravi mengerjakan frontend di tiap fase.

---

## Fase 1 — Core loop (XP + streak + level)

| Task | Owner | Acceptance Criteria | Status |
|---|---|---|---|
| Backend XP/streak/level engine + endpoint | Desta + Ariq | XP dihitung server-side, 4 endpoint jalan, unit test lulus | Selesai |
| Neon setup + migration | Ariq | Tabel ada di Neon, `GET /gamification/stats` balikin data | Selesai (DB sudah dikonfigurasi) |
| Frontend: device ID + API client | Ravi | UUID di localStorage, header `X-Device-Id` terkirim, method `recordAttempt`/`getStats` | Selesai |
| Frontend: trigger record setelah submit | Ravi | Setiap submit kuis memanggil `record-attempt` | Selesai |
| Frontend: tampilkan XP/level/streak di nav | Ravi | Nav menampilkan level, progress XP, streak (Lucide icon, no emoji) | Selesai |
| Frontend: feedback "XP +N" / "Level up" di result | Ravi | Banner reward muncul setelah submit (XP, level up, badge baru) | Selesai |

> **Fase 1 SELESAI end-to-end (backend + frontend), terverifikasi dengan Neon.**
> Verifikasi browser 2026-05-19: nav menampilkan Lv + XP + streak, RewardBanner muncul di result page.

---

## Bug fixes & tech debt (sambil jalan)

| Task | Owner | Detail | Status |
|---|---|---|---|
| CORS: izinkan header `X-Device-Id` | Ravi | Tanpa ini browser preflight memblokir semua call gamifikasi (curl lolos, browser tidak) | Selesai |
| Classifier guardrail: skor rendah tidak boleh "high" | Ravi (tambal) | ML sempat klasifikasi 20% sebagai "high" untuk waktu cepat (29s) | Selesai (sabuk pengaman, dipertahankan) |
| Retrain classifier dengan range waktu realistis | Ravi (ambil alih) | Root cause: `data_generation.py` melatih `time_taken_seconds` di range (60, 1800). Diubah ke `(10, 1800)` dan di-retrain. Model sekarang benar tanpa perlu guardrail (akurasi 94.1%, sklearn 1.8.0, tidak ada version mismatch lagi). | Selesai |

---

## Fase 2 — Audry (Quiz Generator): Tingkat Kesulitan Adaptif + Riwayat Kuis

Owner utama: **Audry**. Frontend pendukung: Ravi.
Tema: gamifikasi yang menyentuh generator kuis (domain Audry).

| Task | Owner | Acceptance Criteria |
|---|---|---|
| Generator: tingkat kesulitan adaptif berdasarkan level user | Audry | Makin tinggi level, kuis makin menantang (jumlah soal / kompleksitas naik). Generator menerima parameter difficulty |
| Generator: integrasi riwayat (regenerate dari kuis lama) | Audry | `quiz_id` konsisten; kuis bisa di-regenerate dari halaman riwayat |
| Generator: daily challenge (opsional) | Audry | Satu kuis spesial per hari dengan bonus XP |
| Frontend: indikator difficulty + tombol regenerate dari riwayat | Ravi | Difficulty terlihat di UI; regenerate dari riwayat berfungsi |

---

## Fase 3 — Ariq (Data & Analisis): Analitik + Mastery per Topik

Owner utama: **Ariq**. Frontend pendukung: Ravi.
Tema: analisis data (domain Ariq). Selaras dengan judul capstone "Deteksi Tingkat Pemahaman".

| Task | Owner | Acceptance Criteria |
|---|---|---|
| Endpoint analitik (rata-rata skor, tren skor over time, jumlah kuis) | Ariq | Endpoint balikin agregat siap pakai untuk dashboard |
| Per-topic mastery: tag topik per kuis + agregasi pemahaman per topik | Ariq | Skor per topik terlacak; topik lemah teridentifikasi (butuh sumber tag topik, koordinasi dgn Audry) |
| Ringkasan di history endpoint | Ariq | `GET /gamification/history` + ringkasan (total kuis, rata-rata skor) |
| Frontend: dashboard tren + halaman mastery per topik | Ravi | Grafik tren skor; daftar pemahaman per topik |

---

## Fase 4 — Desta (Logic, Insight, Recommendation): Achievements + Daily Goal + Nudge

Owner utama: **Desta**. Frontend pendukung: Ravi.
Tema: aturan & logika deterministik (domain Desta, sama seperti insight/recommendation/classifier).

| Task | Owner | Acceptance Criteria |
|---|---|---|
| Perluas achievement rules (lebih banyak badge deterministik) | Desta | Badge baru di `achievements.py` + unit test |
| Daily goal logic (target XP harian + progress + reset harian) | Desta | Logika deterministik; progress harian tersedia di `/stats` |
| Gamified nudges (rekomendasi berbasis state gamifikasi) | Desta | Contoh: "tinggal 50 XP ke level berikutnya", "jaga streak-mu hari ini" |
| Frontend: daily goal ring, achievements page, nudge display | Ravi | UI progress harian + halaman badge (locked/unlocked) + nudge |

---

## Catatan teknis untuk tim

- **Identitas**: anonymous device ID (UUID di localStorage, header `X-Device-Id`). Tidak ada login. Skema sudah siap di-upgrade ke auth nanti tanpa migrasi.
- **Anti-cheat**: XP/streak/level dihitung di backend, bukan client. Jangan pindahkan logika ini ke frontend.
- **Brand voice**: Lucide icon bukan emoji (`Zap` XP, `Flame` streak, `TrendingUp` level, `Trophy`/`Star`/`Sparkles` badge). Tetap "kamu", tetap honest (bukan "GREAT JOB!!!").
- **Graceful degradation**: kalau `DATABASE_URL` kosong, endpoint gamifikasi balikin 503 dan fitur kuis inti tetap jalan. Frontend harus handle 503 dengan menyembunyikan UI gamifikasi, bukan crash.

---

## Catatan capstone

Ekspansi ini (DB + identitas user) keluar dari scope proposal awal. **Sudah/akan dibahas dengan advisor (Rosyiidah) di sesi 23 Mei.** Kalau advisor minta scope dikembalikan, gamifikasi bisa di-toggle off via `DATABASE_URL` kosong tanpa mengganggu demo kuis inti.
