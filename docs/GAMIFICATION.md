# Gamification Direction. Asahlagi

**Status**: OPEN. No decision made.
**Owner**: Ravi (Frontend lead, idea originator)
**Created**: 2026-05-18
**Last updated**: 2026-05-18

---

## 1. Context

Ravi mengajukan ide untuk menjadikan Asahlagi terasa seperti Duolingo (gamification, engagement-driven). Dokumen ini menangkap konteks, trade-off, dan jalur opsi yang tersedia, supaya keputusan bisa diambil dengan info lengkap (bukan reaktif).

Dokumen ini **bukan komitmen implementasi**. Tujuannya: align dulu antara Ravi, tim backend, dan pembimbing capstone sebelum eksekusi.

---

## 2. Kenapa ini penting (perlu dipikir baik-baik)

Capstone TP-G005 punya identitas yang sudah lock di proposal akademik dan dokumen tim:

| Aspek | Identitas saat ini | Identitas Duolingo |
|---|---|---|
| **Judul formal** | Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data | Bahasa/skill learning game |
| **Tujuan utama** | Alat ukur (assessment + analitis) | Engagement loop (habit-forming) |
| **DNA** | Honest, calm, library-vibe (per BRAND.md §6) | Energetic, encouraging, gamified |
| **Output kunci** | Score + understanding level + insight + recommendation | XP + streak + level + badges |
| **Persistence** | In-memory, single session | Persistent user state, riwayat panjang |
| **User** | Anonim, satu sesi pakai | Akun, pengguna jangka panjang |

Dua DNA ini tidak fundamental kontradiktif (game pendidikan juga butuh measurement), tapi **prioritas berbeda**. Pilihan jalur menentukan seberapa banyak elemen DNA Duolingo masuk tanpa mengorbankan deliverable capstone.

---

## 3. State saat ini (snapshot 2026-05-18)

- Backend: FastAPI, in-memory storage (`quiz_storage.py` = `dict`), 3 PIC backend (Audry / Ariq / Desta) sudah selesai.
- Frontend: React + Vite + Tailwind, end-to-end flow jalan (text / URL / PDF input → quiz → result).
- Tests: 43 passed di backend, typecheck + build hijau di frontend.
- Brand identity (BRAND.md) sudah final: voice "honest tapi tidak cheesy", anti "Yuk semangat!", anti emoji excessive, "kamu" bukan "Anda".
- Scope per CLAUDE.md: input → kuis → hasil. **Out of scope**: auth, complex DB, full LMS, gamification.
- Timeline plan (TASKS.md): 5 minggu, deadline original 2026-05-04. Sekarang sudah 2026-05-18, jadi dalam masa polishing / pre-demo.

---

## 4. Pertanyaan terbuka (Ravi / tim perlu jawab)

Tanpa ini, semua opsi di bawah cuma teori.

1. **Tujuan**: gamification untuk **memenangkan demo capstone**, atau **roadmap produk pasca-capstone** (Asahlagi jadi produk sendiri post-submission)?
2. **Timeline demo capstone**: tanggal pasti? Berapa hari tersisa?
3. **Tim alignment**: Audry, Ariq, Desta sudah tahu rencana ini? Mereka setuju? Bagian mereka stabil atau perlu di-rework?
4. **Pembimbing akademik**: setuju kalau project di-pivot atau di-extend? Atau lebih aman pertahankan scope original?
5. **Fitur Duolingo yang paling kamu suka**: yang mana yang bikin "klik" buat kamu? Streak? XP? Skill tree? Mascot? Hearts? Daily goal? Animasi/sounds? Leaderboard? (Inventori lengkap di §7.)

---

## 5. Tiga jalur opsi

### Jalur A. Demo polish gamified (1 hingga 3 jam)

**What**: tambah lapis gamification ringan tanpa mengubah struktur project.

Konkretnya:
- Streak counter via `localStorage` (hitung hari berturut-turut pakai aplikasi)
- XP per quiz (formula sederhana, contoh: `score_percentage × 10 + streak_bonus`)
- Total XP tampil di nav atau home page
- Animasi celebration di result page (confetti subtle saat skor tinggi, smooth fade saat skor rendah)
- "Personal best" per topik (tracking di localStorage berdasarkan hash materi)
- Sound effect optional di submit (bisa di-mute)

**Yang tidak diubah**:
- Backend (zero change)
- Database (tetap in-memory)
- Authentication (tetap tidak ada)
- Capstone identity (tetap "Sistem Deteksi Tingkat Pemahaman")
- BRAND.md voice (tetap calm, tidak Duolingo cheesy)

**Risk**:
- Tidak betulan "Duolingo". Lebih ke "engagement layer".
- LocalStorage hilang kalau user clear browser data atau pakai incognito.

**Cocok untuk**: demo capstone yang feel-nya lebih hidup tanpa mengganggu deliverable.

---

### Jalur B. Hybrid product (3 hingga 7 hari)

**What**: tambah profile + riwayat + achievement system, tapi tanpa pivot total.

Konkretnya:
- User profile via localStorage (nama, avatar emoji-free pakai inisial atau Lucide icon, level)
- Quiz history (riwayat 10-20 quiz terakhir)
- Level system (level naik tiap kelipatan XP tertentu)
- Achievement / badge system (deterministic, contoh: "Quiz pertama", "5 quiz dalam seminggu", "Skor sempurna", "10 quiz dalam 1 topik")
- Daily goal (target XP per hari, configurable)
- Halaman baru: `ProfilePage`, `HistoryPage`, `AchievementsPage`

**Yang berubah**:
- Frontend: 3 halaman baru, navigation update, profile drawer/page
- Backend: optional (bisa tetap in-memory, profile data di-store client-side)
- BRAND.md: perlu refresh voice untuk celebrate moments (tetap honest, tapi lebih engagement-friendly)

**Yang tidak diubah**:
- Capstone deliverable (measurement tool tetap core)
- Auth (masih client-side only)
- Database (tetap optional)

**Risk**:
- Tim backend sudah selesai. Kalau tidak butuh perubahan backend = aman; kalau butuh = perlu koordinasi.
- Lebih banyak halaman = lebih banyak design + copy work.
- Scope creep risk (gamification rabbit hole: skill tree, leaderboard, friend system, dll).

**Cocok untuk**: capstone yang sudah aman (demo lewat), lalu Asahlagi dilanjutkan sebagai roadmap produk pribadi.

---

### Jalur C. Pivot Duolingo-clone (minggu-an, mungkin 2-4 minggu)

**What**: rebuild project sebagai full learning game platform.

Konkretnya:
- User accounts + auth (Supabase Auth, Clerk, atau setara)
- Database persistent (Postgres / Supabase / SQLite untuk MVP)
- Lessons curriculum (curated atau user-generated)
- Hearts / lives system (terbatas, regenerate over time)
- Leaderboard / leagues (weekly competition)
- Streak freeze items (premium-style mechanics)
- Mascot character (illustrated, animations)
- Sound design + animations (Lottie, motion library)
- Skill tree visual

**Yang berubah** (besar):
- Capstone identity: judul perlu di-rebrand, proposal akademik perlu di-update
- Tim coordination: Audry / Ariq / Desta perlu re-skoping. Classifier + insight + recommendation existing jadi "feature lama" yang sebagian dipakai sebagian dibuang
- Backend: full rewrite untuk persistent + multi-user
- Frontend: design system perlu diperbarui (Duolingo aesthetic vs Supabase aesthetic sekarang)
- BRAND.md: pivot total. Voice baru, palette baru kemungkinan
- Timeline: blowback ke deadline capstone

**Risk** (tinggi):
- Mengancam deadline capstone.
- Coordinasi tim ulang dari 0.
- Existing work (PRD, ARCHITECTURE, DESIGN, BRAND, TASKS, semua dokumentasi tim) perlu di-rewrite besar-besaran.
- Pembimbing akademik kemungkinan tidak menyetujui pivot di akhir capstone.

**Cocok untuk**: pasca-capstone, kalau Ravi serius ingin bikin Asahlagi jadi produk komersial. Bukan untuk window saat ini.

---

## 6. Rekomendasi default

**Saran**: **Jalur A** sekarang (untuk demo), lalu setelah capstone lulus baru pertimbangkan **B**. Jalur **C** sebaiknya post-graduate.

Alasan:
1. Capstone perlu di-ship dulu dengan identitas yang sudah disetujui pembimbing.
2. Tim backend sudah selesai. Mengubah sekarang = mengorbankan momentum.
3. BRAND.md voice ("honest, anti-cheesy") justru bisa jadi differentiator dari Duolingo. Pertahankan, tapi tambah dimensi engagement secukupnya.
4. Brand mechanic "asah lagi" di recommendation sudah engagement-friendly tanpa perlu mascot. Itu sudah jadi mini gamification natural.

---

## 7. Inventory fitur gamification (referensi)

Tabel di bawah mapping fitur ke jalur. Centang = fit naturally di jalur itu.

| Fitur | A (Demo polish) | B (Hybrid) | C (Pivot) | Catatan |
|---|:-:|:-:|:-:|---|
| Streak counter | y | y | y | localStorage di A; sync DB di C |
| XP per quiz | y | y | y | Formula sederhana di A; lebih kompleks di B/C |
| Total XP display | y | y | y |  |
| Level system | . | y | y | Butuh threshold table |
| Daily goal | . | y | y | Butuh UI tracker |
| Hearts / lives | . | . | y | Butuh state management + regen logic |
| Achievement / badges | . | y | y | Deterministic rules. Bisa pakai Lucide icons (no emoji per memory) |
| Quiz history | . | y | y | Butuh persistence (localStorage di B, DB di C) |
| Leaderboard | . | . | y | Butuh multi-user + auth |
| Skill tree | . | . | y | Butuh curriculum design |
| Mascot | . | . | y | Illustrated character, animations |
| Sound effects | y | y | y | Subtle di A (submit ping, success chord). Lebih banyak di C |
| Confetti / celebration animation | y | y | y | CSS-only di A. Library di B/C |
| Personal best tracking | y | y | y | Per-topic hash di localStorage |
| Streak freeze items | . | . | y | Premium-style mechanic |
| Friend system / social | . | . | y | Auth + relations table |

---

## 8. Implikasi ke dokumen lain

| Dokumen | Jalur A | Jalur B | Jalur C |
|---|---|---|---|
| `BRAND.md` | minor update §6 (voice can do mini-celebration) | refresh §6, §7 (celebrate templates) | rewrite |
| `PRD.md` | tambah section "engagement layer" | tambah section "user profile, history, achievements" | rewrite scope |
| `ARCHITECTURE.md` | tidak berubah | tambah note: client-side state (no backend impact) | rewrite (auth, DB, services baru) |
| `DESIGN.md` | tambah token untuk celebration colors | tambah pages, badge designs | rewrite (Duolingo aesthetic) |
| `CLAUDE.md` | tidak berubah | scope update | rewrite product identity |
| `API.md` | tidak berubah | tidak berubah (atau optional: endpoint history) | rewrite (auth, profile, leaderboard endpoints) |
| `TASKS.md` | tambah 1 ticket | tambah 5-8 ticket | rewrite roadmap |

---

## 9. Brand voice considerations

Memory rule (Ravi's preference, persistent): **no emojis, no em dashes in UI. Lucide icons instead of emojis**. Gamification umumnya pakai banyak emoji (streak fire 🔥, XP bolt ⚡, achievement star ⭐). Untuk Asahlagi:

- Pakai Lucide icons: `Flame` untuk streak, `Zap` untuk XP, `Trophy` untuk achievement, `Sparkles` untuk celebration.
- Voice tetap "kamu" bukan "Anda".
- Voice tetap honest. Misal saat skor rendah: "Pemahamanmu masih perlu diasah" (bukan "JANGAN MENYERAH!").
- Brand callback "asah lagi" tetap dipakai di recommendation.

---

## 10. Action items

- [ ] Ravi: jawab 4 pertanyaan di §4 (di chat atau update doc ini).
- [ ] Ravi: ngobrol singkat dengan tim backend (Audry / Ariq / Desta), kasih heads-up.
- [ ] Ravi: konfirmasi ke pembimbing akademik kalau ada perubahan scope.
- [ ] Setelah info lengkap: pilih jalur (A / B / C), update bagian §11.
- [ ] Kalau A: scope 1 ticket frontend (~3 jam), schedule.
- [ ] Kalau B: scope 5-8 tickets, schedule sprint pasca-capstone.
- [ ] Kalau C: schedule full re-planning session dengan tim.

---

## 11. Decision log

| Tanggal | Keputusan | Reason |
|---|---|---|
| 2026-05-18 | (OPEN) | Dokumen dibuat. Menunggu input dari Ravi + tim. |

---

## 12. Reference

- `BRAND.md` §6 (voice & tone)
- `BRAND.md` §7.7 (recommendation brand mechanic — "asah lagi" callback)
- `CLAUDE.md` "Product Rules" (honesty, anti-pretension)
- `CLAUDE.md` "Out of Scope" (auth, complex DB out)
- `PRD.md` (capstone scope lock)
- `TASKS.md` (5-week timeline)
